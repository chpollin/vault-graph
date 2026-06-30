---
title: Architecture
project:
  name: vault-graph
  repository: https://github.com/chpollin/vault-graph
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
status: complete
created: 2026-05-14
updated: 2026-06-30
version: 1.0
language: de
related: [specification, methodik, testing, design]
template:
  name: Vorlage Architecture
  version: 0.1
  url: https://dhcraft.org/Promptotyping/promptotyping-document/architecture
---

# Architecture

Wie vault-graph technisch realisiert ist. Dieses Dokument ist die kanonische Heimat fuer die Modul-Liste und Pipeline, die Datenarchitektur, die Privacy-Implementierung, die Determinismus-Mechanik, den semantischen Scout als gebautes Modul und die Output-Artefakte. Die epistemische Begruendung der Sichten, Aussagetypen und der Triangulationsmethode liegt in [methodik](methodik.md), die Pruefung der Garantien in [testing](testing.md).

## Pipeline und Module

Die Phasen liegen je als Modul in `vault_graph/`, orchestriert ueber `__main__.py`. Der Lauf geht von Parse zu Topology und Pragmatics, daraus Render und Explorer. Der semantische Scout laeuft als getrennter Modell-Lauf daneben.

- `parse.py` liest den Vault read-only ein, extrahiert den gerichteten Linkgraph aus Wikilinks samt Frontmatter, toten Links und Orphans, wendet den Privacy-Remap an und schreibt `graph.json`. Knoten-Schluessel ist der Dateiname-Stem.
- `topology.py` rechnet die Centrality-Suite (Degree in und out, Betweenness, Eigenvector, PageRank), die Louvain-Communities auf dem ungerichteten Projekt des Graphen, die K-Core-Dekomposition und die Brueckenknoten als Z-Score-Differenz `betweenness_z - degree_z >= 1.5`.
- `pragmatics.py` erfasst die pragmatische Sicht aus Top-Level-Ordner-Partition und Tags und kreuzt sie mit der topologischen Community zu Reinheit, NMI und Tag-Kohaesion, mit Ausreisser-Knoten als Diagnose-Kandidaten.
- `render.py` erzeugt die selfcontained `topology.html`, einen D3-Force-Directed-Graph, Knoten gefaerbt nach Community, Groesse nach PageRank, Bruecken markiert, mit Suche, Zoom, Label-Toggle und Detail-Panel.
- `explorer.py` erzeugt die read-only Werkbank `explorer.html` mit dem Graphen als Hauptflaeche und verbindet Topologie, Inhalts-Schicht und Triangulation in einem angereicherten PAYLOAD, das gebaute Interface beschreibt [design](design.md).
- `semantics.py` ist der semantische Scout (siehe eigener Abschnitt).
- `report_parse.py`, `report_topology.py` und `report_pragmatics.py` schreiben die Markdown-Berichte fuer die Gate-Kontrolle.

Diese Module implementieren die topologische und die pragmatische Sicht plus den semantischen Scout, die Sichten und die Triangulationsmethode selbst sind in [methodik](methodik.md) dargestellt.

## Konfiguration

Die Laufparameter stehen als Konstanten in `__main__.py`, der Vault-Pfad `VAULT_PATH`, das Output-Verzeichnis, die ausgeschlossenen Ordner, die Louvain- und Schwellwert-Parameter und der Privacy-Schalter. Der Vault-Pfad und die Privacy-Regel sind damit heute an diese Instanz gebunden, nicht an ein Argument oder eine Config-Datei. Ihre Hebung in echte Konfiguration ist der Schritt, der das Tool forkbar macht, gefuehrt als eigener Meilenstein in [plan](plan.md).

## Datenarchitektur

Topologie und Inhalt liegen in zwei getrennten Schichten, der Schluessel fuer jedes Frontend.

Die Topologie-Schicht steckt im eingebetteten PAYLOAD von `topology.html` und `explorer.html` mit `id`, `title`, `path`, `is_moc`, `anon`, `community`, `pagerank`, `degree`, `in_degree`, `out_degree`, `betweenness`, `k_core` und `is_bridge`.

Die Inhalts-Schicht steckt in `graph.json` mit `key`, `title`, `path`, vollstaendigem `frontmatter` inklusive `tags` und `type`, `body_preview`, `aliases`, `privacy_anonymized` und `is_moc`, dazu die globalen Strukturen `dead_links`, `orphans` und `stats`.

Beide Schichten sind ueber den Dateiname-Stem joinbar, `PAYLOAD.id` gleich `graph.json` `key`, fuer alle Knoten ausser dem anonymisierten Sonderfall. Ein reiches Read-Frontend mit Community-, Tag- und type-Filter, Orphan- und Bruecken-Hervorhebung und Atom-Sprung ist daraus zur Build-Zeit baubar, ohne die Pipeline neu zu laufen.

## Privacy-Implementierung

Knoten aus `Business/Angebote/` werden mehrlagig anonymisiert. Der Titel wird zu `Angebot-hash`, der Body nicht eingelesen, die sensitiven Frontmatter-Felder `invoice`, `summary` und `aliases` werden gestrippt, `key` und `path` im JSON ersetzt. An anderen Knoten werden Wikilinks auf einen anonymisierten Knoten im `body_preview` maskiert. Der Prefix `Business/Angebote` und die gestrippten Felder stehen heute als Konstanten in `parse.py`, ihre Hebung in echte Konfiguration laeuft als Forkbarkeits-Schritt in [plan](plan.md).

Der Remap ist eine Quelle der Wahrheit. `build_key_remap` und `export_path_for` liegen in `parse.py`, `write_graph_json`, `render` und `explorer` verwenden sie gemeinsam fuer Knoten-`id`, Pfad und Kanten-Endpunkte. Damit ist die fruehere Regression behoben, bei der `render.py` das PAYLOAD aus dem Live-Graphen vor dem Anonymisierungs-Remap baute, sodass der Klartext-Dateiname eines anonymisierten Business-Knotens in der generierten `topology.html` stand, waehrend `write_graph_json` bereits korrekt remappte. Zusaetzlich werden tote Links und Orphans anonymisierter Knoten aus der Explorer-Pflege-Triage herausgehalten.

Warum anonymisiert wird und warum Privacy die Befunde nicht glaetten darf, steht in [methodik](methodik.md).

## Semantischer Scout

`semantics.py` ist gebaut, Schicht 1 der Wissensgraph-Richtung. Es bettet jede nicht-anonymisierte Notiz lokal ein und bestimmt je Knoten die top-k inhaltlich naechsten Notizen ueber Cosinus-Aehnlichkeit. Daraus eine Diagnose-Liste latenter Verknuepfungen, hochaehnliche Paare ohne direkten Wikilink, rangiert nach Aehnlichkeit und mit der aktuellen Link-Distanz je Paar, direkt verlinkte Paare sind ausgeschlossen.

Die Schichtlogik laeuft ueber eine injizierbare Embedding-Funktion. Das trennt die deterministisch testbare Logik (Dokumentaufbau, Top-k, Schwelle, Ausschluss verlinkter Paare, Privacy-Filter) vom realen Modell-Lauf. Privacy liegt hinter demselben Remap, anonymisierte Business-Knoten werden nie eingebettet, ihr Rohtext nie gelesen, sie erscheinen weder als Knoten noch als Nachbar im Artefakt. Der Volltext wird frisch von der Platte gelesen, das Modell laeuft lokal, der Rohtext verlaesst den Rechner nicht. Modellwahl ist `multilingual-e5-large`. `sentence-transformers` und `torch` sind lazy in `requirements.txt`, Kern und Tests laufen ohne sie. Offen ist der echte Freeze gegen den lebenden Vault ueber `python -m vault_graph.semantics`, der die Paketinstallation und den Modell-Download braucht und `similarity.json` einfriert.

Die Vorwaertsrichtung auf getypte Relationen (M4) und die WEFT-Evidenzschicht steht in [plan](plan.md).

## Determinismus-Mechanik

Die Seeds und Schwellwerte stehen als Konstanten in `__main__.py`, darunter Louvain seed 42 und resolution 1.0, die Bruecken-Schwelle und die Reinheitsschwelle. Damit sind `graph.json` und `explorer.html` byte-identisch ueber Laeufe gegen denselben Vault-Stand. Der Determinismus ist relativ zu einem festen `vault_path`, der in `graph.json` serialisiert wird, in Betrieb ist `VAULT_PATH` konstant. Der semantische Scout traegt eine eigene Determinismus-Trennung, `similarity.json` ist byte-identisch bei fester injizierter Embedding-Funktion, der reale Modell-Lauf liegt als eingefrorenes Artefakt mit fixierter Modellversion und Seed ausserhalb des Determinismus-Tests.

Das Reproduzierbarkeitsprinzip steht in [methodik](methodik.md), die Garantie und wie sie maschinell geprueft ist in [testing](testing.md).

## Output-Artefakte

Output liegt in `output/`, ist gitignored und deterministisch regenerierbar ueber `python -m vault_graph`.

- `data/graph.json`
- `findings/parse-bericht.md`
- `findings/topology-bericht.md`
- `findings/triangulation-bericht.md`
- `visualisierung/topology.html`
- `visualisierung/explorer.html`

Der getrennte Semantik-Lauf erzeugt zwei weitere gitignored Artefakte.

- `data/similarity.json`
- `findings/latente-verknuepfungen.md`

## Was diese Architektur bewusst nicht leistet

Sie schreibt nie in den Vault, vault-graph ist reines Lese- und Analysewerkzeug. Sie haelt keine getypten Relationen vor, M4 ist gescopt, nicht gebaut. Sie schliesst die volle Triangulation aus drei Achsen nicht, der semantische Modell-Lauf bleibt bis zum Freeze offen. Sie fuehrt keine Wertung, Handlungsempfehlung oder inhaltliche Aussage ueber einzelne Dokumente, das ist eine methodische Grenze, kein technischer Mangel.
