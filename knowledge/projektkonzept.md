# Projektkonzept

Ziele, Architektur und Vorgehen des vault-graph-Tools. Methodische Grundlage in [../METHODIK.md](../METHODIK.md).

## Frage

Welche Wissensnetzwerke existieren in einem Obsidian-Vault, und wie lassen sich diese methodisch belastbar identifizieren?

## Anspruch

Das Tool produziert keine weitere Graph-Visualisierung, sondern eine begründete Aussage darüber, welche Knotengruppen Wissensnetzwerke sind und welche nur topologische Cluster ohne epistemischen Anspruch.

## Ziele

1. **Identifikation.** Pro Vault-Lauf eine Liste identifizierter Wissensnetzwerke mit Stützungs-Score (1, 2 oder 3 von drei Sichten konvergent), Mitgliederliste und Größenangabe.
2. **Begründung.** Jede Aussage in den Findings führt auf Daten und Methode zurück. Befund, Diagnose und Hypothese werden konsequent unterschieden und markiert.
3. **Diagnose.** Divergenzen zwischen den drei Sichten werden als eigenständige Befunde ausgewiesen und liefern operative Hinweise: fehlende Links, veraltete MOCs, emergente Cluster ohne Hub.

## Architektur

Vier Phasen, jeweils ein Modul in `vault_graph/`.

1. **Parse** (`parse.py`): Vault einlesen, Linkgraph und Texte extrahieren, Privacy-Filter inline anwenden
2. **Analyze**: drei Sichten parallel
   - `topology.py`: Centrality, Communities, Brückenknoten, K-Core
   - `semantics.py`: Embeddings, HDBSCAN, Linking-Kandidaten
   - `pragmatics.py`: MOCs (primär), Tags und Ordner (sekundär), Reifegrad
3. **Triangulate** (`triangulate.py`): Konvergenz der Sichten, Wissensnetzwerk-Identifikation, Divergenz-Diagnose
4. **Render** (`render.py`): zwei HTML-Visualisierungen, vier Markdown-Findings, ein Synthese-Dokument im Vault

Begleitend: `report_parse.py`, `report_topology.py`, etc. erzeugen pro Phase einen deskriptiven Bericht. Diese Berichte sind keine Findings im methodischen Sinn, sondern Sanity-Checks für die Gate-Kontrolle.

Konfiguration als Konstanten in `vault_graph/__main__.py`: Vault-Pfad, Schwellwerte, Privacy-Default.

## Output

Im `output/`-Verzeichnis (nicht versioniert):

- `data/graph.json`: Linkgraph mit Frontmatter
- `data/embeddings.npy`: Knoten-Embeddings
- `data/analyses.json`: Centrality, Cluster, Triangulationsmaße, Reproduzierbarkeits-Metadaten
- `findings/wissensnetzwerke.md`: getriangulierte Befunde
- `findings/querkonzepte.md`: datengetriebene Brückenknoten
- `findings/pflegeschulden.md`: operative Hinweise
- `findings/divergenzen.md`: Divergenz-Diagnosen
- `visualisierung/kontrast_map.html`: Hauptvisualisierung
- `visualisierung/triangulation.html`: Wissensnetzwerk-Karte

Plus eine Synthese-Datei zurück in den Vault unter `Vault Operations/`.

## Vorgehen

Sechs Hauptcommits, jeder einzeln prüfbar. Zwischen-Commits für Tests und Privacy-Härtung sind möglich und werden in dieser Tabelle nicht gepflegt. Vor dem nächsten Hauptcommit jeweils Gate-Kontrolle durch den User.

| Commit | Inhalt | Gate-Kontrolle |
|---|---|---|
| C1 | Methodisches Fundament und Modul-Gerüst | Trägt die Methodik epistemisch? |
| C2 | Parse-Phase implementiert, pytest-Suite, Parse-Bericht | Werden Knoten/Kanten korrekt extrahiert, greift der Privacy-Filter mehrlagig? |
| C3 | Topology implementiert | Tauchen erwartete Hubs auf, sind Louvain-Cluster plausibel? |
| C4 | Semantics implementiert | Liegen verwandte Dokumente semantisch zusammen? |
| C5 | Pragmatics und Triangulate implementiert | Welche Wissensnetzwerke kristallisieren sich heraus? |
| C6 | Render und Vault-Anbindung implementiert | Trägt die Visualisierung den methodischen Anspruch? |

Stand (`git log --oneline`):

```
2761654 Tests und Parse-Bericht
5b21b8b Parse-Phase implementiert
af9728a Methodik-Reduktion auf zwei Dokumente
695343b methodisches Fundament und Modul-Geruest
```

## Stage 2

Nach Abschluss von C6 mögliche Erweiterungen, ohne Vorab-Verpflichtung:

- Anker-Ego-Netze: HTML-Subseite pro datengetrieben identifiziertem Querkonzept mit 2-Hop-Nachbarschaft
- Canvas-Generator: pro Wissensnetzwerk eine Obsidian `.canvas`-Datei zur manuellen Kuration
- Sensitivitätsanalyse: Schwellwerte systematisch variieren, robuste von schwellwertabhängigen Befunden trennen
- Zeitreihe: Wachstum und Verschiebung der Wissensnetzwerke über mehrere Läufe

## Erfolgskriterien

1. **Reproduzierbarkeit.** Zweimaliger Lauf gegen denselben Vault-Stand und denselben Tool-Git-Hash führt zu identischen Befunden. Tool-Git-Hash, Seeds, Bibliotheks-Versionen, Modellversionen und Vault-Stand werden in jedem Output mitgespeichert; siehe Abschnitt Reproduzierbarkeit in [../METHODIK.md](../METHODIK.md).
2. **Triangulation greift.** Mindestens ein robust identifiziertes Wissensnetzwerk (3/3 Sichten konvergent) wird gefunden. Andernfalls: Vault zu klein, Methodik falsch parametrisiert oder die Position der drei Sichten zueinander schwächer als angenommen.
3. **Diagnostische Substanz.** Die Divergenz-Befunde liefern mindestens fünf operativ verwertbare Hinweise. Andernfalls ist das Tool deskriptiv, aber nicht produktiv.

## Was das Tool nicht leistet

Keine Wertung, keine Handlungsempfehlung, keine inhaltliche Aussage über Dokumente, keine Kausal-Erklärung. Begründung in [../METHODIK.md](../METHODIK.md).
