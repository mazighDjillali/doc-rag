I had three principle "scary pages"
Sample01 as it contaisn htr 
Sample 08 complex text disposition 
Sample 03 Order.disposition plus Writting relevance (writing relevance is completely dioffetent task then th ocr , so i have to separate them into two different pipelines ) 

---

## Mentor review — 2026-11-14

**Correction (important — fix this):** "two different pipelines" is wrong. It's **one
pipeline, two *stages*.** OCR and relevance are separate *responsibilities*, but they are
sequential components inside the *same* pipeline (OCR → chunk → index → retrieve → answer),
not two parallel pipelines. "Separation of concerns" means one job per *stage*, not one job
per *pipeline*. Rewrite that sentence.

**Good:** you correctly saw that relevance is NOT OCR's job. That instinct is right — keep it.

**Add (you already learned these — just capture them so the artifact is complete):**
- For each page, which quality surface does the failure hit *first*?
  - Sample01 (HTR) → ______
  - Sample08 (reading order) → ______
  - Sample03 (reading order) → ______
- One word of doc type + the specific visual nasty per page.
