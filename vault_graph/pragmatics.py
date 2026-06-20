"""Pragmatische Sicht und Triangulation gegen die Topologie.

Die pragmatische Sicht ist die vom Menschen gelebte Ordnung des Vaults, hier
die Ablage in Top-Level-Ordnern und die Vergabe von Tags. Sie ist kostenfrei
aus den vorhandenen Knoten-Attributen berechenbar, ohne Embeddings und ohne
externen Lauf.

Die Triangulation kreuzt zwei Sichten, die topologische Louvain-Community und
die pragmatische Ordner-Partition. Damit lassen sich drei Aussagetypen sauber
trennen:

- Befund: eine Community deckt sich weitgehend mit einem Ordner (hohe Reinheit).
  Die Topologie bestaetigt die Ablage, das ist datengestuetzt und reproduzierbar.
- Hypothese: eine Community streut quer ueber Ordner (niedrige Reinheit). Ein
  topologischer Cluster ohne pragmatische Stuetze, ein Kandidat fuer ein
  Querthema, das die Ordnerstruktur nicht abbildet.
- Diagnose: ein einzelner Knoten liegt in einem anderen Ordner als der, der
  seine sonst reine Community dominiert. Kandidat fuer woanders vernetzt als
  abgelegt, eine Pflege-Auffaelligkeit.

Gesamtmasse: die size-gewichtete mittlere Community-Reinheit und die Normalized
Mutual Information (NMI) zwischen Community- und Ordner-Partition. NMI ist 1,
wenn beide Partitionen identisch sind, und 0, wenn sie unabhaengig sind.

Privacy: die pragmatische Partition nutzt nur das erste Pfadsegment (Top-Level-
Ordner), nie den Dateinamen, fuer Business-Knoten also Business. Die Tag-Sicht
laesst anonymisierte Knoten aus, sie tragen keine exponierten Tags.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

import networkx as nx

from vault_graph.parse import normalize_tags


def analyze_pragmatics(
    graph: nx.DiGraph,
    topology: dict[str, Any],
    *,
    purity_high: float = 0.7,
    purity_low: float = 0.5,
    outlier_min_purity: float = 0.6,
    tag_min_count: int = 5,
) -> dict[str, Any]:
    """Berechnet die pragmatische Sicht und die Triangulation gegen die Topologie.

    Returns:
        dict mit Schluesseln:
        - folder_of: {node_key: top_level_folder}
        - community_folder: {community_id: {size, dominant_folder, purity,
            distribution}}
        - folder_community: {folder: {size, dominant_community, share,
            n_communities}}
        - outliers: list[dict]  (Knoten in fremdem Ordner trotz reiner Community)
        - tag_cohesion: {tag: {n_nodes, n_communities, dominant_community,
            concentration}}
        - stats: {n_folders, nmi_community_folder, mean_community_purity,
            n_outliers, n_pure_communities, n_cross_communities}
    """
    communities: dict[str, int] = topology["communities"]
    folder_of = {
        key: _top_folder(attrs.get("path", ""))
        for key, attrs in graph.nodes(data=True)
    }

    community_folder = _community_folder_triangulation(communities, folder_of)
    folder_community = _folder_community_triangulation(communities, folder_of)
    outliers = _find_outliers(
        graph, communities, folder_of, community_folder, outlier_min_purity
    )
    tag_cohesion = _tag_cohesion(graph, communities, tag_min_count)

    total = sum(cf["size"] for cf in community_folder.values())
    mean_purity = (
        sum(cf["purity"] * cf["size"] for cf in community_folder.values()) / total
        if total else 0.0
    )
    nmi = _nmi(communities, folder_of)

    return {
        "folder_of": folder_of,
        "community_folder": community_folder,
        "folder_community": folder_community,
        "outliers": outliers,
        "tag_cohesion": tag_cohesion,
        "thresholds": {
            "purity_high": purity_high,
            "purity_low": purity_low,
            "outlier_min_purity": outlier_min_purity,
            "tag_min_count": tag_min_count,
        },
        "stats": {
            "n_folders": len(set(folder_of.values())),
            "nmi_community_folder": nmi,
            "mean_community_purity": mean_purity,
            "n_outliers": len(outliers),
            "n_pure_communities": sum(
                1 for cf in community_folder.values() if cf["purity"] >= purity_high
            ),
            "n_cross_communities": sum(
                1 for cf in community_folder.values() if cf["purity"] < purity_low
            ),
        },
    }


# --- intern ------------------------------------------------------------------


def _top_folder(path: str) -> str:
    """Erstes Pfadsegment als Top-Level-Ordner. Dateien in der Wurzel ergeben
    den Sammelnamen (Wurzel). Nie der Dateiname, daher kein Privacy-Leak."""
    if not path:
        return "(Wurzel)"
    parts = path.split("/")
    if len(parts) <= 1:
        return "(Wurzel)"
    return parts[0]


def _community_folder_triangulation(
    communities: dict[str, int], folder_of: dict[str, str]
) -> dict[int, dict[str, Any]]:
    """Pro Community den dominanten Ordner und die Reinheit."""
    members_by_comm: dict[int, list[str]] = {}
    for key, cid in communities.items():
        members_by_comm.setdefault(cid, []).append(key)

    result: dict[int, dict[str, Any]] = {}
    for cid, members in members_by_comm.items():
        folder_counts = Counter(folder_of.get(m, "(Wurzel)") for m in members)
        dominant, dom_count = folder_counts.most_common(1)[0]
        result[cid] = {
            "size": len(members),
            "dominant_folder": dominant,
            "purity": dom_count / len(members),
            "distribution": dict(folder_counts),
        }
    return result


def _folder_community_triangulation(
    communities: dict[str, int], folder_of: dict[str, str]
) -> dict[str, dict[str, Any]]:
    """Pro Ordner die dominante Community und ihr Anteil."""
    members_by_folder: dict[str, list[str]] = {}
    for key, folder in folder_of.items():
        members_by_folder.setdefault(folder, []).append(key)

    result: dict[str, dict[str, Any]] = {}
    for folder, members in members_by_folder.items():
        comm_counts = Counter(communities.get(m, -1) for m in members)
        dominant, dom_count = comm_counts.most_common(1)[0]
        result[folder] = {
            "size": len(members),
            "dominant_community": dominant,
            "share": dom_count / len(members),
            "n_communities": len(comm_counts),
        }
    return result


def _find_outliers(
    graph: nx.DiGraph,
    communities: dict[str, int],
    folder_of: dict[str, str],
    community_folder: dict[int, dict[str, Any]],
    outlier_min_purity: float,
) -> list[dict[str, Any]]:
    """Knoten, die in einem anderen Ordner liegen als der, der ihre sonst reine
    Community dominiert. Nur Communities ab outlier_min_purity, sonst ist der
    Begriff Ausreisser nicht definiert."""
    outliers = []
    for key in graph.nodes:
        # Anonymisierte Business-Knoten zaehlen in den Aggregaten mit, werden
        # aber nicht einzeln als Pflege-Auffaelligkeit gelistet, konsistent mit
        # der Pflege-Triage.
        if graph.nodes[key].get("privacy_anonymized"):
            continue
        cid = communities.get(key)
        if cid is None:
            continue
        cf = community_folder.get(cid)
        if not cf or cf["purity"] < outlier_min_purity:
            continue
        own = folder_of.get(key, "(Wurzel)")
        if own != cf["dominant_folder"]:
            outliers.append({
                "key": key,
                "title": graph.nodes[key].get("title", key),
                "folder": own,
                "community": cid,
                "community_dominant_folder": cf["dominant_folder"],
                "community_purity": cf["purity"],
            })
    outliers.sort(key=lambda o: o["community_purity"], reverse=True)
    return outliers


def _tag_cohesion(
    graph: nx.DiGraph, communities: dict[str, int], tag_min_count: int
) -> dict[str, dict[str, Any]]:
    """Pro haeufigem Tag die Streuung ueber Communities. Ein konzentrierter Tag
    ist topologisch kohaerent, ein gestreuter ist ein Querschnitts-Tag.
    Anonymisierte Knoten werden ausgelassen."""
    tag_nodes: dict[str, list[str]] = {}
    for key, attrs in graph.nodes(data=True):
        if attrs.get("privacy_anonymized"):
            continue
        for tag in normalize_tags(attrs.get("frontmatter", {}) or {}):
            tag_nodes.setdefault(tag, []).append(key)

    result: dict[str, dict[str, Any]] = {}
    for tag, keys in tag_nodes.items():
        if len(keys) < tag_min_count:
            continue
        comm_counts = Counter(communities.get(k, -1) for k in keys)
        dominant, dom_count = comm_counts.most_common(1)[0]
        result[tag] = {
            "n_nodes": len(keys),
            "n_communities": len(comm_counts),
            "dominant_community": dominant,
            "concentration": dom_count / len(keys),
        }
    return result


def _nmi(labels_a: dict[str, Any], labels_b: dict[str, Any]) -> float:
    """Normalized Mutual Information zwischen zwei Partitionen auf derselben
    Knotenmenge. NMI = I(A;B) / sqrt(H(A) H(B)), in [0, 1]."""
    keys = [k for k in labels_a if k in labels_b]
    n = len(keys)
    if n == 0:
        return 0.0

    a = [labels_a[k] for k in keys]
    b = [labels_b[k] for k in keys]
    count_a = Counter(a)
    count_b = Counter(b)
    count_ab = Counter(zip(a, b))

    def entropy(counter: Counter) -> float:
        return -sum((c / n) * math.log(c / n) for c in counter.values() if c > 0)

    h_a = entropy(count_a)
    h_b = entropy(count_b)
    if h_a == 0.0 or h_b == 0.0:
        return 0.0

    mi = 0.0
    for (x, y), c in count_ab.items():
        p_xy = c / n
        p_x = count_a[x] / n
        p_y = count_b[y] / n
        mi += p_xy * math.log(p_xy / (p_x * p_y))

    return mi / math.sqrt(h_a * h_b)
