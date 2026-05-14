"""CLI-Einstiegspunkt. Orchestriert die vier Phasen.

Ausführung:
    python -m vault_graph

Konfiguration als Modul-Konstanten unten. Anpassbar ohne config-Datei,
solange das Repo persönlich genutzt wird.
"""

from pathlib import Path

# --- Konfiguration -----------------------------------------------------------

VAULT_PATH = Path(r"c:\Users\Chrisi\Documents\obsidian")
OUTPUT_DIR = Path(__file__).parent.parent / "output"

EXCLUDE_FOLDERS = {"_archive"}

# Privacy-Default: strikt. Business-Knoten werden anonymisiert,
# Volltexte aus Angebote-Ordner werden nicht in Embeddings einbezogen.
PRIVACY_STRICT = True

# Schwellwerte (siehe knowledge/methodik-triangulation.md für Begründung)
JACCARD_THRESHOLD = 0.6
BETWEENNESS_ZSCORE_THRESHOLD = 1.5
LOUVAIN_RESOLUTION = 1.0
LOUVAIN_RANDOM_SEED = 42

# Embedding-Modell (siehe METHODIK.md)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# --- Phasen-Orchestrierung ---------------------------------------------------


def main() -> None:
    """Vier Phasen: Parse → Analyze (3 Sichten) → Triangulate → Render."""
    raise NotImplementedError(
        "Commit 1: nur Modul-Gerüst. Implementation folgt in Commits 2-6."
    )


if __name__ == "__main__":
    main()
