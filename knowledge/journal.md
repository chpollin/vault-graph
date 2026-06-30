---
title: Journal
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
related: [specification, architecture, plan, methodik]
template:
  name: Vorlage Journal
  version: 0.1
  url: https://dhcraft.org/Promptotyping/promptotyping-document/journal
---

# vault-graph Lane-Journal

Gedaechtnis der Lane fuer den Wiedereinstieg ohne Gespraechskontext. Je Runde ein Eintrag, neueste oben, knapp gehalten auf Verlauf und Entscheidungs-Provenienz. Der kanonische Wissensstand liegt in den Funktionsdokumenten ([specification](specification.md), [architecture](architecture.md), [methodik](methodik.md)), der Vorwaertsplan in [plan](plan.md), die volle Lane-Synthese im forschungsleitstelle-Repo. Die Eintraege nennen Datei- und Dokumentnamen im Stand ihres jeweiligen Commits; seit dem knowledge-Refactor vom 2026-06-30 gelten die englischen Dateinamen der Funktionsdokumente. Die Reihenfolge traegt die Chronologie, der Commit-Anker im Kopf verknuepft die Runde mit dem Git-Stand.

## M3 Semantischer Scout gebaut, M4 gescopt (dieser Commit)

Order-Runde, der Koordinator hat auf meinem Stand 44547c7 entschieden, M3 bauen, M4 nur scopen, die schwere Abhaengigkeit lazy aufnehmen (orchestrator-entschieden, kein Gate). Nach dem Sync den Auftrag autonom umgesetzt.

M3, der semantische Scout als Schicht 1 der Phase B. Neues Modul `vault_graph/semantics.py`. Es bettet jede nicht-anonymisierte Notiz lokal ein und findet je Knoten die top-k inhaltlich naechsten ueber Cosinus-Aehnlichkeit, dazu eine Diagnose-Liste latenter Verknuepfungen, hochaehnliche Paare ohne direkten Wikilink, rangiert nach Aehnlichkeit, mit der aktuellen Link-Distanz je Paar. Direkt verlinkte Paare (Distanz 1) sind ausgeschlossen, sie sind keine Luecke. Artefakte `output/data/similarity.json` (je Knoten top-k mit Cosinus und Link-Distanz plus die latente-Link-Liste) und der Report `findings/latente-verknuepfungen.md`, beide gitignored unter output/.

Determinismus-Trennung als Konstruktionsprinzip. Die Schichtlogik (Dokumentaufbau, Top-k, Schwelle, Ausschluss verlinkter Paare, Privacy-Filter) laeuft ueber eine injizierbare Embedding-Funktion und ist mit Dummy-Vektoren ohne Modell-Lauf deterministisch testbar; alle Reihenfolgen sind nach Key sortiert, Cosinus auf vier Stellen gerundet, so ist similarity.json byte-identisch ueber zwei Laeufe bei fester injizierter Funktion. Der echte Modell-Lauf bleibt ausserhalb des Determinismus-Tests, sein Ergebnis ist ein eingefrorenes Artefakt mit fixierter Modellversion und Seed.

Privacy hinter dem Remap. Anonymisierte Business-Knoten werden nie eingebettet (uebersprungen ueber `privacy_anonymized`), ihr Rohtext wird nie gelesen, sie erscheinen weder als Knoten noch als Nachbar in similarity.json, kein Geheimtext leakt. Der Volltext wird frisch von der Platte gelesen (graph.json fuehrt nur den Preview, parse.py hatte das so vorgezeichnet), das Modell laeuft lokal, der Rohtext verlaesst den Rechner nicht. Dependency, `sentence-transformers` und `torch` lazy in requirements.txt, erst im Modul-Aufruf importiert, Kern und Tests laufen ohne sie. Modellwahl multilingual-e5-large (mehrsprachig, passt zum deutsch-englischen Vault), als Bau-Zeitpunkt-Abhaengigkeit verdrahtet.

Verifikation. 61 Tests gruen (51 plus 10 neue in tests/test_semantics.py), die Schichtlogik mit kontrollierten Themen-Markern geprueft (ein latent gemeldetes Paar gleichen Themas ohne Link, ein direkt verlinktes Paar trotz Themengleichheit nicht gemeldet, top-k eingehalten, Nachbarn absteigend sortiert), die Privacy-Invariante gegen das serialisierte Artefakt (kein Geheim-Key, kein Angebot-Hash, kein Geheimtext), der Byte-Determinismus ueber zwei Laeufe. Lazy-Import bestaetigt, das Modul laedt ohne installiertes sentence-transformers.

Offen, der echte Freeze. similarity.json gegen den lebenden Vault einfrieren steht noch aus, es braucht die Installation von sentence-transformers und den Modell-Download (torch ist lokal vorhanden, das Paket nicht). Das ist der vom Order getrennte Modell-Lauf, kein Code-Delta. Cross-Lane, vor dem Einfrieren ein frischer Pipeline-Lauf gegen den lebenden Vault, da obsidian-vault flussaufwaerts die geparsten Dateien editiert.

M4 gescopt, nicht gebaut. Auf die M3-Kandidatenpaare setzt eine kleine Relationstaxonomie, sechs SKOS-angelehnte Typen plus verwandt als Rueckfall, sprachmodell-vorgeschlagen und menschlich bestaetigt, als eingefrorenes versioniertes Vorschlagsartefakt getrennt vom deterministischen Kern. Scope-Notiz im projektwissen, Bau erst auf Order.

## Graph-Lesbarkeit, benannte Community-Regionen und Hub-Labels (44547c7)

UI-Milestone aus dem Lesbarkeits-Hebel gebaut, auf das Operator-Signal continue und nach der Operator-Frage, ob die Knotenfarben klar sind und ob es eine Legende gibt. Die ehrliche Lage war, der Ring (Aussagetyp) hatte eine Legende, die Fuellung (Community) hatte keine, und eine Farbe-zu-Nummer-Legende waere nutzlos. Drei Aenderungen, rein im Template, `_build_payload` unangetastet, damit Determinismus- und Privacy-Netz gueltig bleiben.

Erstens, Hub-Labels. Die Top 24 Knoten nach PageRank dauerhaft beschriftet (deterministischer id-Tiebreak), jenseits einer Zoomschwelle erscheint jedes nicht-gedimmte Label, bei Auswahl das Ego-Netz. Zweitens, Community-Regionen. Je Community eine blasse Convex Hull hinter den Knoten, beschriftet mit ihrem dominanten Ordner, so wird aus einer Fuellfarbe eine benennbare Region. Die Legende erklaert jetzt beide Achsen, Fuellung gleich Community, Ring gleich Aussagetyp. Drittens, der Zoom laeuft auf eine eigene Viewport-Gruppe statt auf alle g, das war ohnehin noetig, sobald Hulls und Labels als weitere Gruppen dazukommen.

Ursachenfix statt Symptom. Die erste Sichtung zeigte, dass Convex Hulls nur tragen, wenn die Communities raeumlich getrennt liegen; im reinen Force-Layout ueberlappten sie in einem Ball zu riesigen Flaechen, die Region-Labels stapelten sich in der Mitte. Daher eine Cluster-Kraft, jede Community wird ueber forceX und forceY zu einem eigenen Anker auf einem Ring gezogen, die forceCenter-Kraft entfaellt. Danach trennen sich die Regionen in Lappen, die zweite Sichtung zeigt benannte, separierte Cluster.

Ehrlicher Nebenbefund. Der Ordner Projects erscheint als Region-Label dreimal, weil der Projects-Ordner topologisch in drei Link-Communities zerfaellt; das ist kein Fehler, sondern genau die Triangulations-Aussage, dass Community und Ordner nicht deckungsgleich sind. Das Layout ist in der Force-Mathematik seed-deterministisch, in absoluten Koordinaten aber viewport-relativ; die Datei-Determinismus-Invariante bleibt unberuehrt, weil Positionen im Browser entstehen und nicht in der HTML liegen, 51 Tests gruen.

Verifikation. 51 Tests gruen, Pipeline regeneriert, Browser-Sichtung im Vordergrund, neun benannte Community-Regionen mit Ordner-Labels, 24 Hub-Labels, beide Farbachsen in der Legende, Zoom auf einer Container-Gruppe, Screenshot-Spur des separierten Layouts.

Durable Lehre. Die Browser-Sichtung eines d3-Force-Graphen braucht den Tab im Vordergrund. d3.timer nutzt requestAnimationFrame, das in inaktiven Tabs pausiert, dann macht die Simulation null Ticks, die Knoten bleiben exakt auf den d3-Startpositionen (erster Knoten 7.07, 0), ohne einen Konsolenfehler. Das Aktivieren des Tabs ueber einen Screenshot startet das Ticking.

## Frontend-Bewertung, Haertungsbefunde und Operator-Sichtung Phase A (2aab5da)

Operator hat das Phase-A-Interface lokal im Browser gesichtet (frischer Pipeline-Lauf, ueber localhost serviert) und die Richtung abgenommen, keine Korrektur an Palette oder Layout verlangt. Damit ist die Operator-Spur des M2-Umbaus eingeloest, die Sichtung positiv.

Auf Operator-Frage, ob CSS, HTML und JS zu haerten sind, das Frontend ganz gelesen und drei Befunde erhoben. Erstens, ein latenter Script-Breakout. Das Payload wird als `const PAYLOAD` ueber `json.dumps` in einen `<script>`-Block eingebettet (explorer.py:47 und :320), und `json.dumps` escaped `<` und `>` nicht. Ein Vault-Titel oder -Pfad mit der Zeichenfolge `</script>` braeche aus dem Script-Kontext aus. Heute existiert kein solcher Titel, der Bug ist latent, aber echt, er bricht die Seite und wird bei Weitergabe der HTML zum Injection-Vektor. Der Fix ist klein und determinismus-erhaltend, im eingebetteten JSON `<`, `>`, `&` sowie die Zeilentrenner U+2028 und U+2029 als Unicode-Escapes ausgeben, plus ein Regressionstest im Invarianten-Netz (Fixture-Knoten mit `</script>` im Titel). Zweitens, d3 wird vom CDN geladen (explorer.py:318), was dem Selfcontained-Erfolgskriterium im projektkonzept widerspricht, offline oder bei Weitergabe ohne Netz bricht der Graph. Weiche, d3 inlinen (autark, jede Ausgabe groesser) oder ein SRI-Integrity-Hash (bleibt netzabhaengig). Fachurteil inlinen, weil es den eigenen Anspruch erfuellt. Drittens, das ganze Frontend liegt als ein roher `_TEMPLATE`-String in explorer.py (Zeilen 140 bis 685), rund 550 Zeilen CSS, HTML und JS in einem Python-Literal, ohne Tooling fuer die drei Sprachen. Sauber waere ein Asset-Split nach `vault_graph/assets/` ueber `importlib.resources`, determinismus-sicher bei fixer Zusammensetzung.

Gegenbefund, ehrlich gehalten. Die DOM-Seite ist schon sauber, `escapeHtml` laeuft durchgaengig durch jede innerHTML-Konstruktion, die Obsidian-URI ueber `encodeURIComponent`, der d3-Tooltip ueber `.text()`. Das Privacy- und Determinismus-Netz aus M1 steht. Dort kein Pseudo-Refactor.

Daraus der Vorschlag eines Haertungs-Milestones, Scope schmal (nur Haertung, Datei bleibt Monolith) oder voll (zusaetzlich Asset-Split), Empfehlung voll, weil der Monolith mit jeder Erweiterung der Phase B schwerer wird. Scope-Entscheid und Reihenfolge gegen M3 liegen beim Operator, keine Selbst-Priorisierung.

Standortbestimmung zum Gesamtziel. Erreicht sind zwei der drei Sichten, topologisch und pragmatisch, plus das Phase-A-Interface und das maschinelle Invarianten-Netz. Offen sind die semantische Sicht (M3), die getypten Relationen (M4), die volle Triangulation aus drei Achsen (M5), die gefuellte Wachstums-Linse (M6), die Reproduzierbarkeits-Signatur (M7) und die agent-lesbare Schicht (M8), zusammen sechs Milestones. Selbst der erreichte Teil traegt den latenten Script-Breakout, ist also noch nicht voll abgehaertet.

## Milestone-Runde, Invarianten-Netz und Phase-A-Interface (787fadf, dann Interface-Commit)

Betriebsmodell gewechselt. Die Lane entscheidet offene Gestaltungs- und Methodenfragen jetzt aus der Fachlichkeit und sichert reversibel-internes nach main, statt vor jedem Schritt eine Freigabe einzuholen; nach aussen Wirkendes bleibt operator-gated. Damit faellt das selbst gesetzte Interface-Gate der Vorrunde, der Gestaltungsvorschlag wird nicht mehr vorab freigegeben, sondern als Spur (Screenshots) nachgesichtet. Zwei Milestones gebaut.

M1, Invarianten-Netz. tests/test_invariants.py sichert die zwei zentralen Versprechen maschinell, die bisher nur per Hand geprueft waren. Byte-Determinismus der Pipeline in-process und ueber zwei Subprozesse mit verschiedenem PYTHONHASHSEED, das deckt hash-seed-abhaengige Mengen-Iteration und ungeseedete Zufallsquellen ab. Privacy-Invariante der explorer.html-Payload, anonyme Knoten ohne Inhalts-Metadaten, aus der Triage ausgenommen, kein Sprung, kein Klartext-Leak im gerenderten HTML. Befund nebenbei, der Determinismus ist relativ zu einem festen vault_path, der in graph.json serialisiert wird; in Betrieb ist VAULT_PATH konstant, die Eigenschaft haelt, der Test haelt den Pfad entsprechend fest. 51 Tests gruen.

M2, Phase-A-Interface. explorer.py, Python-Payload verhaltensgleich (Determinismus- und Privacy-Test bleiben gueltig), Template neu. Flaechenumkehr, Graph als Hauptflaeche, Tabelle als eingeklappte Schublade unten, Detail rechts. Kanten im Ruhezustand aus, erst bei Auswahl (De-Hairball, im Browser belegt, null von 6156 Kanten sichtbar im Ruhezustand, 257 bei Auswahl des Top-Hubs Applied-GenerativeAI MOC). Drei Aussagetyp-Akzente als Knotenringe, Befund blau, Diagnose orange, Hypothese violett, anon rot gestrichelt, durchgehend in Graph, Tabelle und Detail. Gruppierte Statuszeile. Drei Linsen ueber dieselbe Karte, Struktur, Pflege (dimmt auf die Diagnose-Knoten, Dock zeigt die Triage), Wachstum (leeres Geruest, so benannt). Stabile Positionen ueber eine geseedete randomSource der Simulation.

Eigene Designentscheidungen gegenueber dem Gestaltungsvorschlag, aus der Fachlichkeit getroffen. Festes Drei-Spalten-Layout statt Vollbild-Umschalter. Community als gedaempfte Knotenfuellung mit dem Aussagetyp als Ring, statt Aussagetyp als Fuellung; so zeigt der Ruhezustand Community-Struktur und die Anomalien stechen als Ring heraus, ein bewusstes Aufloesen der inneren Spannung des Vorschlags. Optionaler Schalter Kanten schwach zeigen, haelt den De-Hairball-Default auffindbar.

Verifikation. 51 Tests gruen. explorer.html byte-identisch ueber zwei volle Laeufe gegen den lebenden Vault. DOM-Sichtpruefung gruen, referentielle Integritaet (null haengende Kanten, null haengende tote Links), vier anonyme Knoten ohne Leak und aus der Triage ausgenommen, Statuszeile deckungsgleich. Browser-Spur mit drei Screenshots, Ruhezustand, Auswahl mit Kanten und Detail, Pflege-Linse mit Triage.

Durable Lehre. d3 forceSimulation laesst sich ueber randomSource(prng) deterministisch machen; der jiggle-Schritt in forceManyBody nutzt sonst Math.random und bricht stabile Positionen ueber Laeufe.

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
