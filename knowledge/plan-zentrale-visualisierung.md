# Plan, zentrale Wissensgraph-Visualisierung

Konzept und Vorgehen für die Neuausrichtung von vault-graph. Die Netzwerkvisualisierung wird vom Seitenpanel zum zentralen UI-Element, und der reine Linkgraph wird zu einem getypten Wissensgraphen, der inhaltliche Nähe nutzt, um neue benannte Beziehungen vorzuschlagen. Lebendes Dokument, iterativ zu schärfen. Methodische Grundlage in [../METHODIK.md](../METHODIK.md), Bau-Stand in [projektwissen.md](projektwissen.md).

Beschlossen im Operator-Dialog am 2026-06-21. Richtung: getypte Relationen statt bloßer Ähnlichkeit, Relationstypen zunächst per Sprachmodell vorgeschlagen und vom Menschen bestätigt.

## Ausgangsproblem

Force-Directed-Graphen zeigen meist Komplexität, nicht Erkenntnis. Der heutige Graph sitzt im schmalen Panel, zeigt alle Kanten gleichzeitig (Hairball) und kennt nur explizite Wikilinks. Ein Gesamtbild des Vaults wird mit jedem neuen Knoten schlechter lesbar. Der Obsidian-eigene Graph-View ist dafür das Mahnmal, beeindruckend und ungenutzt. Wenn vault-graph hier zentral werden soll, muss es das überwinden, sonst dupliziert es Obsidian.

## Leitidee

Die zentrale Visualisierung ist kein Bild des ganzen Netzes, sondern eine navigierbare Karte mit wählbaren Linsen. Man bewegt sich darin, vom Überblick in eine Community, auf einen Knoten und seine Nachbarschaft, wieder zurück. Und man legt verschiedene Linsen darüber, die je eine Frage beantworten. Eine Struktur-Linse zeigt Communities und Brücken, eine Pflege-Linse tote Links und fehlplatzierte Knoten, eine Wachstums-Linse die vorgeschlagenen neuen Beziehungen. Ein Gesamtbild wird beim Wachsen schlechter, eine navigierbare Karte wird reicher.

## Kriterien für ein konstruktives zentrales Element

1. Jede Ansicht beantwortet eine Frage. Der Graph zeigt nie alles auf einmal, sondern eine Linse. Ohne Frage ist es Dekoration.
2. Navigierbar statt betrachtbar. Überblick, Hineinzoomen, Knoten fokussieren mit Nachbarschaft, zurück. Der Obsidian-Sprung ist der Ausgang in den Vault.
3. Skaliert mit dem Wachstum. Communities zu Meta-Knoten aggregieren mit Aufklappen ins Detail, statt immer alle Knoten zu zeigen.
4. Stabile Karte. Gleicher Vault-Stand, gleiche Positionen, damit die räumliche Orientierung über Läufe erhalten bleibt. Passt zum Determinismus-Prinzip.
5. Die methodische Sprache ist sichtbar. Befund, Diagnose, Hypothese als durchgehende visuelle Codes. Tote Links, Ausreißer, Brücken erkennt man im Graphen.
6. Zeigt Bedeutung, nicht nur Links. Neben den expliziten Wikilinks auch latente Nähe und benannte Relationen.
7. Technisch tragfähig. SVG trägt einige Tausend Elemente, darüber Canvas oder WebGL. Die Wahl hängt am Skalierungsanspruch.
8. Graph als Hauptfläche. Tabelle und Detailpanel werden zu Begleitern, die sich aus der Graph-Auswahl speisen.

## Das Zwei-Schichten-Modell der Bedeutung

Der Kern des Plans. Bedeutung wird in zwei Schritten erzeugt, einem billigen vollständigen und einem teuren gezielten.

Schicht eins, semantische Ähnlichkeit als Scout. Ein lokales Embedding-Modell bildet jede Notiz auf einen Vektor ab, die Cosinus-Ähnlichkeit misst inhaltliche Nähe. Diese Nähe ist ungerichtet und unbenannt, sie sagt nur dass zwei Notizen vom Ähnlichen handeln. Ihr Wert liegt darin, aus der unmöglichen Menge aller Notizpaare (bei siebenhundert Notizen eine Viertelmillion) die wenigen Hundert herauszuholen, die überhaupt eine Beziehung haben könnten.

Schicht zwei, getypte Relationen als Karte. Auf die Kandidatenpaare aus Schicht eins setzt eine Typisierung an, die jeder Beziehung über eine kleine Relationstaxonomie Richtung und Bedeutung gibt. Das Embedding sagt nur dass Informed Vibe Coding und Vibe Coding ähnlich sind, die Typisierung sagt dass das eine eine kritische Weiterentwicklung des anderen ist. Das Ergebnis ist kein Ähnlichkeitsnebel, sondern ein getypter Wissensgraph mit gerichteten, nach Relationstyp eingefärbten Kanten.

## Relationstaxonomie, Vorschlag

Klein gehalten, weil eine kleine Taxonomie tatsächlich vergeben wird und eine große in der Praxis erstickt. Sechs Typen, an etabliertes Vokabular angelehnt wo möglich (die enger-breiter-verwandt-Logik von SKOS).

1. spezialisiert, das umgekehrt generalisiert (enger gegen breiter)
2. ist Teil von, das umgekehrt umfasst (Komposition, die MOC-Beziehung)
3. baut auf, stützt (ein Konzept setzt ein anderes voraus oder belegt es)
4. kontrastiert, widerspricht (Spannung oder Alternative)
5. ist Methode für, wird angewandt auf (Methode gegen Anwendung)
6. ist Beispiel für, instanziiert (Instanz gegen Klasse)

Dazu verwandt als neutraler Rückfall für eine bestätigte, aber nicht typisierbare Nähe. Die Liste ist ein Vorschlag zur Schärfung am konkreten Vault.

## Architektur-Einbettung

- Neues Modul für die Ähnlichkeitsschicht, ein lokales mehrsprachiges Embedding-Modell (bge-m3 oder multilingual-e5-large). Lokal aus Datenschutzgründen, der Notiztext verlässt den Rechner nicht.
- Eine Vorschlagsschicht für die Typisierung über ein Sprachmodell, klar getrennt von der deterministischen Kernanalyse.
- Determinismus-Trennung. Der Kern (Parse, Topology, Pragmatics) bleibt byte-deterministisch. Die Sprachmodell-Vorschläge sind es nicht, deshalb werden sie als versioniertes Artefakt eingefroren, eine Vorschlagsdatei, die der Mensch durchgeht. Der reguläre Lauf liest diese eingefrorene Datei, statt live zu fragen. So bleibt die Reproduzierbarkeit erhalten, die Anreicherung ist ein bewusst angestoßener Schritt.
- Privacy. Embedding und Typisierung sitzen hinter dem Privacy-Remap. Knoten aus Business/Angebote werden nicht eingebettet (ihre anonymisierte Form trägt keinen Body) und nicht typisiert.
- Read-only-Grenze. Das Tool gibt Relationen als Vorschlag aus, in einer Vorschlagsliste und als vorgeschlagene Kanten im Graphen. Es schreibt sie nicht in den Vault. Wo bestätigte Relationen persistiert werden, ist eine spätere Frage, sinnvoll wären getypte Links in den Notizen, was die von der Leitstelle gesetzte Schreibgrenze berührt und separat zu klären ist.

## Visualisierung konkret

- Graph als Hauptfläche, Tabelle und Detail als Begleiter aus der Selektion.
- Kanten erst bei Knoten-Auswahl, nicht im Ruhezustand.
- Getypte Kanten gerichtet und nach Relationstyp eingefärbt, sichtbar verschieden eine Spezialisierung von einem Widerspruch.
- Drei Linsen, Struktur, Pflege, Wachstum.
- Stabiles deterministisches Layout, wiedererkennbare Positionen.
- Aggregation zu Community-Meta-Knoten mit Drill-down für die Skalierung.
- Technik SVG bis zu einer Knotenschwelle, darüber Canvas oder WebGL, Entscheidung am Skalierungsanspruch.

## Phasen, Vorschlag ohne feste Reihenfolge

- Phase A, Karte tragfähig. Layout-Umkehr, Linsen-Gerüst, Kanten bei Auswahl, stabile Positionen, Aussagetyp-Farben. Bleibt im bestehenden deterministischen Rahmen, ohne neue Abhängigkeit.
- Phase B, semantische Ähnlichkeit. Lokales Embedding-Modul, Kandidatenpaare, eine Wachstums-Linse mit noch ungetypter latenter Nähe.
- Phase C, getypte Relationen. Vorschlagsschicht über das Sprachmodell, Relationstaxonomie, gerichtete eingefärbte Kanten, Bestätigungs-Workflow.
- Phase D, Skalierung. Aggregation, Drill-down, gegebenenfalls Technikwechsel.

Phase A trägt sofort und ist risikoarm, sie verbessert die heutige Werkbank ohne neue Abhängigkeit. Die schwere Embedding- und Sprachmodell-Schicht kommt erst ab Phase B.

## Offene Entscheidungen

- Skalierungsanspruch, wie groß das Netz werden soll, bestimmt die Technikwahl.
- Speicherung bestätigter Relationen, berührt die Read-only-Grenze.
- Endgültige Relationstaxonomie, welche Typen für diesen Vault.
- Modellwahl, lokales Embedding-Modell und das Sprachmodell für die Typisierung.

## Bezug zur Methodik

Getypte Relationen, besonders die vom Sprachmodell vorgeschlagenen, sind Hypothesen oder Diagnosen, keine Befunde. Der Mensch bestätigt. Die deterministische Kernschicht bleibt unberührt, die Anreicherung läuft als eigene, eingefrorene Schicht daneben. Das Tool schlägt vor, es entscheidet nicht.
