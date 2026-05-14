# Projektkonzept

Ziele, Architektur, Vorgehen und Erfolgskriterien des vault-graph-Tools.

## Frage und Anspruch

**Frage.** Welche Wissensnetzwerke existieren in einem Obsidian-Vault, und wie lassen sich diese methodisch belastbar identifizieren?

**Anspruch.** Das Tool produziert nicht eine weitere Graph-Visualisierung, sondern eine methodisch begründete Aussage darüber, welche Knotengruppen Wissensnetzwerke sind und welche nur topologische Cluster ohne epistemischen Anspruch.

## Ziele

Drei messbare Ziele am Ende der Implementation:

1. **Identifikation.** Für jeden Vault-Lauf liegt eine Liste identifizierter Wissensnetzwerke vor, jeweils mit Stützungs-Score (1, 2 oder 3 von drei Sichten konvergent), Mitgliederliste und Größenangabe.
2. **Begründung.** Jede Aussage in den Findings führt auf Daten und Methode zurück. Befund, Diagnose und Hypothese werden konsequent unterschieden und entsprechend markiert.
3. **Diagnose.** Divergenzen zwischen den drei Sichten werden als eigenständige Befunde ausgewiesen und liefern operative Hinweise (fehlende Links, veraltete MOCs, emergente Cluster ohne Hub).

## Methodischer Kern

Triangulation aus drei methodisch unabhängigen Sichten:

- **Topologisch** — Linkgraph, Community Detection via Louvain
- **Semantisch** — Sentence-Embeddings, dichtebasiertes Clustering via HDBSCAN
- **Pragmatisch** — MOC-Mitgliedschaft, Tag- und Ordnergruppen

Ein Wissensnetzwerk gilt als identifiziert, wenn es in mindestens zwei der drei Sichten als kohärenter Cluster mit ≥ 60% Jaccard-Übereinstimmung erscheint. Ausarbeitung in [methodik-triangulation.md](methodik-triangulation.md), Definitionsfrage in [wissensnetzwerk-definition.md](wissensnetzwerk-definition.md), Validierungs- und Privacy-Regeln in [methodik-validierung.md](methodik-validierung.md).

## Architektur

Vier Phasen, jeweils ein Modul in `vault_graph/`:

1. **Parse** (`parse.py`) — Vault einlesen, Linkgraph und Texte extrahieren, Privacy-Filter inline anwenden
2. **Analyze** — drei Sichten parallel
   - `topology.py` — Centrality, Communities, Brückenknoten, K-Core
   - `semantics.py` — Embeddings, HDBSCAN, Linking-Kandidaten
   - `pragmatics.py` — MOCs, Tags, Ordner, Reifegrad
3. **Triangulate** (`triangulate.py`) — Konvergenz der Sichten, Wissensnetzwerk-Identifikation, Divergenz-Diagnose
4. **Render** (`render.py`) — zwei HTML-Visualisierungen, vier Markdown-Findings, ein Synthese-Dokument im Vault

Konfiguration als Konstanten in `vault_graph/__main__.py` (Vault-Pfad, Schwellwerte, Privacy-Default).

## Vorgehen

Sechs Commits, jeder einzeln prüfbar. Vor dem nächsten Commit jeweils Gate-Kontrolle durch den User.

| Commit | Inhalt | Gate-Kontrolle |
|---|---|---|
| C1 | Methodisches Fundament und Modul-Gerüst | Trägt die Methodik epistemisch? |
| C2 | Parse-Phase implementiert | Werden Knoten/Kanten korrekt extrahiert, Privacy-Filter wirksam? |
| C3 | Topology implementiert | Tauchen erwartete Hubs auf, sind Louvain-Cluster plausibel? |
| C4 | Semantics implementiert | Liegen verwandte Dokumente semantisch zusammen? |
| C5 | Pragmatics und Triangulate implementiert | Welche Wissensnetzwerke kristallisieren sich heraus? |
| C6 | Render und Vault-Anbindung implementiert | Trägt die Visualisierung den methodischen Anspruch? |

## Stage 2

Nach Abschluss von C6 mögliche Erweiterungen, ohne Vorab-Verpflichtung:

- **Anker-Ego-Netze** — eine HTML-Subseite pro datengetrieben identifiziertem Querkonzept mit 2-Hop-Nachbarschaft
- **Canvas-Generator** — pro identifiziertem Wissensnetzwerk eine Obsidian `.canvas`-Datei zur manuellen Kuration
- **Sensitivitätsanalyse** — Schwellwerte (Jaccard, Louvain-Resolution) systematisch variieren, robuste vs. schwellwertabhängige Befunde unterscheiden
- **Zeitreihe** — Wachstum und Verschiebung der Wissensnetzwerke über mehrere Läufe

## Erfolgskriterien

Drei Kriterien, an denen das fertige Tool gemessen wird:

1. **Reproduzierbarkeit.** Zweimaliger Lauf gegen denselben Vault-Stand führt zu identischen Befunden. Random-Seeds, Modellversionen und Vault-Stand sind in `output/data/analyses.json` mitgespeichert.
2. **Triangulation greift.** Mindestens ein robust identifiziertes Wissensnetzwerk (3/3 Sichten konvergent) wird gefunden. Andernfalls ist entweder der Vault zu klein, die Methodik falsch parametrisiert, oder die Position der drei Sichten zueinander schwächer als angenommen.
3. **Diagnostische Substanz.** Die Divergenz-Befunde liefern mindestens fünf operativ verwertbare Hinweise (Linking-Vorschläge, MOC-Pflegehinweise, emergente Cluster-Kandidaten). Andernfalls ist das Tool deskriptiv, aber nicht produktiv.

## Was das Tool nicht leistet

- Keine Wertung von Wissensnetzwerken (nicht "wichtig", "interessant", "zentral")
- Keine Handlungsempfehlungen (nur Diagnosen)
- Keine inhaltliche Aussage über Dokumente (nur über deren Verlinkung, Sprache, Frontmatter)
- Keine kausalen Erklärungen (nur Korrelationen)

Begründung in [methodik-validierung.md](methodik-validierung.md).
