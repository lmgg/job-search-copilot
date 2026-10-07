from streamlit.testing.v1 import AppTest

from src import scorer
from tests.fakes import sample_report


def test_score_and_save_review(tmp_path, monkeypatch):
    monkeypatch.setenv("COPILOT_DB", str(tmp_path / "test.db"))
    monkeypatch.setattr(scorer, "score", lambda cv, posting: sample_report())

    at = AppTest.from_file("../app.py").run()
    at.selectbox[0].select("01_pm_fintech_payments.md").run()
    at.button[0].click().run()
    assert not at.exception
    assert at.metric[0].value == "72 / 100"

    at.radio(key="gap0").set_value("accept")
    at.radio(key="overall").set_value("reject")
    at.button[1].click().run()  # form submit
    assert "Saved 2 review(s)." in at.success[0].value
    assert at.dataframe[0].value["review_count"][0] == 2
