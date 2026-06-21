# Methodik

Die epistemische Position des Tools auf einer Seite. Projektkonzept in [knowledge/projektkonzept.md](knowledge/projektkonzept.md), aktueller Bau-Stand in [knowledge/projektwissen.md](knowledge/projektwissen.md).

## Frage

Welche Strukturen lassen sich im Linkgraph eines Obsidian-Vaults methodisch belastbar identifizieren, und was sagen sie ueber die gelebte Wissensorganisation?

## Position

Das Tool arbeitet auf zwei von drei Sichten. Die topologische Sicht auf dem Linkgraph aus Wikilinks und die pragmatische Sicht, die die Link-Communities gegen die Ordnerstruktur trianguliert. Die semantische Sicht, inhaltliche Aehnlichkeit ueber Embeddings, ist als Vorlage ausgearbeitet, aber nicht gebaut.

Solange die semantische Sicht fehlt, bleibt die Triangulation aus drei unabhaengigen Sichten unvollstaendig. Die vorhandene Triangulation aus zwei Sichten, Topologie gegen Ordner, traegt bereits. Sie zeigt, wo die gewachsene Link-Struktur und die abgelegte Ordner-Struktur uebereinstimmen und wo sie auseinanderlaufen. Ob aus topologischen Clustern *Wissensnetzwerke* im vollen Sinn werden, bleibt offen, bis die dritte Sicht ergaenzt ist.

## Topologische Sicht

Operationalisierung:

- **Communities** via Louvain (Blondel et al. 2008) auf dem ungerichteten Projekt des Linkgraphen. Resolution 1.0, Seed 42 fuer Reproduzierbarkeit. Modularitaet ueber 0.3 gilt als substanzielle Community-Struktur (Newman 2006).
- **Centrality** pro Knoten: Degree (in/out/total), Betweenness, Eigenvector, PageRank.
- **Brueckenknoten** via Z-Score-Differenz: Knoten mit hoher Betweenness bei moderater Degree (`betweenness_z - degree_z >= 1.5`). Kandidaten fuer Querkonzepte.
- **K-Core-Dekomposition**: hoechster k-Core, in dem ein Knoten liegt. Innerster Kern ist der dichteste vernetzte Bereich des Vaults.

Annahme: Wikilinks materialisieren epistemische Naehe. Schwaeche: Wikilinks tragen verschiedene Funktionen (Spezialisierung, Kontrast, Workflow), die Topologie ignoriert.

## Pragmatische Sicht und Triangulation

Die pragmatische Sicht kreuzt zwei unabhaengig entstandene Partitionen des Vaults, die Link-Community (gewachsen aus dem Verlinken) und die Ordnerstruktur (gesetzt beim Ablegen).

- **Uebereinstimmung** gemessen als groessengewichtete mittlere Reinheit der Communities und als Normalized Mutual Information (NMI) zwischen beiden Partitionen.
- **Ausreisser** sind Knoten, die in einem fremden Ordner liegen, obwohl ihre Community ueberwiegend rein ist (Reinheitsschwelle 0.60). Sie sind Diagnose-Kandidaten, ein thematisch zugehoeriger Knoten an unerwartetem Ablageort.

Die Treffermenge der Ausreisser haengt empfindlich an der Reinheitsschwelle. Das ist methodisch zu berichten, nicht zu glaetten.

## Drei Aussagetypen

**Befund.** Datengestuetzt, pruefbar, etwa die Knotenzahl einer Community oder der PageRank eines Hubs. Reproduzierbar gegen denselben Vault-Stand und denselben Tool-Git-Hash.

**Diagnose.** Datengestuetzte Auffaelligkeit, die Pflege nahelegt, etwa tote Wikilinks oder ein Ausreisser-Knoten in einem fremden Ordner.

**Hypothese.** Schwaecher gestuetzt. Ein topologischer Cluster ohne semantische Stuetzung ist eine Hypothese ueber ein Wissensnetzwerk, kein Befund im vollen Sinn.

Nicht zulaessig: Wert-Aussagen ("wichtig"), Soll-Aussagen ("sollte gepflegt werden"), inhaltliche Aussagen ueber Dokumente, Kausal-Erklaerungen.

## Privacy

Knoten in `Business/Angebote/` werden anonymisiert. Mehrlagig:

**Am anonymisierten Knoten selbst:**
- Titel wird zu `Angebot-{hash8}`
- Body wird nicht eingelesen, `body_preview` ist leer
- Sensitive Frontmatter-Felder werden gestrippt: `invoice`, `summary`, `aliases`
- `key` und `path` werden im exportierten JSON durch den Anonym-Title ersetzt

**An anderen Knoten:**
- Wikilinks, die auf einen anonymisierten Knoten zeigen, werden in deren `body_preview` durch den Anonym-Title ersetzt

Topologie bleibt sichtbar (in/out-Degree, Community). Die Visualisierung exportiert keine Body-Volltexte. Ein Embedding-Schritt der kuenftigen semantischen Sicht muesste hinter diesem Privacy-Remap sitzen, nie davor.

Privacy darf nicht zu Glaettung fuehren. Methodisch korrekte Befunde werden ausgegeben, auch wenn unbequem.

## Reproduzierbarkeit

Deterministische Seeds (Louvain seed=42, resolution=1.0) und Schwellwerte als Konstanten in `vault_graph/__main__.py`. Zweimaliger Lauf gegen denselben Vault-Stand liefert byte-identische Ausgaben. Eine vollstaendige Reproduzierbarkeits-Signatur pro Lauf (Tool-Git-Hash, Bibliotheks-Versionen, Vault-mtime in einer `analyses.json`) ist noch nicht implementiert.

## Was das Tool nicht leistet

- Keine semantische Analyse. Inhaltliche Aehnlichkeit zwischen Knoten wird noch nicht gemessen, die Vorlage dazu liegt in [knowledge/aehnlichkeitsanalyse-vorlage.md](knowledge/aehnlichkeitsanalyse-vorlage.md).
- Keine vollstaendige Triangulation aus drei Sichten, solange die semantische Sicht fehlt.
- Keine Wert- oder Empfehlungs-Aussagen, keine inhaltlichen oder kausalen Aussagen ueber Dokumente.

## Quellen

Newman, M. E. J. (2006). Modularity and community structure in networks. *PNAS* 103(23).

Blondel, V. D. et al. (2008). Fast unfolding of communities in large networks. *J. Stat. Mech.*

Denzin, N. K. (1978). *The Research Act.* McGraw-Hill. (Referenz fuer die Triangulations-Position.)

Munafo, M. R. et al. (2017). A manifesto for reproducible science. *Nature Human Behaviour* 1.
