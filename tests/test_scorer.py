import pytest

from src.scorer import FitReport, ScoringError, score
from tests.fakes import FakeClient, sample_report


def test_score_returns_parsed_report():
    client = FakeClient(report=sample_report())
    report = score("my cv", "a posting", client=client)
    assert isinstance(report, FitReport)
    assert report.fit_score == 72


def test_score_sends_cv_and_posting_in_prompt():
    client = FakeClient(report=sample_report())
    score("CV-TEXT", "POSTING-TEXT", client=client)
    content = client.calls[0]["messages"][0]["content"]
    assert "CV-TEXT" in content and "POSTING-TEXT" in content
    assert client.calls[0]["output_format"] is FitReport


def test_score_raises_on_refusal():
    with pytest.raises(ScoringError):
        score("cv", "posting", client=FakeClient(report=None, stop_reason="refusal"))


def test_score_raises_when_output_missing():
    with pytest.raises(ScoringError):
        score("cv", "posting", client=FakeClient(report=None, stop_reason="max_tokens"))
