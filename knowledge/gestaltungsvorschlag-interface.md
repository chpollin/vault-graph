# Gestaltungsvorschlag Interface (explorer.html)

Antwort auf das Operator-Feedback der Konsolidierungsrunde, die Werkbank ist zu textlastig, zu unuebersichtlich und aesthetisch noch nicht anspruchsvoll genug. Verlangt sind weniger Text, eine klare visuelle Hierarchie und eine anspruchsvollere Aesthetik. Dies ist der Gestaltungsvorschlag, der laut order vor dem Umbau vorliegen muss. Er ist Entwurf, kein gebautes Interface, und konkret genug zur Sichtung. Grundlage ist die Leitidee aus [plan-zentrale-visualisierung.md](plan-zentrale-visualisierung.md), die Visualisierung als navigierbare Karte. Dieser Vorschlag fuellt davon die Gestaltungsschicht, Layout, Hierarchie, Aesthetik, und ist baulich deckungsgleich mit Phase A des Plans.

## Die drei Schwaechen, auf die der Vorschlag antwortet

Das invertierte Flaechenverhaeltnis. Die Tabelle besetzt die breite Hauptflaeche, der Graph sitzt im schmalen rechten Panel, obwohl der Graph die einzige Flaeche ist, die raeumliche Struktur traegt. Die Werkbank zeigt damit Zahlen gross und Struktur klein.

Die Textwand. Die Statuszeile ist eine undifferenzierte Reihe von elf Kennzahlen ohne Gruppierung, die Tabelle fuehrt sieben numerische Spalten gleichzeitig, davon mehrere redundant, und die methodische Sprache aus Befund, Diagnose und Hypothese ist nur deklariert, nicht durchgaengig sichtbar.

Der Hairball und die flache Aesthetik. Alle Kanten liegen bei voller Deckkraft uebereinander und verdecken genau die Community-Struktur, die der Graph zeigen soll. Die Flaeche wirkt technisch, nicht gestaltet, gleich starke Linien, gleich grosse Zahlen, kein ruhiger Grund.

## Leitbild der Gestaltung

Der Graph ist die Buehne, alles andere ist Apparat darum herum. Im Ruhezustand ist die Flaeche ruhig und zeigt Struktur, nicht Datenfuelle. Information erscheint auf Anforderung, durch Auswahl eines Knotens oder einer Linse, nicht alle gleichzeitig. Die methodische Sprache wird vom erklaerten Etikett zum durchgehenden visuellen System, dieselben drei Akzente tragen ueberall dieselbe Bedeutung. Aesthetik heisst hier nicht Dekoration, sondern dass Wichtiges gross und ruhig steht und Beiwerk klein und zurueckgenommen.

## Layout

Die Flaechenumkehr ist der erste und groesste Hebel. Der Graph wird die Hauptflaeche, Tabelle und Detail werden Begleiter, die sich aus der Graph-Auswahl speisen.

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

Die linke Leiste traegt die aktive Linse und die Filter, schmal und sekundaer. Die rechte Detailschublade ist im Ruhezustand leer oder eingeklappt und oeffnet bei Knoten-Auswahl mit den Massen, Nachbarn, Tags und dem Obsidian-Sprung. Die Tabelle wandert unter den Graphen und ist eingeklappt, sie ist nicht mehr die Buehne, sondern ein aufklappbarer Begleiter, der der Graph-Auswahl folgt.

## Visuelle Hierarchie und Textreduktion

Die Statuszeile wird von elf gleichrangigen Zahlen zu wenigen benannten Gruppen, etwa Struktur (Knoten, Kanten, Communities, Modularitaet), Pflege (tote Links, Orphans) und Triangulation (NMI, Reinheit, Ausreisser). Die Gruppen stehen sekundaer und ruhig, nicht als Wand im Vordergrund.

Die Tabelle zeigt im Ruhezustand zwei bis drei tragende Spalten, Titel, Community und ein Leitmass, der Rest liegt hinter einer Aufklapp-Option. Redundante Masse verschwinden aus der Standardansicht.

Die drei Aussagetypen werden ein durchgehendes Farbsystem. Befund, Diagnose und Hypothese tragen je einen festen Akzent, der im Graphen, in der Tabelle, im Detail und in der Pflege-Linse dieselbe Bedeutung hat. Tote Links, Ausreisser und Bruecken werden so im Graphen erkennbar, nicht nur in einer Liste benannt.

## Aesthetik

Ein ruhiger Grund, damit der Graph liest. Zurueckgenommene Palette, grosszuegiger Weissraum, klare typografische Hierarchie mit wenigen Stufen, Ziffern mit Tabellenziffern fuer ruhige Spalten. Eine zurueckhaltende Grundfarbe fuer die Flaeche und genau drei Aussagetyp-Akzente, die die einzigen kraeftigen Farben sind. Vorschlag fuer den Grund ein sehr helles Neutralgrau wie `#fafafa` mit Linien in `#dddddd`, fuer die drei Akzente ein gedecktes Blau fuer Befund, ein warmes Orange fuer Diagnose wie das bestehende `#b8541d`, und ein zurueckgenommenes Violett oder Gruen fuer Hypothese. Die genauen Werte sind eine offene Gestaltungsentscheidung. Die Community-Einfaerbung der Knoten wird durch Form oder Helligkeit gestuetzt, weil vierzehn Farben allein kaum unterscheidbar sind.

## Der Graph selbst

Kanten im Ruhezustand ausgeblendet, erst bei Knoten-Auswahl gezeigt, der Hervorhebungspfad existiert im Code bereits. Damit verschwindet der Hairball, und die Community-Struktur wird im Ruhezustand sichtbar. Stabiles deterministisches Layout, gleicher Vault-Stand fuehrt zu gleichen Positionen, sodass die raeumliche Orientierung ueber Laeufe erhalten bleibt. Die Knoten tragen die Aussagetyp-Farben, ein toter-Link-Quellknoten oder ein Ausreisser ist im Graphen erkennbar. Die drei Linsen, Struktur, Pflege, Wachstum, sind das zentrale Steuerelement, jede legt eine Frage ueber dieselbe Karte.

## Was bewusst nicht in diesem Schritt liegt

Keine semantische Schicht. Embedding-Aehnlichkeit und getypte Relationen kommen ab Phase B des Plans und sind hier nicht enthalten, die Wachstums-Linse bleibt vorerst ein leeres Geruest. Keine neue Abhaengigkeit. Kein Abschaffen der zweiten Graph-Seite topology.html, das ist eine eigene Scope-Entscheidung und beruehrt diesen Vorschlag nicht. Der Umbau bleibt im bestehenden deterministischen Rahmen.

## Offene Gestaltungsentscheidungen

- Vollbild-Umschalter fuer den Graphen gegen ein festes Drei-Spalten-Layout.
- Die genauen Farbwerte der drei Aussagetyp-Akzente.
- Ob Filter, Sortierung und Auswahl ueber einen Reload erhalten bleiben (Zustandsspeicher im Browser).
- Ob die schlichte zweite Graph-Seite topology.html erhalten bleibt oder mit dem Vollbild-Graphen entfaellt, getrennte Scope-Frage.

## Bezug zu Phase A und zum Plan

Dieser Vorschlag ist die Gestaltungsschicht von Phase A aus [plan-zentrale-visualisierung.md](plan-zentrale-visualisierung.md). Bei Freigabe baut Phase A genau dieses Layout, Flaechenumkehr, Kanten bei Auswahl, Linsen-Geruest, stabile Positionen, Aussagetyp-Farben, gruppierte Statuszeile, eingedampfte Tabelle. Erst die Freigabe dieses Vorschlags loest den Bau aus.
