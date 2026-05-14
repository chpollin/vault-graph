"""Topology-Bericht.

Schreibt output/findings/topology-bericht.md mit den topologischen Befunden:
Centrality-Hubs, Louvain-Communities mit Mitgliedern, Brueckenknoten,
K-Core-Schichten. Alle Aussagen sind Befunde im Sinne von METHODIK.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx


TOP_N = 20
COMMUNITY_SAMPLE = 15


def write_topology_report(
    graph: nx.DiGraph,
    topology: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = _build_report(graph, topology)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _title_of(graph: nx.DiGraph, key: str) -> str:
    return graph.nodes.get(key, {}).get("title", key)


def _build_report(graph: nx.DiGraph, topology: dict[str, Any]) -> list[str]:
    centralities = topology["centralities"]
    communities = topology["communities"]
    community_sizes = topology["community_sizes"]
    modularity = topology["modularity"]
    k_core = topology["k_core"]
    bridges = topology["bridges"]
    stats = topology["stats"]

    lines: list[str] = []
    lines.append("# Topology-Bericht")
    lines.append("")
    lines.append(
        "Topologische Sicht auf den Linkgraph. Centrality-Hubs, Louvain-"
        "Communities, Brueckenknoten, K-Core-Schichten. Alles ist Befund:"
        " reproduzierbar gegen denselben Vault-Stand mit denselben"
        " Schwellwerten."
    )
    lines.append("")

    lines.append("## Globalmasse")
    lines.append("")
    lines.append(f"- Knoten: {stats['n_nodes']}")
    lines.append(f"- Kanten (gerichtet): {stats['n_edges']}")
    lines.append(f"- Louvain-Communities: {stats['n_communities']}")
    lines.append(
        f"- Modularity: {modularity:.3f}"
        " (Newman 2006: > 0.3 deutet auf substanzielle Community-Struktur)"
    )
    lines.append(f"- Brueckenknoten: {stats['n_bridges']}")
    lines.append(f"- Maximaler K-Core: {stats['max_k_core']}")
    lines.append("")

    lines.append("## Centrality-Hubs")
    lines.append("")
    lines.append(_centrality_table(graph, centralities, "pagerank",
                                   "Nach PageRank"))
    lines.append("")
    lines.append(_centrality_table(graph, centralities, "betweenness",
                                   "Nach Betweenness (Vermittlerrolle)"))
    lines.append("")
    lines.append(_centrality_table(graph, centralities, "eigenvector",
                                   "Nach Eigenvector (Naehe zu anderen Hubs)"))
    lines.append("")

    lines.append("## Louvain-Communities")
    lines.append("")
    lines.append(
        "Pro Community: Groesse und die zentralsten Mitglieder (nach"
        " PageRank). Communities mit < 5 Knoten werden als Mikro-Cluster"
        " ausgewiesen (siehe METHODIK.md)."
    )
    lines.append("")
    sorted_communities = sorted(
        community_sizes.items(), key=lambda x: x[1], reverse=True
    )
    for cid, size in sorted_communities:
        members = [k for k, v in communities.items() if v == cid]
        marker = " (Mikro-Cluster)" if size < 5 else ""
        lines.append(f"### Community {cid}: {size} Knoten{marker}")
        lines.append("")
        members_by_pagerank = sorted(
            members,
            key=lambda m: centralities[m]["pagerank"],
            reverse=True,
        )
        for m in members_by_pagerank[:COMMUNITY_SAMPLE]:
            title = _title_of(graph, m)
            pr = centralities[m]["pagerank"]
            deg = int(centralities[m]["degree"])
            lines.append(f"- `{title}` (PageRank {pr:.4f}, Degree {deg})")
        if len(members) > COMMUNITY_SAMPLE:
            lines.append(f"- ... {len(members) - COMMUNITY_SAMPLE} weitere")
        lines.append("")

    lines.append("## Brueckenknoten")
    lines.append("")
    lines.append(
        "Knoten mit hoher Betweenness bei moderater Degree (Z-Score-Diff >="
        " 1.5). Kandidaten fuer Querkonzepte oder Vermittler zwischen"
        " Communities."
    )
    lines.append("")
    if bridges:
        lines.append("| Rang | Titel | Betweenness | Degree | Community |")
        lines.append("|---|---|---:|---:|:---:|")
        for rank, key in enumerate(bridges[:TOP_N], 1):
            title = _title_of(graph, key)
            bet = centralities[key]["betweenness"]
            deg = int(centralities[key]["degree"])
            cid = communities.get(key, "?")
            lines.append(f"| {rank} | {title} | {bet:.4f} | {deg} | {cid} |")
    else:
        lines.append("Keine Brueckenknoten unter der aktuellen Schwelle.")
    lines.append("")

    lines.append("## K-Core-Schichten")
    lines.append("")
    lines.append(
        "Knoten nach hoechstem K-Core, in dem sie liegen. Die innerste"
        " Schicht ist der dichteste vernetzte Kern."
    )
    lines.append("")
    by_core: dict[int, list[str]] = {}
    for node, k in k_core.items():
        by_core.setdefault(k, []).append(node)
    for k in sorted(by_core.keys(), reverse=True)[:5]:
        nodes_in_layer = by_core[k]
        lines.append(f"### {k}-Core: {len(nodes_in_layer)} Knoten")
        lines.append("")
        top_in_layer = sorted(
            nodes_in_layer,
            key=lambda n: centralities[n]["pagerank"],
            reverse=True,
        )[:10]
        for n in top_in_layer:
            lines.append(f"- `{_title_of(graph, n)}`")
        lines.append("")

    return lines


def _centrality_table(
    graph: nx.DiGraph,
    centralities: dict,
    metric: str,
    heading: str,
) -> str:
    rows = [f"### {heading}", ""]
    top = sorted(
        centralities.items(),
        key=lambda x: x[1][metric],
        reverse=True,
    )[:TOP_N]
    rows.append(f"| Rang | Titel | {metric} | Degree | In | Out |")
    rows.append("|---|---|---:|---:|---:|---:|")
    for rank, (key, c) in enumerate(top, 1):
        title = _title_of(graph, key)
        rows.append(
            f"| {rank} | {title} | {c[metric]:.4f} |"
            f" {int(c['degree'])} | {int(c['in_degree'])} |"
            f" {int(c['out_degree'])} |"
        )
    return "\n".join(rows)
