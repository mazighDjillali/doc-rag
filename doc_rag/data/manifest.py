"""Corpus manifest + template-disjoint splitting.

A MANIFEST is one row per page/image in the corpus. It is the contract the rest of the project
reads the corpus through: provenance (hash + source) and the split assignment that keeps
evaluation honest.

SPLIT-UNIT DECISION (see PROGRESS.md): we split on `source_id` (DocVQA ucsf_document_id), NOT
`doc_id`, so no source document's pages straddle two splits -> no template leakage.

This module ships as a SKELETON. Functions raise NotImplementedError and the tests fail until
you implement the TODOs. Turn the tests green; the leakage test is the Phase 1 gate.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace, asdict
from enum import Enum
from pathlib import Path
from typing import Counter, Iterable, Sequence


class Split(str, Enum):
    TRAIN = "train"
    DEV = "dev"
    TEST = "test"
    UNSEEN_TEMPLATE = "unseen_template"  # >=1 whole source held out as a brand-new-layout slice


@dataclass(frozen=True)
class DocRecord:
    doc_id: str           # DocVQA docId  -> identifies ONE page/image
    source_id: str        # DocVQA ucsf_document_id -> the SPLIT UNIT (template/source)
    page_no: int          # ucsf_document_page_no
    image_path: str       # path to the saved PNG, relative to repo root
    file_hash: str        # sha256 of the image bytes -> provenance + duplicate detection
    num_questions: int    # how many eval questions target this page
    split: Split | None = None  # set by assign_splits(), not by build_records()


def sha256_file(path: str | Path) -> str:
    """Return the hex sha256 of a file's bytes. (Mechanical.)"""
    # TODO: open in binary, read in chunks, return hashlib.sha256(...).hexdigest()
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
    #raise NotImplementedError





def assign_splits(
    records: Sequence[DocRecord],
    fractions: dict[Split, float],
    seed: int = 0,
) -> list[DocRecord]:
    """Assign each record a split so EVERY source_id lands entirely in ONE split.

    This is the leakage-prevention core. The unit you shuffle and allocate is the SOURCE
    (source_id), never the individual record: all pages of a source move together.

    You must:
      - group record indices by source_id,
      - shuffle the SOURCES deterministically using `seed`,
      - allocate whole sources to splits according to `fractions` (which should include
        at least a small UNSEEN_TEMPLATE share),
      - return NEW records with split set (use dataclasses.replace; records are frozen).

    Invariant the tests enforce: no source_id appears in more than one split.
    """
    # TODO: implement. Hint: random.Random(seed).shuffle(sorted(unique_sources)).
    raise NotImplementedError


def save_manifest(records: Sequence[DocRecord], path: str | Path) -> None:
    """Write the manifest as JSONL, one record per line. (Mechanical.)"""
    # TODO: for each record, json.dumps a dict; store split as its string value, not the enum.
    raise NotImplementedError


def load_manifest(path: str | Path) -> list[DocRecord]:
    """Read a JSONL manifest back into DocRecords. (Mechanical.)"""
    # TODO: parse each line; rebuild Split from its string; return list[DocRecord].
    raise NotImplementedError

def build_records(examples: Iterable[dict], image_dir: str | Path) -> list[DocRecord]:
    """Turn raw DocVQA examples into one DocRecord per PAGE (not per question).

    Each example dict has keys: docId, ucsf_document_id, ucsf_document_page_no, image (PIL),
    questionId, answers, ...

    You must:
      - collapse the ~4 questions per docId into a SINGLE record (one page = one record),
      - save each page's PIL image to  image_dir / f"{docId}.png"  (once),
      - set file_hash = sha256 of that saved PNG,
      - set num_questions = how many questions targeted that page,
      - leave split = None (assign_splits handles it).
    """
    image_dir = Path(image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)
    acc: dict[str, DocRecord] = {}
    for  ex in examples:
        doc_id = str(ex["docId"])  
        if doc_id not in acc:
            # first time seeing this page, create a new record
            path = image_dir / f"{doc_id}.png"
            ex["image"].save(path)  # save the PIL image to disk
            file_hash = sha256_file(path)  # compute the hash of the saved image
            acc[doc_id] = DocRecord(
                doc_id=doc_id,
                source_id=ex["ucsf_document_id"],
                page_no=int(ex["ucsf_document_page_no"]),
                image_path=str(path),
                file_hash=file_hash,
                num_questions=1,  # first question for this page
            )
        else:
            # already seen this page, increment the question count
            record = acc[doc_id]
            acc[doc_id] = replace(record, num_questions=record.num_questions + 1)

    return list(acc.values())

if __name__ == "__main__":
    # Quick sanity check: the first two sample images we pulled from DocVQA should match the
    # hashes in the manifest. If you re-run pull_samples.py, these will change.
    print(sha256_file("data/raw/sample_00.png"))  # sanity check: should match the hash in the manifest
    print(sha256_file("data/raw/sample_01.png"))  # sanity check: should match the hash in the manifest