# RÉFÉRENCE — pour voir le regroupement de tes propres yeux.
from collections import Counter
from datasets import load_dataset

ds = load_dataset("lmms-lab/DocVQA", "DocVQA", split="validation", streaming=True)
c = Counter()
for i, ex in enumerate(ds):
    if i >= 300: break
    c[ex["docId"]] += 1
# combien de pages uniques, et la distribution questions/page
print("pages uniques :", len(c))
print("exemples de comptes :", c.most_common(5))   # tu verras des docId à 2, 3, 5...