---
title: Methodik
project:
  name: vault-graph
  repository: https://github.com/chpollin/vault-graph
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
status: complete
created: 2026-05-14
updated: 2026-06-30
version: 1.0
language: de
related: [specification, architecture, plan, journal]
template:
  name: Vorlage Domaenenwissen
  version: 0.1
  url: https://dhcraft.org/Promptotyping/promptotyping-document/domain-knowledge
---

# Methodik

Die epistemische Position des Tools. Was vault-graph aus einem Obsidian-Linkgraph methodisch belastbar herauslesen darf, mit welcher Berechtigung, und wo die Aussagekraft endet. Die Operationalisierung der Begriffe steht hier, der Bau der Module in [architecture](architecture.md), die Vorwaertsrichtung in [plan](plan.md).

## Frage

Welche Strukturen lassen sich im Linkgraph eines Obsidian-Vaults methodisch belastbar identifizieren, und was sagen sie ueber die gelebte Wissensorganisation?

## Position

Die Analyse beruht auf drei Sichten, die denselben Vault aus unabhaengigen Achsen lesen. Die topologische Sicht arbeitet auf dem Linkgraph aus Wikilinks. Die pragmatische Sicht trianguliert die Link-Communities gegen die Ordnerstruktur. Die semantische Sicht misst inhaltliche Aehnlichkeit ueber Embeddings.

Topologische und pragmatische Sicht laufen. Die semantische Sicht ist als Code gebaut, der Modell-Lauf, der ihre Nachbarschaften gegen den lebenden Vault einfriert, steht aus. Damit ist die volle Triangulation aus drei Achsen vorbereitet, aber noch nicht geschlossen. Die vorhandene Triangulation aus zwei Achsen, Topologie gegen Ordner, traegt bereits. Sie zeigt, wo die gewachsene Link-Struktur und die abgelegte Ordner-Struktur uebereinstimmen und wo sie auseinanderlaufen. Ob aus einem topologischen Cluster ein Wissensnetzwerk im vollen Sinn wird, bleibt eine Hypothese, bis die semantische Achse den Cluster inhaltlich stuetzt.

Die Methode ist Triangulation im Sinne von Denzin 1978. Eine Auffaelligkeit, die nur eine Sicht sieht, ist schwaecher gestuetzt als eine, die zwei oder drei unabhaengige Achsen gemeinsam zeigen. Konvergenz erhaertet, Divergenz markiert eine offene Frage, keine der Achsen wird ueber die andere gestellt.

## Topologische Sicht

Die topologische Sicht behandelt den Vault als ungerichtetes Projekt seines Linkgraphen und operationalisiert vier Begriffe.

- Communities via Louvain (Blondel et al. 2008). Resolution 1.0, Seed 42. Modularitaet ueber 0.3 gilt als substanzielle Community-Struktur (Newman 2006).
- Centrality pro Knoten, gemessen als Degree (in, out, total), Betweenness, Eigenvector und PageRank.
- Brueckenknoten ueber die Z-Score-Differenz `betweenness_z - degree_z >= 1.5`, also hohe Vermittlungslast bei moderater eigener Vernetzung. Kandidaten fuer Querkonzepte.
- K-Core-Dekomposition, der hoechste k-Core, in dem ein Knoten liegt. Der innerste Kern ist der dichteste vernetzte Bereich des Vaults.

Die tragende Annahme lautet, Wikilinks materialisieren epistemische Naehe. Ihre Schwaeche ist, dass ein Wikilink verschiedene Funktionen traegt (Spezialisierung, Kontrast, Workflow-Verweis), die die reine Topologie nicht unterscheidet. Genau hier setzt die pragmatische Achse als Korrektiv an.

## Pragmatische Sicht und Triangulation

Die pragmatische Sicht kreuzt zwei unabhaengig entstandene Partitionen desselben Vaults, die Link-Community, gewachsen aus dem Verlinken, und die Ordnerstruktur, gesetzt beim Ablegen. Stimmen beide ueberein, stuetzen sich gewachsene und gesetzte Ordnung gegenseitig, laufen sie auseinander, liegt eine Diagnose-Kandidatin vor.

- Uebereinstimmung gemessen als groessengewichtete mittlere Reinheit der Communities und als Normalized Mutual Information (NMI) zwischen beiden Partitionen (Danon et al. 2005).
- Ausreisser sind Knoten in einem fremden Ordner, deren Community ueberwiegend rein ist (Reinheitsschwelle 0.60). Ein thematisch zugehoeriger Knoten an unerwartetem Ablageort.

Die Tag-Kohaesion ergaenzt das Bild auf der Tag-Achse. Sie misst, wie konzentriert die Knoten eines Tags in einer einzelnen Community liegen, ein konzentrierter Tag ist topologisch geschlossen, ein gestreuter ein Querschnitts-Tag. Reine Mikro-Communities aus wenigen Knoten sind trivial rein und werden im Bericht gesondert ausgewiesen, damit ihre triviale Reinheit die size-gewichtete Gesamtaussage nicht verzerrt.

Die Treffermenge der Ausreisser haengt empfindlich an der Reinheitsschwelle. Diese Empfindlichkeit wird methodisch berichtet, nicht geglaettet. Ein Ausreisser ist eine Diagnose, kein Fehler, die Entscheidung ueber Pflege bleibt beim Operator.

## Drei Aussagetypen

Jede Ausgabe des Tools traegt genau einen von drei Aussagetypen. Die Trennung haelt die Beweislast pro Aussage explizit.

Befund. Datengestuetzt und pruefbar, etwa die Knotenzahl einer Community oder der PageRank eines Hubs. Ein Befund ist reproduzierbar gegen denselben Vault-Stand und denselben Tool-Git-Hash.

Diagnose. Eine datengestuetzte Auffaelligkeit, die Pflege nahelegt, etwa ein toter Wikilink oder ein Ausreisser-Knoten in einem fremden Ordner. Eine Diagnose benennt die Auffaelligkeit, nicht die Handlung.

Hypothese. Schwaecher gestuetzt, weil eine stuetzende Achse fehlt. Ein topologischer Cluster ohne semantische Stuetzung ist eine Hypothese ueber ein Wissensnetzwerk, kein Befund.

Nicht zulaessig sind Wert-Aussagen (wichtig), Soll-Aussagen (sollte gepflegt werden), inhaltliche Aussagen ueber den Text eines Dokuments und Kausal-Erklaerungen.

## Privacy

Welche Knoten anonymisiert werden, ist Konfiguration des jeweiligen Vaults. Diese Instanz anonymisiert die Knoten in `Business/Angebote/`, weil sie Auftraggeber- und Honorardaten tragen, die in einem Analyse-Artefakt nichts zu suchen haben. Die Topologie dieser Knoten bleibt sichtbar (Degree, Community-Zugehoerigkeit), ihr Inhalt verschwindet hinter einem Hash-Titel. Damit bleibt die Strukturaussage moeglich, ohne den sensiblen Gehalt zu exportieren.

Zwei Prinzipien binden die Anonymisierung.

- Keine Glaettung. Anonymisierung darf einen methodisch korrekten Befund nicht unterdruecken. Auch eine unbequeme Diagnose ueber einen anonymisierten Bereich wird ausgegeben, sie nennt nur die Inhalte nicht.
- Embedding hinter dem Remap. Jeder kuenftige semantische Schritt liest erst den anonymisierten Knoten, nie den Rohtext davor. Die Reihenfolge ist erst anonymisieren, dann einbetten, nie umgekehrt.

Die Implementierung des Remaps, welche Felder gestrippt werden und wie der Schritt vor dem Export sitzt, steht in [architecture](architecture.md).

## Reproduzierbarkeit

Jeder Befund muss gegen denselben Vault-Stand und denselben Tool-Stand identisch wieder herstellbar sein, sonst ist er kein Befund (Munafo et al. 2017). Reproduzierbarkeit ist deshalb keine nachtraegliche Eigenschaft, sondern die Bedingung, unter der das Tool ueberhaupt von Befunden spricht. Stochastik wird auf feste Seeds festgenagelt, Entscheidungsschwellen sind Konstanten, kein Lauf haengt an Zufall oder an einer Eingabereihenfolge.

Die Mechanik dieses Prinzips, die konkreten Seeds und Schwellwerte als Konstanten sowie die Determinismus-Trennung der semantischen Sicht, steht in [architecture](architecture.md). Wie die byte-identische Wiederholbarkeit geprueft und garantiert wird, steht in [testing](testing.md).

## Was das Tool nicht leistet

vault-graph ist ein reines Lese- und Analysewerkzeug. Es schreibt nie in den Vault, jede Ausgabe ist ein separates Artefakt, ueber das der Operator entscheidet.

Es trifft keine Wert-, Soll- oder Empfehlungs-Aussagen, keine inhaltlichen Aussagen ueber den Text eines Dokuments und keine kausalen Erklaerungen. Die Grenze verlaeuft an den drei Aussagetypen oben, alles jenseits von Befund, Diagnose und Hypothese liegt ausserhalb der Berechtigung des Tools.

Die volle Triangulation aus drei Achsen ist noch nicht geschlossen. Der semantische Scout ist als Code gebaut, offen ist der Modell-Lauf, der seine Nachbarschaften gegen den lebenden Vault einfriert. Solange dieser Freeze aussteht, bleibt ein topologischer Cluster ohne semantische Stuetzung eine Hypothese, kein Befund.

## Quellen

Blondel, V. D., Guillaume, J.-L., Lambiotte, R., Lefebvre, E. (2008). Fast unfolding of communities in large networks. *J. Stat. Mech.*

Newman, M. E. J. (2006). Modularity and community structure in networks. *PNAS* 103(23).

Danon, L., Diaz-Guilera, A., Duch, J., Arenas, A. (2005). Comparing community structure identification. *J. Stat. Mech.*

Denzin, N. K. (1978). *The Research Act.* McGraw-Hill. Referenz fuer die Triangulations-Position.

Munafo, M. R. et al. (2017). A manifesto for reproducible science. *Nature Human Behaviour* 1.
