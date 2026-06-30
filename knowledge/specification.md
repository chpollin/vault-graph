---
title: Specification
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
related: [methodik, architecture, plan, journal]
template:
  name: Vorlage Specification
  version: 0.1
  url: https://dhcraft.org/Promptotyping/promptotyping-document/specification
---

# Specification

Was vault-graph leisten soll und warum, samt der getroffenen Entscheidungen. Die technische Umsetzung steht in [architecture](architecture.md), der Vorwaertsplan in [plan](plan.md), die epistemische Grundlage in [methodik](methodik.md).

## Was vault-graph ist

vault-graph ist ein generisches Lese- und Analysewerkzeug fuer eine Markdown-Wissensbasis. Es parst einen Obsidian-Vault read-only, liefert eine topologische und eine pragmatische Analyse seines Linkgraphen und erzeugt zwei selfcontained HTML-Ansichten. Es ist nicht an einen bestimmten Vault gebunden, sondern als forkbares Werkzeug gedacht, das jeder gegen den eigenen Vault konfiguriert. Diese Repository-Instanz laeuft gegen den Vault des Operators und wird als Lane der Forschungsleitstelle betrieben, dieser Betrieb ist Instanz-Kontext, kein Teil der Werkzeug-Identitaet (siehe unten).

## Frage und Anspruch

Welche Strukturen lassen sich im Linkgraph eines Obsidian-Vaults methodisch belastbar identifizieren? Drei Sichten beantworten sie gemeinsam, die topologische ueber den Linkgraph aus Wikilinks, die pragmatische ueber die Triangulation gegen die gelebte Ablage in Ordnern und Tags, die semantische ueber inhaltliche Aehnlichkeit. Volle Darstellung der drei Sichten und der Triangulations-Methode in [methodik](methodik.md).

Das Tool liefert die topologische und die pragmatische Analyse plus zwei interaktive HTML-Ausgaben, dazu den semantischen Scout als Kandidaten-Generator. Es macht keine Wertung und keine inhaltliche Aussage ueber einzelne Dokumente. Es trennt die drei Aussagetypen Befund, Diagnose und Hypothese sauber (siehe [methodik](methodik.md)) und haelt diese Disziplin auch in jedem Frontend durch.

## Ziele

1. Topologische Befunde. Communities mit Modularitaet, Centrality-Hubs, Brueckenknoten, K-Core-Schichten, reproduzierbar gegen denselben Vault-Stand.
2. Pragmatische Sicht und Triangulation. Kreuzung der topologischen Communities mit der Ordner-Partition, gemessen ueber size-gewichtete Reinheit und Normalized Mutual Information, dazu die Tag-Kohaesion und Ausreisser-Knoten als Diagnose-Kandidaten.
3. Visualisierung. Selfcontained HTML ohne Server-Setup. Eine schlichte Force-Visualisierung und die Werkbank explorer.html mit dem Graphen als Hauptflaeche, benannten Community-Regionen, Hub-Labels, Kanten bei Auswahl und den drei Aussagetyp-Akzenten.
4. Privacy. Knoten eines konfigurierbaren Bereichs werden mehrlagig anonymisiert, ohne die Topologie zu glaetten. Begruendung in [methodik](methodik.md), Implementierung in [architecture](architecture.md).
5. Methodische Disziplin. Die drei Aussagetypen bleiben getrennt, Wert-, Soll- und Kausalaussagen sind ausgeschlossen.
6. Forkbarkeit. Vault-Pfad und Privacy-Regeln sind Konfiguration, kein Quelltext, sodass das Werkzeug ohne Code-Aenderung gegen einen fremden Vault laeuft. Heute liegen sie als Konstanten vor, die Hebung in echte Konfiguration ist als Meilenstein in [plan](plan.md) gefuehrt.

## Erfolgskriterien

1. Reproduzierbarkeit. Zweimaliger Lauf gegen denselben Vault-Stand und denselben Seed fuehrt zu byte-identischen Ausgaben. Das Prinzip steht in [methodik](methodik.md), die Mechanik und die maschinelle Pruefung in [architecture](architecture.md).
2. Plausibilitaet. Die Top-Hubs nach PageRank sind erkennbar zentrale Knoten des Vaults, MOCs landen unter den Top-Brueckenknoten.
3. Bedienbarkeit. Die HTML-Ausgaben laufen im Browser ohne Server-Setup, Suche, Zoom und Selektion funktionieren.

## Was das Tool nicht leistet

Keine Wertung, keine Handlungsempfehlung, keine inhaltliche Aussage ueber Dokumente, keine Kausal-Erklaerung, und die volle Triangulation aus drei Achsen ist vorbereitet, aber noch nicht geschlossen. Die methodische Begruendung dieser Grenzen traegt [methodik](methodik.md).

## Entscheidungen

Drei Operator-Beschluesse sind geschlossen und bilden die Kerninvarianten des Tools.

- Reines Lese- und Analysewerkzeug. vault-graph parst den Vault read-only und schreibt nie in ihn, nur in das eigene output-Verzeichnis. Damit ist die fruehere Frage nach kuratorischem Rueckschreiben gegenstandslos, ein Schreibterritorium gegen die Vault-Lane muss nicht gezogen werden. Sprachmodell-Vorschlaege laufen als eingefrorene Schicht daneben, das Tool schlaegt vor und schreibt nichts in den Vault.
- main als einzige Arbeitslinie. Gearbeitet wird ohne eigene Branches mit Hintergrund-Commit auf explizite Pfade, der Merge ist nach dem Prototyp-Feedback freigegeben, eine Branch-Gate-Frage entfaellt.
- Read-only-Grenze als feste Invariante. Sie ist die Bedingung dafuer, dass vault-graph als Messinstrument neben der Vault-Lane arbeitet, ohne Datei-Kollision.

## Einbettung in die Forschungsleitstelle (diese Instanz)

Dieser Abschnitt beschreibt den Betrieb der konkreten Repository-Instanz, nicht das generische Werkzeug. Ein Fork laesst ihn weg.

vault-graph ist hier eine Lane der Forschungsleitstelle mit der Rolle Beobachtungsinstrument. Weil es den Vault read-only parst, ist es das Messinstrument fuer den Wissenstransfer zwischen den Projekten. Die Projekt-Lanes sind die Messobjekte, ihr Transfer in den Vault ist das, was gemessen wird.

Kommunikation laeuft nur ueber zwei Dateien im forschungsleitstelle-Repo, reports/order-vault-graph.md herein und reports/handoff-vault-graph.md hinaus. Der Arbeitsmodus ist autonom auf main ohne eigene Branches, der handoff meldet das Delta, neue inhaltliche Fragen gehen als Operator-Frage oder Klaerung hinaus.

Konflikt-Radar gegen die Vault-Lane als Upstream. Die Vault-Lane ist Datenquelle und Upstream, sie editiert genau die Dateien, die hier geparst werden, jeder Move, Rename oder Dead-Link-Fix veraendert den Graphen flussaufwaerts. Die Read-only-Grenze haelt diese Abhaengigkeit kollisionsfrei, es gibt keine Datei-Kollision mit der Vault-Lane. Ein moeglicher kuenftiger Speicherort fuer bestaetigte getypte Relationen wird im eigenen Repo gefuehrt oder, falls je in den Vault, nur nach Abstimmung mit der Vault-Lane.
