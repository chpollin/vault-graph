---
title: Plan
project:
  name: vault-graph
  repository: https://github.com/chpollin/vault-graph
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
status: draft
created: 2026-06-21
updated: 2026-06-30
version: 1.0
language: de
related: [specification, architecture, methodik, journal]
template:
  name: Vorlage Plan
  version: 0.1
  url: https://dhcraft.org/Promptotyping/promptotyping-document/plan
---

# Plan

Der vorwaertsgerichtete Leitplan von vault-graph. Er haelt fest, wohin das Tool waechst, in welcher Reihenfolge die Schichten gebaut werden und welche Entscheidungen dafuer noch fallen muessen. Er fuehrt das Zwei-Schichten-Modell der Bedeutung als tragende Idee und beschreibt mit der WEFT-Evidenzschicht den aktuellen Bauplan fuer die getypte Karte. Den erreichten Stand pro Runde haelt das [journal](journal.md), das rueckwaertsgerichtete Pendant.

## Leitidee

Die zentrale Visualisierung ist kein Bild des ganzen Netzes, sondern eine navigierbare Karte mit waehlbaren Linsen. Man bewegt sich darin, vom Ueberblick in eine Community, auf einen Knoten und seine Nachbarschaft, wieder zurueck, und legt verschiedene Linsen darueber, die je eine Frage beantworten. Eine Struktur-Linse zeigt Communities und Bruecken, eine Pflege-Linse tote Links und fehlplatzierte Knoten, eine Wachstums-Linse die latente Naehe und die vorgeschlagenen Relationen. Ein Gesamtbild wird beim Wachsen schlechter lesbar, eine navigierbare Karte wird reicher.

Dahinter steht die These, dass Bedeutung im Kontext steckt, also in den Beziehungen zwischen Notizen, nicht im einzelnen Dokument. Der reine Linkgraph aus expliziten Wikilinks kennt nur einen Bruchteil dieser Beziehungen. Das Ziel ist ein getypter Wissensgraph, in dem latente Naehe sichtbar und benannte, gerichtete Relationen die Karte tragen.

## Zwei-Schichten-Modell der Bedeutung

Bedeutung entsteht in zwei Schritten, einem billigen vollstaendigen und einem teuren gezielten.

Schicht eins ist die semantische Aehnlichkeit als Scout. Ein lokales Embedding-Modell bildet jede Notiz auf einen Vektor ab, die Cosinus-Aehnlichkeit misst inhaltliche Naehe. Diese Naehe ist ungerichtet und unbenannt, sie sagt nur, dass zwei Notizen vom Aehnlichen handeln. Ihr Wert liegt darin, aus der quadratisch wachsenden Menge aller Notizpaare die wenigen herauszuziehen, die ueberhaupt eine Beziehung haben koennten. Methodisch ist sie ein Kandidaten-Generator, kein Befund, jedes gemeldete Paar bleibt eine Hypothese (zu den drei Aussagetypen siehe [methodik](methodik.md)).

Schicht zwei sind getypte Relationen als Karte. Auf die Kandidatenpaare aus Schicht eins setzt eine Typisierung an, die jeder Beziehung ueber eine kleine Relationstaxonomie Richtung und Bedeutung gibt. Das Embedding sagt nur, dass zwei Notizen aehnlich sind, die Typisierung sagt, dass die eine eine kritische Weiterentwicklung der anderen ist. Das Ergebnis ist kein Aehnlichkeitsnebel, sondern ein getypter Wissensgraph mit gerichteten, nach Relationstyp eingefaerbten Kanten. Die Typvorschlaege kommen vom Sprachmodell und werden vom Menschen bestaetigt, sie sind Hypothesen oder Diagnosen, keine Befunde.

## Relationstaxonomie

Die Taxonomie bleibt klein, weil eine kleine Taxonomie tatsaechlich vergeben wird und eine grosse in der Praxis erstickt. Sechs Typen, an die enger-breiter-verwandt-Logik von SKOS angelehnt, wo moeglich.

1. spezialisiert, umgekehrt generalisiert (enger gegen breiter)
2. ist Teil von, umgekehrt umfasst (Komposition, die MOC-Beziehung)
3. baut auf, stuetzt (ein Konzept setzt ein anderes voraus oder belegt es)
4. kontrastiert, widerspricht (Spannung oder Alternative)
5. ist Methode fuer, wird angewandt auf (Methode gegen Anwendung)
6. ist Beispiel fuer, instanziiert (Instanz gegen Klasse)

Dazu verwandt als neutraler Rueckfall fuer eine bestaetigte, aber nicht typisierbare Naehe. Die Liste ist ein Vorschlag zur Schaerfung am konkreten Vault, die endgueltige Fassung ist eine offene Entscheidung. In der maschinenlesbaren Form (WEFT) tragen die Typen verifizierte CiTO-IRIs, zwei davon brechen das Symmetrie-Muster, `cito:usesMethodIn` hat `cito:providesMethodFor` als Inverse, und `cito:disagreesWith` ist gerichtet mit `cito:isDisagreedWithBy`, nicht symmetrisch.

## WEFT-Evidenzschicht

vault-graph ist das Operationalisierungs-Instrument des Forschungsprojekts WEFT. Die Evidenzschicht ist der Weg von der finalisierten Relations-Ontologie zu einem typisierten, provenienztragenden Instanzgraphen, den das WEFT-Frontend und die geplante Ablationsstudie konsumieren. Eingaben sind das finalisierte Relations-Set v1 der Application-Profile-Ontologie (menschenlesbare Quelle im Vault unter Vault Operations) und seine maschinenlesbare Form `weft.ttl` im weft-Repo.

Der Bauplan traegt fuenf Bausteine.

1. Erweitertes Kantenschema. Beide Exporter-Pfade emittieren dasselbe Schema {endpoints, relation_type, confidence, provenance, evidence, frozen_at}, der `write_graph_json`-Pfad in parse.py mit {from,to}, das Payload in explorer.py mit {source,target}. Strukturelle Vorbedingung, die dem semantischen Mapping vorausliegt (Konsistenzbedingung C7).

2. Anreicherungsmodul, gebaut analog zum semantischen Scout (Modulaufbau siehe [architecture](architecture.md)). Es schlaegt aus den mutual-kNN-Kandidatenpaaren und den Notiz-Bodies typisierte Kanten vor, also relation_type aus dem Set v1 plus confidence, evidence (das Kandidatenpaar), provenance llm-proposed und epistemicStatus hypothese. Es bleibt strikt getrennt vom byte-deterministischen Kern und wird als versioniertes Artefakt neben similarity.json eingefroren.

3. Konsistenz-Sensoren als Pipeline-Schritt, mit verifizierter Aufteilung. Die lokalen Checks C5 (Provenienz-Status), C6 (stabile Identitaet) und C7 (Kantenschema) sind in SHACL Core ausdrueckbar und werden dort gespiegelt. Die transitiven und graphweiten Checks C1 (Azyklizitaet), C2 (Hierarchie disjunkt von Assoziation, SKOS S27), C3 (Inversen-Vollstaendigkeit), C4 (Tag gegen Link) und die Objektseite von C8 (Privacy-Scope) sind nicht in SHACL Core ausdrueckbar und laufen prozedural im Exporter, optional zusaetzlich als SHACL-SPARQL. Die Shapes liegen in weft/shapes/weft.shacl.ttl.

4. Stabile Knoten-Identitaet. Jeder Knoten traegt eine vom Dateiname-Stem entkoppelte Kennung (id/uid oder Inhalts-Hash). Vorbedingung jeder persistenten Typisierung, sonst bricht jede bestaetigte Kante beim Umbenennen. Der heutige Knoten-Schluessel ist der Stem, die Entkopplung ist noch zu bauen.

5. Export. Der typisierte Instanzgraph als JSON fuer das Frontend und als Turtle-A-Box fuer das weft-Repo und die Validierung, getrennt vom deterministischen Kern.

Abgrenzung. Kein SPARQL-Endpoint, kein Triple Store. Das Turtle ist die abgeleitete Maschinenform und wandert ins weft-Repo. Die Schreibgrenze bleibt, keine sprachmodell-vorgeschlagene Hypothese-Kante wird vor menschlicher Abnahme in den Vault persistiert.

Verifikation auf drei Ebenen. Deterministisch, ein Goldbild (gueltige Beispiel-A-Box) besteht alle Checks, je ein vergiftetes Gegenbild pro Bedingung wird vom richtigen Check gefangen, dazu Turtle-Parse und SHACL-Validierung, Fixtures in weft/examples/. Populationsqualitaet, die vorgeschlagenen Typen halten gegen einen handgetypten Goldkorpus, gemessen ueber Precision, Recall, F1 je Typ und Konfusionsmatrix. Forschungsbehauptung, die Ablationsstudie (flacher Text gegen untypisierte Links gegen ungetypte Kandidaten gegen volle getypte Ontologie) als eigener spaeterer Milestone, anschlussfaehig an das ablate-run-score-Muster von reasoning-prompt-bench.

## Phasen und Stand

Die Phasen bauen die Schichten in Reihenfolge des Risikos, die leichte tragfaehige Karte zuerst, die schwere Embedding- und Sprachmodell-Schicht danach.

- Phase A, Karte tragfaehig. Erledigt. Die Werkbank explorer.html ist zur navigierbaren Karte umgebaut, Graph als Hauptflaeche, Kanten erst bei Auswahl, stabile Positionen, Aussagetyp als Knotenring, drei Linsen. Das gebaute Interface ist deklarativ in [design](design.md) beschrieben.
- Phase B, semantische Aehnlichkeit. Scout M3 ist als Modul gebaut, lokales Embedding, top-k Cosinus-Nachbarn, Diagnose-Liste latenter Verknuepfungen. Offen bleibt nur der reale Modell-Lauf, der similarity.json gegen den lebenden Vault einfriert, er braucht die Installation von sentence-transformers und den Modell-Download.
- Phase C, getypte Relationen. Gescopt, nicht gebaut. Sie setzt die WEFT-Evidenzschicht um, die Vorschlagsschicht ueber das Sprachmodell, die Relationstaxonomie, gerichtete eingefaerbte Kanten und den Bestaetigungs-Workflow.
- Phase D, Skalierung. Aggregation zu Community-Meta-Knoten, Drill-down, gegebenenfalls Technikwechsel von SVG zu Canvas oder WebGL. Die Wahl haengt am Skalierungsanspruch.

Beispielkorpus und erstes Goldbild ist das Palaeographie-Beispiel (weft/examples/example-graph.ttl) als erste A-Box. Den laufenden Verlauf je Runde haelt das [journal](journal.md).

## Agent-lesbare Schicht und semantische Suche

Der Embedding-Index aus Schicht eins traegt mehr als die latente-Link-Diagnose. Er erlaubt semantische Suche ueber den Vault, ein Agent fragt nach Bedeutung statt nach Link und holt Notizen in der Naehe von X, auch ohne expliziten Pfad. Damit wird die semantische Sicht zugleich das Substrat fuer eine agent-lesbare Schicht ueber dem Vault, und der Anknuepfungspunkt fuer das forkbare Frontend ueber dem eigenen Vault. Diese Verwendung beruehrt die Arbeit der obsidian-vault-Lane an einer agent-tauglichen Wissensarchitektur und ist gegen sie abzustimmen, statt einen konkurrierenden Zugang zu bauen. Ein zweiter Ertrag derselben Schicht sind Near-Dubletten, Paare sehr hoher Aehnlichkeit als Kurationssignal zur Redundanz-Aufloesung, heute nicht gebaut, anschlussfaehig an dieselbe Aehnlichkeitsmatrix.

## Generalisierung und Forkbarkeit

Der Analysekern ist bereits vault-agnostisch, drei Kopplungen binden das Tool aber heute an die Operator-Instanz und sind zu loesen, damit ein Fork ohne Code-Aenderung gegen einen fremden Vault laeuft.

1. Vault-Pfad als Konfiguration. `VAULT_PATH` ist heute eine Konstante in `__main__.py`. Es wird ein CLI-Argument oder eine Config-Datei, sodass der Lauf den Pfad als Eingabe nimmt statt als Quelltext.
2. Privacy-Regeln als Konfiguration. Der Prefix `Business/Angebote` und die gestrippten Frontmatter-Felder sind heute Konstanten in `parse.py`. Sie werden konfigurierbar als Liste von Glob-Mustern plus Liste zu strippender Felder, ein Fork ohne sensiblen Bereich schaltet die Anonymisierung schlicht ab.
3. Neutrale Nutzer-Texte. Die explorer- und Bericht-Texte reden von Business-Knoten. Sie werden auf neutrales Wording wie anonymisierte Knoten gezogen, damit ein Fork keine fremde Vault-Semantik liest.

Der Operator-Vault wird damit zur Referenz-Instanz, an der dogfooded wird, ein Config-Eintrag statt eines Hardcodes. Die Read-only-Grenze und der Determinismus-Kern bleiben dabei unberuehrt.

## Offene Entscheidungen

Vier Detailweichen fallen einzeln, wenn ihre Phase sie braucht.

- Skalierungsanspruch. Wie gross das Netz werden soll, bestimmt die Technikwahl in Phase D.
- Speicherung bestaetigter Relationen. Sie beruehrt die Read-only-Grenze. vault-graph schreibt nie in den Vault, ein Speicherort fuer bestaetigte getypte Relationen, etwa als getypte Links in den Notizen, waere mit der Vault-Lane abzustimmen.
- Endgueltige Relationstaxonomie. Welche Typen fuer diesen Vault tatsaechlich tragen, geschaerft am konkreten Material.
- Modellwahl. Das lokale Embedding-Modell der Schicht eins und das Sprachmodell fuer die Typisierung der Schicht zwei.
