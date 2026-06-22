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
# Latente Verknuepfung ueber gegenseitige k-naechste Nachbarn (mutual kNN), nicht
# ueber eine absolute Cosinus-Schwelle. Transformer-Embeddings sind anisotrop, ihr
# Cosinus traegt einen hohen Grundwert (bei e5-large liegen selbst die naechsten
# Nachbarn im Median bei rund 0.9), eine absolute Schwelle flutet die Diagnose
# oder verfehlt sie. Das Rangkriterium ist anisotropie-robust. Der Floor schliesst
# nur schwache Paare in duennen Regionen aus.
DEFAULT_MIN_COSINE = 0.0
LATENT_CRITERION = "mutual-knn"
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


def embed_documents(
    graph: nx.DiGraph,
    vault_path: Path,
    embed_fn: EmbedFn,
) -> tuple[list[str], "np.ndarray"]:
    """Bettet jede nicht-anonymisierte Notiz ein und gibt Keys plus
    einheitsnormierte Vektoren zurueck, beide nach Key sortiert.

    Dies ist der teure, nicht-deterministische Schritt (Modell-Lauf). Sein
    Ergebnis ist das einzufrierende Artefakt, getrennt von der billigen,
    deterministischen Analyse-Schicht (analyze_similarity).
    """
    docs = gather_documents(graph, vault_path)
    keys = [k for k, _ in docs]
    texts = [t for _, t in docs]
    if not keys:
        return [], np.zeros((0, 0), dtype=np.float64)
    unit, _dim = _unit_vectors(embed_fn, texts)
    return keys, unit


def analyze_similarity(
    keys: list[str],
    unit: "np.ndarray",
    graph: nx.DiGraph,
    *,
    top_k: int = DEFAULT_TOP_K,
    min_cosine: float = DEFAULT_MIN_COSINE,
    model_name: str = "injected",
    seed: int = 42,
) -> dict[str, Any]:
    """Deterministische Analyse-Schicht ueber vorab eingebetteten Vektoren.

    Bestimmt je Knoten die top-k Cosinus-Nachbarn und die latenten
    Verknuepfungen ueber gegenseitige k-naechste Nachbarn (mutual kNN): ein Paar
    ist latent, wenn beide Notizen einander unter ihren top-k naechsten fuehren,
    nicht direkt verlinkt sind und den Cosinus-Floor halten. Rangbasiert statt
    schwellenbasiert, damit anisotropie-robust.

    Args:
        keys: Knoten-Keys, parallel zu den Zeilen von unit
        unit: einheitsnormierte Embedding-Matrix (n, d)
        graph: der Linkgraph, liefert die Link-Distanzen
        top_k: Zahl der Nachbarn je Knoten und Reichweite des mutual-kNN
        min_cosine: Cosinus-Floor, schliesst schwache Paare in duennen Regionen aus
        model_name, seed: Provenienz-Marker

    Returns:
        Dict mit Provenienz, je-Knoten-Nachbarn und nach Cosinus sortierten
        latenten Verknuepfungen. Deterministisch bei gegebenem keys und unit.
    """
    n_anon = sum(
        1 for _, a in graph.nodes(data=True) if a.get("privacy_anonymized")
    )
    n = len(keys)
    if n == 0:
        return _empty_result(model_name, seed, top_k, min_cosine, 0, n_anon)

    # Determinismus: nach Key sortieren, Vektoren mitziehen.
    order = sorted(range(n), key=lambda i: keys[i])
    keys = [keys[i] for i in order]
    unit = np.asarray(unit, dtype=np.float64)[order]
    dim = int(unit.shape[1])

    sim = unit @ unit.T

    undirected = graph.to_undirected()
    dist_from = {k: nx.single_source_shortest_path_length(undirected, k) for k in keys}

    nodes_out: list[dict[str, Any]] = []
    topk_keys: list[set[str]] = []
    cosine_of: dict[tuple[str, str], float] = {}

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
        top = ranked[:top_k]
        nodes_out.append(
            {
                "key": key,
                "neighbors": [
                    {
                        "key": other,
                        "cosine": cosine,
                        "link_distance": dist_from[key].get(other),
                    }
                    for cosine, other in top
                ],
            }
        )
        topk_keys.append({other for _, other in top})
        for cosine, other in top:
            cosine_of[(key, other)] = cosine

    latent: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()
    for i, key in enumerate(keys):
        for other in topk_keys[i]:
            j = keys.index(other)
            if key not in topk_keys[j]:
                continue  # nicht gegenseitig, kein mutual-kNN-Paar
            pair = (key, other) if key < other else (other, key)
            if pair in seen_pairs:
                continue
            distance = dist_from[key].get(other)
            if distance == 1:
                continue  # bereits direkt verlinkt, keine latente Luecke
            cosine = cosine_of.get((key, other), cosine_of.get((other, key)))
            if cosine < min_cosine:
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
        "criterion": LATENT_CRITERION,
        "top_k": top_k,
        "min_cosine": min_cosine,
        "dim": dim,
        "n_embedded": n,
        "n_skipped_anon": n_anon,
        "nodes": nodes_out,
        "latent_links": latent,
    }


def compute_similarity(
    graph: nx.DiGraph,
    vault_path: Path,
    embed_fn: EmbedFn,
    *,
    top_k: int = DEFAULT_TOP_K,
    min_cosine: float = DEFAULT_MIN_COSINE,
    model_name: str = "injected",
    seed: int = 42,
) -> dict[str, Any]:
    """Bequemer Gesamtlauf, bettet ein und analysiert. Embedding und Analyse sind
    getrennt (embed_documents, analyze_similarity), damit die teure Einbettung
    einmal eingefroren und die Analyse-Schicht beliebig oft billig und
    deterministisch nachgerechnet werden kann."""
    keys, unit = embed_documents(graph, vault_path, embed_fn)
    return analyze_similarity(
        keys, unit, graph, top_k=top_k, min_cosine=min_cosine,
        model_name=model_name, seed=seed,
    )


def save_embeddings(keys: list[str], unit: "np.ndarray", output_path: Path) -> None:
    """Friert die eingebetteten Vektoren ein, damit die Analyse ohne erneuten
    Modell-Lauf nachgerechnet werden kann. Keys als Unicode-Array (kein pickle)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(output_path, keys=np.array(keys), vectors=np.asarray(unit, dtype=np.float64))


def load_embeddings(input_path: Path) -> tuple[list[str], "np.ndarray"]:
    """Laedt eingefrorene Vektoren zur Wiederholung der Analyse-Schicht."""
    data = np.load(input_path)
    return [str(k) for k in data["keys"]], data["vectors"]


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
        "Diagnose-Report des semantischen Scouts (Schicht 1). Notizpaare, die "
        "einander unter ihren naechsten inhaltlichen Nachbarn fuehren (mutual "
        "kNN), aber nicht direkt verlinkt sind, rangiert nach Cosinus-"
        "Aehnlichkeit. Jede Zeile ist eine Hypothese, kein Befund. Zwei Notizen "
        "liegen inhaltlich nah, sind aber nicht verlinkt, ob die Verbindung "
        "traegt, entscheidet die menschliche Sichtung.",
        "",
        f"Modell {result['model']}, Kriterium {result['criterion']}, top-k "
        f"{result['top_k']}, Floor {result['min_cosine']}. Eingebettet "
        f"{result['n_embedded']} Knoten, anonymisierte Business-Knoten "
        f"ausgenommen ({result['n_skipped_anon']}).",
        "",
    ]

    if not latent:
        lines.append("Keine gegenseitig-naechsten Paare ohne Link.")
    else:
        shown = min(limit, len(latent))
        lines.append(
            f"Latente Paare {len(latent)}, gezeigt {shown}."
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
    min_cosine: float,
    dim: int,
    n_anon: int,
) -> dict[str, Any]:
    return {
        "model": model_name,
        "seed": seed,
        "criterion": LATENT_CRITERION,
        "top_k": top_k,
        "min_cosine": min_cosine,
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

    # Embedding-Cache. Die Einbettung ist der teure Schritt, die Analyse billig.
    # Liegt ein Cache vor, nur nachrechnen, sonst frisch einbetten und einfrieren.
    embeddings_path = output_dir / "data" / "embeddings.npz"
    if embeddings_path.exists():
        print(f"vault-graph: lade Embedding-Cache {embeddings_path}")
        keys, unit = load_embeddings(embeddings_path)
    else:
        print(f"vault-graph: embed (model={model_name})")
        keys, unit = embed_documents(graph, vault_path, default_embed_fn(model_name))
        save_embeddings(keys, unit, embeddings_path)
        print(f"  -> {embeddings_path}")

    print(f"vault-graph: analyse top-{DEFAULT_TOP_K}, mutual-kNN")
    result = analyze_similarity(
        keys, unit, graph, model_name=model_name, seed=seed,
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
