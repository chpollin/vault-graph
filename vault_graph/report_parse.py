"""Explorations-Bericht zur Parse-Phase.

Produziert output/findings/parse-bericht.md: deskriptive Statistiken ueber
das, was die Parse-Phase aus dem Vault sehen kann. Keine methodischen
Aussagen ueber Wissensnetzwerke (kommen in Commit 5), keine Wertungen.

Befund nach den drei Aussagetypen aus METHODIK.md. Alles in diesem Bericht
ist Befund (reproduzierbar) oder Diagnose (datengestuetzte Auffaelligkeit).
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import networkx as nx


TOP_N = 20
DEAD_LINKS_SAMPLE = 30


def write_parse_report(graph: nx.DiGraph, output_path: Path) -> None:
    """Schreibt den Parse-Bericht nach output_path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = _build_report(graph)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _build_report(graph: nx.DiGraph) -> list[str]:
    n_nodes = graph.number_of_nodes()
    n_edges = graph.number_of_edges()
    dead_links = graph.graph.get("dead_links", [])
    orphans = graph.graph.get("orphans", [])
    n_anon = sum(
        1 for _, a in graph.nodes(data=True) if a.get("privacy_anonymized")
    )
    n_mocs_heuristic = sum(
        1 for _, a in graph.nodes(data=True) if a.get("is_moc")
    )

    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())
    total_degree = {n: in_degrees[n] + out_degrees[n] for n in graph.nodes}

    lines: list[str] = []
    lines.append("# Parse-Bericht")
    lines.append("")
    lines.append(
        "Deskriptive Statistiken aus der Parse-Phase. Keine methodischen"
        " Aussagen ueber Wissensnetzwerke (kommen in Commit 5). Alle Zahlen"
        " sind Befunde im Sinne von METHODIK.md: reproduzierbar gegen den"
        " gleichen Vault-Stand und die gleiche Konfiguration."
    )
    lines.append("")

    lines.append("## Vault-Umfang")
    lines.append("")
    lines.append(f"- Knoten (Markdown-Dateien): {n_nodes}")
    lines.append(f"- Gerichtete Kanten (Wikilinks): {n_edges}")
    lines.append(f"- Anonymisierte Knoten (Business/Angebote): {n_anon}")
    lines.append(f"- MOC-Heuristik-Treffer: {n_mocs_heuristic}")
    lines.append("")

    if n_nodes:
        avg_out = n_edges / n_nodes
        lines.append(
            f"- Mittlerer Out-Grad: {avg_out:.2f} ausgehende Wikilinks pro"
            " Knoten"
        )
    lines.append("")

    lines.append("## Hubs nach eingehenden Wikilinks")
    lines.append("")
    lines.append(
        "Knoten, auf die im Vault am haeufigsten verlinkt wird. Aus der"
        " Topologie allein noch kein Wissensnetzwerk-Indikator — siehe"
        " METHODIK.md, Triangulation in Commit 5."
    )
    lines.append("")
    top_in = sorted(
        graph.nodes(data=True),
        key=lambda x: in_degrees.get(x[0], 0),
        reverse=True,
    )[:TOP_N]
    lines.append("| Rang | Titel | eingehend | ausgehend | MOC-Heuristik |")
    lines.append("|---|---|---:|---:|:---:|")
    for rank, (key, attrs) in enumerate(top_in, 1):
        title = attrs.get("title", key)
        is_moc = "X" if attrs.get("is_moc") else ""
        lines.append(
            f"| {rank} | {title} | {in_degrees[key]} | {out_degrees[key]} |"
            f" {is_moc} |"
        )
    lines.append("")

    lines.append("## Hubs nach ausgehenden Wikilinks")
    lines.append("")
    lines.append(
        "Knoten, die selbst am haeufigsten andere referenzieren. Typischerweise"
        " MOCs, Hub-Seiten, Active-Work-Dokumente."
    )
    lines.append("")
    top_out = sorted(
        graph.nodes(data=True),
        key=lambda x: out_degrees.get(x[0], 0),
        reverse=True,
    )[:TOP_N]
    lines.append("| Rang | Titel | ausgehend | eingehend | MOC-Heuristik |")
    lines.append("|---|---|---:|---:|:---:|")
    for rank, (key, attrs) in enumerate(top_out, 1):
        title = attrs.get("title", key)
        is_moc = "X" if attrs.get("is_moc") else ""
        lines.append(
            f"| {rank} | {title} | {out_degrees[key]} | {in_degrees[key]} |"
            f" {is_moc} |"
        )
    lines.append("")

    lines.append("## Linkgrad-Verteilung")
    lines.append("")
    lines.append(_linkgrad_histogram(total_degree, in_degrees, out_degrees))
    lines.append("")

    lines.append("## Toter-Link-Diagnose")
    lines.append("")
    lines.append(
        f"Gesamt: {len(dead_links)} tote Wikilinks. Targets, die zu keinem"
        " Knoten und keinem Alias aufloesen. Hinweise auf geplante Dokumente,"
        " Tippfehler oder Pfad-Wikilinks (z.B. zu Ordnern)."
    )
    lines.append("")
    lines.extend(_dead_links_by_top_targets(dead_links))
    lines.append("")
    lines.extend(_dead_links_by_source_folder(dead_links, graph))
    lines.append("")
    lines.append(
        "Stichprobe der ersten Eintraege (nicht erschoepfend, vollstaendige"
        " Liste in `output/data/graph.json` unter `dead_links`):"
    )
    lines.append("")
    for entry in dead_links[:DEAD_LINKS_SAMPLE]:
        from_attrs = graph.nodes.get(entry["from"], {})
        from_title = from_attrs.get("title", entry["from"])
        lines.append(f"- `{from_title}` -> `{entry['to']}`")
    if len(dead_links) > DEAD_LINKS_SAMPLE:
        lines.append(f"- ... {len(dead_links) - DEAD_LINKS_SAMPLE} weitere")
    lines.append("")

    lines.append("## Orphans")
    lines.append("")
    lines.append(
        f"Knoten ohne ein- und ausgehende Wikilinks: {len(orphans)}. Kandidaten"
        " fuer Pflege, oder bewusste Stub-Dokumente."
    )
    lines.append("")
    for orphan in orphans:
        attrs = graph.nodes.get(orphan, {})
        title = attrs.get("title", orphan)
        path = attrs.get("path", "")
        lines.append(f"- `{title}` ({path})")
    lines.append("")

    lines.append("## Verteilung nach Top-Level-Ordnern")
    lines.append("")
    folder_dist = _folder_distribution(graph)
    lines.append("| Ordner | Knoten | eingehend (gesamt) | ausgehend (gesamt) |")
    lines.append("|---|---:|---:|---:|")
    for folder, stats in folder_dist:
        lines.append(
            f"| `{folder}` | {stats['nodes']} | {stats['in']} | {stats['out']} |"
        )
    lines.append("")

    lines.append("## Privacy-Wirkung")
    lines.append("")
    if n_anon == 0:
        lines.append(
            "Keine anonymisierten Knoten — entweder leerer Business/Angebote-"
            "Ordner oder Privacy-Filter inaktiv."
        )
    else:
        lines.append(
            f"{n_anon} Knoten wurden anonymisiert. Sichtbar bleibt ihre"
            " Topologie (Wikilinks rein und raus), unsichtbar werden Titel,"
            " Body, Aliase und sensitive Frontmatter-Felder. In der Triangulation"
            " erreichen diese Knoten maximal 2 der 3 Sichten (siehe METHODIK.md)."
        )
        lines.append("")
        for key, attrs in graph.nodes(data=True):
            if attrs.get("privacy_anonymized"):
                lines.append(
                    f"- `{attrs.get('title', key)}` —"
                    f" in: {in_degrees[key]}, out: {out_degrees[key]}"
                )
    lines.append("")

    return lines


def _linkgrad_histogram(
    total_degree: dict[str, int],
    in_degrees: dict[str, int],
    out_degrees: dict[str, int],
) -> str:
    buckets = [(0, 0), (1, 2), (3, 5), (6, 10), (11, 20), (21, 50), (51, 9999)]
    rows = ["| Linkgrad (total) | Knoten | Anteil |", "|---|---:|---:|"]
    n = len(total_degree) or 1
    for lo, hi in buckets:
        count = sum(1 for v in total_degree.values() if lo <= v <= hi)
        label = f"{lo}" if lo == hi else f"{lo}–{hi}" if hi < 9000 else f"{lo}+"
        rows.append(f"| {label} | {count} | {count/n:.1%} |")
    rows.append("")
    rows.append(
        "Hoher Out-Grad ohne ebenso hohen In-Grad ist typisch fuer MOCs und"
        " Aktivdokumente, hoher In-Grad ohne ebenso hohen Out-Grad fuer"
        " etablierte Wissensdokumente."
    )
    return "\n".join(rows)


def _dead_links_by_top_targets(dead_links: list[dict]) -> list[str]:
    if not dead_links:
        return ["Keine toten Links."]
    counter = Counter(d["to"] for d in dead_links)
    lines = ["**Haeufigste tote Targets** — Hinweise auf geplante, verschobene"
             " oder umbenannte Knoten:", ""]
    lines.append("| Target | Anzahl Verweise |")
    lines.append("|---|---:|")
    for target, count in counter.most_common(10):
        if count < 2:
            break
        lines.append(f"| `{target}` | {count} |")
    return lines


def _dead_links_by_source_folder(
    dead_links: list[dict], graph: nx.DiGraph
) -> list[str]:
    if not dead_links:
        return []
    folder_counter: Counter[str] = Counter()
    for entry in dead_links:
        from_key = entry["from"]
        path = graph.nodes.get(from_key, {}).get("path", "")
        folder = path.split("/", 1)[0] if "/" in path else "(root)"
        folder_counter[folder] += 1
    lines = ["", "**Tote Links nach Quell-Ordner** — wo wird am meisten"
             " ins Leere verlinkt:", ""]
    lines.append("| Ordner | Tote Links |")
    lines.append("|---|---:|")
    for folder, count in folder_counter.most_common(10):
        lines.append(f"| `{folder}` | {count} |")
    return lines


def _folder_distribution(graph: nx.DiGraph) -> list[tuple[str, dict[str, int]]]:
    folder_stats: dict[str, dict[str, int]] = {}
    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())
    for key, attrs in graph.nodes(data=True):
        path = attrs.get("path", "")
        folder = path.split("/", 1)[0] if "/" in path else "(root)"
        stats = folder_stats.setdefault(folder, {"nodes": 0, "in": 0, "out": 0})
        stats["nodes"] += 1
        stats["in"] += in_degrees.get(key, 0)
        stats["out"] += out_degrees.get(key, 0)
    return sorted(folder_stats.items(), key=lambda x: x[1]["nodes"], reverse=True)
