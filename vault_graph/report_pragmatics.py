"""Triangulations-Bericht.

Schreibt output/findings/triangulation-bericht.md. Kreuzt die topologische
Louvain-Community mit der pragmatischen Ordner-Partition und trennt Befund,
Hypothese und Diagnose, wie in METHODIK.md festgelegt. Titel werden ueber das
Knoten-Attribut title gezogen, das fuer anonymisierte Knoten bereits der
Angebot-hash ist, daher leakt der Bericht keinen Klartext-Business-Namen.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx


TOP_N = 25
MICRO_MIN = 5


def write_pragmatics_report(
    graph: nx.DiGraph,
    topology: dict[str, Any],
    pragmatics: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = _build_report(graph, topology, pragmatics)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _title_of(graph: nx.DiGraph, key: str) -> str:
    return graph.nodes.get(key, {}).get("title", key)


def _build_report(
    graph: nx.DiGraph,
    topology: dict[str, Any],
    pragmatics: dict[str, Any],
) -> list[str]:
    cf = pragmatics["community_folder"]
    fc = pragmatics["folder_community"]
    outliers = pragmatics["outliers"]
    tags = pragmatics["tag_cohesion"]
    stats = pragmatics["stats"]
    thr = pragmatics["thresholds"]
    community_sizes = topology["community_sizes"]

    lines: list[str] = []
    lines.append("# Triangulations-Bericht")
    lines.append("")
    lines.append(
        "Kreuzung zweier Sichten, der topologischen Louvain-Community und der"
        " pragmatischen Ordner-Partition (Top-Level-Ordner). Die Frage ist, ob"
        " die aus den Links berechneten Gruppen sich mit der gelebten Ablage"
        " decken. Befund, Hypothese und Diagnose sind getrennt ausgewiesen."
    )
    lines.append("")

    lines.append("## Globalmasse")
    lines.append("")
    lines.append(f"- Top-Level-Ordner: {stats['n_folders']}")
    lines.append(
        f"- NMI Community gegen Ordner: {stats['nmi_community_folder']:.3f}"
        " (1.0 deckungsgleich, 0.0 unabhaengig)"
    )
    lines.append(
        f"- Size-gewichtete mittlere Community-Reinheit:"
        f" {stats['mean_community_purity']:.3f}"
    )
    lines.append(
        f"- Reine Communities (Reinheit >= {thr['purity_high']:.2f}):"
        f" {stats['n_pure_communities']}"
    )
    lines.append(
        f"- Quer liegende Communities (Reinheit < {thr['purity_low']:.2f}):"
        f" {stats['n_cross_communities']}"
    )
    lines.append(f"- Ausreisser-Knoten: {stats['n_outliers']}")
    lines.append("")

    # --- Befund -------------------------------------------------------------
    lines.append("## Befund: Communities, die sich mit einem Ordner decken")
    lines.append("")
    lines.append(
        "Reinheit ist der Anteil der Community-Mitglieder im dominanten Ordner."
        f" Ab {thr['purity_high']:.2f} gilt die Community als ordnerdeckend, die"
        " Topologie bestaetigt die Ablage. Datengestuetzt und reproduzierbar."
    )
    lines.append("")
    pure = sorted(
        (
            (cid, d) for cid, d in cf.items()
            if d["purity"] >= thr["purity_high"]
        ),
        key=lambda x: (x[1]["size"], x[1]["purity"]),
        reverse=True,
    )
    significant = [(cid, d) for cid, d in pure if d["size"] >= MICRO_MIN]
    micro = [(cid, d) for cid, d in pure if d["size"] < MICRO_MIN]
    if significant:
        lines.append("| Community | Groesse | Dominanter Ordner | Reinheit |")
        lines.append("|---:|---:|---|---:|")
        for cid, d in significant:
            lines.append(
                f"| {cid} | {d['size']} | {d['dominant_folder']} |"
                f" {d['purity']:.2f} |"
            )
    else:
        lines.append(
            f"Keine Community ab Groesse {MICRO_MIN} erreicht die"
            " Reinheitsschwelle."
        )
    if micro:
        lines.append("")
        lines.append(
            f"Dazu {len(micro)} reine Mikro-Community(s) der Groesse unter"
            f" {MICRO_MIN}. Eine Community aus wenigen Knoten ist trivial rein"
            " und nur eingeschraenkt aussagekraeftig."
        )
    lines.append("")

    # --- Hypothese ----------------------------------------------------------
    lines.append("## Hypothese: Communities quer zu den Ordnern")
    lines.append("")
    lines.append(
        f"Unter {thr['purity_low']:.2f} Reinheit streut eine Community ueber"
        " mehrere Ordner. Das ist ein topologischer Cluster ohne pragmatische"
        " Stuetze, ein Kandidat fuer ein Querthema, das die Ordnerstruktur nicht"
        " abbildet. Keine Wertung, nur ein Hinweis fuer die inhaltliche Pruefung."
    )
    lines.append("")
    cross = sorted(
        (
            (cid, d) for cid, d in cf.items()
            if d["purity"] < thr["purity_low"]
        ),
        key=lambda x: x[1]["size"],
        reverse=True,
    )
    if cross:
        for cid, d in cross:
            top_members = _top_community_members(graph, topology, cid, 6)
            spread = _format_distribution(d["distribution"])
            lines.append(
                f"### Community {cid}: {d['size']} Knoten, Reinheit"
                f" {d['purity']:.2f}"
            )
            lines.append("")
            lines.append(f"- Ordnerstreuung: {spread}")
            lines.append(f"- Zentrale Mitglieder: {top_members}")
            lines.append("")
    else:
        lines.append("Keine Community liegt unter der Querschwelle.")
        lines.append("")

    # --- Diagnose -----------------------------------------------------------
    lines.append("## Diagnose: Ausreisser-Knoten")
    lines.append("")
    lines.append(
        "Knoten, die in einem anderen Ordner liegen als der, der ihre sonst"
        f" reine Community (Reinheit >= {thr['outlier_min_purity']:.2f})"
        " dominiert. Kandidat fuer woanders vernetzt als abgelegt. Eine"
        " Pflege-Auffaelligkeit, kein Fehlerurteil."
    )
    lines.append("")
    if outliers:
        lines.append(
            "| Titel | Liegt in Ordner | Community | Community-Ordner |"
            " Reinheit |"
        )
        lines.append("|---|---|---:|---|---:|")
        for o in outliers[:TOP_N]:
            lines.append(
                f"| {o['title']} | {o['folder']} | {o['community']} |"
                f" {o['community_dominant_folder']} | {o['community_purity']:.2f} |"
            )
        if len(outliers) > TOP_N:
            lines.append("")
            lines.append(f"... {len(outliers) - TOP_N} weitere Ausreisser.")
    else:
        lines.append("Keine Ausreisser unter den aktuellen Schwellen.")
    lines.append("")

    # --- Tag-Kohaesion ------------------------------------------------------
    lines.append("## Tag-Kohaesion")
    lines.append("")
    lines.append(
        "Pro haeufigem Tag die Konzentration seiner Knoten in einer Community."
        " Hohe Konzentration heisst topologisch kohaerent, niedrige heisst"
        " Querschnitts-Tag ueber viele Communities. Anonymisierte Knoten sind"
        " ausgelassen."
    )
    lines.append("")
    if tags:
        ranked = sorted(
            tags.items(),
            key=lambda x: (x[1]["concentration"], x[1]["n_nodes"]),
            reverse=True,
        )
        lines.append("| Tag | Knoten | Communities | Konzentration |")
        lines.append("|---|---:|---:|---:|")
        for tag, d in ranked[:TOP_N]:
            lines.append(
                f"| {tag} | {d['n_nodes']} | {d['n_communities']} |"
                f" {d['concentration']:.2f} |"
            )
    else:
        lines.append("Keine Tags ueber der Mindesthaeufigkeit.")
    lines.append("")

    # --- Ordner-Sicht -------------------------------------------------------
    lines.append("## Ordner-Sicht")
    lines.append("")
    lines.append(
        "Pro Top-Level-Ordner die dominante Community und ihr Anteil sowie die"
        " Zahl der Communities, ueber die der Ordner verteilt ist. Ein Ordner"
        " mit hohem Anteil in einer Community ist topologisch geschlossen."
    )
    lines.append("")
    folders_ranked = sorted(fc.items(), key=lambda x: x[1]["size"], reverse=True)
    lines.append("| Ordner | Groesse | Dominante Community | Anteil | Communities |")
    lines.append("|---|---:|---:|---:|---:|")
    for folder, d in folders_ranked:
        lines.append(
            f"| {folder} | {d['size']} | {d['dominant_community']} |"
            f" {d['share']:.2f} | {d['n_communities']} |"
        )
    lines.append("")

    return lines


def _top_community_members(
    graph: nx.DiGraph, topology: dict[str, Any], cid: int, n: int
) -> str:
    centralities = topology["centralities"]
    members = [k for k, v in topology["communities"].items() if v == cid]
    members.sort(key=lambda m: centralities[m]["pagerank"], reverse=True)
    titles = [f"`{_title_of(graph, m)}`" for m in members[:n]]
    return ", ".join(titles) if titles else "keine"


def _format_distribution(distribution: dict[str, int]) -> str:
    ordered = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
    return ", ".join(f"{folder} {count}" for folder, count in ordered[:6])
