import json

from src import evaluate
from src.scorer import Gap
from tests.fakes import sample_report


def test_found_gaps_matches_keywords_case_insensitively():
    report = sample_report(gaps=[Gap(requirement="No PAYMENTS experience", severity="must_have", note="")])
    result = evaluate.found_gaps({"payments": ["payment"], "mobile": ["ios"]}, report)
    assert result == {"payments": True, "mobile": False}


def test_found_gaps_ignores_keywords_inside_other_words():
    report = sample_report(gaps=[Gap(requirement="Maintain dashboards", severity="must_have", note="")])
    assert evaluate.found_gaps({"ai": ["ai"]}, report) == {"ai": False}


def test_evaluate_one_and_summarize():
    label = {"expected_label": "high", "expected_gaps": {"fintech": ["fintech"], "mobile": ["mobile"]}}
    row = evaluate.evaluate_one("01.md", label, sample_report())  # medium, has a fintech gap
    assert row["label_ok"] is False
    assert (row["gaps_found"], row["gaps_expected"]) == (1, 2)
    assert row["missed_gaps"] == ["mobile"]
    assert evaluate.summarize([row]) == {"label_accuracy": 0.0, "gap_recall": 0.5}


def test_labels_cover_every_sample_posting():
    labels = {k for k in json.loads(evaluate.LABELS.read_text()) if not k.startswith("_")}
    postings = {p.name for p in evaluate.POSTINGS.glob("*.md")}
    assert labels == postings


def test_to_markdown_marks_wrong_labels():
    row = evaluate.evaluate_one("01.md", {"expected_label": "high", "expected_gaps": {}}, sample_report())
    md = evaluate.to_markdown([row], evaluate.summarize([row]))
    assert "| 01.md | 72 | medium ✗ | high |" in md
