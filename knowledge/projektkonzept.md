# Projektkonzept

Ziele, Architektur und Vorgehen des vault-graph-Tools. Methodische Grundlage in [../METHODIK.md](../METHODIK.md). Der aktuelle Bau-Stand mit Datenarchitektur und Befunden steht in [projektwissen.md](projektwissen.md), der Verlauf in [journal.md](journal.md). Dieses Dokument haelt den Plan und das Rationale, nicht den laufenden Zustand.

## Frage

Welche Strukturen lassen sich im Linkgraph eines Obsidian-Vaults methodisch belastbar identifizieren? Topologisch ueber den Linkgraph, pragmatisch ueber die Triangulation gegen die Ordnerstruktur, und perspektivisch semantisch ueber inhaltliche Aehnlichkeit.

## Anspruch

Das Tool liefert eine topologische und eine pragmatische Analyse plus zwei interaktive HTML-Ausgaben. Es ist ehrlich darin, was es noch nicht leistet, naemlich die semantische Sicht und damit die volle Triangulation aus drei Sichten. Es macht keine Wertung und keine inhaltliche Aussage ueber einzelne Dokumente.

## Ziele

1. **Topologische Befunde.** Communities mit Modularitaet, Centrality-Hubs, Brueckenknoten, K-Core-Schichten. Reproduzierbar mit fixen Seeds.
2. **Pragmatische Sicht.** Triangulation der Link-Communities gegen die Ordnerstruktur, gemessen ueber Reinheit und NMI, mit Ausreisser-Knoten als Diagnose-Kandidaten.
3. **Visualisierung.** Selfcontained HTML. Eine schlichte Force-Visualisierung (topology.html) und die Werkbank explorer.html mit dem Graphen als Hauptflaeche, Kanten bei Auswahl, drei Aussagetyp-Akzenten, gruppierter Statuszeile, schlanker Begleittabelle und drei Linsen (Struktur, Pflege, Wachstum).
4. **Privacy.** Business-Knoten werden mehrlagig anonymisiert. Topologie bleibt sichtbar.
5. **Methodische Disziplin.** Befund, Diagnose, Hypothese werden unterschieden.

## Architektur

Phasen als Module in `vault_graph/`, orchestriert ueber `__main__.py`.

1. **Parse** (`parse.py`): Vault einlesen, Linkgraph extrahieren, Privacy-Filter, `graph.json`
2. **Topology** (`topology.py`): Centrality-Suite, Louvain-Communities, K-Core, Brueckenknoten
3. **Pragmatics** (`pragmatics.py`): Triangulation Community gegen Ordner, NMI, Reinheit, Ausreisser, Tag-Kohaesion
4. **Render** (`render.py`): schlichte HTML-Visualisierung `topology.html`
5. **Explorer** (`explorer.py`): Werkbank `explorer.html`, Graph als Hauptflaeche, Linsen, Kanten bei Auswahl, Aussagetyp-Ringe

Begleitend erzeugen `report_parse.py`, `report_topology.py` und `report_pragmatics.py` Markdown-Berichte fuer die Gate-Kontrolle.

## Output

Im `output/`-Verzeichnis (nicht versioniert):

- `data/graph.json`: Linkgraph mit Frontmatter, dead_links, orphans, stats
- `findings/parse-bericht.md`: deskriptive Parse-Statistiken
- `findings/topology-bericht.md`: Communities, Centrality-Hubs, Brueckenknoten, K-Core
- `findings/triangulation-bericht.md`: Community gegen Ordner, NMI, Reinheit, Ausreisser
- `visualisierung/topology.html`: schlichte Force-Directed-Visualisierung
- `visualisierung/explorer.html`: Werkbank, Graph als Hauptflaeche, Linsen, Begleittabelle, Triage, Detail

## Vorgehen

Iterative Commits, jeder einzeln pruefbar. Der laufende Verlauf steht in [journal.md](journal.md).

## Offen, die semantische Sicht und der Wissensgraph

Die zentrale Richtung ist beschlossen, die Netzwerkvisualisierung wird das zentrale UI-Element und der reine Linkgraph wird zu einem getypten Wissensgraphen. Der ausgearbeitete Plan steht in [plan-zentrale-visualisierung.md](plan-zentrale-visualisierung.md), der Gestaltungsvorschlag fuer den Interface-Umbau in [gestaltungsvorschlag-interface.md](gestaltungsvorschlag-interface.md), als Phase A umgesetzt (Graph als Hauptflaeche, Linsen, Kanten bei Auswahl, Aussagetyp-Ringe, gruppierte Statuszeile, schlanke Tabelle, stabile Positionen), die semantische Schicht im Detail in [aehnlichkeitsanalyse-vorlage.md](aehnlichkeitsanalyse-vorlage.md). Noch nicht gebaut sind:

- Semantische Sicht ueber Text-Embeddings, ein lokales mehrsprachiges Modell, Linking-Kandidaten via Kosinusaehnlichkeit (Schicht eins, Scout)
- Getypte Relationen ueber eine kleine Taxonomie, vom Sprachmodell vorgeschlagen und vom Menschen bestaetigt (Schicht zwei, Karte)
- Die semantische Partition als dritte Achse der Triangulation, neben Community und Ordner
- Ein Diagnose-Bericht latenter Verknuepfungen (aehnliche, aber unverlinkte Notizen)
- Eine vollstaendige Reproduzierbarkeits-Signatur pro Lauf (Tool-Git-Hash, Versionen, Vault-mtime)

## Erfolgskriterien

1. **Reproduzierbarkeit.** Zweimaliger Lauf gegen denselben Vault-Stand und denselben Seed fuehrt zu byte-identischen Ausgaben.
2. **Plausibilitaet.** Die Top-Hubs nach PageRank sind erkennbar zentrale Knoten des Vaults. MOCs landen unter den Top-Brueckenknoten.
3. **Bedienbarkeit.** Die HTML-Ausgaben laufen im Browser ohne Server-Setup, Search, Zoom und Selektion funktionieren.

## Was das Tool nicht leistet

Keine Wertung, keine Handlungsempfehlung, keine inhaltliche Aussage ueber Dokumente, keine Kausal-Erklaerung. Die volle Triangulation aus drei Sichten bleibt offen, solange die semantische Sicht fehlt. Begruendung in [../METHODIK.md](../METHODIK.md).
