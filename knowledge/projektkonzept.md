# Projektkonzept

Ziele, Architektur und Vorgehen des vault-graph-Tools. Methodische Grundlage in [../METHODIK.md](../METHODIK.md).

## Frage

Welche Strukturen lassen sich im Linkgraph eines Obsidian-Vaults methodisch belastbar identifizieren? Im MVP nur topologisch; in Stage 2 dreifach trianguliert.

## MVP-Anspruch

Der MVP liefert eine topologische Analyse plus eine interaktive HTML-Visualisierung. Er ist ehrlich darin, was er noch *nicht* leistet: keine semantische Sicht, keine Triangulation, keine Aussage über *Wissensnetzwerke* im vollen Sinn.

## Ziele (MVP)

1. **Topologische Befunde.** Communities mit Modularität, Centrality-Hubs, Brückenknoten, K-Core-Schichten. Reproduzierbar mit fixen Seeds.
2. **Visualisierung.** Ein selfcontained HTML-File, Force-Directed-Graph, Knoten gefärbt nach Community, Größe nach PageRank, Brückenknoten markiert. Search, Zoom, Detail-Panel.
3. **Privacy.** Business-Knoten werden mehrlagig anonymisiert. Topologie bleibt sichtbar.
4. **Methodische Disziplin.** Befund, Diagnose, Hypothese werden unterschieden.

## Architektur (MVP)

Drei Phasen, je ein Modul in `vault_graph/`.

1. **Parse** (`parse.py`): Vault einlesen, Linkgraph extrahieren, Privacy-Filter, `graph.json`
2. **Topology** (`topology.py`): Centrality-Suite, Louvain-Communities, K-Core, Brückenknoten
3. **Render** (`render.py`): HTML-Visualisierung

Begleitend: `report_parse.py` und `report_topology.py` erzeugen Markdown-Berichte für die Gate-Kontrolle.

## Output (MVP)

Im `output/`-Verzeichnis (nicht versioniert):

- `data/graph.json`: Linkgraph mit Frontmatter, dead_links, orphans, stats
- `findings/parse-bericht.md`: deskriptive Parse-Statistiken
- `findings/topology-bericht.md`: Communities, Centrality-Hubs, Brückenknoten, K-Core
- `visualisierung/topology.html`: interaktive Force-Directed-Visualisierung

## Vorgehen

Iterative Commits, jeder einzeln prüfbar.

Stand (`git log --oneline`):

```
... MVP-Reset und Topology+Render
ef0b038 Knowledge-Synchronisation mit Stand nach Commit 2
2761654 Tests und Parse-Bericht
5b21b8b Parse-Phase implementiert
af9728a Methodik-Reduktion auf zwei Dokumente
695343b methodisches Fundament und Modul-Geruest
```

## Stage 2 (nach MVP)

- Semantische Sicht: `semantics.py` mit Sentence-Embeddings (`all-MiniLM-L6-v2`), HDBSCAN-Cluster, Linking-Kandidaten
- Pragmatische Sicht: `pragmatics.py` mit MOC-Cluster (primär), Tag- und Ordner-Cluster (sekundär)
- Triangulation: `triangulate.py` mit AMI-Matrix, paarweise Jaccard ≥ 0.6, vier Divergenz-Typen, Querkonzept-Identifikation
- Vier zusätzliche Findings-Dokumente (Wissensnetzwerke, Querkonzepte, Pflegeschulden, Divergenzen)
- Reproduzierbarkeits-Metadaten in `analyses.json` (Tool-Git-Hash, Versionen, Vault-mtime)

## Erfolgskriterien (MVP)

1. **Reproduzierbarkeit.** Zweimaliger Lauf gegen denselben Vault-Stand und denselben Seed führt zu identischen Communities und Modularität.
2. **Plausibilität.** Die Top-Hubs nach PageRank sind erkennbar zentrale Knoten des Vaults. MOCs landen unter den Top-Brückenknoten.
3. **Bedienbarkeit.** Die HTML-Visualisierung läuft im Browser ohne Server-Setup, Search und Zoom funktionieren.

## Was der MVP nicht leistet

Keine Wertung, keine Handlungsempfehlung, keine inhaltliche Aussage über Dokumente, keine Kausal-Erklärung, keine Triangulation. Begründung in [../METHODIK.md](../METHODIK.md).
