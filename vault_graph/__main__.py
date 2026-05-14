"""CLI-Einstiegspunkt fuer den MVP.

Drei Phasen: Parse -> Topology -> Render.
Ausfuehrung: python -m vault_graph
"""

from pathlib import Path

from vault_graph.parse import parse_vault, write_graph_json
from vault_graph.report_parse import write_parse_report
from vault_graph.topology import analyze_topology
from vault_graph.report_topology import write_topology_report
from vault_graph.render import render_topology_html


# --- Konfiguration -----------------------------------------------------------

VAULT_PATH = Path(r"c:\Users\Chrisi\Documents\obsidian")
OUTPUT_DIR = Path(__file__).parent.parent / "output"

EXCLUDE_FOLDERS = {"_archive"}

PRIVACY_STRICT = True

LOUVAIN_RESOLUTION = 1.0
LOUVAIN_RANDOM_SEED = 42
BRIDGE_Z_THRESHOLD = 1.5


def main() -> None:
    print(f"vault-graph: parse {VAULT_PATH}")
    graph = parse_vault(
        vault_path=VAULT_PATH,
        exclude=EXCLUDE_FOLDERS,
        privacy_strict=PRIVACY_STRICT,
    )

    graph_json_path = OUTPUT_DIR / "data" / "graph.json"
    write_graph_json(graph, graph_json_path)

    parse_report_path = OUTPUT_DIR / "findings" / "parse-bericht.md"
    write_parse_report(graph, parse_report_path)

    print(f"  nodes={graph.number_of_nodes()}"
          f" edges={graph.number_of_edges()}"
          f" dead_links={len(graph.graph.get('dead_links', []))}"
          f" orphans={len(graph.graph.get('orphans', []))}")
    print(f"  -> {graph_json_path}")
    print(f"  -> {parse_report_path}")

    print(f"vault-graph: topology (louvain resolution={LOUVAIN_RESOLUTION},"
          f" seed={LOUVAIN_RANDOM_SEED})")
    topology = analyze_topology(
        graph,
        louvain_resolution=LOUVAIN_RESOLUTION,
        louvain_seed=LOUVAIN_RANDOM_SEED,
        bridge_z_threshold=BRIDGE_Z_THRESHOLD,
    )
    topology_report_path = OUTPUT_DIR / "findings" / "topology-bericht.md"
    write_topology_report(graph, topology, topology_report_path)

    print(f"  communities={topology['stats']['n_communities']}"
          f" modularity={topology['modularity']:.3f}"
          f" bridges={topology['stats']['n_bridges']}"
          f" max_k_core={topology['stats']['max_k_core']}")
    print(f"  -> {topology_report_path}")

    print("vault-graph: render")
    html_path = OUTPUT_DIR / "visualisierung" / "topology.html"
    render_topology_html(graph, topology, html_path)
    print(f"  -> {html_path}")


if __name__ == "__main__":
    main()
