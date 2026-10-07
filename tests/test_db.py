import sqlite3

import pytest

from src import db
from tests.fakes import sample_report


@pytest.fixture
def conn():
    return db.connect(":memory:")


def test_run_round_trip(conn):
    posting_id = db.add_posting(conn, "PM, Payments", "posting text", source="01.md")
    report = sample_report()
    run_id = db.add_run(conn, posting_id, report, cv_name="fake_cv.md", model="m", prompt_version="v1")
    assert db.get_report(conn, run_id) == report


def test_list_runs_counts_reviews(conn):
    posting_id = db.add_posting(conn, "PM, Payments", "posting text")
    run_id = db.add_run(conn, posting_id, sample_report(), "fake_cv.md", "m", "v1")
    db.add_review(conn, run_id, "gap", "accept", item_index=0)
    db.add_review(conn, run_id, "overall", "edit", note="Score feels high")
    [row] = db.list_runs(conn)
    assert row["title"] == "PM, Payments"
    assert row["review_count"] == 2


def test_invalid_verdict_is_rejected(conn):
    posting_id = db.add_posting(conn, "t", "x")
    run_id = db.add_run(conn, posting_id, sample_report(), "cv", "m", "v1")
    with pytest.raises(sqlite3.IntegrityError):
        db.add_review(conn, run_id, "gap", "maybe")


def test_review_needs_existing_run(conn):
    with pytest.raises(sqlite3.IntegrityError):
        db.add_review(conn, 999, "overall", "accept")
