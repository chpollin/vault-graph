"""Phase 1 — Parse.

Vault einlesen, Linkgraph und Texte extrahieren, Privacy-Filter inline anwenden.

Output: nx.DiGraph mit Knoten-Attributen (frontmatter, body, path, privacy)
und Wikilink-Kanten (gerichtet). Persistiert als output/data/graph.json.

Privacy-Regel (siehe METHODIK.md):
- Knoten in Business/Angebote/ behalten ihre Topologie, verlieren Titel und Body
- Titel werden zu "Angebot-{hash8}"
- Frontmatter-Felder invoice, summary werden bei Business-Knoten gestrippt
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import frontmatter
import networkx as nx


WIKILINK_PATTERN = re.compile(
    r"\[\[(?P<target>[^\[\]\|#\n]+?)(?:#[^\[\]\|\n]+)?(?:\|[^\[\]\n]+)?\]\]"
)

CODE_FENCE_PATTERN = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_PATTERN = re.compile(r"`[^`\n]+`")

PRIVACY_BUSINESS_PREFIX = "Business/Angebote"
PRIVACY_STRIPPED_FIELDS = {"invoice", "summary"}
BODY_PREVIEW_CHARS = 500


def parse_vault(
    vault_path: Path,
    exclude: set[str],
    privacy_strict: bool,
) -> nx.DiGraph:
    """Liest den Vault und gibt einen attributierten Linkgraphen zurueck.

    Args:
        vault_path: Wurzel des Obsidian-Vaults
        exclude: Top-Level-Ordnernamen, die ausgeschlossen werden (z.B. _archive)
        privacy_strict: True aktiviert Anonymisierung fuer Business-Knoten

    Returns:
        nx.DiGraph. Knoten-Attribute: title, path, frontmatter, body_preview,
        body_full (nur intern, nicht serialisiert), privacy_anonymized (bool),
        is_moc (bool, heuristisch ueber type oder Tags). Kanten: keine Attribute.
        Graph-Attribute: dead_links (list[dict]), orphans (list[str]).
    """
    files = _walk_vault(vault_path, exclude)
    nodes_raw = [_read_file(p, vault_path, privacy_strict) for p in files]

    title_to_key = {}
    alias_to_key = {}
    for node in nodes_raw:
        title_to_key.setdefault(node["title_lookup"], node["key"])
        for alias in node["aliases"]:
            alias_to_key.setdefault(alias.lower(), node["key"])

    graph = nx.DiGraph()
    for node in nodes_raw:
        graph.add_node(
            node["key"],
            title=node["title"],
            path=node["path_relative"],
            frontmatter=node["frontmatter"],
            body_preview=node["body_preview"],
            aliases=node["aliases"],
            privacy_anonymized=node["privacy_anonymized"],
            is_moc=node["is_moc"],
        )

    dead_links: list[dict[str, str]] = []
    for node in nodes_raw:
        for target in node["raw_link_targets"]:
            resolved = _resolve_target(target, title_to_key, alias_to_key)
            if resolved is None:
                dead_links.append({"from": node["key"], "to": target})
                continue
            if resolved == node["key"]:
                continue
            graph.add_edge(node["key"], resolved)

    orphans = [
        n for n in graph.nodes
        if graph.in_degree(n) == 0 and graph.out_degree(n) == 0
    ]

    graph.graph["dead_links"] = dead_links
    graph.graph["orphans"] = orphans
    graph.graph["vault_path"] = str(vault_path)
    graph.graph["privacy_strict"] = privacy_strict
    return graph


def extract_wikilinks(text: str) -> list[str]:
    """Extrahiert Wikilink-Targets aus Markdown-Text.

    Behandelt:
    - [[Doc]] -> "Doc"
    - [[Doc|Alias]] -> "Doc"
    - [[Doc#Heading]] -> "Doc"
    - [[Doc#Heading|Alias]] -> "Doc"

    Code-Bloecke (``` und `inline`) werden vor der Extraktion entfernt, weil
    Wikilinks in Code-Beispielen keine semantischen Kanten sind.
    """
    cleaned = CODE_FENCE_PATTERN.sub("", text)
    cleaned = INLINE_CODE_PATTERN.sub("", cleaned)
    targets = []
    for match in WIKILINK_PATTERN.finditer(cleaned):
        target = match.group("target").strip()
        if target:
            targets.append(target)
    return targets


def write_graph_json(graph: nx.DiGraph, output_path: Path) -> None:
    """Serialisiert Graph + Statistiken als JSON.

    Format: {"nodes": [...], "edges": [...], "dead_links": [...],
    "orphans": [...], "stats": {...}}.
    body_full wird nicht serialisiert (wird nur in semantics.py gebraucht und
    dort frisch eingelesen).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    nodes = []
    for key, attrs in graph.nodes(data=True):
        nodes.append({
            "key": key,
            "title": attrs.get("title", key),
            "path": attrs.get("path", ""),
            "frontmatter": attrs.get("frontmatter", {}),
            "body_preview": attrs.get("body_preview", ""),
            "aliases": attrs.get("aliases", []),
            "privacy_anonymized": attrs.get("privacy_anonymized", False),
            "is_moc": attrs.get("is_moc", False),
        })

    edges = [{"from": u, "to": v} for u, v in graph.edges]

    payload = {
        "vault_path": graph.graph.get("vault_path", ""),
        "privacy_strict": graph.graph.get("privacy_strict", True),
        "nodes": nodes,
        "edges": edges,
        "dead_links": graph.graph.get("dead_links", []),
        "orphans": graph.graph.get("orphans", []),
        "stats": _compute_stats(graph),
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# --- intern ------------------------------------------------------------------


def _walk_vault(vault_path: Path, exclude: set[str]) -> list[Path]:
    """Sammelt alle .md-Dateien, ohne ausgeschlossene Top-Level-Ordner und
    versteckte Verzeichnisse (.obsidian, .git, .trash)."""
    files = []
    for path in vault_path.rglob("*.md"):
        rel = path.relative_to(vault_path)
        parts = rel.parts
        if any(p.startswith(".") for p in parts):
            continue
        if parts[0] in exclude:
            continue
        files.append(path)
    return sorted(files)


def _read_file(
    path: Path,
    vault_root: Path,
    privacy_strict: bool,
) -> dict[str, Any]:
    """Liest eine Markdown-Datei und gibt ein normalisiertes Node-Dict zurueck."""
    rel_path = path.relative_to(vault_root)
    key = path.stem
    posix_path = rel_path.as_posix()
    is_business = posix_path.startswith(PRIVACY_BUSINESS_PREFIX + "/")

    try:
        post = frontmatter.load(path)
    except Exception:
        post = frontmatter.Post(content=path.read_text(encoding="utf-8", errors="replace"))

    fm = dict(post.metadata) if post.metadata else {}
    body = post.content or ""

    aliases_raw = fm.get("aliases") or fm.get("alias") or []
    if isinstance(aliases_raw, str):
        aliases = [aliases_raw]
    elif isinstance(aliases_raw, list):
        aliases = [str(a) for a in aliases_raw if a]
    else:
        aliases = []

    title = key
    raw_targets = extract_wikilinks(body)

    privacy_anonymized = False
    body_preview = body[:BODY_PREVIEW_CHARS]

    if privacy_strict and is_business:
        privacy_anonymized = True
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:8]
        title = f"Angebot-{digest}"
        body_preview = ""
        for field in PRIVACY_STRIPPED_FIELDS:
            fm.pop(field, None)
        aliases = []

    is_moc = _looks_like_moc(key, fm)

    return {
        "key": key,
        "title": title,
        "title_lookup": key.lower(),
        "path_relative": posix_path,
        "frontmatter": _jsonable_frontmatter(fm),
        "body_preview": body_preview,
        "aliases": aliases,
        "raw_link_targets": raw_targets,
        "privacy_anonymized": privacy_anonymized,
        "is_moc": is_moc,
    }


def _looks_like_moc(key: str, fm: dict[str, Any]) -> bool:
    """Heuristik: MOCs erkennen wir an Frontmatter-type 'vault-organisation'
    oder am 'hub'-Tag oder am Suffix 'MOC' im Dateinamen. In pragmatics.py
    wird diese Heuristik praezisiert."""
    if fm.get("type") == "vault-organisation":
        return True
    tags = fm.get("tags") or []
    if isinstance(tags, list) and "hub" in tags:
        return True
    if "MOC" in key:
        return True
    return False


def _resolve_target(
    target: str,
    title_to_key: dict[str, str],
    alias_to_key: dict[str, str],
) -> str | None:
    """Loest einen Wikilink-Target auf einen Node-Key auf.

    Reihenfolge: exakter Titel-Match, dann Alias-Match. Vergleich case-insensitiv.
    Pfad-Wikilinks (z.B. [[folder/Doc]]) werden auf das Stem-Segment reduziert.
    """
    cleaned = target.strip()
    if "/" in cleaned:
        cleaned = cleaned.rsplit("/", 1)[-1]
    cleaned = cleaned.lower()
    if cleaned in title_to_key:
        return title_to_key[cleaned]
    if cleaned in alias_to_key:
        return alias_to_key[cleaned]
    return None


def _jsonable_frontmatter(fm: dict[str, Any]) -> dict[str, Any]:
    """Macht Frontmatter JSON-serialisierbar (Datumswerte zu Strings)."""
    out = {}
    for k, v in fm.items():
        out[k] = _jsonable_value(v)
    return out


def _jsonable_value(v: Any) -> Any:
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, list):
        return [_jsonable_value(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _jsonable_value(x) for k, x in v.items()}
    return str(v)


def _compute_stats(graph: nx.DiGraph) -> dict[str, Any]:
    n_nodes = graph.number_of_nodes()
    n_edges = graph.number_of_edges()
    n_dead = len(graph.graph.get("dead_links", []))
    n_orphans = len(graph.graph.get("orphans", []))
    n_anon = sum(
        1 for _, a in graph.nodes(data=True) if a.get("privacy_anonymized")
    )
    n_mocs = sum(1 for _, a in graph.nodes(data=True) if a.get("is_moc"))
    return {
        "nodes": n_nodes,
        "edges": n_edges,
        "dead_links": n_dead,
        "orphans": n_orphans,
        "anonymized": n_anon,
        "mocs": n_mocs,
    }
