"""CLI-Einstiegspunkt. Orchestriert die vier Phasen.

Ausfuehrung:
    python -m vault_graph

Konfiguration als Modul-Konstanten unten.
"""

from pathlib import Path

from vault_graph.parse import parse_vault, write_graph_json
from vault_graph.report_parse import write_parse_report


# --- Konfiguration -----------------------------------------------------------

VAULT_PATH = Path(r"c:\Users\Chrisi\Documents\obsidian")
OUTPUT_DIR = Path(__file__).parent.parent / "output"

EXCLUDE_FOLDERS = {"_archive"}

# Privacy-Default: strikt. Siehe METHODIK.md.
PRIVACY_STRICT = True

# Schwellwerte (Begruendung in METHODIK.md)
JACCARD_THRESHOLD = 0.6
BETWEENNESS_ZSCORE_THRESHOLD = 1.5
LOUVAIN_RESOLUTION = 1.0
LOUVAIN_RANDOM_SEED = 42

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# --- Phasen-Orchestrierung ---------------------------------------------------


def main() -> None:
    """Vier Phasen: Parse -> Analyze (3 Sichten) -> Triangulate -> Render."""
    print(f"vault-graph: parse {VAULT_PATH}")
    graph = parse_vault(
        vault_path=VAULT_PATH,
        exclude=EXCLUDE_FOLDERS,
        privacy_strict=PRIVACY_STRICT,
    )

    graph_json_path = OUTPUT_DIR / "data" / "graph.json"
    write_graph_json(graph, graph_json_path)

    report_path = OUTPUT_DIR / "findings" / "parse-bericht.md"
    write_parse_report(graph, report_path)

    stats = graph.graph.get("dead_links", []), graph.graph.get("orphans", [])
    print(f"  nodes:      {graph.number_of_nodes()}")
    print(f"  edges:      {graph.number_of_edges()}")
    print(f"  dead_links: {len(stats[0])}")
    print(f"  orphans:    {len(stats[1])}")
    n_anon = sum(
        1 for _, a in graph.nodes(data=True) if a.get("privacy_anonymized")
    )
    n_mocs = sum(1 for _, a in graph.nodes(data=True) if a.get("is_moc"))
    print(f"  anonymized: {n_anon}")
    print(f"  mocs:       {n_mocs}")
    print(f"  -> {graph_json_path}")
    print(f"  -> {report_path}")

    print("vault-graph: analyze/triangulate/render — Commits 3-6")


if __name__ == "__main__":
    main()
