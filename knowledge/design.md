---
title: Design
project:
  name: vault-graph
  repository: https://github.com/chpollin/vault-graph
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
status: complete
created: 2026-06-21
updated: 2026-06-30
version: 1.0
language: de
related: [specification, plan, methodik]
template:
  name: Vorlage Design
  version: 0.1
  url: https://dhcraft.org/Promptotyping/promptotyping-document/design
---

# Design

Die Gestalt der gebauten Werkbank explorer.html (Phase A). Das Interface ist umgesetzt und im Browser gesichtet, dieses Dokument beschreibt es deklarativ im Praesens. Plan und Meilensteine stehen in [plan](plan.md), die epistemische Bedeutung der Aussagetypen in [methodik](methodik.md).

## Leitbild

Der Graph ist die Buehne, alles andere ist Apparat darum herum. Im Ruhezustand ist die Flaeche ruhig und zeigt Struktur, nicht Datenfuelle. Information erscheint auf Anforderung, durch Auswahl eines Knotens oder einer Linse, nicht alle gleichzeitig. Die methodische Sprache ist kein erklaertes Etikett, sondern ein durchgehendes visuelles System, dieselben Akzente tragen ueberall dieselbe Bedeutung. Aesthetik heisst hier nicht Dekoration, sondern dass Wichtiges gross und ruhig steht und Beiwerk klein und zurueckgenommen.

## Layout

Die Flaechenumkehr traegt das Layout. Der Graph ist die Hauptflaeche, Tabelle und Detail sind Begleiter, die sich aus der Graph-Auswahl speisen.

```
+---------------------------------------------------------------+
|  vault-graph        [Struktur] [Pflege] [Wachstum]   n=...    |  schmale Kopfleiste, eine Linsenwahl
+--------+--------------------------------------------+---------+
|        |                                            |         |
| Linse  |                                            | Detail  |
| Filter |              G R A P H                      | zum     |
| (rail) |          (Hauptflaeche, ruhig)              | aus-    |
|        |                                            | gewaehl |
|        |                                            | ten     |
|        |                                            | Knoten  |
+--------+--------------------------------------------+---------+
|  Begleittabelle, eingeklappt, oeffnet auf Wunsch oder Auswahl |
+---------------------------------------------------------------+
```

Die linke Leiste traegt die aktive Linse und die Filter, schmal und sekundaer. Die rechte Detailschublade ist im Ruhezustand leer oder eingeklappt und oeffnet bei Knoten-Auswahl mit Massen, Nachbarn, Tags und dem Obsidian-Sprung. Die Tabelle liegt unter dem Graphen und ist eingeklappt, sie ist nicht die Buehne, sondern ein aufklappbarer Begleiter, der der Graph-Auswahl folgt.

## Visuelle Hierarchie und Textreduktion

Die Statuszeile ist in drei benannte Gruppen gefasst, Struktur, Pflege und Triangulation, statt einer undifferenzierten Reihe gleichrangiger Zahlen. Die Gruppen stehen sekundaer und ruhig, nicht als Wand im Vordergrund.

Die Tabelle zeigt im Ruhezustand drei tragende Spalten, Titel, Community und ein Leitmass. Der Rest liegt hinter einer Aufklapp-Option, redundante Masse verschwinden aus der Standardansicht.

## Aussagetyp-Farbsystem

Die drei Aussagetypen (siehe [methodik](methodik.md)) sind ein durchgehendes Farbsystem mit fester Zuordnung. Befund blau, Diagnose orange, Hypothese violett. Anonymisierte Knoten tragen einen rot gestrichelten Ring, der visuelle Code fuer den anonymisierten Sonderfall, dessen Begruendung in [methodik](methodik.md) steht. Die Farbe erscheint als Knotenring im Graphen und als Punkt in der Tabelle, derselbe Akzent traegt ueberall dieselbe Bedeutung.

Knoten tragen zwei Farbachsen zugleich. Die Community liegt als gedaempfte Fuellung, der Aussagetyp als kraeftiger Ring. Diese Trennung ist eine bewusste Entscheidung gegenueber dem fruehen Vorschlag, damit der Ruhezustand Struktur zeigt und der methodische Status zugleich lesbar bleibt. Die Legende erklaert beide Achsen ausdruecklich, Fuellung gleich Community und im Graphen als benannte Region hinterlegt, Ring gleich Aussagetyp.

## Der Graph

Kanten liegen im Ruhezustand aus und erscheinen erst bei Knoten-Auswahl. Damit verschwindet der Hairball, und der Ruhezustand zeigt Community-Struktur statt eines Kantenknaeuels. Die Knotenpositionen sind ueber eine geseedete Zufallsquelle der Simulation stabil, derselbe Vault-Stand fuehrt zu denselben Positionen, sodass die raeumliche Orientierung ueber Laeufe erhalten bleibt.

Hub-Labels machen die wichtigsten Knoten dauerhaft lesbar, die Top-Knoten nach PageRank sind beschriftet, der Rest erscheint ab einer Zoomschwelle, bei Auswahl das Ego-Netz. Je Community liegt eine blasse Convex Hull als Region hinter den Knoten, beschriftet mit ihrem dominanten Ordner, sodass aus der reinen Fuellfarbe eine benennbare Region wird. Damit die Hulls als Regionen tragen, treibt eine Cluster-Kraft die Knoten, forceX und forceY je Community-Anker auf einem Ring statt forceCenter, sodass sich die Communities raeumlich trennen statt zu einem Ball zu ueberlappen, und der Zoom haengt an einer eigenen Viewport-Gruppe statt an allen Ebenen.

Drei Linsen legen je eine Frage ueber dieselbe Karte. Struktur zeigt Communities, Bruecken und Hubs. Pflege hebt die Diagnose hervor, das Dock zeigt die Triage. Wachstum ist das Geruest fuer die semantische Schicht, im Phase-A-Stand noch leer und so benannt.

Ein ehrlicher Nebenbefund, der Ordner Projects erscheint dreimal als Region-Label, weil er topologisch in drei Link-Communities zerfaellt. Das ist die Triangulations-Aussage selbst, kein Fehler, die aus den Links berechneten Gruppen decken sich hier nicht mit der gelebten Ablage.

## Offene Gestaltungsentscheidungen

- Die genauen Farbwerte der drei Aussagetyp-Akzente und der gedaempften Community-Fuellung.
- Ob Filter, Sortierung und Auswahl ueber einen Reload erhalten bleiben (Zustandsspeicher im Browser).
- Ob die schlichte zweite Graph-Seite topology.html erhalten bleibt oder mit dem Vollbild-Graphen entfaellt, eine getrennte Scope-Frage.
