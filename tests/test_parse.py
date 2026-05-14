"""Korrektheits-Tests fuer die Parse-Phase.

Fokus: drei methodisch tragende Aspekte.

1. Wikilink-Extraktion — wenn die Regex falsch ist, ist jeder spaetere Befund
   (Topologie, Triangulation, Findings) auf Sand gebaut.
2. Privacy-Filter — sicherheitskritisch fuer die Vault-Regel "kein absolutes
   Detailwissen". Ein Bug macht das Tool methodisch unbrauchbar.
3. Alias-Aufloesung — wenn Aliase nicht greifen, wird die dead_links-Liste
   aufgeblaeht und Konvergenz kuenstlich geschwaecht.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vault_graph.parse import (
    extract_wikilinks,
    parse_vault,
    write_graph_json,
)


# --- Wikilink-Extraktion ----------------------------------------------------


class TestWikilinkExtraction:
    def test_plain_link(self):
        assert extract_wikilinks("siehe [[Doc]]") == ["Doc"]

    def test_link_with_alias(self):
        assert extract_wikilinks("siehe [[Doc|Anzeigename]]") == ["Doc"]

    def test_link_with_heading(self):
        assert extract_wikilinks("siehe [[Doc#Heading]]") == ["Doc"]

    def test_link_with_heading_and_alias(self):
        assert extract_wikilinks("siehe [[Doc#Heading|Anzeige]]") == ["Doc"]

    def test_multiple_links_one_line(self):
        text = "[[A]] und [[B|alias]] und [[C#h]]"
        assert extract_wikilinks(text) == ["A", "B", "C"]

    def test_link_with_path_segment_kept_raw(self):
        # Wikilinks koennen Pfadsegmente enthalten. Die Aufloesung auf das
        # Stem-Segment passiert in _resolve_target, nicht in extract_wikilinks.
        assert extract_wikilinks("[[folder/Doc]]") == ["folder/Doc"]

    def test_link_with_special_chars(self):
        # Umlaute, Bindestriche, Klammern im Doc-Namen
        assert extract_wikilinks("[[Übersicht über X-Tools]]") == [
            "Übersicht über X-Tools"
        ]

    def test_code_fence_links_ignored(self):
        text = """
Normale [[Echt-Link]] hier.

```python
# [[Code-Link]] soll ignoriert werden
text = "[[Auch-im-Code]]"
```

Wieder normal [[Zweiter-Link]].
"""
        result = extract_wikilinks(text)
        assert "Echt-Link" in result
        assert "Zweiter-Link" in result
        assert "Code-Link" not in result
        assert "Auch-im-Code" not in result

    def test_inline_code_links_ignored(self):
        text = "Normaler [[Link]] und `[[Code-Inline]]` im Inline-Code."
        result = extract_wikilinks(text)
        assert "Link" in result
        assert "Code-Inline" not in result

    def test_no_match_on_single_brackets(self):
        # [Doc] ist Markdown-Link, kein Wikilink
        assert extract_wikilinks("[nicht ein wikilink]") == []
        assert extract_wikilinks("[Markdown-Link](url)") == []

    def test_empty_string(self):
        assert extract_wikilinks("") == []

    def test_whitespace_in_target_trimmed(self):
        # Obsidian erlaubt Leerzeichen am Anfang/Ende des Targets nicht streng,
        # aber wir sollten sie defensiv strippen.
        assert extract_wikilinks("[[ Doc ]]") == ["Doc"]

    def test_unclosed_link_ignored(self):
        assert extract_wikilinks("[[unvollstaendig") == []
        assert extract_wikilinks("unvollstaendig]]") == []

    def test_newline_in_target_rejected(self):
        # Wikilinks ueber Zeilenumbruch sind in Obsidian keine Wikilinks
        assert extract_wikilinks("[[Erste\nZeile]]") == []


# --- Privacy-Filter ---------------------------------------------------------


class TestPrivacyFilter:
    @pytest.fixture
    def fake_vault(self, tmp_path: Path) -> Path:
        """Erzeugt einen Mini-Vault mit einem Business-Angebot, einem
        normalen Projekt-Knoten und einem Knoten, der das Angebot verlinkt."""
        (tmp_path / "Business" / "Angebote").mkdir(parents=True)
        (tmp_path / "Projects").mkdir()

        angebot = tmp_path / "Business" / "Angebote" / "Kunde X - Angebot.md"
        angebot.write_text(
            "---\n"
            "type: knowledge\n"
            "invoice: offen\n"
            "summary: Geheime Zusammenfassung\n"
            "tags: [business]\n"
            "aliases: [\"Geheim-Alias\"]\n"
            "---\n"
            "\n"
            "# Kunde X - Angebot\n"
            "\n"
            "Geheimer Body-Text mit Details und Preisen.\n"
            "Verweis auf [[Projekt A]].\n",
            encoding="utf-8",
        )

        projekt = tmp_path / "Projects" / "Projekt A.md"
        projekt.write_text(
            "---\ntype: knowledge\ntags: [project]\n---\n"
            "# Projekt A\n\nReferenz: [[Kunde X - Angebot]]\n",
            encoding="utf-8",
        )

        return tmp_path

    def test_business_node_title_anonymized(self, fake_vault: Path):
        graph = parse_vault(fake_vault, exclude=set(), privacy_strict=True)
        node = graph.nodes["Kunde X - Angebot"]
        assert node["title"].startswith("Angebot-")
        assert "Kunde X" not in node["title"]
        assert node["title"] != "Kunde X - Angebot"

    def test_business_node_body_stripped(self, fake_vault: Path):
        graph = parse_vault(fake_vault, exclude=set(), privacy_strict=True)
        node = graph.nodes["Kunde X - Angebot"]
        assert node["body_preview"] == ""

    def test_business_node_sensitive_frontmatter_removed(self, fake_vault: Path):
        graph = parse_vault(fake_vault, exclude=set(), privacy_strict=True)
        node = graph.nodes["Kunde X - Angebot"]
        assert "invoice" not in node["frontmatter"]
        assert "summary" not in node["frontmatter"]
        # Neutrale Felder bleiben
        assert node["frontmatter"].get("type") == "knowledge"

    def test_business_node_aliases_stripped(self, fake_vault: Path):
        # Aliase eines Business-Knotens duerfen nicht zur Aufloesung beitragen
        graph = parse_vault(fake_vault, exclude=set(), privacy_strict=True)
        node = graph.nodes["Kunde X - Angebot"]
        assert node["aliases"] == []

    def test_business_node_marked_anonymized(self, fake_vault: Path):
        graph = parse_vault(fake_vault, exclude=set(), privacy_strict=True)
        node = graph.nodes["Kunde X - Angebot"]
        assert node["privacy_anonymized"] is True

    def test_non_business_node_untouched(self, fake_vault: Path):
        graph = parse_vault(fake_vault, exclude=set(), privacy_strict=True)
        node = graph.nodes["Projekt A"]
        assert node["title"] == "Projekt A"
        assert "Projekt A" in node["body_preview"]
        assert node["privacy_anonymized"] is False

    def test_topology_preserved_under_anonymization(self, fake_vault: Path):
        # Kritischer methodischer Punkt: anonymisierte Knoten verlieren Inhalt,
        # bleiben aber topologisch und pragmatisch sichtbar (max 2/3 Sichten).
        graph = parse_vault(fake_vault, exclude=set(), privacy_strict=True)
        assert graph.has_edge("Projekt A", "Kunde X - Angebot")
        assert graph.has_edge("Kunde X - Angebot", "Projekt A")

    def test_serialized_json_contains_no_secret(self, fake_vault: Path, tmp_path: Path):
        # Ende-zu-Ende: nichts aus dem Business-Knoten leakt im persistierten
        # JSON. Das betrifft Body, sensitive Frontmatter, Aliase, aber auch
        # den urspruenglichen Dateinamen ("Kunde X") in key/path/edges.
        graph = parse_vault(fake_vault, exclude=set(), privacy_strict=True)
        out = tmp_path / "graph.json"
        write_graph_json(graph, out)
        text = out.read_text(encoding="utf-8")
        assert "Geheime Zusammenfassung" not in text
        assert "Geheim-Alias" not in text
        assert "Geheimer Body-Text" not in text
        assert "Details und Preisen" not in text
        assert "Kunde X" not in text


# --- Alias-Aufloesung -------------------------------------------------------


class TestAliasResolution:
    @pytest.fixture
    def alias_vault(self, tmp_path: Path) -> Path:
        """Knoten A traegt Alias 'Querbegriff', Knoten B verlinkt auf
        [[Querbegriff]], Knoten C verlinkt direkt auf [[A]]. Beide sollen
        bei A ankommen."""
        (tmp_path / "A.md").write_text(
            "---\ntype: knowledge\naliases: [\"Querbegriff\", \"QB\"]\n---\n"
            "# A\n\nInhalt.\n",
            encoding="utf-8",
        )
        (tmp_path / "B.md").write_text(
            "---\ntype: knowledge\n---\n# B\n\nSiehe [[Querbegriff]].\n",
            encoding="utf-8",
        )
        (tmp_path / "C.md").write_text(
            "---\ntype: knowledge\n---\n# C\n\nSiehe [[A]].\n",
            encoding="utf-8",
        )
        return tmp_path

    def test_alias_link_resolves_to_canonical_node(self, alias_vault: Path):
        graph = parse_vault(alias_vault, exclude=set(), privacy_strict=False)
        assert graph.has_edge("B", "A")
        assert not graph.has_node("Querbegriff")

    def test_canonical_link_resolves(self, alias_vault: Path):
        graph = parse_vault(alias_vault, exclude=set(), privacy_strict=False)
        assert graph.has_edge("C", "A")

    def test_unresolvable_link_becomes_dead_link(self, tmp_path: Path):
        (tmp_path / "X.md").write_text(
            "---\ntype: knowledge\n---\n# X\n\nSiehe [[NichtVorhanden]].\n",
            encoding="utf-8",
        )
        graph = parse_vault(tmp_path, exclude=set(), privacy_strict=False)
        dead = graph.graph["dead_links"]
        assert any(d["from"] == "X" and d["to"] == "NichtVorhanden" for d in dead)
        assert not graph.has_node("NichtVorhanden")

    def test_alias_case_insensitive(self, alias_vault: Path):
        # Obsidian behandelt Wikilink-Targets case-insensitiv. Wir auch.
        (alias_vault / "D.md").write_text(
            "---\ntype: knowledge\n---\n# D\n\nSiehe [[querbegriff]].\n",
            encoding="utf-8",
        )
        graph = parse_vault(alias_vault, exclude=set(), privacy_strict=False)
        assert graph.has_edge("D", "A")

    def test_multiple_aliases_per_node(self, alias_vault: Path):
        # Knoten A hat zwei Aliase: 'Querbegriff' und 'QB'. Beide aufloesbar.
        (alias_vault / "E.md").write_text(
            "---\ntype: knowledge\n---\n# E\n\nSiehe [[QB]].\n",
            encoding="utf-8",
        )
        graph = parse_vault(alias_vault, exclude=set(), privacy_strict=False)
        assert graph.has_edge("E", "A")
