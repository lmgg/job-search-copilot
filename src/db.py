"""SQLite storage for postings, scoring runs and human reviews."""

import sqlite3
from pathlib import Path

from src.scorer import FitReport

DEFAULT_DB = Path(__file__).parent.parent / "data" / "copilot.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS postings (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    source TEXT,                       -- file name or URL of the public posting
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY,
    posting_id INTEGER NOT NULL REFERENCES postings(id),
    cv_name TEXT NOT NULL,
    model TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    fit_score INTEGER NOT NULL,
    fit_label TEXT NOT NULL,
    report_json TEXT NOT NULL,          -- full FitReport
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES runs(id),
    item_type TEXT NOT NULL CHECK (item_type IN ('overall', 'gap', 'bullet', 'cover_point')),
    item_index INTEGER,                 -- position in the report list; NULL for 'overall'
    verdict TEXT NOT NULL CHECK (verdict IN ('accept', 'edit', 'reject')),
    edited_text TEXT,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(path: Path | str = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def add_posting(conn: sqlite3.Connection, title: str, text: str, source: str | None = None) -> int:
    cur = conn.execute(
        "INSERT INTO postings (title, text, source) VALUES (?, ?, ?)", (title, text, source)
    )
    conn.commit()
    return cur.lastrowid


def add_run(
    conn: sqlite3.Connection,
    posting_id: int,
    report: FitReport,
    cv_name: str,
    model: str,
    prompt_version: str,
) -> int:
    cur = conn.execute(
        """INSERT INTO runs (posting_id, cv_name, model, prompt_version, fit_score, fit_label, report_json)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (posting_id, cv_name, model, prompt_version, report.fit_score, report.fit_label,
         report.model_dump_json()),
    )
    conn.commit()
    return cur.lastrowid


def add_review(
    conn: sqlite3.Connection,
    run_id: int,
    item_type: str,
    verdict: str,
    item_index: int | None = None,
    edited_text: str | None = None,
    note: str | None = None,
) -> int:
    cur = conn.execute(
        """INSERT INTO reviews (run_id, item_type, item_index, verdict, edited_text, note)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (run_id, item_type, item_index, verdict, edited_text, note),
    )
    conn.commit()
    return cur.lastrowid


def get_report(conn: sqlite3.Connection, run_id: int) -> FitReport:
    row = conn.execute("SELECT report_json FROM runs WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        raise KeyError(f"No run with id {run_id}")
    return FitReport.model_validate_json(row["report_json"])


def list_runs(conn: sqlite3.Connection, limit: int = 20) -> list[sqlite3.Row]:
    return conn.execute(
        """SELECT runs.id, postings.title, runs.fit_score, runs.fit_label,
                  runs.prompt_version, runs.created_at,
                  (SELECT COUNT(*) FROM reviews WHERE reviews.run_id = runs.id) AS review_count
           FROM runs JOIN postings ON postings.id = runs.posting_id
           ORDER BY runs.id DESC LIMIT ?""",
        (limit,),
    ).fetchall()
