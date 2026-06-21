# vault-graph Lane-Journal

Gedaechtnis der Lane fuer den Wiedereinstieg ohne Gespraechskontext. Je Runde ein Eintrag, neueste oben, knapp gehalten auf Verlauf und Entscheidungs-Provenienz. Der kanonische Wissensstand bleibt projektwissen.md, der Plan plan-zentrale-visualisierung.md, die volle Lane-Synthese liegt im forschungsleitstelle-Repo. Alle Eintraege sind Runden desselben Arbeitstags 2026-06-21, die Reihenfolge traegt die Chronologie, der Commit-Anker im Kopf verknuepft die Runde mit dem Git-Stand.

## Arbeitsphase, Frisch-Lauf und Gate-Schaerfung

v3-Statusmeldung an die Leitstelle abgegeben. Frischer Pipeline-Lauf gegen den lebenden Vault, weil die obsidian-vault-Lane flussaufwaerts die geparsten Dateien editiert, Ergebnis drift-frei, graph.json und explorer.html byte-identisch ueber zwei Laeufe, Testsuite gruen. Damit sind die Determinismus-Aussagen der Synthese aktuell.

Das Interface-Gate geschaerft, Korrektur der pauschalen Gate-Setzung der Vorrunde. Phase A zerfaellt in zwei Teile. Geschmacksneutral und ohne Freigabe baubar, weil er nur die ausdrueckliche Operator-Kritik vollzieht und von Palette und Layout unabhaengig ist, Kanten im Ruhezustand aus (De-Hairball, der Hervorhebungspfad liegt schon im Code), Statuszeile von elf flachen Kennzahlen zu benannten Gruppen, Tabelle auf tragende Spalten eingedampft mit Aufklapp-Rest. Vorbehalten und an die Freigabe gebunden, die Hex-Palette der drei Aussagetyp-Akzente, die volle Flaechenumkehr samt Vollbild-gegen-Drei-Spalten-Frage, die Aussagetyp-Faerbung der Knoten. Offen beim Operator, den neutralen Teil vorziehen oder erst nach Freigabe alles bauen. Cross-Lane fuer obsidian-vault, spuerbares Tote-Link-Substrat im aktuellen Vault, regenerierbar in parse-bericht.md.

## Konsolidierungsrunde, Gestaltungsvorschlag und knowledge-Bereinigung (b25945c)

Die order-Konsolidierung in drei Aufgaben abgearbeitet, Code, knowledge, Vault-Delta. Code verhaltenswahrend, ein ungenutzter Import raus. Den in den Befunden grossen Hebel zentraler Node-Record-Builder bei Sichtung verworfen, die Privacy-Invariante hat mit build_key_remap und export_path_for schon eine einzige Quelle der Wahrheit, die drei Record-Formen unterscheiden sich echt (graph.json mit Frontmatter und Body, HTML-Builder ohne, Triage filtert anonyme tote Links), ein erzwungener Builder waere Abstraktion ohne Gewinn und gefaehrdet den Byte-Determinismus. Der echte Dublettenfall render.py gegen explorer.py gehoert in den gegateten UI-Umbau.

knowledge verfestigt, variante-b-schreibterritorium.md und frontend-refactoring-befunde.md geloescht, beide durch die order-Entscheidungen gegenstandslos. Neu gestaltungsvorschlag-interface.md als Antwort auf textlastig, unuebersichtlich, flache Aesthetik, baulich deckungsgleich mit Phase A. Vault-Delta an die Leitstelle im handoff, die Vault-Session arbeitet es ein.

## Richtungsentscheidung Wissensgraph und Plan (abaa7d0)

Die zentrale Richtung im Operator-Dialog beschlossen. Die Netzwerkvisualisierung wird zum zentralen UI-Element, der reine Linkgraph zum getypten Wissensgraphen. Die tragende Idee kam vom Operator, Bedeutung steckt im Kontext der Beziehungen, nicht im einzelnen Dokument, dazu der Vorschlag einer Relationstaxonomie. Daraus das Zwei-Schichten-Modell, Embedding-Aehnlichkeit als billiger vollstaendiger Scout fuer Kandidatenpaare, getypte Relationen als bedeutungstragende Karte, vom Sprachmodell vorgeschlagen und vom Menschen bestaetigt.

Festgehalten in plan-zentrale-visualisierung.md, mit Leitidee (navigierbare Karte mit Linsen), acht Kriterien, sechs Relationstypen SKOS-angelehnt, Determinismus-Trennung ueber eine eingefrorene Vorschlagsschicht, Privacy hinter dem Remap, read-only Vorschlaege, vier Phasen mit Phase A risikoarm ohne neue Abhaengigkeit. Diese Entscheidung verschmilzt die zuvor getrennten Straenge Interface und Semantik zu einem Vorhaben. Offen gehalten, Skalierungsanspruch, Speicherung bestaetigter Relationen (beruehrt die Read-only-Grenze), endgueltige Taxonomie, Modellwahl.

## Autonomes Aufraeumen, tote Kennzahl und Doku-Versoehnung (ca5b3af)

closeness aus topology.py entfernt, als toter Code verifiziert (berechnet und in den Knoten-Record geschrieben, von keinem Konsumenten gelesen, Grep ueber das ganze Repo), seither fuenf statt sechs Centrality-Masse und die teuerste Berechnung faellt weg. Doku-Versoehnung, projektkonzept.md und METHODIK.md rahmten die laengst gebaute pragmatische Sicht noch als Stage-2-Zukunft und nannten ein nie existierendes triangulate.py, jetzt korrekt. Verifiziert, Tests gruen, Ausgaben byte-identisch, closeness null Treffer.

## Leitstellen-order, Aehnlichkeitsanalyse-Vorlage, Konsolidierung auf main (1992bcc)

Drei order-Entscheidungen geschlossen. vault-graph bleibt reines Lese- und Analysewerkzeug ohne Vault-Schreibzugriff, damit ist die Variante-B-Frage mit Nein entschieden. Vault-Name als obsidian verifiziert. Arbeitsmodus auf alles in main ohne eigene Branches umgestellt, main per Fast-Forward vom MVP 4383e93 auf den Session-Stand d8b90dd konsolidiert.

aehnlichkeitsanalyse-vorlage.md ausgearbeitet, die volle Vorlage zur semantischen Aehnlichkeitsanalyse, Funktionsweise in vier Schritten, Modellwahl lokal gegen API mit dem Datenschutz als Entscheidungsachse, Erkenntnisgewinn (latente Verknuepfungen, dritte Triangulationsachse, Near-Dubletten, Agent-Substrat), Empfehlung lokales Modell und neues Modul semantics.py. Zwei Operator-Entscheidungen offen, das Gewicht der torch-Abhaengigkeit und ob die Semantiksicht zugleich das Agent-Substrat wird.

## Analyse-Session und Ursprung der UI-Kritik (456c50b)

Auf Operator-Wunsch eine UI-Analyse, eine Refactoring-Bewertung und eine knowledge-Hygiene-Bewertung, kein Code geaendert. Hier entstand die UI-Kritik, zu textlastig, zu unuebersichtlich, flache Aesthetik, die spaeter in den Gestaltungsvorschlag wanderte. Die Befunde lagen in frontend-refactoring-befunde.md, in der Konsolidierungsrunde aufgeloest und geloescht.

## Portfolio-Runde, Browser-Sichtung und Verfahrenslehren (2b0e0f8)

Frischer Pipeline-Lauf deterministisch verifiziert, Testsuite gruen, explorer.html erstmals im Browser gesichtet mit Screenshot-Spur, headless im DOM geprueft auf referentielle Integritaet, Privacy, Stats-Deckung, Facetten-Filter und Obsidian-Sprung. variante-b-schreibterritorium.md als entscheidungsreife Vorlage geschrieben, spaeter durch die read-only-Entscheidung gegenstandslos.

Durable Verfahrenslehren aus dieser Runde. Browser-Sichtung lokaler HTML laeuft ueber localhost, nicht ueber file (wird auf https umgeschrieben) und nicht ueber 127.0.0.1 (nicht freigegeben). JS-Rueckgaben mit Query-String-artigen URIs werden vom Harness geblockt, daher strukturelle Boolean-Checks statt roher URI-Strings. D3 mutiert edge.source und edge.target nach Simulationsstart zu Knotenobjekten, Integritaetschecks muessen das aufloesen.
