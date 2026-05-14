"""Phase 2b — Semantics.

Embedding-basierte Analyse. Liefert die zweite der drei Sichten (siehe METHODIK.md).

Verantwortlich für:
- Knoten-Embeddings via sentence-transformers/all-MiniLM-L6-v2 (lokal, CPU)
- Eingabe pro Knoten: Titel + erste 500 Zeichen Body
- Kosinusähnlichkeitsmatrix
- HDBSCAN-Cluster auf den Embeddings (Dichte-basiert, kein k zu wählen)
- Linking-Kandidaten: hohe Semantik-Ähnlichkeit + große Graph-Distanz

Anonymisierte Knoten (Privacy-Filter) erhalten keine Embeddings —
ihr Body wurde nicht eingelesen. Siehe knowledge/methodik-validierung.md.

Output: Embedding-Matrix (numpy), Cluster-Zuordnung, Linking-Kandidaten.
"""

import networkx as nx


def compute_embeddings(graph: nx.DiGraph, model_name: str):
    """Erzeugt Embeddings pro Knoten.

    Knoten ohne Body (anonymisiert) werden übersprungen und in einer
    separaten Liste ausgegeben.

    Returns:
        (embeddings: np.ndarray, node_order: list[str], skipped: list[str])
    """
    raise NotImplementedError("Commit 4.")


def cluster_semantic(embeddings, min_cluster_size: int = 5) -> dict:
    """HDBSCAN-Cluster auf den Embeddings.

    Returns:
        {cluster_id: [node_id, ...], "noise": [node_id, ...]}
    """
    raise NotImplementedError("Commit 4.")


def suggest_links(graph: nx.DiGraph, similarities, top_n: int = 50) -> list[tuple]:
    """Linking-Kandidaten: hohe Ähnlichkeit, große Graph-Distanz.

    Returns:
        Liste von (node_a, node_b, similarity, graph_distance), sortiert
        nach Ähnlichkeit absteigend.
    """
    raise NotImplementedError("Commit 4.")
