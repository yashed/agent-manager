import json

from harness.aggregator import build_summary


def _report(cell_id, result, category=None, missing=None, violations=None):
    return {
        "cellId": cell_id,
        "result": result,
        "category": category,
        "coverage": {
            "expected": ["llm"],
            "actual": ["llm"],
            "missing": missing or [],
        },
        "violations": violations or [],
    }


def test_summary_counts_results(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps(_report("a", "pass")))
    (tmp_path / "b.json").write_text(
        json.dumps(_report("b", "fail", "schema-violation"))
    )
    (tmp_path / "c.json").write_text(json.dumps(_report("c", "skipped", missing=[])))
    s = build_summary(tmp_path, default_cell_id="a")
    assert "1 pass" in s and "1 fail" in s and "1 skipped" in s
    assert "a" in s
    assert "b" in s


def test_summary_marks_default_cell(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps(_report("a", "pass")))
    s = build_summary(tmp_path, default_cell_id="a")
    assert "default cell, required" in s
