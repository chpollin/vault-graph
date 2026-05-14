# Methodik

Die epistemologische Position dieses Tools. Wer mit den Ergebnissen arbeitet, sollte zuerst hier lesen.

## Die Frage

Ein Obsidian-Vault enthält hunderte Wikilinks zwischen Konzepten. Aus diesem Linkgraph lässt sich ein hübsches Force-Directed-Diagramm zeichnen. Die Suggestion dieser Visualisierung ist stark: das Bild zeigt Cluster, also gibt es Wissensnetzwerke.

Diese Schlussfolgerung ist nicht zulässig. Ein Cluster im Linkgraph ist eine topologische Beobachtung. Ob daraus ein **Wissensnetzwerk** wird — also eine epistemisch gehaltvolle Gruppierung von Dokumenten —, ist eine separate Frage.

Dieses Tool unterscheidet die topologische Beobachtung vom epistemischen Anspruch und macht beide nachvollziehbar.

## Was ist ein Wissensnetzwerk?

Drei konkurrierende Antworten konkurrieren in der Literatur und in der Praxis. Jede ist plausibel, jede ist unvollständig.

### Antwort 1 — Topologisch

Ein Wissensnetzwerk ist eine Community im Linkgraph: eine Knotengruppe, die untereinander dichter verlinkt ist als zur Außenwelt. Methodisch: Louvain, Leiden, Modularitätsmaximierung (Newman 2006).

Annahme: Wikilinks materialisieren epistemische Nähe. Wenn zwei Dokumente verlinkt sind, gehören ihre Inhalte zusammen.

Problem: Wikilinks entstehen oft aus Schreibflusslogik, nicht aus methodischer Zuordnung. Ein Verweis kann *spezialisieren*, *kontrastieren*, *fundieren* oder *anwenden* meinen — der Topologie ist das egal. Topologische Cluster können Schreib-Gewohnheiten widerspiegeln statt Wissens-Struktur.

### Antwort 2 — Semantisch

Ein Wissensnetzwerk ist eine Gruppe von Dokumenten, die semantisch über dasselbe sprechen. Methodisch: Knoten-Embeddings, Ähnlichkeitsmatrix, Dichte-basiertes Clustering (HDBSCAN).

Annahme: Sprache ist der direkte Marker für Zugehörigkeit. Wenn zwei Dokumente sprachlich ähnlich sind, behandeln sie verwandte Themen.

Problem: Semantische Ähnlichkeit erfasst Oberfläche. Zwei Dokumente können dasselbe Vokabular nutzen ohne methodisch verwandt zu sein; zwei andere können methodisch eng zusammenhängen ohne lexikalische Überschneidung. Embedding-Modelle haben außerdem Bias gegenüber häufigen Konstruktionen.

### Antwort 3 — Pragmatisch

Ein Wissensnetzwerk ist eine Menge von Dokumenten, die *zusammen für einen Zweck* mobilisiert werden — Vortrag, Paper, Workshop, Antrag. Methodisch: MOC-Mitgliedschaft, Tag-Gruppen, deklarierte Anker.

Annahme: Der Vault-Eigentümer hat durch Hubs und Tags explizit gemacht, welche Dokumente zusammengehören. Diese Zuordnung ist intentional und damit valide.

Problem: Pragmatische Cluster spiegeln die *Ablage-Logik*, nicht notwendig die *Wissens-Logik*. MOCs werden gepflegt, wenn Zeit ist, und veralten. Tags sind im Schreibmoment gesetzt, nicht aus Distanz reflektiert.

## Triangulation als Antwort

Keine der drei Antworten ist allein hinreichend. Aber sie sind **methodisch unabhängig**: Topologie kennt die Sprache nicht, Semantik kennt die Links nicht, Pragmatik kennt beides nicht direkt.

Konvergenz dreier unabhängiger Methoden auf dasselbe Ergebnis ist epistemisch stärker als ein Befund aus einer Methode (Triangulation, Denzin 1978). Wenn ein Cluster topologisch, semantisch und pragmatisch übereinstimmend identifiziert wird, ist die Hypothese "dies ist ein Wissensnetzwerk" robust gestützt.

Genauso wichtig sind die **Divergenzen**:

- **Topologie ohne Semantik** — Knoten sind verlinkt, aber sprechen nicht ähnlich → der Linkgraph ist hier durch andere Logik gewachsen (Workflow, Genealogie, kontrastierende Verweise).
- **Semantik ohne Topologie** — Knoten sind sprachlich nah, aber nicht verlinkt → **fehlende Links**, Pflege-Vorschlag.
- **Pragmatik ohne Topologie/Semantik** — MOC sammelt Knoten, die weder verlinkt noch sprachlich verwandt sind → MOC veraltet, Pflege-Vorschlag.
- **Topologie + Semantik ohne Pragmatik** — Cluster ist real, aber kein MOC adressiert ihn → **emergentes Wissensnetzwerk**, MOC-Kandidat.

## Operationalisierung

Konkret im Tool:

**Stützungs-Score pro Knotengruppe.** Für jede in einer der drei Sichten identifizierte Gruppe wird geprüft, ob mindestens 60% ihrer Knoten auch in einer zweiten Sicht zusammen erscheinen. Bei Konvergenz in zwei Sichten: identifiziertes Wissensnetzwerk. Bei Konvergenz in drei Sichten: robust identifiziertes Wissensnetzwerk. Bei nur einer Sicht: Hypothese.

**Schwellwert begründet, nicht beliebig.** 60% ist gewählt, weil unterhalb der Konvergenz-Anteil zufällig sein kann (zwei Cluster, die zufällig überlappen). 80% wäre zu strikt für reale Vault-Daten mit Querkonzepten, die per Definition in mehreren Clustern auftauchen. Schwellwert ist im Code dokumentiert und änderbar; jede Änderung muss in METHODIK.md begründet werden.

**Brückenknoten als datengetriebene Querkonzepte.** Knoten mit hoher Betweenness-Centrality bei moderater Degree (Z-Score-basiert) sind topologische Brücken. Wenn sie zusätzlich in mehreren semantischen Clustern hohe Ähnlichkeit aufweisen, sind sie Querkonzepte im strengen Sinn. Ohne diese Doppelbedingung sind sie nur topologische Brücken.

## Falsifizierbarkeit

Das Tool macht Aussagen. Diese Aussagen müssen prüfbar sein, damit das Tool methodisch erwachsen ist.

**Prüfbare Aussagen** (Beispiele aus den Findings):

- "Cluster X enthält 47 Knoten." → durch Auszählen falsifizierbar
- "Cluster X hat Modularität 0.42." → durch Neuberechnung falsifizierbar
- "Cluster X ist semantisch kohärent (Silhouette-Score 0.31)." → durch Neuberechnung falsifizierbar
- "Knoten K hat Betweenness 0.34." → durch Neuberechnung falsifizierbar
- "Es gibt 12 tote Wikilinks." → durch Inspektion falsifizierbar
- "Cluster X und MOC Y überlappen zu 73%." → durch Mengenoperation falsifizierbar

**Nicht prüfbare, aber begründete Aussagen:**

- "Cluster X ist ein Wissensnetzwerk." — folgt aus Schwellwert (begründet in METHODIK.md), aber Schwellwert selbst ist Konvention
- "Knoten K ist ein Querkonzept." — folgt aus Brückenknoten-Definition (Betweenness + Multi-Cluster-Semantik), aber Definition selbst ist Konvention

**Niemals als Aussagen formuliert:**

- "Cluster X ist *wichtig*." — Wichtigkeit ist nicht messbar
- "Knoten K *sollte* gepflegt werden." — Sollens-Aussagen sind nicht datengetrieben
- "Wissensnetzwerk X ist *interessant*." — Interessantheit ist nicht messbar

Findings unterscheiden konsequent zwischen Befund (datengestützt), Diagnose (datengestützte Auffälligkeit, die Pflege nahelegt) und Hypothese (nur in einer Sicht gestützt).

## Reproduzierbarkeit

Random-Seeds werden in `output/data/analyses.json` mitgespeichert. Embedding-Modellname und Version werden mitgespeichert. Vault-Stand wird über einen Git-Hash des Vaults dokumentiert (falls verfügbar) oder über die letzte mtime aller eingelesenen Dateien. Damit ist jede Analyse reproduzierbar, solange Vault und Code-Version vorliegen.

## Privacy als methodische Frage

Privacy ist nicht nur ethische Pflicht, sondern methodisch relevant. Anonymisierte Knoten verändern den Linkgraph (Knotentitel wird unkenntlich, aber Knoten existiert weiter). Entfernte Volltexte verändern die semantische Sicht (keine Embeddings für Business/Angebote-Knoten).

Konsequenz: Anonymisierte Knoten erscheinen in topologischer Sicht, aber nicht in semantischer Sicht. Ihre Triangulation kann nur 2/3 Sichten erreichen. Das wird in den Findings explizit ausgewiesen, nicht versteckt.

## Was dieses Tool nicht leistet

- **Keine Wertung.** Wir messen Vernetzung, Reife, Kohärenz. Wir bewerten nicht *gut* oder *schlecht*.
- **Keine Empfehlung.** Pflege-Diagnosen sind datengetriebene Auffälligkeiten, keine Handlungsanweisungen.
- **Keine Generierung.** Wir schreiben keine neuen Wissensdokumente, sondern analysieren bestehende.
- **Keine semantische Tiefe.** Embeddings erfassen Oberfläche; das Tool versucht nicht, "Bedeutung" zu rekonstruieren.

## Quellen

Newman, M. E. J. (2006). *Modularity and community structure in networks.* PNAS 103(23).

Blondel, V. D. et al. (2008). *Fast unfolding of communities in large networks.* Journal of Statistical Mechanics.

Denzin, N. K. (1978). *The research act: A theoretical introduction to sociological methods.* McGraw-Hill.

Reimers, N. & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.* EMNLP.

McInnes, L. et al. (2017). *hdbscan: Hierarchical density based clustering.* JOSS.

Borgman, C. L. (2015). *Big Data, Little Data, No Data: Scholarship in the Networked World.* MIT Press. [für die epistemologische Rahmung]
