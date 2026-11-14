from datasets import load_dataset
ds = load_dataset("lmms-lab/DocVQA", "DocVQA", split="validation", streaming=True)
for i, ex in enumerate(ds):
    if i >= 10: break
    ex["image"].save(f"data/raw/sample_{i:02d}.png")   # a PIL image
    print(i, "Q:", ex["question"], "| A:", ex.get("answers"))