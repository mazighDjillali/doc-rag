# scripts/pull_samples.py  — plumbing to get 10 pages on disk. Public dataset, no login needed.
from pathlib import Path
from datasets import load_dataset

out = Path("data/raw"); out.mkdir(parents=True, exist_ok=True)
ds = load_dataset("lmms-lab/DocVQA", "DocVQA", split="validation", streaming=True)

with open("data/raw/questions.txt", "w", encoding="utf-8") as f:
    for i, ex in enumerate(ds):
        if i >= 300:
            break
        ex["image"].save(out / f"sample_{i:02d}.png")      # ex["image"] is a PIL image
        f.write(f"sample_{i:02d}  Q: {ex['question']}  A: {ex['answers']}\n")
        print(f"saved sample_{i:02d}.png")