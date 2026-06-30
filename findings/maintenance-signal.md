# Pflegesignal Vault aus vault-graph

Read-only Diagnose des Vault-Linkgraphen, erzeugt vom Tool vault-graph (Analysecode unveraendert seit Tool-Commit 2b0e0f8) gegen den lebenden Vault am 2026-06-21. Snapshot, deterministisch regenerierbar mit python -m vault_graph. Dies ist ein Pflegesignal fuer die Vault-Lane, kein Auftrag und keine Wertung. Was davon bearbeitet wird, entscheidet die Vault-Lane.

Methodische Einordnung. Tote Links und Orphans sind Diagnosen, also datengestuetzte Pflege-Auffaelligkeiten, keine Befunde ueber Inhalt und keine Soll-Aussagen. Ein toter Link ist ein Wikilink, dessen Zielnotiz nicht existiert.

## Globaler Stand

Knoten 718, Kanten 6145, 14 Louvain-Communities, Modularity 0.502, 3 Brueckenknoten, hoechster K-Core 12, MOCs 60, anonymisierte Knoten 4.

Die Tote-Link- und Orphan-Diagnose unten ist gegenueber dem Lauf vom 2026-06-20 stabil (145 tote Links in 53 Quellknoten, identische Top-Quellen, dieselben 4 Orphans). Der Vault ist leicht gewachsen, das Pflegebild der Linkhygiene blieb unveraendert.

## Tote Links (145)

145 tote Links verteilt auf 53 Quellknoten. Die Konzentration liegt bei wenigen Dokumenten, eine Reparatur dort raeumt den groessten Teil ab. Quellknoten mit den meisten toten Links:

| tote Links | Quellknoten |
|---|---|
| 22 | Wissensdokument PF 4.4 Tag 3 Forschungsinfrastruktur |
| 21 | HOME |
| 13 | Wissensdokument PF 4.4 Tag 2 Forschungsinfrastruktur |
| 8 | DHCraft Blog Drafts |
| 7 | teiCrafter |
| 4 | Visual Analytics und Human-AI-Interaction |
| 4 | Skriptum VU 7a.4.1 KI in Bibliotheken |
| 4 | Data Steward Graz Hub |
| 3 | Project Overview M³GIM |
| 3 | FemPrompt-SozArb MOC |
| 3 | VetMedAI Promptotyping und KI-Kompetenzaufbau |
| 3 | Workshop-Ausarbeitung |

## Orphans (4)

Knoten ohne ein- und ausgehende Wikilinks. Zu trennen sind echte Wissens-Orphans von generierten Vorlagen, die bewusst unverlinkt bleiben.

- Programmieren 2.0 Inhalte, type knowledge, tags ['coding', 'context-engineering', 'museum']
- T-Lane-Knowledge-Doc, type kein type, tags keine tags
- T-Literature, type kein type, tags keine tags
- T-Specification, type kein type, tags keine tags

Einordnung. Drei der vier Orphans sind Vorlagen in Vault Operations/Templates/ (T-Lane-Knowledge-Doc, T-Literature, T-Specification) ohne Frontmatter, erwartbar unverlinkt. Der einzige echte Wissens-Orphan ist Programmieren 2.0 Inhalte (type knowledge), ein Anbinde-Kandidat fuer die Vault-Lane.
