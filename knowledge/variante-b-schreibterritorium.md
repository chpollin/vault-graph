# Variante B, Schreibterritorium gegen die obsidian-vault-Lane

Entscheidungsreife Vorlage fuer den Operator. Variante A (read-only Werkbank explorer.html) ist gebaut, verifiziert und gegen den lebenden Vault frisch gelaufen. Variante B (kuratorisches Rueckschreiben in den Vault) bleibt gegated. Dieses Dokument schaerft die Frage so weit, dass der Operator sie entscheiden kann, ohne sie hier vorwegzunehmen. Die Scope-Wahl A gegen B trifft der Operator.

## Die Frage

Soll vault-graph seine Pflege-Befunde als Datei in den Vault schreiben, sodass sie in Obsidian sichtbar sind und der Mensch oder die obsidian-vault-Lane sie an Ort und Stelle triagieren kann, oder bleiben die Befunde im vault-graph-Repo und werden von dort konsumiert?

Mit dem Rueckschreiben wird vault-graph vom reinen Messinstrument zum Schreiber im Vault. Genau dort sitzt schon die obsidian-vault-Lane, der Vault-Architekt, dessen Repo der Vault selbst ist. Ohne vorher gezogenes Territorium kollidieren zwei Schreiber auf denselben Dateien. Die Freigabe von B haengt also nicht am Tooling, das Tooling ist trivial, sondern an einer sauberen Territorialgrenze.

## Was die obsidian-vault-Lane schreibt

Verifiziert aus ihrer Registrierung dieser Runde. Die Lane arbeitet auf `main` direkt im Vault und editiert die Steuerdokumente (CLAUDE.md, VAULT-OPERATIONS, ACTIVE-WORK, TAG-TAXONOMY, HOME), die Architektur-Dokumente (Blueprint, Erklaerdokument, Session-Synthese), die Konventionen, die MOCs und die inhaltlichen Atome samt deren Frontmatter. Sie benennt sich selbst als Upstream von vault-graph, jeder ihrer Moves, Renames und Dead-Link-Fixes veraendert flussaufwaerts den Linkgraph, den vault-graph misst.

Ihre kuratorische Arbeit ist genau die Reparatur der Zustaende, die vault-graph diagnostiziert. Sie behebt tote Links, fuehrt Dubletten zusammen, legt Ausreisser um, justiert Tags. vault-graph erkennt diese Zustaende, die obsidian-vault-Lane repariert sie. Beide greifen am selben Problem an, von entgegengesetzten Enden.

## Die Kollision und der saubere Schnitt

Naives B liesse vault-graph in dieselben Atome und dasselbe Frontmatter schreiben, die die obsidian-vault-Lane editiert, auf demselben `main`. Das ist die direkte Datei-Kollision, die order und Projektwissen bereits als Grund fuer das Gate nennen. Zwei Schreiber auf einer Datei erzeugen Merge-Konflikte und, schlimmer, widersprechende Wahrheiten in einem Dokument.

Der Schnitt, der die Kollision aufhebt, trennt Signal von Reparatur. vault-graph besitzt das Signal-Artefakt allein, die obsidian-vault-Lane besitzt jede Reparatur allein. Damit die beiden Schreibmengen disjunkt sind und nicht nur per Absprache getrennt, muss das Signal-Artefakt drei Eigenschaften tragen.

Erstens ein einziger, vault-graph allein gehoeriger Ort. Zweitens maschinell erzeugt und bei jedem Lauf vollstaendig ueberschrieben, nie von Hand editiert, sodass es gar keine geteilte Editierflaeche gibt, auf der ein Konflikt entstehen koennte. Drittens aus Sicht der obsidian-vault-Lane read-only, sie konsumiert und verlinkt es, sie editiert es nie. Wenn vault-graph nur diese eine Datei schreibt und die obsidian-vault-Lane alles ausser dieser Datei, ist die Konfliktflaeche per Konstruktion null.

## Das konkrete Schreibterritorium

Variante B im minimalen, freigebbaren Zuschnitt schreibt genau einen Ort im Vault.

- Ein maschinell erzeugtes Pflegesignal-Dokument, Vorschlag `Vault Operations/Pflegesignale/vault-graph-pflegesignal.md`, allein von vault-graph beschrieben.
- Bei jedem Lauf vollstaendig regeneriert, kein Anhaengen, kein Teil-Edit. Der Inhalt ist die Pflege-Triage, tote Links nach Quellknoten und Orphans, plus die Triangulations-Diagnose (Ausreisser, niedrig-reine Communities).
- Frontmatter weist es als maschinelles Snapshot-Dokument aus, `author: vault-graph-tool`, `type: snapshot` oder das im Vault gefuehrte Aequivalent, ein Generierungsstempel, und eine sichtbare Kopfzeile, die festhaelt, dass die Datei maschinell erzeugt ist, nicht von Hand editiert wird und bei jedem Lauf ueberschrieben wird.
- Verlinkt die betroffenen Atome per Wikilink, sodass der Sprung aus Obsidian direkt zum kaputten Knoten fuehrt, derselbe Mechanismus wie der obsidian-Sprung der Werkbank.
- Privacy laeuft ueber denselben build_key_remap wie graph.json und explorer.html, anonymisierte Business-Knoten erscheinen als Angebot-hash, tote Links und Orphans anonymisierter Knoten bleiben aus dem Signal heraus.

Negatives Territorium, was vault-graph unter B nie schreibt. Keine inhaltlichen Atome, keine MOCs, keine Steuerdokumente, kein Frontmatter einer bestehenden Datei, keine Reparatur eines toten Links, keine Tag-Aenderung, kein Move oder Rename. Diese Menge gehoert ganz der obsidian-vault-Lane. vault-graph liefert das Signal, die Reparatur bleibt in einer Hand.

## Konventions-Auflagen, falls B in den Vault schreibt

Das Pflegesignal-Dokument enthaelt volatile Mengen (Zahl toter Links, Counts pro Quellknoten). CLAUDE.md Paragraph 6 verbietet solche Mengen in Wissens-, Strategie- und Overview-Dokumenten, erlaubt sie aber ausdruecklich in Snapshot- und Session-Dokumenten. Das Dokument muss daher als Snapshot typisiert sein, sonst verletzt es die Vault-Regel beim ersten Lauf. Die Provenienz-Regel (Paragraph 3) verlangt `author`-Marker und, bis zur menschlichen Sichtung, `human-reviewed: false`; bei einem rein maschinellen, staendig ueberschriebenen Artefakt ist stattdessen ein klarer Maschinen-Marker zu setzen und die Datei aus dem human-review-Lauf herauszuhalten. Die Privacy-Regel (Paragraph 7) ist durch den bestehenden Remap erfuellt, muss aber im Vault-Kontext erneut verifiziert werden, weil das Dokument dort fuer Menschen sichtbar wird.

## Drei Ausbaustufen zur Wahl

B0, Status quo, ist die read-only Linie. Die Befunde liegen im vault-graph-Repo (findings/pflegesignal-vault-lane.md), die obsidian-vault-Lane zieht sie von dort. Kein Schreibzugriff auf den Vault. Das ist der Stand nach Variante A.

B1, minimal, ist der oben gezeichnete Zuschnitt. Genau ein maschinell erzeugtes, wholesale ueberschriebenes Pflegesignal-Dokument im Vault, read-only fuer die obsidian-vault-Lane, als Snapshot typisiert, privacy-remapped. Disjunkt zur Lane per Konstruktion. Das ist die natuerliche erste Form von B, falls B genommen wird.

B2, maximal, annotiert das Frontmatter der Atome selbst, etwa ein Feld graph-community oder graph-degree pro Knoten. Das ist genau der Kollisionsfall. Es ist nur tragfaehig mit einer harten Regel, dass die obsidian-vault-Lane diese Felder nie anfasst, und diese Trennung innerhalb einer Datei ist fragil, weil zwei Schreiber dieselbe Datei oeffnen. B2 ist das nicht empfohlene Ende des Spektrums, hier nur benannt, damit die Grenze sichtbar ist.

## Was offen bleibt fuer den Operator

Zwei Entscheidungen. Erstens das Go oder No-Go fuer Variante B insgesamt, also ob vault-graph ueberhaupt in den Vault schreibt. Zweitens, falls Go, welche Stufe, wobei B1 der einzige Zuschnitt ist, der gegen die obsidian-vault-Lane disjunkt steht. Der Merge des Session-Branches nach main bleibt davon unabhaengig operator-gated.

Die Empfehlung dieser Lane beschraenkt sich auf die Territorialgrenze, nicht auf die Scope-Wahl. Wenn B genommen wird, ist B1 der einzige kollisionsfreie Schnitt, und er ist nur kollisionsfrei, solange die drei Eigenschaften (Allein-Besitz, vollstaendige Regeneration, read-only fuer die Lane) zusammen gelten. Faellt eine davon, faellt die Disjunktheit.
