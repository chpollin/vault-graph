# vault-graph Projektwissen

Konsolidierter Wissensstand des Tools, ergaenzt [projektkonzept.md](projektkonzept.md) (operativer Plan) und [../METHODIK.md](../METHODIK.md) (epistemische Position) um den aktuellen Stand, die Datenarchitektur, die Befunde der Frontend-Vorbereitung und die Einbettung in die Forschungsleitstelle. Zahlen stehen git-deterministisch (Commit-SHA) oder als Verweis auf ein committetes Artefakt, Vault-Metriken qualitativ, weil sie mit jedem Vault-Stand wandern.

## Zweck

Dieses Dokument haelt fest, was ueber vault-graph bekannt ist, sodass eine neue Instanz oder eine andere Lane den Stand ohne Gespraechskontext aufnehmen kann. Es ist die Wissensbasis, projektkonzept.md bleibt der Plan, METHODIK.md die Methodenseite.

## Was das Tool ist

vault-graph parst einen Obsidian-Vault read-only und liefert eine topologische Analyse seines Linkgraphen plus eine selfcontained HTML-Visualisierung. Es extrahiert den gerichteten Linkgraph aus Wikilinks, rechnet Communities, Centrality, Brueckenknoten und K-Core und erzeugt deskriptive Findings-Berichte. Der Vault ist die Datenquelle, geschrieben wird nur in das eigene output-Verzeichnis.

## Methodische Position

Das Tool arbeitet auf zwei der drei Sichten. Die topologische Sicht ist der Linkgraph aus Wikilinks. Die pragmatische Sicht ist die gelebte Ablage in Top-Level-Ordnern und die Tag-Vergabe, kostenfrei aus den vorhandenen Attributen berechnet. Aus beiden entsteht die erste echte Triangulation, die Kreuzung von topologischer Community und pragmatischer Ordner-Partition. Die semantische Sicht (Embeddings) fehlt noch und ist gegated, weil sie einen kostenpflichtigen Lauf bedeuten kann. Erst mit ihr waere die Triangulation aus drei Sichten vollstaendig.

Drei Aussagetypen werden getrennt. Befund ist datengestuetzt und reproduzierbar gegen denselben Vault-Stand und Tool-Git-Hash. Diagnose ist eine datengestuetzte Pflege-Auffaelligkeit wie tote Links. Hypothese ist schwaecher gestuetzt, etwa ein topologischer Cluster ohne semantische Stuetze. Nicht zulaessig sind Wert-, Soll- und Kausalaussagen. Diese Disziplin ist der Kern und gilt auch fuer jedes Frontend.

## Architektur

Drei Phasen, je ein Modul in vault_graph/, orchestriert ueber __main__.py mit den Schwellwerten als Konstanten.

Parse (parse.py) liest den Vault ein, extrahiert den Linkgraph samt Frontmatter, toten Links und Orphans, wendet den Privacy-Filter an und schreibt graph.json. Der Knoten-Schluessel ist der Dateiname-Stem.

Topology (topology.py) rechnet die Centrality-Suite (Degree in und out, Betweenness, Eigenvector, PageRank), Louvain-Communities auf dem ungerichteten Projekt des Graphen (Resolution 1.0, Seed 42), die K-Core-Dekomposition und die Brueckenknoten. Brueckenknoten sind Knoten mit hoher Betweenness bei moderater Degree, operationalisiert als Z-Score-Differenz betweenness_z minus degree_z groesser gleich 1.5, also Kandidaten fuer Querkonzepte.

Pragmatics (pragmatics.py) erfasst die pragmatische Sicht, die Top-Level-Ordner-Partition und die Tags, und kreuzt sie mit der topologischen Community (siehe Triangulation). Render (render.py) erzeugt eine selfcontained HTML mit einem D3-Force-Directed-Graph, Knoten gefaerbt nach Community, Groesse nach PageRank, Bruecken markiert, mit Suche, Zoom, Label-Toggle und Detail-Panel. Explorer (explorer.py) erzeugt darueber hinaus die read-only Werkbank explorer.html, die Topologie, Inhalts-Schicht und Triangulation in einem angereicherten PAYLOAD verbindet (siehe Erste Frontend-Stufe). Begleitend schreiben report_parse.py, report_topology.py und report_pragmatics.py die Markdown-Berichte fuer die Gate-Kontrolle.

## Datenarchitektur

Topologie und Inhalt liegen in zwei getrennten Schichten, das ist der Schluessel fuer jedes Frontend. Die Topologie-Schicht steckt im eingebetteten PAYLOAD von topology.html (id, title, path, is_moc, anon, community, pagerank, degree, in_degree, out_degree, betweenness, k_core, is_bridge). Die Inhalts-Schicht steckt in graph.json (key, title, path, vollstaendiges frontmatter inklusive tags und type, body_preview, aliases, privacy_anonymized, is_moc) plus den globalen Strukturen dead_links, orphans und stats.

Beide Schichten sind per Dateiname-Stem joinbar (PAYLOAD.id gleich graph.json key), fuer alle Knoten ausser dem anonymisierten Sonderfall. Ein reiches Read-Frontend mit Community-, Tag- und type-Filter, Orphan- und Bruecken-Hervorhebung und Atom-Sprung ist daraus zur Build-Zeit baubar, ohne die Pipeline neu zu laufen. Das macht eine erste Frontend-Stufe billig.

## Triangulation

Die Triangulation kreuzt die topologische Louvain-Community mit der pragmatischen Ordner-Partition und fragt, ob die aus den Links berechneten Gruppen sich mit der gelebten Ablage decken. Drei Aussagetypen werden getrennt. Befund ist eine Community, die sich weitgehend mit einem Ordner deckt (hohe Reinheit), die Topologie bestaetigt die Ablage. Hypothese ist eine Community, die quer ueber Ordner streut (niedrige Reinheit), ein Kandidat fuer ein Querthema ohne pragmatische Stuetze. Diagnose ist ein einzelner Ausreisser-Knoten, der in einem anderen Ordner liegt als der, der seine sonst reine Community dominiert, also woanders vernetzt als abgelegt.

Gesamtmasse sind die size-gewichtete mittlere Community-Reinheit und die Normalized Mutual Information (NMI) zwischen Community- und Ordner-Partition. NMI ist 1 bei deckungsgleichen, 0 bei unabhaengigen Partitionen. Zusaetzlich misst die Tag-Kohaesion, wie konzentriert die Knoten eines Tags in einer Community liegen, ein konzentrierter Tag ist topologisch geschlossen, ein gestreuter ein Querschnitts-Tag. Privacy bleibt gewahrt, die Ordner-Partition nutzt nur das erste Pfadsegment, nie den Dateinamen, anonymisierte Knoten zaehlen in den Aggregaten mit, werden aber nicht einzeln als Ausreisser gelistet. Reine Mikro-Communities aus wenigen Knoten sind trivial rein und werden im Bericht gesondert ausgewiesen.

## Privacy

Knoten aus Business/Angebote/ werden mehrlagig anonymisiert. Am Knoten selbst wird der Titel zu Angebot-hash, der Body nicht eingelesen, sensitive Frontmatter (invoice, summary, aliases) gestrippt, key und path im JSON ersetzt. An anderen Knoten werden Wikilinks auf einen anonymisierten Knoten im body_preview maskiert. Die Topologie bleibt sichtbar, Privacy darf die Befunde nicht glaetten.

Behobene Regression. Frueher baute render.py das PAYLOAD aus dem Live-Graphen vor dem Anonymisierungs-Remap, daher stand der Klartext-Dateiname eines anonymisierten Business-Knotens in der generierten topology.html, waehrend write_graph_json korrekt remappte. Der Fix zieht das Remap als eine Quelle der Wahrheit nach parse.py (build_key_remap und export_path_for); write_graph_json, render und explorer verwenden es gemeinsam fuer Knoten-id, Pfad und Kanten-Endpunkte. Verifiziert gegen den lebenden Vault, kein Klartext-Business-Name mehr in topology.html, explorer.html oder graph.json, die anonymisierten Knoten erscheinen durchgaengig als Angebot-hash. Zusaetzlich werden tote Links und Orphans anonymisierter Knoten aus der Explorer-Pflege-Triage herausgehalten.

## Output und Reproduzierbarkeit

Output liegt in output/ und ist gitignored, also nicht versioniert, aber deterministisch regenerierbar mit python -m vault_graph. Erzeugt werden data/graph.json, findings/parse-bericht.md, findings/topology-bericht.md, findings/triangulation-bericht.md, visualisierung/topology.html und visualisierung/explorer.html. Reproduzierbarkeit ist ueber fixe Seeds (Louvain seed 42) und die Schwellwerte als Konstanten gesichert, graph.json und explorer.html sind byte-identisch ueber Laeufe gegen denselben Vault-Stand. Vollstaendige Reproduzierbarkeits-Metadaten (Tool-Git-Hash, Versionen, Vault-mtime) sind ein offenes Ziel.

## Aktueller Stand

Der MVP (Parse, Topology, Render, Privacy, Tests, fixe Seeds) war die Ausgangslinie, HEAD 4383e93. Inzwischen ist die Session-Arbeit per Fast-Forward auf main konsolidiert, main ist die einzige Arbeitslinie, gearbeitet wird ohne eigene Branches mit Hintergrund-Commit. Ein frischer Lauf gegen den lebenden Vault wurde durchgefuehrt, der Vault ist gegenueber dem alten Snapshot gewachsen und an toten Links und Orphans deutlich sauberer geworden. Die jeweils aktuellen Vault-Metriken sind regenerierbar und stehen nicht eingefroren hier. Den laufenden Verlauf je Runde haelt [journal.md](journal.md).

Von den drei Sichten sind die topologische und die pragmatische gebaut. Die semantische Sicht (Embeddings) ist nicht implementiert, aber nicht mehr nur als gegate Idee gefuehrt, sondern als ausgearbeitete Vorlage, siehe [aehnlichkeitsanalyse-vorlage.md](aehnlichkeitsanalyse-vorlage.md), und als Teil der beschlossenen Wissensgraph-Richtung, siehe Projektrichtung.

Seit dem MVP sind mehrere Schritte hinzugekommen. Der Privacy-Fix ist umgesetzt und gegen den lebenden Vault verifiziert. Die erste Frontend-Stufe ist als Werkbank gebaut, ein neues Modul explorer.py erzeugt zusaetzlich zu topology.html eine read-only Werkbank explorer.html. Die pragmatische Sicht und die erste Triangulation sind gebaut, pragmatics.py und report_pragmatics.py kreuzen Community und Ordner und schreiben den triangulation-bericht.md, das Frontend zeigt Ordner, Ausreisser und die Triangulationsmasse. In der Konsolidierungsrunde wurde der Code verhaltenswahrend aufgeraeumt (tote Kennzahl closeness und ein ungenutzter Import entfernt), die Doku auf den realen Stand gebracht und der knowledge-Ordner verfestigt. Alles ist in die Pipeline aufgenommen, die Outputs bleiben gitignored und deterministisch regenerierbar, die Testsuite deckt die Phasen ab.

## Projektrichtung

Operator-Beschluss als Kontext, vault-graph waechst vom topologischen Analyse-CLI zu einem analytischen Frontend, mit dem der Operator interaktiv am Vault arbeitet. Die bestehende Werkbank explorer.html ist der Keim, der Ausbau ist stufenweise.

Im Operator-Dialog der Konsolidierungsrunde ist die zentrale Richtung beschlossen. Die Netzwerkvisualisierung wird das zentrale UI-Element, und der reine Linkgraph wird zu einem getypten Wissensgraphen. Damit fallen die zwei bisher getrennten offenen Straenge, Interface-Umbau und semantische Faehigkeit, in ein Vorhaben zusammen. Tragende Idee, Bedeutung steckt im Kontext, also in den Beziehungen, nicht im einzelnen Dokument. Daraus das Zwei-Schichten-Modell, Embedding-Aehnlichkeit als billiger vollstaendiger Scout fuer Kandidatenpaare, getypte Relationen ueber eine kleine Taxonomie als bedeutungstragende Karte, vom Sprachmodell vorgeschlagen und vom Menschen bestaetigt. Der ausgearbeitete Plan steht in [plan-zentrale-visualisierung.md](plan-zentrale-visualisierung.md), der Gestaltungsvorschlag fuer den Interface-Umbau in [gestaltungsvorschlag-interface.md](gestaltungsvorschlag-interface.md). Der Determinismus-Kern bleibt unberuehrt, die Sprachmodell-Vorschlaege laufen als eingefrorene Schicht daneben, das Tool schlaegt vor und schreibt nichts in den Vault.

## Erste Frontend-Stufe, umgesetzt

Eine Design-Exploration hat drei unabhaengige UI-Konzepte gegen das echte Datenschema gestellt (Netz-Explorer mit dem Graph als Leitflaeche, Analyse-Werkbank mit sortierbaren Befundtabellen, Pflege-Triage mit der kuratorischen Arbeitsliste vorn) und zu einer Hybridform synthetisiert, Werkbank mit verlinktem Netz. Diese Hybridform ist als explorer.py gebaut. explorer.html traegt eine sortierbare Befundtabelle, ein read-only Pflege-Triage-Panel (tote Links nach Quellknoten, Orphans) und den Force-Graph als Kontextfenster, alle drei ueber eine geteilte Selektion verbunden, mit obsidian-Sprung pro Knoten und den drei Aussagetypen sichtbar getrennt. Die Befundtabelle markiert Community und Bruecke als Hypothese, die uebrigen Spalten als Befund, die Pflege-Flaeche als Diagnose.

Realisiert sind die Konkretisierungen ueber die seed-Visualisierung hinaus, Facetten-Filter nach Community, Tag und type statt nur Volltextsuche, sichtbare Orphans, tote Links als Diagnose-Arbeitsliste, der Sprung ins echte Atom per obsidian-URI und die bidirektionale Selektion zwischen Tabelle, Triage und Graph. Das angereicherte PAYLOAD traegt dafuer zusaetzlich tags und type, joinbar zur Build-Zeit ohne Pipeline-Neulauf. Die Werkbank ist read-only, sie schreibt nichts in den Vault. Die Hybridform wurde gewaehlt, weil sie als einzige gegen die verifizierten realen Zahlen gebaut war und Befund, Diagnose und Hypothese auf drei Flaechen abbildet.

Visueller Funktionstest geleistet. Ein frischer Pipeline-Lauf gegen den lebenden Vault wurde durchgefuehrt und ist deterministisch (graph.json und explorer.html byte-identisch ueber zwei Laeufe), die Testsuite ist gruen. Die explorer.html wurde im Browser gesichtet, mit Screenshot-Spur fuer Befundtabelle, Pflege-Triage und Detail-Panel. Headless gegen das eingebettete PAYLOAD verifiziert, referentiell konsistent (keine haengenden Kanten nach Aufloesung der D3-Objektreferenzen), Privacy sauber (anonymisierte Knoten ohne Inhalts-Metadaten, nicht in der Triage), Stats-Zeile deckungsgleich mit den PAYLOAD-Arrays, Facetten-Filter und Graph-Dimmung konsistent. Der obsidian-Sprung ist pro Knoten geprueft, Schema obsidian://open, Vault-Parameter korrekt, file gleich dem vault-relativen Pfad ohne Endung, Unterordner-Pfade loesen sauber auf, anonymisierte Business-Knoten tragen einen deaktivierten Sprung.

Lehre aus der Exploration. Agenten-Ergebnisse wurden gegen die echten Daten geprueft, nicht uebernommen. Ein Agent hatte zu niedrige Community- und Bruecken-Zahlen gemeldet, die Pruefung gegen PAYLOAD und graph.json korrigierte das. Verify not trust gilt auch fuer die eigenen Subagenten.

## Offene Operator-Entscheidungen

Die order der Konsolidierungsrunde hat die frueher offenen Grundsatzfragen geschlossen. vault-graph bleibt reines Lese- und Analysewerkzeug und schreibt nie in den Vault, damit ist die fruehere Variante-B-Frage (kuratorisches Rueckschreiben in den Vault) gegenstandslos, das Schreibterritorium gegen die obsidian-vault-Lane muss nicht mehr gezogen werden. main ist konsolidiert, ohne eigene Branches gearbeitet, der Merge ist nach dem Prototyp-Feedback freigegeben, die fruehere Branch-Gate-Frage entfaellt.

Offen ist jetzt anderes. Der Interface-Umbau ist beauftragt, aber gegated, die Lane legt mit [gestaltungsvorschlag-interface.md](gestaltungsvorschlag-interface.md) den verlangten Gestaltungsvorschlag vor und baut erst nach dessen Sichtung. Aus dem Wissensgraph-Plan kommen vier Detailweichen, die einzeln fallen, wenn ihre Phase sie braucht, nicht dringend. Der Skalierungsanspruch (wie gross das Netz wird, bestimmt die Technikwahl), die Speicherung bestaetigter Relationen (beruehrt die Read-only-Grenze und waere mit der obsidian-vault-Lane abzustimmen), die endgueltige Relationstaxonomie und die Modellwahl fuer Embedding und Typisierung.

## Einbettung in die Forschungsleitstelle

vault-graph ist eine Lane der Forschungsleitstelle, Kennung Repo plus Rolle, vault-graph · Beobachtungsinstrument. Weil das Tool den Vault read-only parst, ist es das Messinstrument fuer den Wissenstransfer zwischen den Projekten. Kommunikation laeuft nur ueber zwei Dateien im forschungsleitstelle-Repo, reports/order-vault-graph.md herein und reports/handoff-vault-graph.md hinaus. Der Arbeitsmodus ist autonom auf main, ohne eigene Branches, mit Hintergrund-Commit auf explizite Pfade, der handoff meldet das Delta, neue inhaltliche Fragen gehen als Operator-Frage oder klaerung hinaus.

Konflikt-Radar. Die Vault-Lane ist Datenquelle und Upstream, sie editiert genau die Dateien, die hier geparst werden, jeder Move, Rename oder Dead-Link-Fix der Vault-Lane veraendert den Graphen flussaufwaerts. Die Projekt-Lanes sind die Messobjekte, ihr Wissenstransfer in den Vault ist das, was gemessen wird. Die Read-only-Grenze ist fest, vault-graph schreibt nie in den Vault, damit gibt es keine Datei-Kollision mit der Vault-Lane. Pflegesignale und ein moeglicher kuenftiger Speicherort fuer bestaetigte getypte Relationen werden im eigenen Repo gefuehrt oder, falls je in den Vault, nur nach Abstimmung mit der Vault-Lane, das ist eine der offenen Detailweichen.

## Quellen

Blondel, V. D. et al. (2008). Fast unfolding of communities in large networks. J. Stat. Mech.

Newman, M. E. J. (2006). Modularity and community structure in networks. PNAS 103(23).

Danon, L. et al. (2005). Comparing community structure identification. J. Stat. Mech. P09008. Grundlage der Normalized Mutual Information als Partitionsvergleich.

Denzin, N. K. (1978). The Research Act. McGraw-Hill. Referenz fuer die Triangulations-Position, mit der Kreuzung von topologischer und pragmatischer Sicht jetzt einschlaegig.

Munafo, M. R. et al. (2017). A manifesto for reproducible science. Nature Human Behaviour 1.
