# Was ist ein Wissensnetzwerk?

Drei konkurrierende Antworten und die hier vertretene integrierte Position.

## Ausgangsproblem

"Wissensnetzwerk" zirkuliert als Begriff in Tooltexten, DH-Vorträgen und Obsidian-Tutorials, ohne dass die zugrundeliegende Definition jedes Mal geklärt wird. Implizit wird oft angenommen: ein Wissensnetzwerk ist das, was der Graph View zeigt.

Das genügt nicht. Was der Graph View zeigt, ist ein Linkgraph — Dokumente als Knoten, Wikilinks als Kanten. Ob daraus ein Wissensnetzwerk wird, hängt von Annahmen ab, die das Wort *Wissen* erst rechtfertigen.

## Antwort 1 — Topologisch

**Definition.** Ein Wissensnetzwerk ist eine Community im Linkgraph: eine Knotengruppe, die untereinander dichter verlinkt ist als zur Außenwelt.

**Operationalisierung.** Modularitätsmaximierung (Newman 2006), Algorithmen wie Louvain (Blondel et al. 2008) oder Leiden (Traag et al. 2019). Modularitätswerte über 0.3 gelten als substanzielle Community-Struktur.

**Annahme.** Wikilinks materialisieren epistemische Nähe.

**Stärken.** Vollautomatisch reproduzierbar, keine Sprachverarbeitung nötig, etablierte Validitätsmaße.

**Schwächen.**

- Wikilinks tragen verschiedene Funktionen (Spezialisierung, Kontrast, Fundierung, Anwendung, Kritik). Topologie ignoriert diese Unterschiede.
- MOCs überrepräsentieren als Hubs.
- Schreibgewohnheiten formen den Linkgraph mit.

**Konsequenz.** Topologische Cluster sind ein starkes Indiz, kein hinreichender Beweis.

## Antwort 2 — Semantisch

**Definition.** Ein Wissensnetzwerk ist eine Gruppe von Dokumenten, die sprachlich ähnlich über dasselbe sprechen.

**Operationalisierung.** Sentence-Embeddings (Reimers/Gurevych 2019), Kosinusähnlichkeit, dichtebasiertes Clustering (HDBSCAN, McInnes et al. 2017).

**Annahme.** Sprache ist direkter Marker für epistemische Zugehörigkeit.

**Stärken.** Findet thematische Nähe auch ohne Links, identifiziert Linking-Lücken, unabhängig von Tagging-Disziplin, robust gegen MOC-Verzerrung.

**Schwächen.**

- Embeddings erfassen sprachliche Oberfläche, nicht zwingend methodische Verwandtschaft.
- Methodisch verwandte Dokumente können lexikalisch divergieren.
- Embedding-Modelle haben Bias gegenüber häufigen Konstruktionen.
- Modellwahl beeinflusst Ergebnis.

**Konsequenz.** Semantische Cluster sind ein unabhängiges Indiz. Stärke liegt in der Unabhängigkeit von der Topologie.

## Antwort 3 — Pragmatisch

**Definition.** Ein Wissensnetzwerk ist eine Menge von Dokumenten, die zusammen für einen Zweck mobilisiert werden — Vortrag, Paper, Workshop, Antrag.

**Operationalisierung.** MOC-Mitgliedschaft, Tag-Gruppen, Ordnerstruktur, Frontmatter-Felder wie `anchor-project`.

**Annahme.** Der Vault-Eigentümer hat durch Hubs intentionale Zugehörigkeiten materialisiert.

**Stärken.** Spiegelt explizit gewollte Strukturierung, direkt interpretierbar, transparent.

**Schwächen.**

- MOCs veralten.
- Tags werden im Schreibmoment gesetzt, nicht aus Distanz reflektiert.
- Ordnerstruktur ist Ablage, nicht Wissenslogik.
- Mehrfachzugehörigkeiten erzwingen Reduktion.

**Konsequenz.** Pragmatische Cluster sind das explizite Selbstmodell des Vaults. Valide als Aussage des Eigentümers, nicht zwingend als Aussage über die Wissensstruktur.

## Die integrierte Position

Keine der drei Antworten ist allein hinreichend. Sie sind methodisch unabhängig:

| Sicht | Sieht | Sieht nicht |
|---|---|---|
| Topologisch | Links | Inhalt, Intention |
| Semantisch | Sprache | Links, Intention |
| Pragmatisch | Intention | direkter Inhalt, direkte Topologie |

Drei methodisch unabhängige Verfahren, die zu demselben Ergebnis kommen, stützen das Ergebnis stärker als ein einzelnes Verfahren (Triangulation, Denzin 1978).

**Definition für vault-graph:**

> Ein Wissensnetzwerk ist eine Knotengruppe, die in mindestens zwei der drei Sichten als kohärenter Cluster identifiziert wird, mit einer paarweisen Jaccard-Übereinstimmung von mindestens 0.6.

**Konsequenzen:**

- Drei Sichten konvergent: robust identifiziertes Wissensnetzwerk
- Zwei Sichten konvergent: identifiziertes Wissensnetzwerk
- Eine Sicht: Hypothese, in Findings als solche markiert
- Divergenzen: eigene Befunde (siehe [methodik-triangulation.md](methodik-triangulation.md))

## Eigenschaften der Definition

**Nicht-reduktionistisch.** Reduziert Wissensnetzwerke nicht auf Topologie, Semantik oder Deklaration allein.

**Falsifizierbar.** "Cluster X ist ein Wissensnetzwerk" hat klare Bedingungen, die der Code prüft.

**Diagnostisch.** Divergenzen sind keine Fehler der Methode, sondern eigene Information.

## Quellen

Newman, M. E. J. (2006). *Modularity and community structure in networks.* PNAS 103(23).

Blondel, V. D. et al. (2008). *Fast unfolding of communities in large networks.* J. Stat. Mech.

Traag, V. A., Waltman, L., van Eck, N. J. (2019). *From Louvain to Leiden.* Scientific Reports 9.

Reimers, N., Gurevych, I. (2019). *Sentence-BERT.* EMNLP.

McInnes, L. et al. (2017). *hdbscan: Hierarchical density based clustering.* JOSS.

Denzin, N. K. (1978). *The research act.* McGraw-Hill.
