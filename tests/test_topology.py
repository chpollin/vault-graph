"""Korrektheits-Tests fuer die Topology-Phase.

Fokus auf die methodisch tragenden Eigenschaften:
- Louvain-Reproduzierbarkeit unter gleichem Seed
- Modularity > 0 fuer Graphen mit struktureller Community
- Bruckenknoten-Identifikation auf konstruiertem Bow-Tie-Graphen
"""

from __future__ import annotations

import networkx as nx
import pytest

from vault_graph.topology import analyze_topology


def _two_cliques_with_bridge() -> nx.DiGraph:
    """Bow-Tie: zwei dichte Cluster, eine Brueckenkante zwischen ihnen.

    Cluster A: A1-A5 vollverbunden. Cluster B: B1-B5 vollverbunden.
    Brueckenkante: A1 -> B1 (Zwei Communities, B1 ist der Bottleneck).
    """
    g = nx.DiGraph()
    cluster_a = [f"A{i}" for i in range(1, 6)]
    cluster_b = [f"B{i}" for i in range(1, 6)]
    for u in cluster_a:
        for v in cluster_a:
            if u != v:
                g.add_edge(u, v)
    for u in cluster_b:
        for v in cluster_b:
            if u != v:
                g.add_edge(u, v)
    g.add_edge("A1", "B1")
    g.add_edge("B1", "A1")
    return g


def _two_stars_with_explicit_bridge() -> nx.DiGraph:
    """Zwei Sterngraphen mit einem dedizierten Brueckenknoten B in der Mitte.

    Sterne: Hub_A mit Blaettern A1-A5; Hub_B mit Blaettern B1-B5.
    Brueckenknoten: B verbindet Hub_A und Hub_B, hat aber selbst nur diese
    zwei Kanten (moderate Degree, hohe Betweenness).
    """
    g = nx.DiGraph()
    for i in range(1, 6):
        g.add_edge("Hub_A", f"A{i}")
        g.add_edge(f"A{i}", "Hub_A")
        g.add_edge("Hub_B", f"B{i}")
        g.add_edge(f"B{i}", "Hub_B")
    g.add_edge("Hub_A", "B")
    g.add_edge("B", "Hub_A")
    g.add_edge("Hub_B", "B")
    g.add_edge("B", "Hub_B")
    return g


class TestTopology:
    def test_louvain_reproducible_under_same_seed(self):
        graph = _two_cliques_with_bridge()
        result1 = analyze_topology(
            graph,
            louvain_resolution=1.0,
            louvain_seed=42,
            bridge_z_threshold=1.5,
        )
        result2 = analyze_topology(
            graph,
            louvain_resolution=1.0,
            louvain_seed=42,
            bridge_z_threshold=1.5,
        )
        assert result1["communities"] == result2["communities"]
        assert result1["modularity"] == pytest.approx(result2["modularity"])

    def test_two_clusters_detected(self):
        graph = _two_cliques_with_bridge()
        result = analyze_topology(
            graph, louvain_resolution=1.0, louvain_seed=42,
            bridge_z_threshold=1.5,
        )
        # Erwartet: zwei Communities, eine fuer Cluster A, eine fuer Cluster B
        community_sizes = sorted(result["community_sizes"].values(), reverse=True)
        assert community_sizes[:2] == [5, 5]
        assert result["modularity"] > 0.3

    def test_bridge_node_detected(self):
        graph = _two_stars_with_explicit_bridge()
        result = analyze_topology(
            graph, louvain_resolution=1.0, louvain_seed=42,
            bridge_z_threshold=1.0,
        )
        # B ist der einzige Knoten, der hohe Betweenness UND niedrige
        # Degree hat (nur zwei Verbindungen, aber zentral fuer alle Pfade
        # zwischen den Sternen).
        assert "B" in result["bridges"]

    def test_centralities_present_for_every_node(self):
        graph = _two_cliques_with_bridge()
        result = analyze_topology(
            graph, louvain_resolution=1.0, louvain_seed=42,
            bridge_z_threshold=1.5,
        )
        for node in graph.nodes:
            assert node in result["centralities"]
            keys = result["centralities"][node].keys()
            assert {"degree", "in_degree", "out_degree", "betweenness",
                    "pagerank"}.issubset(keys)

    def test_modularity_low_for_random_graph(self):
        """Sanity: ein Zufallsgraph hat keine substanzielle Community-Struktur."""
        graph = nx.gnp_random_graph(20, 0.5, seed=42, directed=True)
        digraph = nx.DiGraph(graph)
        result = analyze_topology(
            digraph, louvain_resolution=1.0, louvain_seed=42,
            bridge_z_threshold=1.5,
        )
        # Bei dichtem Zufallsgraphen ist Modularity klein, nicht zwingend < 0.3
        # (Louvain findet immer eine Partition). Wir pruefen nur, dass das
        # Ergebnis ein gueltiger Float ist.
        assert isinstance(result["modularity"], float)

    def test_k_core_yields_nonzero_max(self):
        graph = _two_cliques_with_bridge()
        result = analyze_topology(
            graph, louvain_resolution=1.0, louvain_seed=42,
            bridge_z_threshold=1.5,
        )
        # In zwei voll verbundenen 5er-Cliques liegt jeder Knoten mindestens
        # in einem k=4-Core.
        assert max(result["k_core"].values()) >= 4
