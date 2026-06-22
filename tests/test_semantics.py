"""Korrektheits- und Invarianten-Tests fuer den semantischen Scout.

Zwei Ebenen. Die Analyse-Schicht (analyze_similarity) wird mit handgesetzten
Vektoren direkt geprueft, ohne Einbettung, so ist das mutual-kNN-Kriterium
vollstaendig kontrolliert. Die Integration (compute_similarity ueber einen
Fixture-Vault) prueft Privacy und Determinismus mit einer injizierten
Embedding-Funktion ueber Themen-Marker.

Geprueft:
- mutual-kNN, eine latente Verknuepfung ist ein gegenseitig-naechstes Paar ohne
  direkten Wikilink. Ein nur einseitig naechstes Paar wird nicht gemeldet, ein
  direkt verlinktes nicht.
- Determinismus, similarity.json byte-identisch ueber zwei Laeufe bei fester
  injizierter Embedding-Funktion (Gruen-Kriterium der order).
- Privacy, anonymisierte Business-Knoten werden nie eingebettet und erscheinen
  weder als Knoten noch als Nachbar im Artefakt, ihr Geheimtext leakt nicht.
- Embedding-Cache, save/load der Vektoren reproduziert die Analyse exakt.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import networkx as nx
import numpy as np

from vault_graph.parse import parse_vault
from vault_graph.semantics import (
    analyze_similarity,
    compute_similarity,
    embed_documents,
    gather_documents,
    load_embeddings,
    save_embeddings,
    write_similarity_json,
)


# Themen-Marker steuern die Dummy-Vektoren. Gleicher Marker, gleicher Vektor,
# also Cosinus 1.0. So ist jede Aehnlichkeit im Test bewusst gesetzt.
_THEMES = {
    "THEMA_BLAU": np.array([1.0, 0.0, 0.0]),
    "THEMA_GRUEN": np.array([0.0, 1.0, 0.0]),
    "THEMA_ROT": np.array([0.0, 0.0, 1.0]),
}


def _marker_embed(texts: list[str]) -> np.ndarray:
    """Deterministische Embedding-Funktion: ein Marker im Text waehlt den Vektor,
    sonst ein neutraler vierter Basisvektor. Haengt nur am Textinhalt, also
    stabil ueber Laeufe und Hash-Seeds."""
    out = []
    for text in texts:
        vec = np.array([0.0, 0.0, 0.0, 1.0])
        for marker, base in _THEMES.items():
            if marker in text:
                vec = np.concatenate([base, [0.0]])
                break
        out.append(vec)
    return np.asarray(out, dtype=np.float64)


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _build_fixture_vault(root: Path) -> Path:
    """Mini-Vault mit kontrollierten Themen.

    Alpha und Beta teilen THEMA_BLAU, sind aber nicht verlinkt, das ist die
    latente Verknuepfung. Gamma und Delta teilen THEMA_GRUEN und sind direkt
    verlinkt, also keine latente Luecke. Der anonymisierte Business-Knoten traegt
    ebenfalls THEMA_BLAU, darf aber nie eingebettet werden und nie auftauchen.
    """
    _write(
        root / "Alpha.md",
        "---\ntype: knowledge\n---\n# Alpha\n\nText zu THEMA_BLAU ohne Link.\n",
    )
    _write(
        root / "Beta.md",
        "---\ntype: knowledge\n---\n# Beta\n\nAuch THEMA_BLAU, nicht zu Alpha verlinkt.\n",
    )
    _write(
        root / "Gamma.md",
        "---\ntype: knowledge\n---\n# Gamma\n\nText zu THEMA_GRUEN, siehe [[Delta]].\n",
    )
    _write(
        root / "Delta.md",
        "---\ntype: knowledge\n---\n# Delta\n\nText zu THEMA_GRUEN, siehe [[Gamma]].\n",
    )
    _write(
        root / "Solo.md",
        "---\ntype: knowledge\n---\n# Solo\n\nText zu THEMA_ROT, allein.\n",
    )
    _write(
        root / "Business" / "Angebote" / "Kunde Geheim - Angebot.md",
        "---\ntype: knowledge\nsummary: Geheim\n---\n"
        "# Kunde Geheim - Angebot\n\nGeheimer Text zu THEMA_BLAU mit Preisen.\n",
    )
    return root


def _result(tmp_path: Path, **kwargs) -> dict:
    vault = _build_fixture_vault(tmp_path / "vault")
    graph = parse_vault(vault, exclude=set(), privacy_strict=True)
    return compute_similarity(graph, vault, _marker_embed, **kwargs)


class TestMutualKNN:
    """Analyse-Schicht direkt, mit gradierten Winkel-Vektoren, damit
    Asymmetrie entsteht und das Gegenseitigkeits-Kriterium pruefbar wird."""

    def _setup(self):
        keys = ["A", "B", "C", "D"]
        ang = np.deg2rad([0.0, 5.0, 50.0, 90.0])
        unit = np.column_stack([np.cos(ang), np.sin(ang)])
        g = nx.DiGraph()
        for k in keys:
            g.add_node(k, privacy_anonymized=False, path=f"{k}.md")
        return keys, unit, g

    def _pairs(self, result):
        return {(r["a"], r["b"]) for r in result["latent_links"]}

    def test_mutual_pairs_latent_asymmetric_excluded(self):
        keys, unit, g = self._setup()
        result = analyze_similarity(keys, unit, g, top_k=2, min_cosine=0.0)
        pairs = self._pairs(result)
        # A-B, B-C, C-D sind gegenseitig naechste Paare.
        assert ("A", "B") in pairs
        assert ("B", "C") in pairs
        assert ("C", "D") in pairs
        # A-C und B-D sind nur einseitig naechst, also kein mutual-kNN-Paar.
        assert ("A", "C") not in pairs
        assert ("B", "D") not in pairs

    def test_directly_linked_mutual_pair_excluded(self):
        keys, unit, g = self._setup()
        g.add_edge("A", "B")  # nun direkt verlinkt
        result = analyze_similarity(keys, unit, g, top_k=2, min_cosine=0.0)
        pairs = self._pairs(result)
        assert ("A", "B") not in pairs
        assert ("B", "C") in pairs

    def test_floor_excludes_weak_pairs(self):
        keys, unit, g = self._setup()
        # Floor oberhalb von C-D (cos40 ~ 0.766) schliesst dieses Paar aus.
        result = analyze_similarity(keys, unit, g, top_k=2, min_cosine=0.8)
        pairs = self._pairs(result)
        assert ("A", "B") in pairs  # cos5 ~ 0.996
        assert ("C", "D") not in pairs


class TestIntegration:
    def test_top_k_respected(self, tmp_path: Path):
        result = _result(tmp_path, top_k=2)
        for node in result["nodes"]:
            assert len(node["neighbors"]) <= 2

    def test_same_theme_unlinked_is_latent(self, tmp_path: Path):
        result = _result(tmp_path, min_cosine=0.5)
        pairs = {(r["a"], r["b"]) for r in result["latent_links"]}
        assert ("Alpha", "Beta") in pairs

    def test_latent_pair_carries_cosine_and_distance(self, tmp_path: Path):
        result = _result(tmp_path, min_cosine=0.5)
        ab = next(r for r in result["latent_links"] if (r["a"], r["b"]) == ("Alpha", "Beta"))
        assert ab["cosine"] == 1.0
        assert ab["link_distance"] is None  # getrennte Komponenten

    def test_directly_linked_pair_not_latent(self, tmp_path: Path):
        result = _result(tmp_path, min_cosine=0.5)
        pairs = {(r["a"], r["b"]) for r in result["latent_links"]}
        assert ("Delta", "Gamma") not in pairs
        assert ("Gamma", "Delta") not in pairs

    def test_neighbors_sorted_by_descending_cosine(self, tmp_path: Path):
        result = _result(tmp_path, top_k=8)
        for node in result["nodes"]:
            cosines = [n["cosine"] for n in node["neighbors"]]
            assert cosines == sorted(cosines, reverse=True)

    def test_criterion_recorded(self, tmp_path: Path):
        result = _result(tmp_path)
        assert result["criterion"] == "mutual-knn"


class TestPrivacy:
    def test_anon_node_not_embedded(self, tmp_path: Path):
        vault = _build_fixture_vault(tmp_path / "vault")
        graph = parse_vault(vault, exclude=set(), privacy_strict=True)
        docs = gather_documents(graph, vault)
        keys = {k for k, _ in docs}
        assert "Kunde Geheim - Angebot" not in keys
        assert all("Geheim" not in text for _, text in docs)

    def test_anon_absent_from_artifact(self, tmp_path: Path):
        result = _result(tmp_path)
        assert result["n_skipped_anon"] == 1
        node_keys = {n["key"] for n in result["nodes"]}
        assert all("Geheim" not in k and not k.startswith("Angebot-") for k in node_keys)
        for node in result["nodes"]:
            for neighbor in node["neighbors"]:
                assert "Geheim" not in neighbor["key"]
                assert not neighbor["key"].startswith("Angebot-")
        for link in result["latent_links"]:
            assert "Geheim" not in link["a"] and "Geheim" not in link["b"]

    def test_secret_text_not_in_serialized_artifact(self, tmp_path: Path):
        result = _result(tmp_path)
        out = tmp_path / "similarity.json"
        write_similarity_json(result, out)
        text = out.read_text(encoding="utf-8")
        for secret in ("Geheim", "mit Preisen", "Angebot-"):
            assert secret not in text, secret


class TestDeterminism:
    def test_artifact_byte_identical_over_two_runs(self, tmp_path: Path):
        result1 = _result(tmp_path, top_k=4, min_cosine=0.5)
        result2 = _result(tmp_path, top_k=4, min_cosine=0.5)
        out1 = tmp_path / "sim1.json"
        out2 = tmp_path / "sim2.json"
        write_similarity_json(result1, out1)
        write_similarity_json(result2, out2)
        h1 = hashlib.sha256(out1.read_bytes()).hexdigest()
        h2 = hashlib.sha256(out2.read_bytes()).hexdigest()
        assert h1 == h2

    def test_empty_graph_is_handled(self, tmp_path: Path):
        empty = nx.DiGraph()
        result = compute_similarity(empty, tmp_path, _marker_embed)
        assert result["n_embedded"] == 0
        assert result["nodes"] == []
        assert result["latent_links"] == []


class TestEmbeddingCache:
    def test_save_load_reproduces_analysis(self, tmp_path: Path):
        vault = _build_fixture_vault(tmp_path / "vault")
        graph = parse_vault(vault, exclude=set(), privacy_strict=True)
        keys, unit = embed_documents(graph, vault, _marker_embed)
        cache = tmp_path / "embeddings.npz"
        save_embeddings(keys, unit, cache)
        keys2, unit2 = load_embeddings(cache)
        assert keys2 == keys
        r1 = analyze_similarity(keys, unit, graph, min_cosine=0.5)
        r2 = analyze_similarity(keys2, unit2, graph, min_cosine=0.5)
        out1, out2 = tmp_path / "a.json", tmp_path / "b.json"
        write_similarity_json(r1, out1)
        write_similarity_json(r2, out2)
        assert out1.read_bytes() == out2.read_bytes()
