# vault-graph

Methodisch begründete Analyse und Visualisierung der Wissensnetzwerke in einem Obsidian-Vault. Triangulation aus drei Sichten: Topologie (Linkgraph), Semantik (Embeddings), Pragmatik (MOCs, Tags, Frontmatter).

## Frage

Welche Wissensnetzwerke existieren in einem Obsidian-Vault, und wie lassen sich diese methodisch belastbar identifizieren?

## Antwort

Ein Wissensnetzwerk gilt als identifiziert, wenn es in mindestens zwei der drei Sichten als kohärenter Cluster mit paarweiser Jaccard-Übereinstimmung von mindestens 0.6 erscheint. Konvergenzen sind Befund, Divergenzen sind Diagnose.

Methodische Position in [METHODIK.md](METHODIK.md). Operativer Plan in [knowledge/projektkonzept.md](knowledge/projektkonzept.md).

## Architektur

Vier Phasen, je ein Modul in `vault_graph/`:

1. **Parse** — Vault einlesen, Linkgraph und Texte extrahieren, Privacy-Filter inline
2. **Analyze** — drei Sichten parallel: Topology, Semantics, Pragmatics
3. **Triangulate** — Konvergenz und Divergenz, Wissensnetzwerk-Identifikation
4. **Render** — zwei HTML-Visualisierungen, vier Markdown-Findings, ein Synthese-Dokument im Vault

## Output

Im `output/`-Verzeichnis (nicht versioniert):

- `data/graph.json` — Linkgraph mit Frontmatter
- `data/embeddings.npy` — Knoten-Embeddings
- `data/analyses.json` — Centrality, Cluster, Triangulationsmaße, Reproduzierbarkeits-Metadaten
- `findings/wissensnetzwerke.md` — getriangulierte Befunde
- `findings/querkonzepte.md` — datengetriebene Brückenknoten
- `findings/pflegeschulden.md` — operative Hinweise
- `findings/divergenzen.md` — Divergenz-Diagnosen
- `visualisierung/kontrast_map.html` — Hauptvisualisierung
- `visualisierung/triangulation.html` — Wissensnetzwerk-Karte

## Privacy

Strikt by default. Business-Knoten werden anonymisiert (`Angebot-{hash8}`), sensitive Frontmatter-Felder gestrippt, Volltexte aus `Business/Angebote/` nicht in Embeddings einbezogen. Methodische Konsequenzen in [METHODIK.md](METHODIK.md).

## Ausführung

```
pip install -r requirements.txt
python -m vault_graph
```

Konfiguration als Konstanten in `vault_graph/__main__.py` (Vault-Pfad, Schwellwerte, Privacy-Default).

## Status

Commit 1 — methodisches Fundament und Modul-Gerüst. Implementation der Phasen folgt in den Commits 2 bis 6, jeweils mit Gate-Kontrolle vor dem nächsten Schritt. Detail in [knowledge/projektkonzept.md](knowledge/projektkonzept.md).
