# Plan: WEFT-Evidenzschicht

## Zweck

vault-graph ist das Operationalising-Instrument des Forschungsprojekts WEFT. Dieser Plan beschreibt den Bau der Evidenz-Schicht, also den Weg von der finalisierten Relations-Ontologie zu einem typisierten, provenienztragenden Instanzgraphen, den das WEFT-Frontend und die geplante Ablationsstudie konsumieren. Er fokussiert die Evidenz-Schicht und ersetzt für diese Phase den Explorer-zentrierten `plan-zentrale-visualisierung.md` als Leitplan.

## Eingaben

- Das finalisierte Relations-Set v1 der Application-Profile-Ontologie (menschenlesbare Quelle im Obsidian-Vault, Vault Operations).
- Die maschinenlesbare Form `weft.ttl` im weft-Repo. Die CiTO-IRIs sind gegen die offizielle SPAR-Spezifikation verifiziert (2026-06-22). Zwei Inversen brechen das Muster, `cito:usesMethodIn` hat `cito:providesMethodFor`, und `cito:disagreesWith` ist gerichtet mit `cito:isDisagreedWithBy`, nicht symmetrisch.

## Bausteine

1. **Erweitertes Kantenschema.** Beide Exporter-Pfade (write_graph_json in parse.py mit {from,to}, das Payload in explorer.py mit {source,target}) emittieren dasselbe Schema {endpoints, relation_type, confidence, provenance, evidence, frozen_at}. Strukturelle Vorbedingung, die dem semantischen Mapping vorausliegt (Konsistenzbedingung C7).

2. **Anreicherungsmodul.** Ein Modul analog `semantics.py`, das aus den mutual-kNN-Kandidatenpaaren und den Notiz-Bodies typisierte Kanten vorschlägt, also relation_type aus dem Set v1, dazu confidence, evidence (das Kandidatenpaar), provenance llm-proposed und epistemicStatus hypothese. Es bleibt strikt getrennt vom byte-deterministischen Kern aus Parse, Topology und Pragmatics und wird als versioniertes Artefakt neben similarity.json eingefroren.

3. **Konsistenz-Sensoren.** Als Pipeline-Schritt, mit der verifizierten Aufteilung. Lokale Checks C5 (Provenienz-Status), C6 (stabile Identität) und C7 (Kantenschema) sind in SHACL Core ausdrückbar und werden auch dort gespiegelt. Die transitiven und graphweiten Checks C1 (Azyklizität), C2 (Hierarchie disjunkt von Assoziation, SKOS S27), C3 (Inversen-Vollständigkeit), C4 (Tag-gegen-Link) und die Objektseite von C8 (Privacy-Scope) sind nicht in SHACL Core ausdrückbar und laufen prozedural im Exporter, optional zusätzlich als SHACL-SPARQL. Die Shapes liegen in weft/shapes/weft.shacl.ttl.

4. **Stabile Knoten-Identität.** Jeder Knoten trägt eine vom Dateiname-Stem entkoppelte Kennung (id/uid oder Inhalts-Hash). Vorbedingung jeder persistenten Typisierung, sonst bricht jede bestätigte Kante beim Umbenennen.

5. **Export.** Der typisierte Instanzgraph als JSON (für das Frontend) und als Turtle-A-Box (für das weft-Repo und Validierung), getrennt vom deterministischen Kern.

## Verifikation

Drei Ebenen, Details in der Ontologie-Spec.

- **Deterministisch.** Ein Goldbild (gültige Beispiel-A-Box) muss alle Checks bestehen, je ein vergiftetes Gegenbild pro Bedingung muss vom richtigen Check gefangen werden. Fixtures liegen in weft/examples/. Dazu Turtle-Parse und SHACL-Validierung.
- **Populationsqualität.** Die vorgeschlagenen Relationstypen gegen den handgetypten Goldkorpus halten, Precision, Recall, F1 je Typ plus Konfusionsmatrix.
- **Forschungsbehauptung.** Die Ablationsstudie (flacher Text gegen untypisierte Links gegen ungetypte Kandidaten gegen volle getypte Ontologie), eigener späterer Milestone, anschlussfähig an das ablate-run-score-Muster von reasoning-prompt-bench.

## Abgrenzung

Kein SPARQL-Endpoint, kein Triple Store. Das Turtle ist die abgeleitete Maschinenform, es wandert ins weft-Repo. Die Schreibgrenze bleibt, keine LLM-vorgeschlagene Hypothese-Kante wird vor menschlicher Abnahme in den Vault persistiert.

## Stand

Plan steht. Beispielkorpus ist das Paläographie-Beispiel (weft/examples/example-graph.ttl) als erste A-Box und Goldbild. Offen ist die Code-Implementierung der Bausteine 1 bis 5 und das Frontend Phase 2, das den Export konsumiert.
