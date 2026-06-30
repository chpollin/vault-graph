---
title: Testing
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
related: [architecture, methodik]
template:
  name: Vorlage Testing
  version: 0.1
  url: https://dhcraft.org/Promptotyping/promptotyping-document/testing
---

# Testing

Was die Testsuite garantiert, was sie bewusst nicht abdeckt, und wie geprueft wird. Die Suite sichert maschinell die zwei Versprechen, auf denen die Glaubwuerdigkeit des Werkzeugs ruht, Byte-Determinismus der Pipeline und die Privacy-Invariante der Ausgabe. Die aktuelle Testanzahl liest sich aus `python -m pytest tests/`, sie ist hier nicht eingefroren.

## Garantien

Was die Suite gegen Regression schuetzt.

- Byte-Determinismus der Pipeline. Zweimaliger Lauf gegen denselben Vault-Stand erzeugt byte-identische `graph.json` und `explorer.html`. Geprueft in-process und zusaetzlich ueber zwei Subprozesse mit verschiedenem `PYTHONHASHSEED`, das deckt eine hash-seed-abhaengige Mengen-Iteration und eine ungeseedete Zufallsquelle ab. Das Prinzip der Reproduzierbarkeit liegt in [methodik](methodik.md), die Mechanik (Seeds, Schwellwerte als Konstanten, geseedete Force-Simulation) in [architecture](architecture.md).
- Privacy-Invariante der `explorer.html`-Payload. Anonymisierte Knoten tragen keine Inhalts-Metadaten, sind aus der Pflege-Triage (tote Links, Orphans) ausgenommen, bekommen keinen Obsidian-Sprung, und kein Klartext-Business-Name leakt in das gerenderte HTML. Damit ist der frueher latente Render-Remap-Bug gegen Wiederkehr gesichert, der Test zieht einen Fixture-Knoten mit `</script>` im Titel ein, sodass auch der Script-Breakout-Pfad abgedeckt ist.
- Determinismus der Semantik relativ zu festem Rahmen. `similarity.json` ist byte-identisch ueber zwei Laeufe bei festem `vault_path` und fester injizierter Embedding-Funktion. Alle Reihenfolgen sind nach Key sortiert, der Cosinus auf vier Stellen gerundet, so traegt die Schichtlogik ihre Determinismus-Eigenschaft ohne Modell-Lauf.

## Was bewusst nicht garantiert wird

Negative Selbstdefinition, damit die Garantien nicht ueberlesen werden.

- Kein Determinismus des realen Modell-Laufs. Der echte Embedding-Lauf gegen den lebenden Vault bleibt ausserhalb der Suite, sein Ergebnis ist ein eingefrorenes Artefakt mit fixierter Modellversion und Seed, kein laufender Test. Die Suite prueft die Schichtlogik mit einer injizierten Dummy-Funktion, nicht das Modell.
- Keine absoluten Layout-Koordinaten. Die D3-Force-Mathematik ist ueber `randomSource(prng)` seed-deterministisch, die resultierenden Knotenpositionen sind jedoch viewport-relativ und entstehen erst im Browser. Sie liegen nicht in der HTML, deshalb beruehrt diese Nicht-Garantie die Datei-Determinismus-Invariante nicht.

## Teststruktur

Eine Datei je Phase, jeweils auf die methodisch tragenden Eigenschaften fokussiert.

- `tests/test_invariants.py`, das Invarianten-Netz. Byte-Determinismus der ganzen Pipeline in-process und ueber zwei Subprozesse mit verschiedenem `PYTHONHASHSEED`, und die Privacy-Invariante der gerenderten `explorer.html`.
- `tests/test_parse.py`, die Parse-Korrektheit. Wikilink-Extraktion, der mehrlagige Privacy-Filter samt Cross-References, Alias-Aufloesung und der nested-archive-Filter, also die Eigenschaften, auf denen jeder spaetere Befund aufsetzt.
- `tests/test_semantics.py`, der semantische Scout. Das mutual-kNN-Kriterium der latenten Verknuepfung mit handgesetzten Vektoren, plus Privacy und Byte-Determinismus von `similarity.json` ueber eine injizierte Embedding-Funktion und Themen-Marker.
- `tests/test_topology.py`, die Topology-Phase. Louvain-Reproduzierbarkeit unter gleichem Seed, positive Modularity bei struktureller Community und Brueckenknoten-Identifikation auf einem konstruierten Bow-Tie-Graphen.
- `tests/test_pragmatics.py`, die Pragmatik und Triangulation. Reinheit und NMI bei deckungsgleicher und bei unabhaengiger Partition, Ausreisser-Erkennung in einer sonst reinen Community, der Ausschluss anonymisierter Knoten aus der einzeln gelisteten Diagnose und die Tag-Kohaesion.

## Verifikations-Disziplin

Verify not trust gilt auch fuer die eigenen Subagenten. Gemeldete Agenten-Zahlen werden gegen die committeten Artefakte gegengeprueft, nicht uebernommen. Ein Agent hatte zu niedrige Community- und Bruecken-Zahlen gemeldet, die Pruefung gegen die PAYLOAD von `explorer.html` und gegen `graph.json` korrigierte das.

Die Browser-Sichtung laeuft ueber localhost, nicht ueber `file` (wird auf https umgeschrieben) und nicht ueber 127.0.0.1 (nicht freigegeben). Der d3-Force-Graph braucht den Tab im Vordergrund, weil `d3.timer` ueber `requestAnimationFrame` laeuft und dieses in inaktiven Tabs pausiert, dann tickt die Simulation nicht und die Knoten bleiben auf den d3-Startpositionen stehen, ohne einen Konsolenfehler. Das Aktivieren des Tabs startet das Ticking. Bei JS-Rueckgaben mit Query-String-artigen URIs greifen strukturelle Boolean-Checks statt roher URI-Strings, weil der Harness solche Strings blockt, und Integritaetschecks loesen die D3-Objektreferenzen auf, da `edge.source` und `edge.target` nach Simulationsstart zu Knotenobjekten mutieren.
