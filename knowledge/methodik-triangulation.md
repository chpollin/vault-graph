# Triangulation

Operationalisierung der Konvergenz und Divergenz der drei Sichten. Schwellwerte mit Begründung.

## Begriff

Triangulation bezeichnet in der Sozialforschung (Denzin 1978) die Anwendung mehrerer methodisch unabhängiger Verfahren auf dieselbe Frage. Konvergenz unabhängiger Verfahren ist epistemisch stärker als ein einzelner Befund.

Für die Identifikation von Wissensnetzwerken bedeutet das: keine einzelne Methode ist allein autoritativ. Erst die Kreuzung der drei Methoden liefert belastbare Aussagen.

## Voraussetzung — methodische Unabhängigkeit

| Sicht | Datengrundlage | Algorithmus | Was sie ignoriert |
|---|---|---|---|
| Topologisch | Wikilinks (Kanten) | Louvain | Texte, Frontmatter |
| Semantisch | Body-Text (erste 500 Zeichen + Titel) | HDBSCAN auf Embeddings | Links, Frontmatter |
| Pragmatisch | MOC-Mitgliedschaft, Tags, Ordner | Mengenoperationen | Texte, direkte Links |

Die drei Verfahren sehen jeweils einen anderen Aspekt desselben Vaults. Übereinstimmung ist nicht Artefakt eines geteilten Inputs.

## Operationalisierung der Konvergenz

Jede Sicht liefert eine Partitionierung der Knoten.

### Paarweise Konvergenz

Für jedes Sicht-Paar:

1. **Adjusted Mutual Information (AMI)** als Globalmaß. AMI=0 ist Zufalls-Übereinstimmung, AMI=1 ist perfekte Übereinstimmung. AMI > 0.3 wird als substanzielle Übereinstimmung interpretiert.
2. **Pro Cluster**: stärkste Überlappung über Jaccard-Index.

### Cluster-Level-Konvergenz

Ein **identifiziertes Wissensnetzwerk** ist ein Cluster, der in mindestens zwei Sichten erscheint und paarweise Jaccard-Übereinstimmung ≥ 0.6 aufweist.

**Begründung des 60%-Schwellwerts:**

- Unter 0.5: Überlappung schwächer als "Hälfte der Mitglieder stimmt überein" — zu unsicher
- 0.5 bis 0.6: Überlappung kann zufälligen Ursprung haben
- 0.6 bis 0.8: substanzielle Übereinstimmung mit Raum für Querkonzept-Randabweichungen
- Über 0.8: zu strikt für reale Vaults

Schwellwert ist im Code als Konstante hinterlegt. Jede Änderung muss in METHODIK.md begründet werden.

### Dreifach-Konvergenz

Ein **robust identifiziertes Wissensnetzwerk** liegt vor, wenn ein Cluster in allen drei Sichten erscheint und jeweils paarweise mindestens 60% Übereinstimmung aufweist.

## Operationalisierung der Divergenz

Divergenzen sind nicht Fehler, sondern eigenständige Befunde. Vier systematisch relevante Typen:

### Typ A — Topologie ohne Semantik

Knoten sind verlinkt, sprechen aber nicht sprachlich ähnlich.

Mögliche Erklärungen: Workflow-Links, genealogische Links, Kontrast-Links.

Diagnostischer Wert: Wikilinks im Vault erfüllen verschiedene Funktionen jenseits inhaltlicher Nähe.

### Typ B — Semantik ohne Topologie

Knoten sind sprachlich nah, aber nicht verlinkt.

Wahrscheinliche Erklärung: Linking-Lücke.

Diagnostischer Wert: konkreter Linking-Vorschlag, in `pflegeschulden.md` nach Ähnlichkeit absteigend ausgegeben.

### Typ C — Pragmatik ohne Topologie/Semantik

Ein MOC sammelt Knoten, die weder verlinkt noch sprachlich verwandt sind.

Mögliche Erklärungen: MOC veraltet oder bewusst heterogen (z.B. "alle Projekte einer Förderlinie").

Diagnostischer Wert: MOC-Pflege-Vorschlag oder Erklärung der Heterogenität.

### Typ D — Topologie + Semantik ohne Pragmatik

Ein Cluster ist topologisch und semantisch klar, aber kein MOC adressiert ihn.

Wahrscheinliche Erklärung: emergentes Wissensnetzwerk ohne expliziten Hub.

Diagnostischer Wert: Kandidat für einen neuen Cluster-MOC.

## Brückenknoten

Querkonzepte verhalten sich anders als Cluster-Mitglieder. Sie sind per Definition in mehreren Clustern aktiv.

Operationalisierung:

- **Topologisch**: hohe Betweenness bei moderater Degree (Z-Score ≥ 1.5)
- **Semantisch**: Knoten-Embedding nahe an mehreren Cluster-Zentroiden (Distanzen zu Top-3-Zentroiden ähnlich)
- **Pragmatisch**: in mehreren MOCs als Mitglied oder zentraler Verweis

Ein Knoten wird als **Querkonzept** identifiziert, wenn mindestens zwei der drei Bedingungen erfüllt sind.

Das Ergebnis ist eine datengetriebene Anker-Liste in `findings/querkonzepte.md`, jeweils mit den drei Maßen als Begründung.

## Wann die Triangulation versagt

- **Sehr kleine Cluster** (< 5 Knoten): statistisch instabil
- **MOC-armes Subnetz**: Triangulation reduziert sich auf Topologie + Semantik, Aussagen mit explizitem Hinweis
- **Anonymisierte Knoten** (Business-Bereich): keine semantische Sicht, Aussagen mit 2/3-Marker
- **Sehr neue Knoten**: nur in semantischer Sicht, als Hypothese markiert

Das Tool macht solche Einschränkungen sichtbar, statt sie zu glätten.

## Anti-Fallstrick — Triangulation ist nicht Mehrheit

Wenn nur eine Sicht einen Knoten zu Cluster A zuordnet und zwei zu Cluster B, ist Cluster B nicht automatisch korrekt. Was zählt, ist die paarweise Konvergenz zwischen *unabhängigen* Methoden.

Praktisch: Topologie und Pragmatik konvergent ist stark (zwei unterschiedliche Daten-Aspekte). Tags und MOCs konvergent ist schwach (beide Selbst-Deklarationen, nicht methodisch unabhängig).

Das Tool berechnet Konvergenz nur zwischen den drei Sichten, nicht zwischen Sub-Methoden derselben Sicht.

## Quellen

Denzin, N. K. (1978). *The research act.* McGraw-Hill.

Vinh, N. X., Epps, J., Bailey, J. (2010). *Information theoretic measures for clusterings comparison.* JMLR 11.

Newman, M. E. J. (2006). *Modularity and community structure in networks.* PNAS 103(23).

Traag, V. A., Waltman, L., van Eck, N. J. (2019). *From Louvain to Leiden.* Scientific Reports 9.
