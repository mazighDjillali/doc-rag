# Project ledger — doc-rag

A RAG application that answers questions over a corpus of **scanned** documents, where OCR is the
ingest layer that turns page images into retrievable text. Update this file at the end of every
session. It is the memory of the project — for you, for me, and for whoever reads the repo in six
months (including an interviewer).

## Charter

*Filled in Phase 0 (2026-11-14), revisited at every phase gate.*

- **Problem in one sentence:** Given a corpus of scanned document images, answer natural-language
  questions about them with a cited answer, using OCR → retrieval → LLM.
- **Document types and volumes:** DocVQA family (scanned real-world documents — letters, forms,
  tables, reports, invoices, handwritten notes). Start on a small slice (hundreds of pages); the
  full DocVQA set is ~12k images / ~50k questions.
- **Languages / scripts:** English, Latin script only. (Deliberately avoids the RTL/mixed-script
  complexity — one less variable while learning.)
- **Output contract:** For each question → an answer string **plus a citation** (which document /
  page the answer came from). Citations are a hard requirement: a RAG answer with no source is a
  guess.
- **Quality surfaces (TWO, not one):**
  - *OCR quality* — CER / WER against ground-truth text.
  - *RAG quality* — retrieval recall@k, and answer correctness. DocVQA's official answer metric is
    **ANLS** (Average Normalized Levenshtein Similarity) — not exact match. Learn why before Phase 2.
- **Business / success metric and target:** TBD — set *after* the Phase 2 baseline produces a real
  number. Do not invent a target before we have a baseline.
- **Cost of a wrong answer:** In this (portfolio/public-data) context the failure that matters most
  is a **confident wrong answer with a citation that doesn't support it** — that's the trust-killer
  we design the eval around.
- **Latency / throughput target:** Interactive query. Local 7–8B LLM will be the slow part; p95
  target TBD after we measure the baseline.
- **Hard constraints:**
  - Hardware: single machine — RTX 4060 **8GB** VRAM, 32GB DDR5, 1TB SSD. Kaggle (free T4 16GB,
    ~30h/week) available as a *lab* for heavy/batch jobs, **not** for serving.
  - Hosting: local-first (Ollama + 7–8B 4-bit), designed swappable so a cloud API is a config swap.
    See ADR-001.
  - Time: ~10 focused hours/week. No hard deadline.
- **Learner profile:** Mid-level across ML / software engineering / infrastructure. **Primary goal:
  strengthen coding.** → Mentor weights toward SWE rigor (typed contracts, tests, clean swappable
  interfaces, the service layer) while keeping ML/eval honest.

## Current state

| | |
|---|---|
| Phase | 1 · Data foundation (in progress) — `build_records` done, split policy next |
| Last session | Session 2 — 2026-11-15 |
| OCR quality (CER/WER, locked test) | — not measured yet |
| RAG answer accuracy (ANLS, locked test) | — not measured yet |
| Retrieval recall@k | — not measured yet |
| p95 query latency | — not measured yet |
| Test set opened N times | 0 |

## Decisions made

| Date | Decision | ADR | Revisit trigger |
|---|---|---|---|
| 2026-11-14 | Corpus = DocVQA family (built-in Q/A eval) | — | If a different corpus becomes necessary for the portfolio story |
| 2026-11-14 | Hosting = local-first, LLM behind a swappable interface (provisional) | ADR-001 (to be written in Phase 3) | Local answer accuracy on DocVQA eval trails cloud by a margin that matters, measured |

## Session log

### Session 1 — 2026-11-14
- **Built:** Project scaffold, charter, paper trail (ADR template, experiment log, .gitignore).
- **Measured:** nothing yet (correct for Phase 0).
- **Broke / learned:** Hardware reality — 8GB VRAM is workable because OCR (ingest) and LLM
  (serve) never run simultaneously; Kaggle is the lab, not the product.
- **Concepts covered:** transcription vs. KIE vs. question-answering; the two quality surfaces of an
  OCR+RAG system; why corpus choice is driven by the availability of an eval set; CER/WER (edit
  distance, S/I/D, reference-length denominator); WER harsher than CER; normalization as a *choice*
  applied identically to both sides; one pipeline / many stages (not parallel pipelines); template
  leakage and template-disjoint splitting.
- **Teach-back grade:** correct ✓, precise ✓ (used the vocabulary unprompted), grounded ✓. Trade-off
  awareness not yet tested. CER/WER drill computed correctly by hand.
- **Corpus notes:** docs/corpus-notes.md written; 3 scary pages identified (HTR, reading order ×2).
  Misconception caught & corrected: "two pipelines" → one pipeline, many stages.
- **Next target (Phase 1):** Pull a larger slice (~200 docs), build a corpus **manifest** (stable id,
  file hash, source/template id, split) and decide a **template-disjoint split policy** with one
  template held out as an unseen-layout slice.

### Session 2 — 2026-11-15
- **Built:** `scripts/explore_schema.py` (data inspection); `build_records()` implemented and
  **passing** `tests/test_build_records.py` (accumulator pattern, `replace` on the frozen dataclass,
  boundary casts `docId` int→str and `page_no` str→int); `requirements.txt`.
- **Measured (on 300 val questions):** DocVQA schema confirmed — `ucsf_document_id` exists and is
  populated, so the split design rests on a real field. 85 distinct `docId` → **~3.5 questions/page**
  (why a question-level split leaks). 85 `docId` collapse to 64 `ucsf_document_id` → source-grouping
  buys ~1.3× over docId-disjoint (≈25% of pages belong to a multi-page source).
- **Broke / learned:** Hit the real wall — translating a spec into code felt "flou". Taught the
  3-step bridge (énoncé → plain-French micro-steps → one code line each → trace variables by hand).
  Clarified honest naming: our split is **source-disjoint**, a *proxy* for template-disjoint (no
  template labels in DocVQA), so `UNSEEN_TEMPLATE` is really "unseen document".
- **Concepts covered:** lazy/streaming iterables & generators; dict-accumulator pattern; frozen
  dataclass + `dataclasses.replace`; type-checking at external boundaries; ANLS mechanism relearned
  (normalized Levenshtein + 0.5 threshold; it ignores citation support → harness needs a separate
  citation metric); exploration code vs production code.
- **Teach-back grade:** not formally run; `build_records` correct and tested.
- **Next target:** implement `assign_splits` (leakage-prevention core) to green its failing test
  (no `source_id` in two splits; deterministic under seed); then `save_manifest`/`load_manifest`;
  then build the real ~200-page slice. Still open from Phase 0: pick the success-metric target.

## Review queue

Concepts to re-test in warm-ups. Retire after two clean recalls.

- [ ] Why is a random train/test split wrong for a document corpus? (template leakage)
- [ ] What is ANLS and why does DocVQA use it instead of exact match?
- [ ] Why can 8GB VRAM serve this pipeline? (ingest/serve staging)

## Parked

Ideas deliberately deferred, with the condition that would revive them.

- Cloud LLM as the default generator — revive once we have a measured local-vs-cloud accuracy gap (Phase 3).
- Full DocVQA corpus — revive after the thin slice works on a few hundred pages (Phase 2+).
- Multi-page / multilingual documents — revive only after the single-page English pipeline ships.
