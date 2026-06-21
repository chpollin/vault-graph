# vault-graph Lane-Journal

Gedaechtnis der Lane fuer den Wiedereinstieg ohne Gespraechskontext. Knapp, je Runde ein Eintrag, neueste oben. Der kanonische Wissensstand bleibt projektwissen.md, das Journal haelt nur den Verlauf und die Entscheidungs-Provenienz.

## 2026-06-21, Portfolio-Runde, Browser-Sichtung und B-Schaerfung

Ausgangslage. Branch session/pflegesignal-vault-2026-06-20, synchron mit origin, Variante A und Triangulation committet (HEAD vor der Runde 2b0e0f8).

Geleistet. Frischer Pipeline-Lauf gegen den lebenden Vault, deterministisch verifiziert (graph.json und explorer.html byte-identisch ueber zwei Laeufe, Hashes geprueft). Testsuite gruen. explorer.html im Browser gesichtet ueber einen lokalen http.server, weil file-URLs in der Extension auf https umgeschrieben werden und 127.0.0.1 nicht freigegeben war, localhost lief. Screenshot-Spur fuer Befundtabelle, Knotenselektion und Pflege-Triage. Headless im DOM verifiziert, referentielle Integritaet (keine haengenden Kanten nach Aufloesung der D3-Objektreferenzen, ein scheinbarer Befund war nur die In-place-Mutation von edge.source durch die Force-Simulation), Privacy (anonymisierte Knoten ohne Inhalts-Metadaten, nicht in der Triage), Stats-Deckung, Facetten-Filter konsistent mit der Graph-Dimmung. Obsidian-Sprung pro Knoten geprueft, Schema und Vault-Parameter korrekt, file gleich vault-relativer Pfad ohne Endung, Unterordner-Pfade sauber, anonymisierte Knoten mit deaktiviertem Sprung.

Neu geschrieben. knowledge/variante-b-schreibterritorium.md, entscheidungsreife Vorlage fuer die Variante-B-Frage mit dem Territorium gegen die obsidian-vault-Lane und dem minimalen kollisionsfreien Zuschnitt B1. projektwissen.md um den geleisteten Funktionstest und den B-Verweis ergaenzt.

Offen, Operator. Go oder No-Go fuer Variante B und, falls Go, die Stufe (B1 ist der einzige disjunkte Schnitt). Merge nach main bleibt gegated.

Verfahren gelernt. Browser-Sichtung lokaler HTML laeuft ueber localhost, nicht file und nicht 127.0.0.1. JS-Rueckgaben mit Query-String-artigen URIs werden vom Harness geblockt, daher strukturelle Boolean-Checks statt roher URI-Strings. D3 mutiert edge.source und edge.target nach Simulationsstart zu Knotenobjekten, Integritaetschecks muessen das aufloesen.
