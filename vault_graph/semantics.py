"""Phase 2 (Schicht 1) — Semantischer Scout.

Bettet jede Notiz lokal ein und findet je Knoten die top-k inhaltlich naechsten
Notizen ueber Cosinus-Aehnlichkeit. Daraus ein Diagnose-Report latenter
Verknuepfungen: hochaehnliche Paare ohne direkten Wikilink.

Methodische Einordnung (siehe METHODIK.md): die Aehnlichkeit ist ein billiger,
vollstaendiger Kandidaten-Generator, kein Befund. Jedes gemeldete Paar ist eine
Hypothese, die menschlich zu bestaetigen ist.

Determinismus-Trennung. Die Schichtlogik (Aufbau der Dokumente, Top-k, Schwelle,
Ausschluss verlinkter Paare, Privacy-Filter) ist deterministisch und ueber eine
injizierbare Embedding-Funktion mit Dummy-Vektoren testbar. Der eigentliche
Modell-Lauf ist nicht Teil des Determinismus-Tests, sein Ergebnis
(similarity.json) ist ein eingefrorenes Artefakt mit fixierter Modellversion und
fixiertem Seed.

Privacy. Anonymisierte Business-Knoten werden nie eingebettet und tauchen weder
als Knoten noch als Nachbar in similarity.json auf. Der Rohtext verlaesst den
Rechner nicht, das Modell laeuft lokal.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import frontmatter
import networkx as nx
import numpy as np

EmbedFn = Callable[[list[str]], "np.ndarray"]

DEFAULT_MODEL = "intfloat/multilingual-e5-large"
DEFAULT_TOP_K = 8
DEFAULT_THRESHOLD = 0.80
COSINE_DECIMALS = 4


def gather_documents(graph: nx.DiGraph, vault_path: Path) -> list[tuple[str, str]]:
    """Sammelt je nicht-anonymisiertem Knoten den einzubettenden Text.

    Liest den Volltext frisch von der Platte (graph.json fuehrt nur den Preview),
    Titel vorangestellt. Anonymisierte Business-Knoten werden uebersprungen, ihr
    Rohtext wird nie gelesen. Rueckgabe nach Knoten-Key sortiert (Determinismus).
    """
    vault_path = Path(vault_path)
    docs: list[tuple[str, str]] = []
    for key in sorted(graph.nodes):
        attrs = graph.nodes[key]
        if attrs.get("privacy_anonymized"):
            continue
        rel = attrs.get("path", "")
        body = _read_body(vault_path / rel)
        title = attrs.get("title", key)
        text = f"{title}\n\n{body}".strip()
        docs.append((key, text))
    return docs


def compute_similarity(
    graph: nx.DiGraph,
    vault_path: Path,
    embed_fn: EmbedFn,
    *,
    top_k: int = DEFAULT_TOP_K,
    threshold: float = DEFAULT_THRESHOLD,
    model_name: str = "injected",
    seed: int = 42,
) -> dict[str, Any]:
    """Berechnet je Knoten die top-k semantischen Nachbarn und die latenten
    Verknuepfungen.

    Args:
        graph: der geparste Linkgraph, liefert Knoten, Pfade und Link-Distanzen
        vault_path: Wurzel des Vaults, fuer das frische Einlesen der Volltexte
        embed_fn: Funktion list[str] -> ndarray (n, d). Injizierbar fuer Tests,
            in Produktion das lokale Modell (default_embed_fn)
        top_k: Zahl der gelisteten Nachbarn je Knoten
        threshold: Cosinus-Mindestwert fuer eine latente Verknuepfung
        model_name: Provenienz-Marker, der in similarity.json landet
        seed: Provenienz-Marker fuer den Modell-Lauf

    Returns:
        Dict mit Provenienz, je-Knoten-Nachbarn und der nach Aehnlichkeit
        sortierten Liste latenter Verknuepfungen. Vollstaendig deterministisch
        bei deterministischer embed_fn.
    """
    docs = gather_documents(graph, vault_path)
    keys = [k for k, _ in docs]
    texts = [t for _, t in docs]
    n = len(keys)
    n_anon = sum(
        1 for _, a in graph.nodes(data=True) if a.get("privacy_anonymized")
    )

    if n == 0:
        return _empty_result(model_name, seed, top_k, threshold, 0, n_anon)

    unit, dim = _unit_vectors(embed_fn, texts)
    sim = unit @ unit.T

    undirected = graph.to_undirected()
    dist_from = {k: nx.single_source_shortest_path_length(undirected, k) for k in keys}

    nodes_out: list[dict[str, Any]] = []
    latent: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()

    for i, key in enumerate(keys):
        row = sim[i]
        ranked = sorted(
            (
                (round(float(row[j]), COSINE_DECIMALS), other)
                for j, other in enumerate(keys)
                if j != i
            ),
            key=lambda pair: (-pair[0], pair[1]),
        )

        neighbors = [
            {
                "key": other,
                "cosine": cosine,
                "link_distance": dist_from[key].get(other),
            }
            for cosine, other in ranked[:top_k]
        ]
        nodes_out.append({"key": key, "neighbors": neighbors})

        for cosine, other in ranked:
            if cosine < threshold:
                break
            distance = dist_from[key].get(other)
            if distance == 1:
                continue  # bereits direkt verlinkt, keine latente Luecke
            pair = (key, other) if key < other else (other, key)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            latent.append(
                {
                    "a": pair[0],
                    "b": pair[1],
                    "cosine": cosine,
                    "link_distance": distance,
                }
            )

    latent.sort(key=lambda r: (-r["cosine"], r["a"], r["b"]))

    return {
        "model": model_name,
        "seed": seed,
        "top_k": top_k,
        "threshold": threshold,
        "dim": dim,
        "n_embedded": n,
        "n_skipped_anon": n_anon,
        "nodes": nodes_out,
        "latent_links": latent,
    }


def write_similarity_json(result: dict[str, Any], output_path: Path) -> None:
    """Schreibt das eingefrorene Aehnlichkeits-Artefakt als JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def write_latent_links_report(
    result: dict[str, Any], output_path: Path, *, limit: int = 60
) -> None:
    """Schreibt den Diagnose-Report latenter Verknuepfungen als Markdown."""
    latent = result["latent_links"]
    lines = [
        "# Latente Verknuepfungen",
        "",
        "Diagnose-Report des semantischen Scouts (Schicht 1). Hochaehnliche "
        "Notizpaare ohne direkten Wikilink, rangiert nach Cosinus-Aehnlichkeit. "
        "Jede Zeile ist eine Hypothese, kein Befund. Zwei Notizen liegen "
        "inhaltlich nah, sind aber nicht verlinkt, ob die Verbindung traegt, "
        "entscheidet die menschliche Sichtung.",
        "",
        f"Modell {result['model']}, Schwelle {result['threshold']}, top-k "
        f"{result['top_k']}. Eingebettet {result['n_embedded']} Knoten, "
        f"anonymisierte Business-Knoten ausgenommen ({result['n_skipped_anon']}).",
        "",
    ]

    if not latent:
        lines.append("Keine Paare ueber der Schwelle.")
    else:
        shown = min(limit, len(latent))
        lines.append(
            f"Paare ueber der Schwelle {len(latent)}, gezeigt {shown}."
        )
        lines.append("")
        lines.append("| Notiz A | Notiz B | Cosinus | Link-Distanz |")
        lines.append("|---|---|---|---|")
        for row in latent[:limit]:
            distance = row["link_distance"]
            dist_label = "getrennt" if distance is None else str(distance)
            lines.append(
                f"| {row['a']} | {row['b']} | {row['cosine']:.4f} | {dist_label} |"
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def default_embed_fn(model_name: str = DEFAULT_MODEL) -> EmbedFn:
    """Liefert die Embedding-Funktion des lokalen Modells.

    sentence-transformers und torch werden erst beim Aufruf importiert (lazy),
    damit Kern und Tests ohne das schwere Paket lauffaehig bleiben. Das Modell
    laeuft lokal, der Rohtext verlaesst den Rechner nicht.
    """

    def _embed(texts: list[str]) -> "np.ndarray":
        model = _load_model(model_name)
        # e5-Modelle erwarten ein Prefix, fuer symmetrische Aehnlichkeit
        # durchgaengig "passage:" verwenden.
        prefixed = [f"passage: {t}" for t in texts]
        emb = model.encode(
            prefixed,
            normalize_embeddings=True,
            batch_size=16,
            show_progress_bar=False,
        )
        return np.asarray(emb, dtype=np.float64)

    return _embed


# --- intern ------------------------------------------------------------------


_MODEL_CACHE: dict[str, Any] = {}


def _load_model(model_name: str) -> Any:
    if model_name not in _MODEL_CACHE:
        from sentence_transformers import SentenceTransformer  # lazy, schwer

        _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
    return _MODEL_CACHE[model_name]


def _read_body(path: Path) -> str:
    """Liest den Notiz-Body frisch, ohne Frontmatter. Faellt auf Rohtext zurueck,
    wenn das Frontmatter-Parsing scheitert."""
    try:
        post = frontmatter.load(path)
        return post.content or ""
    except Exception:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""


def _unit_vectors(embed_fn: EmbedFn, texts: list[str]) -> tuple["np.ndarray", int]:
    """Bettet die Texte ein und normiert auf Einheitslaenge. Null-Vektoren
    bleiben Null (Cosinus 0 statt nan)."""
    vecs = np.asarray(embed_fn(texts), dtype=np.float64)
    if vecs.ndim != 2 or vecs.shape[0] != len(texts):
        raise ValueError(
            f"embed_fn muss (n, d) liefern, n={len(texts)}, bekam {vecs.shape}"
        )
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vecs / norms, int(vecs.shape[1])


def _empty_result(
    model_name: str,
    seed: int,
    top_k: int,
    threshold: float,
    dim: int,
    n_anon: int,
) -> dict[str, Any]:
    return {
        "model": model_name,
        "seed": seed,
        "top_k": top_k,
        "threshold": threshold,
        "dim": dim,
        "n_embedded": 0,
        "n_skipped_anon": n_anon,
        "nodes": [],
        "latent_links": [],
    }


def main() -> None:
    """Echter Modell-Lauf gegen den lebenden Vault, friert similarity.json und
    den Diagnose-Report ein. Ausserhalb des Determinismus-Tests."""
    from vault_graph.parse import parse_vault

    vault_path = Path(r"c:\Users\Chrisi\Documents\obsidian")
    output_dir = Path(__file__).parent.parent / "output"
    model_name = DEFAULT_MODEL
    seed = 42

    print(f"vault-graph: semantics parse {vault_path}")
    graph = parse_vault(vault_path, exclude={"_archive"}, privacy_strict=True)

    print(f"vault-graph: embed (model={model_name}) und top-{DEFAULT_TOP_K}")
    result = compute_similarity(
        graph,
        vault_path,
        default_embed_fn(model_name),
        model_name=model_name,
        seed=seed,
    )

    similarity_path = output_dir / "data" / "similarity.json"
    write_similarity_json(result, similarity_path)
    report_path = output_dir / "findings" / "latente-verknuepfungen.md"
    write_latent_links_report(result, report_path)

    print(
        f"  embedded={result['n_embedded']}"
        f" skipped_anon={result['n_skipped_anon']}"
        f" latent_links={len(result['latent_links'])}"
        f" dim={result['dim']}"
    )
    print(f"  -> {similarity_path}")
    print(f"  -> {report_path}")


if __name__ == "__main__":
    main()
