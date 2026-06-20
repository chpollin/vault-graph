"""Korrektheits-Tests fuer die Pragmatik- und Triangulationsphase.

Fokus auf die methodisch tragenden Eigenschaften:
- Reinheit und NMI bei deckungsgleicher und bei unabhaengiger Partition
- Ausreisser-Erkennung in einer sonst reinen Community
- Ausschluss anonymisierter Knoten aus der einzeln gelisteten Diagnose
- Tag-Kohaesion
"""

from __future__ import annotations

import networkx as nx
import pytest

from vault_graph.pragmatics import analyze_pragmatics, _nmi


def _node(graph: nx.DiGraph, key: str, folder: str, *, anon=False, tags=None) -> None:
    graph.add_node(
        key,
        title=key,
        path=f"{folder}/{key}.md",
        privacy_anonymized=anon,
        frontmatter={"tags": tags or []},
    )


def _topology(communities: dict[str, int]) -> dict:
    return {"communities": communities}


class TestTriangulation:
    def test_perfect_overlap_is_pure_and_nmi_one(self):
        g = nx.DiGraph()
        for k in ("a1", "a2", "a3"):
            _node(g, k, "FolderA")
        for k in ("b1", "b2", "b3"):
            _node(g, k, "FolderB")
        communities = {"a1": 0, "a2": 0, "a3": 0, "b1": 1, "b2": 1, "b3": 1}

        result = analyze_pragmatics(g, _topology(communities))

        assert result["community_folder"][0]["purity"] == pytest.approx(1.0)
        assert result["community_folder"][1]["purity"] == pytest.approx(1.0)
        assert result["stats"]["nmi_community_folder"] == pytest.approx(1.0)
        assert result["stats"]["n_outliers"] == 0
        assert result["stats"]["mean_community_purity"] == pytest.approx(1.0)

    def test_independent_partitions_have_low_nmi(self):
        g = nx.DiGraph()
        _node(g, "n1", "FolderA")
        _node(g, "n2", "FolderA")
        _node(g, "n3", "FolderB")
        _node(g, "n4", "FolderB")
        # Community orthogonal zur Ordner-Partition
        communities = {"n1": 0, "n2": 1, "n3": 0, "n4": 1}

        result = analyze_pragmatics(g, _topology(communities))

        assert result["stats"]["nmi_community_folder"] == pytest.approx(0.0, abs=1e-9)

    def test_outlier_detected_in_pure_community(self):
        g = nx.DiGraph()
        for k in ("a1", "a2", "a3"):
            _node(g, k, "FolderA")
        _node(g, "x", "FolderB")  # liegt in FolderB, aber in Community A
        communities = {"a1": 0, "a2": 0, "a3": 0, "x": 0}

        result = analyze_pragmatics(g, _topology(communities))

        # Community 0 ist zu 3/4 FolderA, Reinheit 0.75 >= 0.6, x ist Ausreisser
        assert result["stats"]["n_outliers"] == 1
        keys = [o["key"] for o in result["outliers"]]
        assert keys == ["x"]
        assert result["outliers"][0]["community_dominant_folder"] == "FolderA"

    def test_anonymized_node_not_listed_as_outlier(self):
        g = nx.DiGraph()
        for k in ("a1", "a2", "a3"):
            _node(g, k, "FolderA")
        _node(g, "secret", "Business", anon=True)
        communities = {"a1": 0, "a2": 0, "a3": 0, "secret": 0}

        result = analyze_pragmatics(g, _topology(communities))

        # secret liegt in fremdem Ordner, wird aber als anon nicht einzeln gelistet
        assert all(o["key"] != "secret" for o in result["outliers"])
        assert result["stats"]["n_outliers"] == 0

    def test_tag_cohesion_concentration(self):
        g = nx.DiGraph()
        for k in ("a1", "a2", "a3"):
            _node(g, k, "FolderA", tags=["thema"])
        communities = {"a1": 0, "a2": 0, "a3": 0}

        result = analyze_pragmatics(g, _topology(communities), tag_min_count=2)

        assert "thema" in result["tag_cohesion"]
        cohesion = result["tag_cohesion"]["thema"]
        assert cohesion["n_nodes"] == 3
        assert cohesion["concentration"] == pytest.approx(1.0)

    def test_folder_partition_uses_top_segment_only(self):
        g = nx.DiGraph()
        g.add_node(
            "deep",
            title="deep",
            path="Projects/sub/deeper/deep.md",
            privacy_anonymized=False,
            frontmatter={},
        )
        result = analyze_pragmatics(g, _topology({"deep": 0}))
        assert result["folder_of"]["deep"] == "Projects"


class TestNMI:
    def test_nmi_in_unit_interval(self):
        a = {"x": 0, "y": 0, "z": 1, "w": 1}
        b = {"x": "p", "y": "q", "z": "p", "w": "q"}
        value = _nmi(a, b)
        assert 0.0 <= value <= 1.0

    def test_nmi_identical_partitions_is_one(self):
        a = {"x": 0, "y": 0, "z": 1, "w": 1}
        assert _nmi(a, dict(a)) == pytest.approx(1.0)

    def test_nmi_empty_is_zero(self):
        assert _nmi({}, {}) == 0.0
