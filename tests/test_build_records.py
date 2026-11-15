from PIL import Image
from doc_rag.data.manifest import build_records


def _fake_example(question_id, doc_id, source_id, page_no):
    return {
        "questionId": question_id, "docId": doc_id,
        "ucsf_document_id": source_id, "ucsf_document_page_no": page_no,
        "image": Image.new("RGB", (8, 8), (255, 255, 255)),
        "answers": ["x"],
    }


def test_one_record_per_page_and_questions_counted(tmp_path):
    examples = [
        _fake_example("q1", 100, "srcA", "1"),
        _fake_example("q2", 100, "srcA", "1"),   # même page -> doit fusionner
        _fake_example("q3", 100, "srcA", "1"),
        _fake_example("q4", 101, "srcA", "2"),   # autre page, même source
    ]
    recs = build_records(examples, tmp_path)

    assert len(recs) == 2                        # 2 pages distinctes, pas 4 questions
    by_id = {r.doc_id: r for r in recs}
    assert "100" in by_id                        # docId int -> str
    assert by_id["100"].num_questions == 3       # 3 questions sur la page 100
    assert by_id["101"].num_questions == 1
    assert by_id["100"].source_id == "srcA"
    assert isinstance(by_id["100"].page_no, int) # page_no str -> int
    assert by_id["100"].split is None            # le split viendra plus tard
    assert (tmp_path / "100.png").exists()        # image sauvée une fois