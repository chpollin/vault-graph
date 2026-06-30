# vault-graph

Topologische und pragmatische Analyse und Visualisierung einer Markdown-Wissensbasis. vault-graph parst einen Obsidian-Vault read-only, extrahiert den Linkgraph aus Wikilinks, rechnet Louvain-Communities, eine Centrality-Suite, Brückenknoten und K-Core-Dekomposition und trianguliert die Communities gegen die Ordnerstruktur. Ausgabe sind zwei selfcontained HTML-Ansichten.

Es ist als forkbares Werkzeug gedacht, das jeder gegen den eigenen Vault konfiguriert. Methodische Position in [knowledge/methodik.md](knowledge/methodik.md), Substanz und Ziele in [knowledge/specification.md](knowledge/specification.md), Wissensbasis-Einstieg über [knowledge/INDEX.md](knowledge/INDEX.md).

## Scope

Das Tool arbeitet auf zwei laufenden Sichten, der topologischen (Linkgraph, Communities, Centrality, Brücken, K-Core) und der pragmatischen mit Triangulation (Community gegen Ordner, NMI, Reinheit, Ausreißer). Die semantische Sicht (inhaltliche Ähnlichkeit über Embeddings) ist als Modul gebaut, der Modell-Lauf, der ihre Nachbarschaften gegen den lebenden Vault einfriert, steht aus. Solange er aussteht, bleibt die volle Triangulation aus drei Achsen vorbereitet, aber noch nicht geschlossen, die topologischen und pragmatischen Befunde stehen für sich.

## Ausführung

```
pip install -r requirements.txt
python -m vault_graph
```

Konfiguration liegt heute als Konstanten in `vault_graph/__main__.py` (Vault-Pfad, Schwellwerte, Seeds). Damit ist diese Instanz an den Vault des Operators gebunden. Vault-Pfad und Privacy-Regeln in echte Konfiguration zu heben, sodass ein Fork ohne Code-Änderung gegen einen fremden Vault läuft, ist als Meilenstein in [knowledge/plan.md](knowledge/plan.md) geführt.

Output (gitignored, deterministisch regenerierbar):

- `output/data/graph.json`: Linkgraph mit Frontmatter, tote Links, Orphans, Statistiken
- `output/findings/parse-bericht.md`, `topology-bericht.md`, `triangulation-bericht.md`: deskriptive Berichte
- `output/visualisierung/topology.html`: schlichte Force-Directed-Visualisierung
- `output/visualisierung/explorer.html`: Werkbank mit Graph als Hauptfläche, Linsen, Pflege-Triage und Detailpanel

## Privacy

Strikt by default. Welche Knoten anonymisiert werden, ist Konfiguration. Diese Instanz anonymisiert die Knoten in `Business/Angebote/` mehrlagig:

- Titel zu `Angebot-{hash8}`, Body und sensitive Frontmatter (`invoice`, `summary`, `aliases`) entfernt
- `key` und `path` im exportierten JSON durch den Anonym-Titel ersetzt
- Wikilinks anderer Knoten auf einen anonymisierten Knoten im body_preview maskiert

Die Topologie bleibt sichtbar. Begründung in [knowledge/methodik.md](knowledge/methodik.md), Implementierung in [knowledge/architecture.md](knowledge/architecture.md).

## Tests

```
python -m pytest tests/
```

Fokus auf Wikilink-Extraktion, Privacy-Filter, Byte-Determinismus der Pipeline und die Privacy-Invariante der Ausgabe. Garantien und Teststruktur in [knowledge/testing.md](knowledge/testing.md).

## Status

| Phase | Status |
|---|---|
| Parse | abgeschlossen |
| Topology | abgeschlossen |
| Render (topology.html plus explorer.html) | abgeschlossen |
| Pragmatics und Triangulation | abgeschlossen |
| Semantik-Scout (Modul) | gebaut, Modell-Lauf offen |
| Getypte Relationen (WEFT) | gescopt |
| Generalisierung / Forkbarkeit | geplant |
