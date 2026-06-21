# Befunde Frontend, Refactoring und Doku, Entscheidungsvorlage naechster Milestone

Diese Analyse entstand am 2026-06-21 nach Abschluss der Browser-Sichtung, auf Operator-Wunsch nach einer konstruktiv-kritischen Bewertung des Interface, der Refactoring-Lage und der Doku-Hygiene. Das Dokument sichert die im Gespraechskontext erarbeiteten Befunde als committetes Artefakt und buendelt die offenen Operator-Entscheidungen, an denen der naechste Milestone haengt.

## Befunde Interface (explorer.html)

Was traegt und bleiben soll. Die geteilte Selektion zwischen Tabelle, Triage, Graph und Detail ist das staerkste Element. Der obsidian-Sprung pro Knoten schliesst die Luecke zur Arbeit am echten Atom. Die methodische Trennung in Befund, Diagnose und Hypothese ist die Identitaet des Tools. Self-contained und durchgehaltene Privacy sind solide.

Die zwei strukturellen Schwaechen. Erstens das invertierte Flaechenverhaeltnis, die Tabelle bekommt die breite Hauptflaeche, der Graph sitzt im schmalen rechten Panel, obwohl der Graph die einzige Flaeche ist, die raeumliche Struktur traegt. Zweitens der Hairball, alle Kanten sind bei voller Deckkraft sichtbar und verdecken genau die Community-Struktur, die der Graph zeigen soll. Der billige Hebel ist, Kanten im Ruhezustand auszublenden und nur bei Knoten-Selektion zu zeigen, der Hervorhebungspfad existiert im Code schon.

Der konzeptionelle Kern ist deklariert, nicht erfahrbar. Befund, Diagnose und Hypothese sind nur punktuell markiert, es fehlt ein durchgaengiges Farbsystem, in dem dieselben drei Akzente ueberall dieselbe Bedeutung tragen.

Detailpunkte. Die Statuszeile ist eine undifferenzierte Wand aus elf Kennzahlen ohne Gruppierung. Die Tabelle fuehrt sieben numerische Spalten gleichzeitig, davon drei redundant. Die Pflege-Triage hat keine Quittierung abgearbeiteter Eintraege und zeigt die toten Ziele nicht inline. Jeder Reload verliert Filter, Sortierung und Selektion. Die Community-Kodierung ist rein farbbasiert, bei vierzehn Communities kaum unterscheidbar. Fachbegriffe sind nicht erklaert.

## Befunde Code-Refactoring

Die grosse Dublette. render.py und explorer.py bauen ein nahezu identisches Payload und tragen je ein vollstaendiges HTML-Template mit eingebettetem D3, der Force-Graph-Kern liegt zweimal vor mit leicht abweichenden Konstanten. Das eigentliche Argument ist die Privacy-Invariante, der Node-Record wird an drei Stellen gebaut (write_graph_json, render, explorer), und jede muss daran denken, build_key_remap und export_path_for aufzurufen, sonst leakt ein Klartext-Dateiname. Ein zentraler Node-Record-Builder macht das Leck strukturell unmoeglich statt per Kommentar-Disziplin in drei Kopien.

closeness ist toter Code, verifiziert. topology._compute_centralities rechnet sechs Masse, closeness wird nirgends gelesen, ist aber die teuerste der sechs Berechnungen. Streichen oder hinter ein Flag legen, eigenvector bleibt (steht im Topologie-Bericht).

Veralteter Kommentar in parse._looks_like_moc, er behauptet eine Praezisierung in pragmatics.py, die es nicht gibt. render.showDetail rechnet die Grade bei jedem Klick neu durch Filtern aller Kanten, relevant nur falls topology.html bleibt.

## Befunde Projektdokumente

knowledge/README.md ist als Index veraltet, journal.md und variante-b-schreibterritorium.md fehlen in Inhalt und Lesepfad. projektkonzept.md und METHODIK.md beschreiben die pragmatische Sicht und die Triangulation als Stage-2-Zukunft, obwohl beide gebaut sind, das widerspricht projektwissen.md als aktuellem Stand. Eingefrorene Zahlen, METHODIK.md traegt Beispielzahlen, die als Fakten gelesen werden, die Wurzel-README nennt eine veraltete Testzahl und fuehrt erledigte Phasen als offen.

## Zu klaerende Operator-Entscheidungen

Drei Buendel, jede Antwort entscheidet mehrere Punkte.

Buendel 1, Arbeitsweise. Reihenfolge der drei Baustellen, Vorschlag erst Interface, dann Code aufraeumen, dann Doku. Funktionserhaltendes Aufraeumen (Ungenutztes entfernen, Doppeltes zusammenfuehren, veraltete Stellen korrigieren) ohne Einzelrueckfrage freigegeben. Zeigerhythmus pro Block statt pro Einzelaenderung.

Buendel 2, Interface-Umbau. Kanten nur bei Selektion zeigen, dem Graph ueber einen Vollbild-Umschalter Platz geben und dafuer die schlichte zweite Graph-Seite (topology.html) abschaffen, die drei Aussagetypen durchgehend farbig kennzeichnen, plus die kleineren Verbesserungen (Kennzahlen gruppieren und erklaeren, Tabelle eindampfen mit Aufklapp-Option, Pflege-Liste abhakbar, Zustand merken, Begriffe erklaeren). Ganz oder als Teilauswahl.

Buendel 3, Grundsatz. Pflege-Hinweise als eigene Datei in den Vault schreiben (Variante B im kollisionsfreien Minimalzuschnitt B1, siehe variante-b-schreibterritorium.md) oder weiter nur im Projektordner halten. Und Session-Branch nach main ueberfuehren oder vorerst getrennt lassen.

## Milestone nach Klaerung

Je nach Antwort auf Buendel 1 und 2 die Interface-Verbesserung an explorer.py, bei Wegfall von topology.html auch das Entfernen von render.py, das funktionserhaltende Aufraeumen und die Doku-Versoehnung. Buendel 3 laeuft unabhaengig und gated, es blockiert den Frontend- und Aufraeum-Milestone nicht.
