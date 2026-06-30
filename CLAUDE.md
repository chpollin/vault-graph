# CLAUDE.md

Action-Layer für Agenten, die an vault-graph arbeiten. Die Wissensbasis liegt in [knowledge/](knowledge/), Einstieg über [knowledge/INDEX.md](knowledge/INDEX.md). Lies sie als Kontext, bevor du Code oder Dokumente änderst.

## Vor der Arbeit lesen

- [knowledge/methodik.md](knowledge/methodik.md) für die epistemische Disziplin. Jede Ausgabe trägt genau einen Aussagetyp, Befund, Diagnose oder Hypothese. Wert-, Soll- und Kausalaussagen sind ausgeschlossen.
- [knowledge/architecture.md](knowledge/architecture.md) für Module, Datenschichten und die Privacy-Implementierung, bevor du am Code arbeitest.
- [knowledge/design.md](knowledge/design.md) vor jeder Änderung am Frontend explorer.html. Der Graph ist die Hauptfläche, die methodische Sprache ist ein durchgehendes visuelles System, nicht Dekoration.
- [knowledge/plan.md](knowledge/plan.md) für die Vorwärtsrichtung und offene Entscheidungen.

## Invarianten, die nie brechen dürfen

- Read-only. vault-graph schreibt nie in den Vault, nur in das eigene `output/`-Verzeichnis. Sprachmodell-Vorschläge laufen als eingefrorene Schicht daneben.
- Byte-Determinismus. Zweimaliger Lauf gegen denselben Vault-Stand erzeugt byte-identische Ausgaben. Seeds und Schwellwerte bleiben Konstanten, keine ungeseedete Zufallsquelle.
- Privacy hinter dem Remap. Anonymisierte Knoten verlieren Titel und Body, ihre Topologie bleibt. Jeder Embedding-Schritt liest erst den anonymisierten Knoten, nie den Rohtext davor.
- Verify not trust. Gemeldete Zahlen, auch die eigener Subagenten, werden gegen die committeten Artefakte (`graph.json`, die PAYLOAD der HTML) geprüft, nicht übernommen.

## Diese Instanz

Dieses Repository wird als Lane der Forschungsleitstelle betrieben, Rolle Beobachtungsinstrument. Kommunikation läuft über `reports/order-vault-graph.md` herein und `reports/handoff-vault-graph.md` im forschungsleitstelle-Repo hinaus, gearbeitet wird autonom auf main ohne eigene Branches. Der Vault-Pfad und die Privacy-Regel (`Business/Angebote`) sind Konstanten dieser Instanz, ein Fork konfiguriert sie um. Details in [knowledge/specification.md](knowledge/specification.md).

## Schreibstil

Knowledge-Dokumente folgen der Konvention für Promptotyping Documents (Frontmatter-Pflichtkern, eine Funktion pro Dokument, Redundanz über Links statt Wiederholung). Ein neues Konzept wird an genau einer kanonischen Stelle erklärt, andere Dokumente verlinken dorthin.
