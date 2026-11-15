# scripts/explore_schema.py — jetable, juste pour VOIR la donnée
from collections import Counter
from datasets import load_dataset

ds = load_dataset("lmms-lab/DocVQA", "DocVQA", split="validation", streaming=True)

# 1) Qu'y a-t-il DANS un exemple ? (la question qui débloque tout)
first = next(iter(ds))
print("=== CLÉS DISPONIBLES ===")
print(list(first.keys()))
print("\n=== VALEURS DU 1er EXEMPLE ===")
for k, v in first.items():
    if k != "image":
        print(f"  {k} = {v!r}")

# 2) Y a-t-il plusieurs pages par source, ou une seule ?
src = Counter()
doc = Counter()
for i, ex in enumerate(ds):
    if i >= 300:
        break
    src[ex.get("ucsf_document_id")] += 1   # None si la clé n'existe pas
    doc[ex.get("docId")] += 1

print("\n=== SUR 300 EXEMPLES ===")
print("sources (ucsf_document_id) distinctes :", len(src))
print("docId distincts                      :", len(doc))