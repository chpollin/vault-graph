# Methodik

Die epistemische Position des Tools auf einer Seite. Projektkonzept in [knowledge/projektkonzept.md](knowledge/projektkonzept.md).

## Frage

Ein Cluster im Linkgraph eines Obsidian-Vaults ist eine topologische Beobachtung. Ob daraus ein *Wissensnetzwerk* wird, also eine epistemisch gehaltvolle Gruppierung von Dokumenten, ist eine separate Frage. Vault-graph trennt beides und macht beide Schritte nachvollziehbar.

## Drei Sichten

Drei methodisch unabhängige Antworten, von denen keine allein hinreicht.

| Sicht | Datengrundlage | Algorithmus | Annahme |
|---|---|---|---|
| Topologisch | Wikilinks | Louvain | Wikilinks materialisieren epistemische Nähe |
| Semantisch | Body-Text (Titel + erste 500 Zeichen) | HDBSCAN auf Sentence-Embeddings | Sprache markiert epistemische Zugehörigkeit |
| Pragmatisch | MOC-Mitgliedschaft, Tags, Ordner | Mengenoperationen | Hubs materialisieren intentionale Strukturierung |

Topologie kennt die Sprache nicht, Semantik kennt die Links nicht, Pragmatik kennt beides nicht direkt. Übereinstimmung zwischen unabhängigen Verfahren ist epistemisch stärker als ein einzelner Befund (Denzin 1978).

## Definition

Ein **Wissensnetzwerk** ist eine Knotengruppe, die in mindestens zwei der drei Sichten als kohärenter Cluster identifiziert wird, mit einer paarweisen Jaccard-Übereinstimmung von mindestens 0.6.

Konvergieren alle drei Sichten, gilt das Wissensnetzwerk als robust identifiziert. Konvergiert nur eine, ist die Aussage eine Hypothese.

## Schwellwert 0.6

Jaccard misst die Überlappung zweier Cluster: |A ∩ B| / |A ∪ B|.

- Unter 0.5: schwächer als hälftige Übereinstimmung, zu unsicher
- 0.5 bis 0.6: Überlappung kann zufällig sein
- 0.6 bis 0.8: substanzielle Übereinstimmung mit Raum für Querkonzept-Randabweichungen
- Über 0.8: zu strikt für reale Vaults

Der Wert ist als Konstante in `vault_graph/__main__.py` hinterlegt. Jede Änderung wird in `output/data/analyses.json` mit Begründung mitgespeichert.

## Divergenzen als Befund

Divergenzen sind nicht Fehler, sondern eigenständige Information.

| Typ | Konstellation | Diagnostischer Wert |
|---|---|---|
| A | Topologie ohne Semantik | Workflow-, genealogische oder Kontrast-Links |
| B | Semantik ohne Topologie | Linking-Lücke, konkreter Vorschlag |
| C | Pragmatik ohne Topologie/Semantik | Veralteter oder bewusst heterogener MOC |
| D | Topologie + Semantik ohne Pragmatik | Emergentes Wissensnetzwerk ohne Hub |

## Brückenknoten

Querkonzepte sind in mehreren Clustern aktiv. Drei Bedingungen:

- Topologisch: hohe Betweenness bei moderater Degree (Z-Score ≥ 1.5)
- Semantisch: Embedding nahe an mehreren Cluster-Zentroiden
- Pragmatisch: Mitglied mehrerer MOCs

Ein Knoten ist **Querkonzept**, wenn mindestens zwei Bedingungen erfüllt sind. Datengetriebene Anker-Liste in `findings/querkonzepte.md`.

## Drei Aussagetypen

Jede Aussage in den Findings ist genau einer Klasse zugeordnet.

**Befund.** Datengestützt, prüfbar. Beispiel: "Cluster 7 enthält 47 Knoten." Wer den Code mit denselben Daten erneut laufen lässt, kommt zur selben Aussage.

**Diagnose.** Datengestützte Auffälligkeit, die Pflege nahelegt. Beispiel: "Knoten A hat semantische Nähe ≥ 0.8 zu B, ist aber nicht verlinkt — möglicher fehlender Link." Anlass, keine Anweisung.

**Hypothese.** Nur eine Sicht gestützt. Mit `[HYPOTHESE]` markiert.

Nicht zulässig: Wert-Aussagen ("wichtig", "zentral"), Soll-Aussagen ("sollte gepflegt werden"), inhaltliche Aussagen über Dokumente, Kausal-Interpretationen.

## Privacy als methodische Frage

Privacy-Filter verändern, was das Tool sehen kann. Business-Knoten (`Business/Angebote/`) werden in der semantischen Sicht ausgeschlossen: Titel wird zu `Angebot-{hash8}`, Body nicht eingelesen. Sensitive Frontmatter-Felder (`invoice`, `summary`) werden gestrippt.

Methodische Konsequenz: anonymisierte Knoten erscheinen in maximal 2 der 3 Sichten und werden mit `[2/3 — Privacy]` annotiert. Konvergenz aus Topologie und Pragmatik genügt für Identifikation, mit dieser einschränkenden Annotation.

Privacy darf nicht zu Glättung führen. Methodisch korrekte Befunde werden ausgegeben, auch wenn unbequem.

## Stille

Drei Fälle, in denen das Tool keine Interpretation versucht:

- Cluster mit weniger als 5 Knoten: als Mikro-Cluster aufgelistet, nicht als Wissensnetzwerk
- Paarweise AMI unter 0.15: als "keine substantielle Konvergenz" markiert
- Anonymisierungs-Anteil über 30% in einem Cluster: als "semantisch nicht ausreichend stützbar" markiert

Stille ist eine valide Tool-Aussage.

## Reproduzierbarkeit

In `output/data/analyses.json` werden pro Lauf mitgespeichert: Random-Seeds (Louvain, HDBSCAN), Bibliotheks-Versionen, Embedding-Modellname und Modellgewicht-Hash, Vault-Stand (Anzahl Dateien, letzte mtime, optional Git-Hash), alle Schwellwerte. Jede Aussage ist damit auf eine konkrete Konfiguration rückführbar.

## Anti-Fallstricke

**Parameter-Anpassung.** Defaults sind im Code dokumentiert und werden nicht zur Glättung verändert. Parameter-Variation ist Forschung, nicht Findings.

**Triangulation ist nicht Mehrheit.** Was zählt, ist die paarweise Konvergenz zwischen unabhängigen Methoden, nicht die Stimmenzahl. Tags und MOCs sind beide Selbst-Deklarationen und nicht methodisch unabhängig.

**Tool gegen Selbstwahrnehmung.** Konvergenz mit der Selbstwahrnehmung des Vault-Eigentümers ist Bestätigung, Divergenz ist eigener Befund. Reflexion statt Schwellwert-Anpassung.

## Was das Tool nicht leistet

Keine Wertung. Keine Handlungsempfehlung. Keine inhaltliche Aussage über Dokumente. Keine Kausal-Erklärung. Keine Generierung neuer Vault-Dokumente außerhalb der Synthese-Datei.

## Quellen

Denzin, N. K. (1978). *The Research Act.* McGraw-Hill.

Newman, M. E. J. (2006). Modularity and community structure in networks. *PNAS* 103(23).

Blondel, V. D. et al. (2008). Fast unfolding of communities in large networks. *J. Stat. Mech.*

Traag, V. A., Waltman, L., van Eck, N. J. (2019). From Louvain to Leiden. *Scientific Reports* 9.

Reimers, N., Gurevych, I. (2019). Sentence-BERT. *EMNLP*.

McInnes, L. et al. (2017). hdbscan: Hierarchical density based clustering. *JOSS*.

Vinh, N. X., Epps, J., Bailey, J. (2010). Information theoretic measures for clusterings comparison. *JMLR* 11.

Munafò, M. R. et al. (2017). A manifesto for reproducible science. *Nature Human Behaviour* 1.
