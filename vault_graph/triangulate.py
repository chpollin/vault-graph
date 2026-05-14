"""Phase 3 — Triangulate.

Konvergenz der drei Sichten. Identifikation von Wissensnetzwerken nach
Triangulationskriterium (siehe knowledge/methodik-triangulation.md).

Verantwortlich für:
- Adjusted Mutual Information (AMI) zwischen den drei Partitionierungen
- Pro Cluster: Jaccard-Übereinstimmung mit korrespondierenden Clustern
  der anderen Sichten
- Wissensnetzwerk-Identifikation:
    * robust (3/3 Sichten konvergent, Jaccard >= 0.6 paarweise)
    * identifiziert (2/3 Sichten konvergent)
    * Hypothese (1/3 Sichten)
- Divergenz-Befunde:
    * Typ A: Topologie ohne Semantik
    * Typ B: Semantik ohne Topologie → Linking-Vorschläge
    * Typ C: Pragmatik ohne Topologie/Semantik → MOC-Pflege
    * Typ D: Topologie + Semantik ohne Pragmatik → neuer MOC-Kandidat
- Querkonzept-Identifikation: Brückenknoten + Multi-Cluster-Semantik

Output: strukturierte Findings für Render-Phase.
"""


def compute_ami_matrix(topo_clusters: dict, sem_clusters: dict, prag_clusters: dict) -> dict:
    """Adjusted Mutual Information zwischen allen Sicht-Paaren.

    Returns:
        {"topo_sem": float, "topo_prag": float, "sem_prag": float}
    """
    raise NotImplementedError("Commit 5.")


def identify_knowledge_networks(
    topo_clusters: dict, sem_clusters: dict, prag_clusters: dict, jaccard_threshold: float
) -> list[dict]:
    """Wissensnetzwerk-Identifikation nach Triangulationskriterium.

    Returns:
        Liste von Wissensnetzwerk-Dicts mit Feldern:
        - members: [node_id, ...]
        - support_score: 1, 2 oder 3 (Anzahl konvergenter Sichten)
        - convergence: {pair: jaccard, ...}
        - classification: "robust" | "identified" | "hypothesis"
    """
    raise NotImplementedError("Commit 5.")


def diagnose_divergences(
    graph, topo_clusters, sem_clusters, prag_clusters, similarities
) -> dict:
    """Diagnostiziert die vier Divergenz-Typen.

    Returns:
        {"type_a": [...], "type_b": [...], "type_c": [...], "type_d": [...]}
        mit konkreten Knoten/Cluster-Referenzen.
    """
    raise NotImplementedError("Commit 5.")


def identify_cross_concepts(centralities: dict, embeddings, clusters: dict) -> list[dict]:
    """Querkonzepte: Brückenknoten (Topologie) + Multi-Cluster-Semantik.

    Mindestens zwei der drei Bedingungen müssen erfüllt sein.
    """
    raise NotImplementedError("Commit 5.")
