# Methodik (MVP)

Die epistemische Position des Tools auf einer Seite. Projektkonzept in [knowledge/projektkonzept.md](knowledge/projektkonzept.md).

## Frage

Welche Strukturen lassen sich im Linkgraph eines Obsidian-Vaults methodisch belastbar identifizieren, und was sagen sie über die gelebte Wissensorganisation?

## Position des MVP

Der MVP arbeitet **nur auf der topologischen Sicht**: dem Linkgraph aus Wikilinks. Semantische Sicht (Embeddings) und pragmatische Sicht (MOCs, Tags, Ordner) sind als Stage 2 dokumentiert, aber nicht implementiert.

Der MVP macht damit keine Aussagen über *Wissensnetzwerke* im vollen methodischen Sinn (Triangulation aus drei Sichten). Er liefert topologische Befunde: Communities, Hubs, Brückenknoten. Die Frage, ob daraus *Wissensnetzwerke* werden, bleibt offen, bis Stage 2 die zweite und dritte Sicht ergänzt.

## Topologische Sicht

Operationalisierung:

- **Communities** via Louvain (Blondel et al. 2008) auf dem ungerichteten Projekt des Linkgraphen. Resolution 1.0, Seed 42 für Reproduzierbarkeit. Modularität > 0.3 gilt als substanzielle Community-Struktur (Newman 2006).
- **Centrality** pro Knoten: Degree (in/out/total), Betweenness, Eigenvector, PageRank, Closeness.
- **Brückenknoten** via Z-Score-Differenz: Knoten mit hoher Betweenness bei moderater Degree (`betweenness_z - degree_z >= 1.5`). Kandidaten für Querkonzepte.
- **K-Core-Dekomposition**: höchster k-Core, in dem ein Knoten liegt. Innerster Kern ist der dichteste vernetzte Bereich des Vaults.

Annahme: Wikilinks materialisieren epistemische Nähe. Schwäche: Wikilinks tragen verschiedene Funktionen (Spezialisierung, Kontrast, Workflow), die Topologie ignoriert.

## Drei Aussagetypen

Auch der MVP unterscheidet:

**Befund.** Datengestützt, prüfbar. "Community 4 enthält 152 Knoten." Reproduzierbar gegen denselben Vault-Stand und denselben Tool-Git-Hash.

**Diagnose.** Datengestützte Auffälligkeit, die Pflege nahelegt. "259 tote Wikilinks im Vault."

**Hypothese.** Schwächer gestützt. Topologische Cluster ohne semantische oder pragmatische Stützung sind **Hypothesen über Wissensnetzwerke**, keine Befunde im vollen Sinn.

Nicht zulässig: Wert-Aussagen ("wichtig"), Soll-Aussagen ("sollte gepflegt werden"), inhaltliche Aussagen über Dokumente, Kausal-Erklärungen.

## Privacy

Knoten in `Business/Angebote/` werden anonymisiert. Mehrlagig:

**Am anonymisierten Knoten selbst:**
- Titel wird zu `Angebot-{hash8}`
- Body wird nicht eingelesen, `body_preview` ist leer
- Sensitive Frontmatter-Felder werden gestrippt: `invoice`, `summary`, `aliases`
- `key` und `path` werden im exportierten JSON durch den Anonym-Title ersetzt

**An anderen Knoten:**
- Wikilinks, die auf einen anonymisierten Knoten zeigen, werden in deren `body_preview` durch den Anonym-Title ersetzt

Topologie bleibt sichtbar (in/out-Degree, Community). Der MVP exportiert keine Body-Texte über die Visualisierung; Privacy-Leaks über free-text-Body kommen erst mit Stage 2 (Embeddings).

Privacy darf nicht zu Glättung führen. Methodisch korrekte Befunde werden ausgegeben, auch wenn unbequem.

## Reproduzierbarkeit

Stage-2-Ziel: pro Lauf Tool-Git-Hash, Seeds, Bibliotheks-Versionen, Vault-mtime in `analyses.json`. Der MVP setzt deterministische Seeds (Louvain seed=42) und dokumentiert Schwellwerte als Konstanten in `vault_graph/__main__.py`. Echte Reproduzierbarkeits-Metadaten folgen in Stage 2.

## Was der MVP nicht leistet

- Keine Triangulation. Topologie ist eine Sicht, kein Befund über Wissensnetzwerke.
- Keine semantische Analyse. Inhaltliche Ähnlichkeit zwischen Knoten wird nicht gemessen.
- Keine pragmatische Sicht. MOCs werden mit einer minimalen Heuristik markiert, aber nicht als eigenständige Sicht ausgewertet.
- Keine Wert- oder Empfehlungs-Aussagen.

## Stage 2 (nach MVP)

- Semantische Sicht: Sentence-Embeddings, HDBSCAN-Cluster, Linking-Kandidaten via Kosinusähnlichkeit
- Pragmatische Sicht: MOC-Cluster (primär), Tag-Cluster, Ordner-Cluster (sekundär/tertiär)
- Triangulation: AMI-Matrix, paarweise Jaccard ≥ 0.6 als Wissensnetzwerk-Schwelle, vier Divergenz-Typen
- Vollständige Reproduzierbarkeits-Metadaten

## Quellen

Newman, M. E. J. (2006). Modularity and community structure in networks. *PNAS* 103(23).

Blondel, V. D. et al. (2008). Fast unfolding of communities in large networks. *J. Stat. Mech.*

Denzin, N. K. (1978). *The Research Act.* McGraw-Hill. (Referenz für die Triangulations-Position, ab Stage 2 relevant.)

Munafò, M. R. et al. (2017). A manifesto for reproducible science. *Nature Human Behaviour* 1.
