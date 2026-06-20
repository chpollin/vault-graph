# vault-graph Projektwissen

Konsolidierter Wissensstand des Tools, ergaenzt [projektkonzept.md](projektkonzept.md) (operativer Plan) und [../METHODIK.md](../METHODIK.md) (epistemische Position) um den aktuellen Stand, die Datenarchitektur, die Befunde der Frontend-Vorbereitung und die Einbettung in die Forschungsleitstelle. Zahlen stehen git-deterministisch (Commit-SHA) oder als Verweis auf ein committetes Artefakt, Vault-Metriken qualitativ, weil sie mit jedem Vault-Stand wandern.

## Zweck

Dieses Dokument haelt fest, was ueber vault-graph bekannt ist, sodass eine neue Instanz oder eine andere Lane den Stand ohne Gespraechskontext aufnehmen kann. Es ist die Wissensbasis, projektkonzept.md bleibt der Plan, METHODIK.md die Methodenseite.

## Was das Tool ist

vault-graph parst einen Obsidian-Vault read-only und liefert eine topologische Analyse seines Linkgraphen plus eine selfcontained HTML-Visualisierung. Es extrahiert den gerichteten Linkgraph aus Wikilinks, rechnet Communities, Centrality, Brueckenknoten und K-Core und erzeugt deskriptive Findings-Berichte. Der Vault ist die Datenquelle, geschrieben wird nur in das eigene output-Verzeichnis.

## Methodische Position

Der gegenwaertige Stand arbeitet nur auf der topologischen Sicht, dem Linkgraph aus Wikilinks. Die semantische Sicht (Embeddings) und die pragmatische Sicht (MOCs, Tags, Ordner) sind als Stage 2 dokumentiert, aber nicht implementiert. Damit trifft das Tool bewusst keine Aussage ueber Wissensnetzwerke im vollen Sinn, das braeuchte die Triangulation aus drei Sichten.

Drei Aussagetypen werden getrennt. Befund ist datengestuetzt und reproduzierbar gegen denselben Vault-Stand und Tool-Git-Hash. Diagnose ist eine datengestuetzte Pflege-Auffaelligkeit wie tote Links. Hypothese ist schwaecher gestuetzt, etwa ein topologischer Cluster ohne semantische Stuetze. Nicht zulaessig sind Wert-, Soll- und Kausalaussagen. Diese Disziplin ist der Kern und gilt auch fuer jedes Frontend.

## Architektur

Drei Phasen, je ein Modul in vault_graph/, orchestriert ueber __main__.py mit den Schwellwerten als Konstanten.

Parse (parse.py) liest den Vault ein, extrahiert den Linkgraph samt Frontmatter, toten Links und Orphans, wendet den Privacy-Filter an und schreibt graph.json. Der Knoten-Schluessel ist der Dateiname-Stem.

Topology (topology.py) rechnet die Centrality-Suite (Degree in und out, Betweenness, Eigenvector, PageRank, Closeness), Louvain-Communities auf dem ungerichteten Projekt des Graphen (Resolution 1.0, Seed 42), die K-Core-Dekomposition und die Brueckenknoten. Brueckenknoten sind Knoten mit hoher Betweenness bei moderater Degree, operationalisiert als Z-Score-Differenz betweenness_z minus degree_z groesser gleich 1.5, also Kandidaten fuer Querkonzepte.

Render (render.py) erzeugt eine selfcontained HTML mit einem D3-Force-Directed-Graph, Knoten gefaerbt nach Community, Groesse nach PageRank, Bruecken markiert, mit Suche, Zoom, Label-Toggle und Detail-Panel. Explorer (explorer.py) erzeugt darueber hinaus die read-only Werkbank explorer.html, die Topologie und Inhalts-Schicht in einem angereicherten PAYLOAD verbindet (siehe Erste Frontend-Stufe). Begleitend schreiben report_parse.py und report_topology.py die Markdown-Berichte fuer die Gate-Kontrolle.

## Datenarchitektur

Topologie und Inhalt liegen in zwei getrennten Schichten, das ist der Schluessel fuer jedes Frontend. Die Topologie-Schicht steckt im eingebetteten PAYLOAD von topology.html (id, title, path, is_moc, anon, community, pagerank, degree, in_degree, out_degree, betweenness, k_core, is_bridge). Die Inhalts-Schicht steckt in graph.json (key, title, path, vollstaendiges frontmatter inklusive tags und type, body_preview, aliases, privacy_anonymized, is_moc) plus den globalen Strukturen dead_links, orphans und stats.

Beide Schichten sind per Dateiname-Stem joinbar (PAYLOAD.id gleich graph.json key), fuer alle Knoten ausser dem anonymisierten Sonderfall. Ein reiches Read-Frontend mit Community-, Tag- und type-Filter, Orphan- und Bruecken-Hervorhebung und Atom-Sprung ist daraus zur Build-Zeit baubar, ohne die Pipeline neu zu laufen. Das macht eine erste Frontend-Stufe billig.

## Privacy

Knoten aus Business/Angebote/ werden mehrlagig anonymisiert. Am Knoten selbst wird der Titel zu Angebot-hash, der Body nicht eingelesen, sensitive Frontmatter (invoice, summary, aliases) gestrippt, key und path im JSON ersetzt. An anderen Knoten werden Wikilinks auf einen anonymisierten Knoten im body_preview maskiert. Die Topologie bleibt sichtbar, Privacy darf die Befunde nicht glaetten.

Behobene Regression. Frueher baute render.py das PAYLOAD aus dem Live-Graphen vor dem Anonymisierungs-Remap, daher stand der Klartext-Dateiname eines anonymisierten Business-Knotens in der generierten topology.html, waehrend write_graph_json korrekt remappte. Der Fix zieht das Remap als eine Quelle der Wahrheit nach parse.py (build_key_remap und export_path_for); write_graph_json, render und explorer verwenden es gemeinsam fuer Knoten-id, Pfad und Kanten-Endpunkte. Verifiziert gegen den lebenden Vault, kein Klartext-Business-Name mehr in topology.html, explorer.html oder graph.json, die anonymisierten Knoten erscheinen durchgaengig als Angebot-hash. Zusaetzlich werden tote Links und Orphans anonymisierter Knoten aus der Explorer-Pflege-Triage herausgehalten.

## Output und Reproduzierbarkeit

Output liegt in output/ und ist gitignored, also nicht versioniert, aber deterministisch regenerierbar mit python -m vault_graph. Erzeugt werden data/graph.json, findings/parse-bericht.md, findings/topology-bericht.md und visualisierung/topology.html. Reproduzierbarkeit ist ueber fixe Seeds (Louvain seed 42) und die Schwellwerte als Konstanten gesichert. Vollstaendige Reproduzierbarkeits-Metadaten (Tool-Git-Hash, Versionen, Vault-mtime) sind ein Stage-2-Ziel.

## Aktueller Stand

Der MVP (Parse, Topology, Render, Privacy, Tests, fixe Seeds) ist committet und gepusht, HEAD der MVP-Linie ist 4383e93. Ein frischer Lauf gegen den lebenden Vault wurde durchgefuehrt, der Vault ist gegenueber dem alten Snapshot gewachsen und an toten Links und Orphans deutlich sauberer geworden. Die konkreten Zahlen stehen im committeten Pflegesignal-Auszug (findings/pflegesignal-vault-lane.md, Commit 970dcb5) und sind regenerierbar. Stage 2 (semantische und pragmatische Sicht) bleibt dokumentiert und unimplementiert.

Seit dem MVP sind zwei Schritte hinzugekommen. Der Privacy-Fix ist umgesetzt und gegen den lebenden Vault verifiziert. Die erste Frontend-Stufe ist als Variante A gebaut, ein neues Modul explorer.py erzeugt zusaetzlich zu topology.html eine read-only Werkbank explorer.html, in die Pipeline aufgenommen und mitregeneriert. Beide Outputs bleiben gitignored und deterministisch regenerierbar.

## Projektrichtung

Operator-Beschluss als Kontext, vault-graph waechst vom topologischen Analyse-CLI zu einem analytischen Frontend, mit dem der Operator interaktiv am Vault arbeitet. Die bestehende topology.html ist der Keim, der Ausbau ist stufenweise.

## Erste Frontend-Stufe, Variante A, umgesetzt

Eine Design-Exploration hat drei unabhaengige UI-Konzepte gegen das echte Datenschema gestellt (Netz-Explorer mit dem Graph als Leitflaeche, Analyse-Werkbank mit sortierbaren Befundtabellen, Pflege-Triage mit der kuratorischen Arbeitsliste vorn) und zu einer Hybridform synthetisiert, Werkbank mit verlinktem Netz. Diese Hybridform ist als explorer.py gebaut. explorer.html traegt eine sortierbare Befundtabelle, ein read-only Pflege-Triage-Panel (tote Links nach Quellknoten, Orphans) und den Force-Graph als Kontextfenster, alle drei ueber eine geteilte Selektion verbunden, mit obsidian-Sprung pro Knoten und den drei Aussagetypen sichtbar getrennt. Die Befundtabelle markiert Community und Bruecke als Hypothese, die uebrigen Spalten als Befund, die Pflege-Flaeche als Diagnose.

Realisiert sind die Konkretisierungen ueber die seed-Visualisierung hinaus, Facetten-Filter nach Community, Tag und type statt nur Volltextsuche, sichtbare Orphans, tote Links als Diagnose-Arbeitsliste, der Sprung ins echte Atom per obsidian-URI und die bidirektionale Selektion zwischen Tabelle, Triage und Graph. Das angereicherte PAYLOAD traegt dafuer zusaetzlich tags und type, joinbar zur Build-Zeit ohne Pipeline-Neulauf. Variante A ist read-only, sie schreibt nichts in den Vault. Stand der Verifikation, PAYLOAD valide und referentiell konsistent, Privacy sauber, eingebettetes JS syntaktisch fehlerfrei, der visuelle Funktionstest im Browser liegt beim Operator.

Die Konkretisierungen ueber die seed-Visualisierung hinaus sind Facetten-Filter nach Community, Tag und type statt nur Volltextsuche, das Sichtbarmachen der Orphans, tote Links als Diagnose-Arbeitsliste, der Sprung ins echte Atom per obsidian-URI und die bidirektionale Selektion zwischen Tabelle und Graph. Die Hybridform wurde gewaehlt, weil sie als einzige gegen die verifizierten realen Zahlen gebaut war und Befund, Diagnose und Hypothese auf drei Flaechen abbildet.

Lehre aus der Exploration. Agenten-Ergebnisse wurden gegen die echten Daten geprueft, nicht uebernommen. Ein Agent hatte zu niedrige Community- und Bruecken-Zahlen gemeldet, die Pruefung gegen PAYLOAD und graph.json korrigierte das. Verify not trust gilt auch fuer die eigenen Subagenten.

## Offene Operator-Entscheidungen

Der Scope der ersten Stufe ist auf Variante A entschieden und gebaut, der Privacy-Fix ist umgesetzt. Diese Entscheidung war erarbeitbar, weil A read-only ist und keine Territorialkollision erzeugt und weil B ohne vorherige Abgrenzung gar nicht freigebbar ist; A ist der natuerliche erste Schritt und schliesst B nicht aus.

Offen bleiben zwei Operator-Entscheidungen. Variante B (zusaetzlich kuratorisch mit Rueckschreiben in den Vault) macht das Tool zum Schreiber neben der Vault-Lane und wird nicht freigegeben, ohne dass vorher das Schreibterritorium gegen die Vault-Lane abgegrenzt ist. Und der Merge des Session-Branches nach main bleibt gegated, weil main-Push eine stehende Gate-Regel ist.

## Einbettung in die Forschungsleitstelle

vault-graph ist eine Lane der Forschungsleitstelle, Kennung Repo plus Rolle, vault-graph · Beobachtungsinstrument. Weil das Tool den Vault read-only parst, ist es das Messinstrument fuer den Wissenstransfer zwischen den Projekten. Kommunikation laeuft nur ueber zwei Dateien im forschungsleitstelle-Repo, reports/order-vault-graph.md herein und reports/handoff-vault-graph.md hinaus. Der Arbeitsmodus ist strikt, ein abgegrenzter Schritt je Order, dann anhalten und den handoff neu schreiben.

Konflikt-Radar. Die Vault-Lane ist Datenquelle und Upstream, sie editiert genau die Dateien, die hier geparst werden, jeder Move, Rename oder Dead-Link-Fix der Vault-Lane veraendert den Graphen flussaufwaerts. Die Projekt-Lanes sind die Messobjekte, ihr Wissenstransfer in den Vault ist das, was gemessen wird. Unter Variante B kaeme das Tool in direkte Datei-Kollision mit der Vault-Lane, daher ist der Schreibpfad gegated. Pflegesignale fuer die Vault-Lane werden im eigenen Repo abgelegt und sind von dort konsumierbar, nicht in den Vault geschrieben.

## Quellen

Blondel, V. D. et al. (2008). Fast unfolding of communities in large networks. J. Stat. Mech.

Newman, M. E. J. (2006). Modularity and community structure in networks. PNAS 103(23).

Denzin, N. K. (1978). The Research Act. McGraw-Hill. Referenz fuer die Triangulations-Position, ab Stage 2 relevant.

Munafo, M. R. et al. (2017). A manifesto for reproducible science. Nature Human Behaviour 1.
