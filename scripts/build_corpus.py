"""Orchestration de la Phase 1 : construit le manifest du corpus de bout en bout.

ORDRE D'EXÉCUTION (chronologique) :
  1. charger les lignes DocVQA              (1 ligne = 1 question)
  2. build_records   -> regroupe par docId, sauve+hash les images, 1 DocRecord/page (split=None)
                        (sha256_file est appelée À L'INTÉRIEUR de build_records)
  3. assign_splits   -> attribue un split par SOURCE entière (barrière anti-leakage)
  4. save_manifest   -> écrit data/manifest.jsonl

Plus tard, d'autres scripts appelleront load_manifest(...) pour relire ce corpus.
Lancer :  python scripts/build_corpus.py
"""
from pathlib import Path

from datasets import load_dataset

from doc_rag.data.manifest import Split, assign_splits, build_records, save_manifest

# --- paramètres (un seul endroit pour les régler) ---
N_ROWS = 300  # combien de LIGNES (questions) de DocVQA parcourir
IMAGE_DIR = Path("data/raw")
MANIFEST_PATH = Path("data/manifest.jsonl")
SEED = 0
FRACTIONS = {Split.TRAIN: 0.6, Split.DEV: 0.2, Split.TEST: 0.1, Split.UNSEEN_TEMPLATE: 0.1}


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    # ÉTAPE 1 — charger les lignes (niveau QUESTION, pas page)
    ds = load_dataset("lmms-lab/DocVQA", "DocVQA", split="validation", streaming=True)
    examples: list[dict] = []
    # TODO: prendre les N_ROWS premières lignes de `ds` et les mettre dans `examples`.
    #       (rappel : plusieurs lignes partageront le même docId — c'est voulu.)

    # ÉTAPE 2 — lignes -> 1 DocRecord par page (split encore None)
    records = build_records(examples, IMAGE_DIR)

    # ÉTAPE 3 — attribuer les splits par source entière
    records = assign_splits(records, FRACTIONS, seed=SEED)

    # ÉTAPE 4 — persister sur disque
    save_manifest(records, MANIFEST_PATH)
    print(f"{len(records)} pages écrites dans {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
