"""Invarianten-Tests, die die beiden zentralen Versprechen des Tools maschinell absichern.

Beide Eigenschaften waren bisher nur per Hand geprueft und sind damit gegen
Regression ungeschuetzt, obwohl die ganze Glaubwuerdigkeit des Werkzeugs auf
ihnen ruht.

1. Determinismus. Zweimaliger Lauf der Pipeline gegen denselben Vault-Stand und
   denselben Seed erzeugt byte-identische Ausgaben (graph.json und
   explorer.html). Das ist das erste Erfolgskriterium (METHODIK.md,
   Reproduzierbarkeit). Eine schleichende Regression (eine unsortierte Menge,
   ein einfuegereihenfolgeabhaengiges dict, eine ungeseedete Zufallsquelle)
   wuerde sonst unbemerkt durchrutschen. Geprueft in-process und zusaetzlich
   ueber zwei Subprozesse mit verschiedenem PYTHONHASHSEED, das deckt auch eine
   hash-seed-abhaengige Mengen-Iteration ab.

2. Privacy in der HTML-Ausgabe. Die Anonymisierung der Business-Knoten ist fuer
   graph.json getestet (test_parse.py), aber die Werkbank explorer.html hatte
   keinen Inhaltstest, obwohl der Interface-Umbau genau diese Flaeche aendert.
   Anonymisierte Knoten tragen keine Inhalts-Metadaten, sind aus der
   Pflege-Triage (tote Links, Orphans) ausgenommen und bekommen keinen
   Obsidian-Sprung.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

from vault_graph.parse import parse_vault, write_graph_json
from vault_graph.topology import analyze_topology
from vault_graph.pragmatics import analyze_pragmatics
from vault_graph.explorer import render_explorer_html, _build_payload


# Pipeline-Konstanten wie im CLI (__main__.py). Die Determinismus-Eigenschaft
# haengt nicht an den konkreten Werten, nur an ihrer Konstanz ueber zwei Laeufe.
_TOPO = dict(louvain_resolution=1.0, louvain_seed=42, bridge_z_threshold=1.5)
_PRAG = dict(purity_high=0.7, purity_low=0.5, outlier_min_purity=0.6, tag_min_count=5)

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _build_fixture_vault(root: Path) -> Path:
    """Mini-Vault, gross genug fuer Louvain, Triangulation und die beiden
    Triage-Ausnahmen. Enthaelt zwei anonymisierte Business-Knoten (einer davon
    isoliert, also Orphan), einen toten Link aus einem normalen und einen aus
    einem anonymisierten Knoten, und einen normalen Orphan."""
    _write(
        root / "Business" / "Angebote" / "Kunde X - Angebot.md",
        "---\ntype: knowledge\ninvoice: offen\nsummary: Geheime Zusammenfassung\n"
        'tags: [business]\naliases: ["Geheim-Alias"]\n---\n'
        "# Kunde X - Angebot\n\nGeheimer Body mit Preisen.\n"
        "Verweis [[Projekt A]] und [[Nicht Vorhanden Geheim]].\n",
    )
    _write(
        root / "Business" / "Angebote" / "Isoliertes Angebot.md",
        "---\ntype: knowledge\nsummary: Auch geheim\n---\n"
        "# Isoliertes Angebot\n\nKein Link.\n",
    )
    _write(
        root / "Projects" / "Projekt A.md",
        "---\ntype: knowledge\ntags: [project]\n---\n# Projekt A\n\n"
        "Siehe [[Kunde X - Angebot]], [[Projekt B]], [[Methodik Hub]] und [[Fehlt Hier]].\n",
    )
    _write(
        root / "Projects" / "Projekt B.md",
        "---\ntype: knowledge\ntags: [project]\n---\n# Projekt B\n\n"
        "Siehe [[Projekt A]] und [[Methodik Hub]].\n",
    )
    _write(
        root / "Projects" / "Projekt C.md",
        "---\ntype: knowledge\ntags: [project]\n---\n# Projekt C\n\nSiehe [[Projekt B]].\n",
    )
    _write(
        root / "Methodik Hub.md",
        "---\ntype: vault-organisation\ntags: [hub]\n---\n# Methodik Hub\n\n"
        "Sammelt [[Projekt A]], [[Projekt B]], [[Projekt C]].\n",
    )
    _write(
        root / "Notiz Solo.md",
        "---\ntype: knowledge\n---\n# Notiz Solo\n\nKeine Links, kein Backlink.\n",
    )
    return root


def _run_pipeline(vault: Path, out: Path) -> tuple[bytes, bytes]:
    """Volle Pipeline gegen einen Vault, gibt die Bytes von graph.json und
    explorer.html zurueck."""
    graph = parse_vault(vault, exclude=set(), privacy_strict=True)
    graph_json = out / "graph.json"
    write_graph_json(graph, graph_json)
    topology = analyze_topology(graph, **_TOPO)
    pragmatics = analyze_pragmatics(graph, topology, **_PRAG)
    explorer_html = out / "explorer.html"
    render_explorer_html(graph, topology, pragmatics, explorer_html)
    return graph_json.read_bytes(), explorer_html.read_bytes()


# Runner fuer den Cross-Hash-Seed-Subprozess. Liest einen bereits gebauten Vault
# (argv[1]) und schreibt nach argv[2], damit der in graph.json serialisierte
# vault_path ueber beide Laeufe identisch ist. Druckt die zwei Hashes.
_RUNNER = """
import sys, hashlib
from pathlib import Path
sys.path.insert(0, sys.argv[3])
from tests.test_invariants import _run_pipeline
graph_json, explorer_html = _run_pipeline(Path(sys.argv[1]), Path(sys.argv[2]))
print(hashlib.sha256(graph_json).hexdigest())
print(hashlib.sha256(explorer_html).hexdigest())
"""


class TestDeterminism:
    def test_outputs_byte_identical_in_process(self, tmp_path: Path):
        vault = _build_fixture_vault(tmp_path / "vault")
        gj1, html1 = _run_pipeline(vault, tmp_path / "run1")
        gj2, html2 = _run_pipeline(vault, tmp_path / "run2")
        assert hashlib.sha256(gj1).hexdigest() == hashlib.sha256(gj2).hexdigest()
        assert hashlib.sha256(html1).hexdigest() == hashlib.sha256(html2).hexdigest()

    def test_outputs_byte_identical_across_hash_seeds(self, tmp_path: Path):
        """Zwei Subprozesse mit verschiedenem PYTHONHASHSEED muessen dieselben
        Hashes liefern. Faengt eine hash-seed-abhaengige Mengen-Iteration und
        jede ungeseedete Zufallsquelle, die zwei Prozesse auseinanderlaufen
        liesse."""
        runner = tmp_path / "runner.py"
        runner.write_text(_RUNNER, encoding="utf-8")
        # Ein Vault, beide Laeufe lesen ihn, damit der serialisierte vault_path
        # identisch ist. Geprueft wird die Pipeline, nicht der Ablageort.
        vault = _build_fixture_vault(tmp_path / "vault")

        def run(seed: int, sub: str) -> list[str]:
            out = tmp_path / sub
            out.mkdir()
            env = dict(os.environ, PYTHONHASHSEED=str(seed))
            proc = subprocess.run(
                [sys.executable, str(runner), str(vault), str(out), str(_REPO_ROOT)],
                capture_output=True, text=True, env=env, cwd=str(_REPO_ROOT),
            )
            assert proc.returncode == 0, proc.stderr
            return proc.stdout.strip().splitlines()

        assert run(0, "seed0") == run(1, "seed1")


class TestExplorerPrivacy:
    def _payload(self, tmp_path: Path) -> dict:
        vault = _build_fixture_vault(tmp_path / "vault")
        graph = parse_vault(vault, exclude=set(), privacy_strict=True)
        topology = analyze_topology(graph, **_TOPO)
        pragmatics = analyze_pragmatics(graph, topology, **_PRAG)
        return _build_payload(graph, topology, pragmatics)

    def test_fixture_is_meaningful(self, tmp_path: Path):
        # Stellt sicher, dass die Privacy-Asserts nicht auf leeren Listen laufen.
        p = self._payload(tmp_path)
        assert any(n["anon"] for n in p["nodes"])
        assert any(not n["anon"] for n in p["nodes"])
        assert p["dead_links"]
        assert p["orphans"]

    def test_anon_nodes_carry_no_content_metadata(self, tmp_path: Path):
        p = self._payload(tmp_path)
        anon = [n for n in p["nodes"] if n["anon"]]
        assert anon
        for n in anon:
            assert n["id"].startswith("Angebot-")
            assert n["tags"] == []
            assert n["type"] == ""

    def test_normal_node_keeps_metadata(self, tmp_path: Path):
        p = self._payload(tmp_path)
        a = next(n for n in p["nodes"] if n["id"] == "Projekt A")
        assert a["anon"] is False
        assert a["type"] == "knowledge"
        assert "project" in a["tags"]

    def test_anon_nodes_excluded_from_triage(self, tmp_path: Path):
        p = self._payload(tmp_path)
        # Tote Links aus anonymisierten Quellknoten sind ausgenommen.
        assert all(not d["from"].startswith("Angebot-") for d in p["dead_links"])
        assert all("Geheim" not in d["to"] for d in p["dead_links"])
        # Der tote Link aus dem normalen Knoten bleibt sichtbar.
        assert any(d["from"] == "Projekt A" and d["to"] == "Fehlt Hier" for d in p["dead_links"])
        # Anonymisierte Orphans sind ausgenommen, der normale Orphan bleibt.
        assert all(not o.startswith("Angebot-") for o in p["orphans"])
        assert "Notiz Solo" in p["orphans"]

    def test_rendered_html_leaks_no_secret(self, tmp_path: Path):
        vault = _build_fixture_vault(tmp_path / "vault")
        graph = parse_vault(vault, exclude=set(), privacy_strict=True)
        topology = analyze_topology(graph, **_TOPO)
        pragmatics = analyze_pragmatics(graph, topology, **_PRAG)
        out = tmp_path / "explorer.html"
        render_explorer_html(graph, topology, pragmatics, out)
        text = out.read_text(encoding="utf-8")
        for secret in (
            "Kunde X", "Geheime Zusammenfassung", "Geheim-Alias", "Geheimer Body",
            "mit Preisen", "Isoliertes Angebot", "Auch geheim", "Nicht Vorhanden Geheim",
        ):
            assert secret not in text, secret
        # Anonymisierte Knoten erscheinen topologisch, nur unter Hash-Titel.
        assert "Angebot-" in text
