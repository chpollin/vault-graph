# Ähnlichkeitsanalyse, ausgearbeitete Vorlage

Entscheidungsvorlage auf Auftrag der Forschungsleitstelle (order 2026-06-21). Kein blockierendes Gate, vorgelegt zur Bewertung. Diese Vorlage beschreibt eine semantische Sicht auf den Vault, die über die bisherige topologische Sicht (Wikilinks, Communities, Centrality) hinausgeht: inhaltliche Nähe zwischen Notizen, gemessen über Text-Embeddings, unabhängig davon ob ein Link existiert.

## Frage, die sie beantwortet

Der bestehende Linkgraph sieht nur, was der Autor explizit verlinkt hat. Zwei Notizen können dasselbe Thema behandeln, ohne dass je ein Wikilink zwischen ihnen gesetzt wurde. Diese latente Nähe ist für das Wissensnetz unsichtbar. Die Ähnlichkeitsanalyse macht sie sichtbar und beantwortet drei Fragen. Welche Notizen gehören thematisch zusammen, sind aber nicht verbunden. Welche Notizen sind inhaltlich fast deckungsgleich (Dubletten). Und wie verhält sich die inhaltliche Gruppierung zur Link-Community und zur Ordnerstruktur.

## Wie sie funktioniert

Vier Schritte, alle deterministisch.

1. Text je Notiz einsammeln. Titel plus Body, der Frontmatter-Block bleibt draußen oder geht nur kuratiert ein (Aliases, Tags). Die Quelle ist graph.json, das den Body bereits geparst vorhält.
2. Embedding je Notiz berechnen. Ein Text-Embedding-Modell bildet jede Notiz auf einen Vektor ab (mehrere hundert Dimensionen), der ihre inhaltliche Bedeutung kodiert. Notizen über verwandte Themen liegen im Vektorraum nah beieinander, auch ohne gemeinsame Wörter.
3. Paarweise Ähnlichkeit messen. Die Cosinus-Ähnlichkeit zwischen zwei Vektoren ist ein Wert zwischen 0 und 1. Für jede Notiz werden die k nächsten Nachbarn bestimmt, ihre semantisch ähnlichsten Notizen.
4. Gegen den Linkgraph spiegeln. Für jedes hochähnliche Paar wird geprüft, ob ein Wikilink existiert und wie weit die beiden Notizen im Linkgraph auseinanderliegen. Hohe Ähnlichkeit bei fehlendem oder weitem Link ist das interessante Signal.

Der Rechenaufwand für Schritt 3 ist unkritisch. Bei rund 700 Knoten sind es etwa 245.000 Paare, das rechnet eine Matrixoperation in Millisekunden. Der Aufwand steckt allein in Schritt 2, dem Embedding.

## Welches Modell

Der Vault ist deutscher Fließtext mit englischen Fachbegriffen. Das verlangt ein mehrsprachiges Embedding-Modell. Zwei Wege stehen offen, lokal oder über eine API.

Lokal. Ein mehrsprachiges Sentence-Transformer-Modell läuft auf dem eigenen Rechner. Geeignete Kandidaten sind `BAAI/bge-m3` (langer Kontext bis 8192 Token, gut für lange Notizen) oder `intfloat/multilingual-e5-large`. Beide sind etwa 2 GB groß, laufen auf CPU in Minuten, auf GPU in Sekunden, und kosten pro Lauf nichts. Der Preis ist eine schwere Abhängigkeit (`sentence-transformers` plus `torch`, zusammen mehrere GB Installationsvolumen) und ein einmaliger Modell-Download.

API. Ein gehostetes Modell wie OpenAI `text-embedding-3-small` oder `-large` liefert ohne lokale Installation Vektoren zurück. Geringfügig höhere Qualität, null Setup, aber der Notiztext verlässt den Rechner.

Der zweite Punkt ist die eigentliche Entscheidung. vault-graph hat als Kerninvariante den Datenschutz, es anonymisiert die Knoten aus `Business/Angebote/` mehrlagig. Den Rohtext der Notizen, darunter Angebote mit Geldbeträgen und Kundendaten, an einen externen Dienst zu schicken, widerspräche genau diesem Prinzip. Die lokale Variante hält alles auf dem Gerät und ist mit der Invariante des Werkzeugs konsistent.

## Kostenschätzung

Monetär ist die Analyse in beiden Wegen nahezu kostenlos, der Unterschied liegt nicht im Geld.

API. Bei rund 700 Notizen und im Schnitt grob 1200 Token je Notiz fallen etwa 840.000 Token für einen vollen Durchlauf an. Bei `text-embedding-3-small` (0,02 Dollar je Million Token) sind das rund zwei Cent pro Vault-Lauf, bei `text-embedding-3-large` (0,13 Dollar je Million Token) rund elf Cent. Wiederholungsläufe kosten dasselbe, ein inkrementeller Lauf nur über geänderte Notizen entsprechend weniger.

Lokal. Kein Token-Preis. Einmalig der Modell-Download (etwa 2 GB) und die Installation der Abhängigkeit. Ein voller Lauf dauert auf CPU einige Minuten, auf GPU Sekunden.

Die ehrliche Lesart. Der Geldbetrag ist in keinem Szenario ein Entscheidungsgrund, selbst die teure API-Variante bleibt im Cent-Bereich pro Lauf. Die realen Kosten sind der Datenabfluss bei der API und das Abhängigkeitsgewicht bei lokal. Wer Datenschutz priorisiert, zahlt mit Installationsvolumen, nicht mit Geld.

## Erkenntnisgewinn

Vier konkrete Erträge.

Latente Verknüpfungen. Notizpaare mit hoher inhaltlicher Ähnlichkeit, zwischen denen kein Wikilink besteht. Das sind Kandidaten, die der Autor verbinden könnte, der Hauptertrag der Analyse. Methodisch eine Diagnose, ein Pflegesignal zum Hinsehen, keine Vorschrift. vault-graph schlägt vor, der Mensch entscheidet, und da das Werkzeug laut order nicht in den Vault schreibt, ist diese Trennung strukturell erzwungen.

Dritte Triangulationsachse. Clustert man die Embeddings, entsteht eine semantische Partition, die sich gegen die bestehenden zwei Partitionen halten lässt, die Link-Community (Louvain) und die Ordnerstruktur. Wo alle drei übereinstimmen, liegt ein robustes Thema. Wo sie auseinanderlaufen, etwa ein Ordner, der semantisch in zwei Gruppen zerfällt, oder eine Link-Community ohne inhaltlichen Zusammenhalt, liegt eine aufschlussreiche Spannung. Das fügt sich direkt in die vorhandene Triangulationsmaschinerie in `pragmatics.py`.

Near-Dubletten. Paare mit sehr hoher Ähnlichkeit markieren inhaltlich fast deckungsgleiche Notizen, ein Kurationssignal im Sinne der Redundanz-Auflösung.

Substrat für die agent-lesbare Schicht. Der Embedding-Index erlaubt semantische Suche über den Vault. Ein Agent könnte nach Bedeutung fragen, nicht nur nach Link, also Notizen in der Nähe von X holen, auch ohne expliziten Pfad. Das ist die Brücke zum zweiten Ausgangsstrang aus dem letzten handoff und der Berührungspunkt mit der obsidian-vault-Lane, die an einer agent-tauglichen Wissensarchitektur arbeitet. Diese Verwendung sollte gegen deren Arbeit abgestimmt werden, statt einen konkurrierenden Zugang zu bauen.

## Methodische Einordnung

Embedding-Ähnlichkeit erzeugt Hypothesen und Diagnosen, nie Befunde. Eine hohe Cosinus-Nähe ist ein statistisches Signal für thematische Überlappung, kein Beweis einer sinnvollen Beziehung. Die Ausgabe ist eine Kandidatenliste zur menschlichen Prüfung, im Rahmen der drei Aussagetypen des Projekts.

Schwellwert-Empfindlichkeit. Was als ähnlich gilt, hängt an einem Grenzwert, wie die Reinheitsschwelle bei den Ausreißern. Der Grenzwert braucht Kalibrierung, und sein Effekt auf die Treffermenge muss berichtet werden, so wie der Ausreißer-Sprung von 15 auf 74 transparent gemacht wurde.

Determinismus. Modellversion und etwaiger Cluster-Seed werden fixiert, damit Läufe byte-stabil bleiben, im Einklang mit dem Determinismus-Prinzip des Projekts.

Datenschutz im Ablauf. Der Embedding-Schritt sitzt hinter dem Privacy-Remap, nie davor. Knoten aus `Business/Angebote/` werden entweder gar nicht eingebettet (ihre anonymisierte Form trägt ohnehin keinen Body) oder erst nach der Anonymisierung. Der Rohtext eines Angebots darf nie in ein Embedding eingehen, schon gar nicht über eine API.

## Empfehlung

Bauen, als Stage-2-Semantiksicht, mit einem lokalen mehrsprachigen Modell (`BAAI/bge-m3` oder `intfloat/multilingual-e5-large`), als neues Modul `semantics.py`. Zwei Produkte. Erstens ein Diagnose-Bericht `findings/latente-verknuepfungen.md`, der hochähnliche Paare ohne Link rangiert, mit Ähnlichkeitswert und aktueller Link-Distanz. Zweitens eine semantische Partition, die als dritte Achse in die bestehende Triangulation einläuft. Beide Ausgaben deterministisch und byte-stabil.

Die API-Variante zurückstellen. Sie kommt nur in Frage, falls die lokale Qualität nicht reicht, und auch dann nur auf bereinigtem Inhalt, nie auf Angebots-Rohtext.

Ehrliche Aufwandsmarke. Das ist ein eigenständiges neues Modul mit einer schweren Abhängigkeit (`torch`), das das Installationsvolumen des Projekts grob verdreifacht. Es ist größer als die bisherige Topologie-Arbeit, kein kleiner Zusatz, und sollte als eigener Bau geführt werden.

## Offen für den Operator

Kein blockierendes Gate. Zwei echte Entscheidungen liegen aber an. Erstens, ob die schwere Abhängigkeit (`sentence-transformers` plus `torch`) ins Projekt aufgenommen wird, denn sie ändert das Installationsprofil deutlich. Zweitens, ob die semantische Sicht zugleich das Substrat für die agent-lesbare Schicht werden soll, jetzt mitgedacht oder als eigene spätere Stufe, was die Abstimmung mit der obsidian-vault-Lane berührt.
