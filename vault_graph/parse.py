"""Phase 1 — Parse.

Vault einlesen, Linkgraph + Texte extrahieren, Privacy-Filter inline anwenden.

Verantwortlich für:
- Walk durch den Vault (ohne _archive/)
- Frontmatter-Extraktion via python-frontmatter
- Wikilink-Extraktion via Regex, Alias-Auflösung, Heading-Link-Reduktion
- Privacy-Filter: Business/Angebote anonymisiert, sensitive Felder gestrippt
- Tote Wikilinks und Orphans als separate Listen
- Body-Text-Sammlung für spätere Embeddings (außer Business)

Output: NetworkX-DiGraph + Listen, persistiert als output/data/graph.json.

Privacy-Regel (siehe knowledge/methodik-validierung.md):
- Knoten in Business/Angebote/ behalten ihre Topologie, verlieren Titel und Body
- Titel werden zu "Angebot-{hash8}"
- Frontmatter-Felder invoice, summary bei Business-Knoten werden gestrippt
"""

import networkx as nx
from pathlib import Path


def parse_vault(vault_path: Path, exclude: set[str], privacy_strict: bool) -> nx.DiGraph:
    """Liest den Vault und gibt einen attributierten Linkgraphen zurück.

    Args:
        vault_path: Wurzel des Obsidian-Vaults
        exclude: Top-Level-Ordnernamen, die ausgeschlossen werden
        privacy_strict: True aktiviert Anonymisierung für Business-Knoten

    Returns:
        nx.DiGraph mit Knoten-Attributen (frontmatter-Felder, body, path)
        und Kanten als Wikilinks (gerichtet)
    """
    raise NotImplementedError("Commit 2.")


def extract_wikilinks(text: str) -> list[str]:
    """Extrahiert Wikilink-Targets aus Markdown-Text.

    Behandelt:
    - [[Doc]] → "Doc"
    - [[Doc|Alias]] → "Doc"
    - [[Doc#Heading]] → "Doc"
    - [[Doc#Heading|Alias]] → "Doc"
    - Escape-Sequenzen (z.B. \\| in Tabellenzellen) werden gefiltert
    """
    raise NotImplementedError("Commit 2.")


def resolve_aliases(graph: nx.DiGraph) -> nx.DiGraph:
    """Löst aliases:-Frontmatter-Felder auf.

    Wenn Knoten A einen Alias "X" trägt und Knoten B verlinkt auf [[X]],
    wird die Kante von B auf A umgebogen.
    """
    raise NotImplementedError("Commit 2.")


def apply_privacy_filter(graph: nx.DiGraph) -> nx.DiGraph:
    """Anonymisiert Business-Knoten und strippt sensitive Frontmatter-Felder.

    Siehe knowledge/methodik-validierung.md für die genauen Regeln.
    """
    raise NotImplementedError("Commit 2.")
