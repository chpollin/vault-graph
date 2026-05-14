"""Topology-Sicht: Linkgraph-Analyse.

Liefert fuer den MVP:
- Centrality-Suite (in/out degree, betweenness, eigenvector, pagerank, closeness)
- Louvain-Communities auf dem ungerichteten Projekt
- Bruckenknoten via Betweenness-Z-Score
- K-Core-Dekomposition
"""

from __future__ import annotations

import statistics
from typing import Any

import community as louvain
import networkx as nx


def analyze_topology(
    graph: nx.DiGraph,
    *,
    louvain_resolution: float,
    louvain_seed: int,
    bridge_z_threshold: float,
) -> dict[str, Any]:
    """Berechnet alle topologischen Maße in einem Schritt.

    Returns:
        dict mit Schluesseln:
        - centralities: {node_key: {degree, in_degree, out_degree, betweenness,
            eigenvector, pagerank, closeness}}
        - communities: {node_key: community_id (int)}
        - community_sizes: {community_id: int}
        - modularity: float
        - k_core: {node_key: int}
        - bridges: list[str]  (node_keys)
        - stats: {n_nodes, n_edges, n_communities, ...}
    """
    centralities = _compute_centralities(graph)
    communities, modularity = _detect_communities(
        graph, resolution=louvain_resolution, seed=louvain_seed
    )
    k_core = _k_core_decomposition(graph)
    bridges = _identify_bridges(centralities, z_threshold=bridge_z_threshold)

    community_sizes: dict[int, int] = {}
    for cid in communities.values():
        community_sizes[cid] = community_sizes.get(cid, 0) + 1

    return {
        "centralities": centralities,
        "communities": communities,
        "community_sizes": community_sizes,
        "modularity": modularity,
        "k_core": k_core,
        "bridges": bridges,
        "stats": {
            "n_nodes": graph.number_of_nodes(),
            "n_edges": graph.number_of_edges(),
            "n_communities": len(community_sizes),
            "modularity": modularity,
            "n_bridges": len(bridges),
            "max_k_core": max(k_core.values()) if k_core else 0,
        },
    }


# --- intern ------------------------------------------------------------------


def _compute_centralities(graph: nx.DiGraph) -> dict[str, dict[str, float]]:
    """Sechs Centrality-Mase pro Knoten.

    Eigenvector und Closeness koennen bei isolierten Teilgraphen versagen
    (PowerIteration konvergiert nicht). Wir fangen das ab und liefern 0.0.
    """
    in_deg = dict(graph.in_degree())
    out_deg = dict(graph.out_degree())
    total_deg = {n: in_deg[n] + out_deg[n] for n in graph.nodes}

    betweenness = nx.betweenness_centrality(graph, normalized=True)
    pagerank = nx.pagerank(graph, alpha=0.85)

    try:
        eigenvector = nx.eigenvector_centrality_numpy(graph, max_iter=1000)
    except Exception:
        eigenvector = {n: 0.0 for n in graph.nodes}

    try:
        closeness = nx.closeness_centrality(graph)
    except Exception:
        closeness = {n: 0.0 for n in graph.nodes}

    result: dict[str, dict[str, float]] = {}
    for node in graph.nodes:
        result[node] = {
            "degree": float(total_deg.get(node, 0)),
            "in_degree": float(in_deg.get(node, 0)),
            "out_degree": float(out_deg.get(node, 0)),
            "betweenness": float(betweenness.get(node, 0.0)),
            "eigenvector": float(eigenvector.get(node, 0.0)),
            "pagerank": float(pagerank.get(node, 0.0)),
            "closeness": float(closeness.get(node, 0.0)),
        }
    return result


def _detect_communities(
    graph: nx.DiGraph, *, resolution: float, seed: int
) -> tuple[dict[str, int], float]:
    """Louvain auf dem ungerichteten Projekt des Linkgraphen.

    Wenn A nach B linkt, wird im Projekt eine ungerichtete Kante A-B gesetzt.
    Mehrfachkanten (A->B und B->A) werden zu einer einzigen ungerichteten Kante.
    Kantengewicht = 1.0 fuer den MVP; gerichtete Asymmetrie ignorieren wir
    bewusst, weil Louvain auf gerichtete Graphen nicht direkt anwendbar ist.
    """
    undirected = nx.Graph()
    undirected.add_nodes_from(graph.nodes)
    for u, v in graph.edges:
        if undirected.has_edge(u, v):
            continue
        undirected.add_edge(u, v, weight=1.0)

    partition = louvain.best_partition(
        undirected, resolution=resolution, random_state=seed
    )
    modularity = louvain.modularity(partition, undirected)
    return partition, modularity


def _k_core_decomposition(graph: nx.DiGraph) -> dict[str, int]:
    """k-Core auf dem ungerichteten Projekt. Self-Loops werden vorher
    entfernt, weil nx.core_number sonst eine Exception wirft."""
    undirected = graph.to_undirected(as_view=False)
    undirected.remove_edges_from(nx.selfloop_edges(undirected))
    return dict(nx.core_number(undirected))


def _identify_bridges(
    centralities: dict[str, dict[str, float]],
    *,
    z_threshold: float,
) -> list[str]:
    """Brueckenknoten: hohe Betweenness bei moderater Degree.

    Operationalisierung: (Z-Score Betweenness) - (Z-Score Degree) >= threshold.
    Z-Scores ueber alle Knoten, robuste Behandlung bei Null-Varianz.
    """
    nodes = list(centralities.keys())
    if len(nodes) < 3:
        return []

    bet_values = [centralities[n]["betweenness"] for n in nodes]
    deg_values = [centralities[n]["degree"] for n in nodes]

    bet_mean = statistics.mean(bet_values)
    bet_std = statistics.pstdev(bet_values) or 1.0
    deg_mean = statistics.mean(deg_values)
    deg_std = statistics.pstdev(deg_values) or 1.0

    bridges = []
    for n in nodes:
        bet_z = (centralities[n]["betweenness"] - bet_mean) / bet_std
        deg_z = (centralities[n]["degree"] - deg_mean) / deg_std
        if (bet_z - deg_z) >= z_threshold:
            bridges.append(n)

    bridges.sort(
        key=lambda n: (
            centralities[n]["betweenness"] / max(centralities[n]["degree"], 1.0)
        ),
        reverse=True,
    )
    return bridges
