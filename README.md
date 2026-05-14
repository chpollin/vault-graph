# vault-graph (MVP)

Topologische Analyse und Visualisierung eines Obsidian-Vaults. Linkgraph aus Wikilinks, Louvain-Communities, Centrality-Suite, Brückenknoten, K-Core-Dekomposition. Eine selfcontained HTML-Visualisierung.

Methodische Position in [METHODIK.md](METHODIK.md). Operativer Plan in [knowledge/projektkonzept.md](knowledge/projektkonzept.md).

## MVP-Scope

Der MVP arbeitet nur auf der topologischen Sicht. Semantische und pragmatische Sicht plus Triangulation sind als Stage 2 dokumentiert. Der MVP macht damit **keine Aussage über Wissensnetzwerke im vollen Sinn**, sondern liefert topologische Befunde, die Stage 2 stützen oder widerlegen kann.

## Ausführung

```
pip install -r requirements.txt
python -m vault_graph
```

Konfiguration als Konstanten in `vault_graph/__main__.py` (Vault-Pfad, Schwellwerte, Seeds).

Output:

- `output/data/graph.json`: Linkgraph mit Frontmatter, tote Links, Orphans, Statistiken
- `output/findings/parse-bericht.md`: deskriptive Parse-Statistiken
- `output/findings/topology-bericht.md`: Communities, Centrality-Hubs, Brückenknoten, K-Core
- `output/visualisierung/topology.html`: interaktive Force-Directed-Visualisierung (Browser öffnen)

## Privacy

Strikt by default. Business-Knoten (`Business/Angebote/`) werden mehrlagig anonymisiert:

- Titel zu `Angebot-{hash8}`, Body und sensitive Frontmatter (`invoice`, `summary`, `aliases`) entfernt
- `key` und `path` im exportierten JSON durch den Anonym-Title ersetzt
- Wikilinks anderer Knoten, die auf einen anonymisierten Knoten zeigen, werden im body_preview durch den Anonym-Title ersetzt

Topologie (in/out-Degree, Community) bleibt sichtbar. Methodische Konsequenzen in [METHODIK.md](METHODIK.md).

## Tests

```
python -m pytest tests/
```

35 Tests, Fokus auf Wikilink-Extraktion, Privacy-Filter (inkl. Cross-References), Alias-Auflösung, nested-archive-Filter, Louvain-Reproduzierbarkeit, Bridge-Detection.

## Status

| Phase | Status |
|---|---|
| Parse | abgeschlossen |
| Topology | abgeschlossen |
| Render (1 HTML) | abgeschlossen |
| Semantics (Stage 2) | offen |
| Pragmatics (Stage 2) | offen |
| Triangulate (Stage 2) | offen |
