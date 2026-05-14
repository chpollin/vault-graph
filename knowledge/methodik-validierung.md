# Validierung

Welche Aussagen das Tool macht, welche prüfbar sind, was Befund von Diagnose von Hypothese unterscheidet, und wie Privacy in die Validierung eingreift.

## Drei Aussagetypen

Jede Aussage in den Findings ist einer der drei Klassen zugeordnet.

### Befund

Datengestützte, prüfbare Aussage. Wer den Code mit denselben Vault-Daten erneut laufen lässt, kommt zu derselben Aussage.

Beispiele:

- "Cluster 7 enthält 47 Knoten."
- "Knoten X hat Betweenness 0.34."
- "Es existieren 12 tote Wikilinks im Vault."
- "Cluster 7 und MOC Y überlappen zu 73% (Jaccard 0.73)."
- "Paarweise Konvergenz Topologie/Semantik: AMI = 0.41."

Befunde sind die Substanz des Tools und für Referenzierung geeignet, sofern Methode und Datenstand mit angegeben werden.

### Diagnose

Datengestützte Auffälligkeit, die einen Pflege-Hinweis nahelegt.

Beispiele:

- "Knoten A hat semantische Nähe ≥ 0.8 zu Knoten B, ist aber nicht verlinkt." (möglicher fehlender Link)
- "MOC X und algorithmischer Cluster 3 überlappen nur zu 23%." (MOC entspricht möglicherweise nicht der gelebten Vernetzung)
- "Cluster 9 hat einen Reifegrad-Index von 0.31." (Konsolidierungsbedarf)
- "Knoten Y ist Sink (15 eingehend, 4 ausgehend)." (möglicher Pflegehinweis)

Diagnosen sind Anlässe für den User, keine Anweisungen.

### Hypothese

Aussage, die nur durch eine Sicht gestützt ist. Wird mit `[HYPOTHESE]` markiert.

Beispiele:

- "Cluster 12 (nur topologisch identifiziert) könnte ein Wissensnetzwerk sein."
- "Knoten Z könnte ein Querkonzept sein (hohe Betweenness, aber keine Multi-Cluster-Semantik)."

Hypothesen werden nicht als Befunde präsentiert.

## Nicht zulässige Aussagen

**Wert-Aussagen.** "Wichtig", "interessant", "zentral" (im informellen Sinn) sind nicht messbar. Was messbar ist, wird mit dem korrekten Begriff bezeichnet.

**Soll-Aussagen.** "Sollte gepflegt werden" — das Tool gibt Diagnosen, keine Anweisungen.

**Inhaltliche Aussagen.** "Knoten X behandelt das Thema Y" — das Tool macht keine inhaltlichen Aussagen über Dokumente.

**Kausalität.** "X ist Querkonzept, weil es Y mit Z verbindet" — Korrelation ja, Kausalität nein.

## Reproduzierbarkeit

In `output/data/analyses.json` werden mitgespeichert:

- Random-Seeds (Louvain, HDBSCAN)
- Versionen der Bibliotheken (`networkx`, `python-louvain`, `hdbscan`, `sentence-transformers`)
- Embedding-Modellname und Modellgewicht-Hash
- Vault-Stand (Anzahl Dateien, letzte mtime, optional Git-Hash)
- Alle Schwellwerte mit aktuellen Werten

Damit ist jede Aussage rückverfolgbar zu einer konkreten Konfiguration.

## Validierung gegen den User

Stimmen die identifizierten Wissensnetzwerke mit der Selbstwahrnehmung des Vault-Eigentümers überein? Drei Ergebnistypen:

1. **Konvergenz.** Erwartet für robust identifizierte Wissensnetzwerke. Mehrwert liegt in der quantitativen Untermauerung und in Begleitstatistiken.
2. **Tool zeigt mehr.** Latente Strukturen werden sichtbar gemacht.
3. **Tool zeigt weniger oder anderes.** Diskrepanz ist eigener Befund: entweder User-Wahrnehmung ist Wunsch statt Realität, oder das Tool übersieht etwas Wesentliches.

Im dritten Fall ist Reflexion nötig, nicht Anpassung der Schwellwerte.

## Privacy als methodische Frage

Privacy-Filter verändern, was das Tool sehen kann. Das hat methodische Konsequenzen.

### Was gefiltert wird

- Knoten in `Business/Angebote/`: Titel anonymisiert (`Angebot-{hash8}`), Body nicht eingelesen
- Frontmatter-Felder `invoice`, `summary` bei Business-Knoten: nicht aufgenommen
- Volltext-Snippets in Hover-Tooltips für Business-Knoten: leer
- Personennamen in Frontmatter (außer öffentliche Wissenschaftsnamen): nicht ausgegeben

### Methodische Konsequenz

Anonymisierte Knoten erscheinen weiterhin topologisch und pragmatisch, aber nicht semantisch. Ihre Cluster-Zuordnung wird mit `[2/3 Sichten verfügbar — Privacy]` annotiert.

Wenn ein Business-Cluster topologisch und pragmatisch konvergiert, gilt er als identifiziertes Wissensnetzwerk, mit dieser einschränkenden Annotation.

### Grenze

Privacy darf nicht zu Glättung führen. Methodisch korrekte Befunde werden ausgegeben, auch wenn unbequem.

## Anti-Fallstrick — Parameter-Anpassung

Bei explorativer Analyse besteht die Gefahr, Parameter so lange anzupassen, bis das gewünschte Bild entsteht. Dagegen:

- **Defaults sind fix dokumentiert.** Louvain Resolution = 1.0, Jaccard-Schwelle = 0.6, Z-Score-Schwelle = 1.5. Abweichungen werden in `analyses.json` mit Begründung gespeichert.
- **Parameter-Variation ist Forschung, nicht Findings.** Wer Parameter variiert, dokumentiert das als separates Experiment, nicht als Standard-Output.
- **Mehrere Modelle parallel** ist legitim. Ergebnis ist eine Sensitivitätsanalyse, kein neuer Befund.

## Wann das Tool Schweigen verlangt

- Cluster mit weniger als 5 Knoten: nicht als Wissensnetzwerk klassifiziert, sondern als "Mikro-Cluster" aufgelistet
- AMI < 0.15 zwischen Sichten: als "keine substantielle Konvergenz" markiert, kein Interpretationsversuch
- Anonymisierungs-Anteil > 30% in einem Cluster: als "semantisch nicht ausreichend stützbar" markiert

Stille ist eine valide Tool-Aussage.

## Quellen

Vinh, N. X., Epps, J., Bailey, J. (2010). *Information theoretic measures for clusterings comparison.* JMLR 11.

Gelman, A., Loken, E. (2014). *The Statistical Crisis in Science.* American Scientist 102(6).

Munafò, M. R. et al. (2017). *A manifesto for reproducible science.* Nature Human Behaviour 1.
