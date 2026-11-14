"""Tests that encode the corpus contract. They FAIL until you implement manifest.py.

The one that matters most is `test_no_source_leaks_across_splits` — that is the Phase 1 gate
written as executable code. If it passes, you cannot accidentally leak a template.
"""
import pytest

from doc_rag.data.manifest import DocRecord, Split, assign_splits


def _fake_records(n_sources: int = 6, pages_per_source: int = 3) -> list[DocRecord]:
    """Synthetic corpus: `n_sources` sources, each with several pages. No images needed."""
    recs: list[DocRecord] = []
    for s in range(n_sources):
        for p in range(pages_per_source):
            recs.append(
                DocRecord(
                    doc_id=f"{s}-{p}",
                    source_id=f"src{s}",
                    page_no=p,
                    image_path=f"data/raw/{s}_{p}.png",
                    file_hash="0" * 64,
                    num_questions=4,
                )
            )
    return recs


def test_no_source_leaks_across_splits():
    """THE invariant: a source_id must never appear in more than one split."""
    out = assign_splits(
        _fake_records(),
        fractions={Split.TRAIN: 0.5, Split.DEV: 0.2, Split.TEST: 0.2, Split.UNSEEN_TEMPLATE: 0.1},
        seed=0,
    )
    split_by_source: dict[str, set] = {}
    for r in out:
        split_by_source.setdefault(r.source_id, set()).add(r.split)
    leaks = {s: sp for s, sp in split_by_source.items() if len(sp) > 1}
    assert not leaks, f"template leakage: sources span multiple splits: {leaks}"


def test_unseen_template_slice_is_nonempty():
    out = assign_splits(
        _fake_records(),
        fractions={Split.TRAIN: 0.6, Split.DEV: 0.2, Split.UNSEEN_TEMPLATE: 0.2},
        seed=0,
    )
    assert any(r.split == Split.UNSEEN_TEMPLATE for r in out), "no unseen-template slice was created"


def test_every_record_gets_a_split():
    out = assign_splits(_fake_records(), {Split.TRAIN: 0.6, Split.DEV: 0.2, Split.TEST: 0.2}, seed=0)
    assert all(r.split is not None for r in out)


def test_assignment_is_deterministic():
    f = {Split.TRAIN: 0.6, Split.DEV: 0.2, Split.TEST: 0.2}
    a = assign_splits(_fake_records(), f, seed=0)
    b = assign_splits(_fake_records(), f, seed=0)
    assert [r.split for r in a] == [r.split for r in b]
