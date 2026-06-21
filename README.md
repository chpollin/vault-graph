# vault-graph

Topologische und pragmatische Analyse und Visualisierung eines Obsidian-Vaults. Linkgraph aus Wikilinks, Louvain-Communities, Centrality-Suite, Brückenknoten, K-Core-Dekomposition, dazu eine Triangulation der Communities gegen die Ordnerstruktur. Zwei selfcontained HTML-Ausgaben.

Methodische Position in [METHODIK.md](METHODIK.md). Operativer Plan in [knowledge/projektkonzept.md](knowledge/projektkonzept.md).

## Scope

Das Tool arbeitet auf zwei Sichten, der topologischen (Linkgraph, Communities, Centrality, Brücken, K-Core) und der pragmatischen mit Triangulation (Community gegen Ordner, NMI, Reinheit, Ausreißer). Offen bleibt die semantische Sicht (inhaltliche Ähnlichkeit über Embeddings), ausgearbeitet als Vorlage in [knowledge/aehnlichkeitsanalyse-vorlage.md](knowledge/aehnlichkeitsanalyse-vorlage.md). Solange sie fehlt, bleibt die volle Triangulation aus drei Sichten unvollständig, die topologischen und pragmatischen Befunde stehen aber für sich.

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
- `output/findings/triangulation-bericht.md`: Community gegen Ordner, NMI, Reinheit, Ausreißer
- `output/visualisierung/topology.html`: schlichte Force-Directed-Visualisierung (Browser öffnen)
- `output/visualisierung/explorer.html`: Werkbank mit Befundtabelle, Pflege-Triage, Graph und Detailpanel

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

44 Tests, Fokus auf Wikilink-Extraktion, Privacy-Filter (inkl. Cross-References), Alias-Auflösung, nested-archive-Filter, Louvain-Reproduzierbarkeit, Bridge-Detection, Triangulation (NMI, Reinheit, Ausreisser).

## Status

| Phase | Status |
|---|---|
| Parse | abgeschlossen |
| Topology | abgeschlossen |
| Render (topology.html plus explorer.html) | abgeschlossen |
| Pragmatics | abgeschlossen |
| Triangulation | abgeschlossen |
| Semantics (Ähnlichkeitsanalyse) | offen, Vorlage liegt vor |
