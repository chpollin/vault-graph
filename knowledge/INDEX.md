---
title: Index
project:
  name: vault-graph
  repository: https://github.com/chpollin/vault-graph
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
status: complete
created: 2026-06-30
updated: 2026-06-30
version: 1.0
language: de
related: [methodik, specification, architecture, design, plan, journal, testing]
template:
  name: Vorlage Index
  version: 0.1
  url: https://dhcraft.org/Promptotyping/promptotyping-document/index
---

# Index

Navigation und Begriffslexikon der Wissensbasis von vault-graph. Der Index zeigt, wo etwas steht, und haelt das kanonische Glossar der konstitutiven Begriffe. Die laufenden Zahlen, also Knoten, Kanten, Communities, tote Links, Tag-Kohaesion, leben in den regenerierbaren output-Artefakten (data/graph.json, die findings-Berichte) und der erzeugten HTML, die der Lauf `python -m vault_graph` gegen den jeweiligen Vault-Stand erzeugt. Adressat ist eine Instanz oder Lane, die den Stand ohne Gespraechskontext aufnimmt.

## Dokumente

Die Reihenfolge folgt der Lese-Logik, von der Methodenseite ueber die Substanz zur Bauweise und Steuerung, nicht dem Alphabet.

| Dokument | Funktion | Update-Rhythmus |
|---|---|---|
| [methodik](methodik.md) | Domaenen- und Methodenwissen, epistemische Position, die drei Sichten, die drei Aussagetypen, die Privacy-Begruendung, das Reproduzierbarkeitsprinzip | bei methodischer Klaerung |
| [specification](specification.md) | Substanz, was das Tool leisten soll und warum, Ziele und Erfolgskriterien | bei Anforderungs- oder Scope-Aenderung |
| [architecture](architecture.md) | Bauweise, Module und Pipeline, die zwei Datenschichten, Privacy-Implementierung, Determinismus-Mechanik, Output-Artefakte | bei Code-Aenderung an Struktur oder Schichten |
| [design](design.md) | Gestalt der Werkbank explorer.html, Graph als Hauptflaeche, Farbsystem, Linsen, Interaktion | bei Interface- oder Gestaltungsaenderung |
| [plan](plan.md) | Plan und Steuerung, erledigte Meilensteine, Vorwaertsrichtung zum getypten Wissensgraphen, Forkbarkeit | bei Phasenwechsel oder Operator-Order |
| [journal](journal.md) | Genese, ein kompakter Eintrag pro substanzieller Runde | je Arbeitsrunde |
| [testing](testing.md) | Qualitaetssicherung, die Determinismus- und Privacy-Garantie und wie sie maschinell geprueft wird | bei Test- oder Garantieaenderung |

Daneben im Repo-Root, nicht in knowledge/, liegen [../README.md](../README.md) als Identitaet des Projekts fuer GitHub und [../CLAUDE.md](../CLAUDE.md) als Action-Layer, der das Agentenverhalten steuert und auf die Wissensbasis verweist.

## Lesepfade

Onboarding, was ist das Tool und auf welcher Methode steht es. [../README.md](../README.md) gibt die Identitaet, [methodik](methodik.md) die epistemische Position mit den drei Sichten und den drei Aussagetypen, [specification](specification.md) das, was daraus an Anforderung folgt, [architecture](architecture.md) die Umsetzung. Der Pfad geht von der Frage zur Antwort und erst dann zum Bau.

Reproduktion, einen Lauf nachstellen und die Garantie pruefen. [architecture](architecture.md) nennt Pipeline, Seeds als Konstanten und Output-Artefakte, [testing](testing.md) sagt, was byte-identisch garantiert ist und wie es maschinell geprueft wird, [journal](journal.md) ordnet den Lauf in seine Runde ein. Der Pfad geht von der Mechanik zur gepruefen Garantie zum Kontext.

Eine Designentscheidung verstehen, warum die Werkbank so aussieht. [specification](specification.md) gibt das Ziel der Visualisierung, [journal](journal.md) haelt fest, aus welchem Operator-Feedback und welcher Runde die Form entstand, [design](design.md) beschreibt den gebauten Zustand. Der Pfad geht vom Anspruch ueber die Genese zur Gestalt, so wird die Entscheidung als Folge sichtbar, nicht als Setzung.

## Konvention

Die Dokumente folgen der [[Konvention Promptotyping Documents]] im Vault, mit den Vorlagen in [[Vorlagen Promptotyping Documents]]. Frontmatter-Pflichtkern, das `template`-Feld und die drei Strukturprinzipien (Trennung Inhalt und Substanzherkunft, Standards im Hauptteil, negative Selbstdefinition) gelten pro Dokument.

## Begriffe

Kanonisches Glossar der konstitutiven Begriffe, alphabetisch. Je Begriff ein knapper Absatz. Die drei Aussagetypen sind hier nur Glossar-Zeilen, ihre volle Definition lebt in [methodik](methodik.md).

**Aussagetyp.** Eine der drei Stufen, in die das Tool seine Aussagen sortiert, Befund, Diagnose, Hypothese. Volle Definition in [methodik](methodik.md), im Interface ein durchgehendes Farbsystem (siehe [design](design.md)).

**Befund.** Datengestuetzte, gegen denselben Vault-Stand und Tool-Git-Hash reproduzierbare Aussage. Erster der drei Aussagetypen, voll in [methodik](methodik.md).

**Brueckenknoten.** Knoten mit hoher Betweenness bei nur moderater Degree, operationalisiert als Z-Score-Differenz betweenness_z - degree_z >= 1.5. Kandidat fuer ein Querkonzept, das sonst getrennte Bereiche verbindet.

**Diagnose.** Datengestuetzte Auffaelligkeit, die Pflege nahelegt, etwa ein toter Wikilink oder ein Ausreisser-Knoten in einem fremden Ordner. Zweiter der drei Aussagetypen, voll in [methodik](methodik.md).

**Hypothese.** Schwaecher gestuetzte Aussage, etwa ein topologischer Cluster ohne semantische Stuetze oder ein hochaehnliches Notizpaar ohne Wikilink, menschlich zu bestaetigen. Dritter der drei Aussagetypen, voll in [methodik](methodik.md).

**K-Core.** Der hoechste k, fuer den ein Knoten in einem Teilgraphen liegt, in dem jeder Knoten mindestens k Nachbarn hat. Der innerste Kern markiert den dichtesten vernetzten Bereich des Vaults.

**Latente Verknuepfung.** Ein Paar inhaltlich hochaehnlicher Notizen ohne direkten Wikilink, vom semantischen Scout als Diagnose gemeldet und nach Aehnlichkeit rangiert. Jedes Paar ist eine Hypothese, kein Befund.

**Louvain-Community.** Eine ueber den Louvain-Algorithmus auf dem ungerichteten Projekt des Linkgraphen gefundene Knotengruppe, gerechnet mit Seed 42 und Resolution 1.0. Bildet die topologische Partition des Vaults.

**Pragmatische Sicht.** Die gelebte Ablage in Top-Level-Ordnern und die Tag-Vergabe, aus den vorhandenen Attributen kostenfrei berechnet. Zweite der drei Sichten, gegen die topologische Community trianguliert.

**Privacy-Remap.** Die einheitliche Umschluesselung anonymisierter Knoten ueber eine Quelle der Wahrheit in der Parse-Stufe, die alle ausgebenden Stufen gemeinsam nutzen. Begruendung in [methodik](methodik.md), Implementierung in [architecture](architecture.md).

**Scout und Karte.** Das Zwei-Schichten-Modell der Wissensgraph-Richtung. Schicht eins ist der Scout, billige vollstaendige Embedding-Aehnlichkeit als Kandidaten-Generator. Schicht zwei ist die Karte, getypte Relationen ueber eine kleine Taxonomie als bedeutungstragende Verbindung. Der Scout ist gebaut, die Karte gescopt (siehe [plan](plan.md)).

**Tag-Kohaesion.** Mass dafuer, wie konzentriert die Knoten eines Tags in einer einzelnen Louvain-Community liegen. Ein konzentrierter Tag ist topologisch geschlossen, ein gestreuter ein Querschnitts-Tag. Teil der pragmatischen Sicht (siehe [methodik](methodik.md)).

**Topologische Sicht.** Der gerichtete Linkgraph aus Wikilinks und seine Strukturmasse, Communities, Centrality, Brueckenknoten, K-Core. Erste der drei Sichten.

**Triangulation.** Die Methode, dieselbe Frage ueber mehrere unabhaengig entstandene Sichten zu kreuzen, derzeit topologische Community gegen pragmatische Ordner-Partition, gemessen ueber Reinheit (Schwelle 0.60) und Normalized Mutual Information. Volle Darstellung in [methodik](methodik.md). Die dritte, semantische Achse ist vorbereitet, die volle Triangulation aus drei Achsen noch nicht geschlossen.

## Was fehlt und warum

Keine data.md. Das verarbeitete Material ist der read-only geparste Vault selbst, kein eigenes Datenkorpus. Seine Struktur, Linkgraph, Frontmatter, die zwei joinbaren Schichten, steht in [architecture](architecture.md), die Einordnung als Datenquelle in [../README.md](../README.md).

Keine report.md in knowledge/. Die Stand-zur-Zeit-Funktion liegt ausserhalb der Wissensbasis in findings/maintenance-signal.md als regenerierbarer Snapshot fuer die Vault-Lane. Sie traegt volatile Zahlen und gehoert deshalb nicht in ein dauerhaftes knowledge-Dokument.
