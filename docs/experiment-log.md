# Experiment log

One row per experiment. The metrics live in the report; this file holds the *reasoning*, which is
what you'll actually want later (and the first thing a good write-up cites).

| # | Date | Hypothesis | Change | Primary metric before → after | Worst slice | Latency | Verdict | Run id |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | keep / revert / inconclusive | |

## Rules

- Write the hypothesis **before** running. "Raising OCR render DPI from 150→300 will cut CER on the
  small-font slice by ≥2 points" — not "tried higher dpi".
- One change per experiment where possible. Two changes and an improvement means you learned nothing
  about either.
- Record the worst slice, not just the average. Average-up with a slice regression is a revert.
- "Inconclusive" is a legitimate verdict — usually means the test set is too small to detect the
  effect. Note the detectable effect size when this happens.
- Record failed experiments. The list of things that didn't work is the most valuable part of this file.
