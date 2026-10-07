"""Streamlit interface: paste a posting, review the suggestions, save your verdicts.

Run with: streamlit run app.py
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src import db, scorer
from src.prompts import PROMPT_VERSION

load_dotenv()
DATA = Path(__file__).parent / "data"
CV_PATH = DATA / "fake_cv.md"
SAMPLES = sorted((DATA / "sample_postings").glob("*.md"))
VERDICTS = ["accept", "edit", "reject"]

conn = db.connect(os.getenv("COPILOT_DB", db.DEFAULT_DB))

st.set_page_config(page_title="Job Search Copilot", layout="wide")
st.title("Job Search Copilot")
st.caption("Suggestions only. You review everything, and nothing is ever sent or applied for you.")

cv_text = CV_PATH.read_text()
with st.expander(f"CV in use: {CV_PATH.name} (fictional)"):
    st.markdown(cv_text)

# --- Input ---
choice = st.selectbox("Job posting", ["Paste my own"] + [p.name for p in SAMPLES])
default_text = "" if choice == "Paste my own" else (DATA / "sample_postings" / choice).read_text()
posting_text = st.text_area("Posting text (public postings only)", value=default_text, height=250)
title = st.text_input("Short title", value=default_text.splitlines()[0].lstrip("# ") if default_text else "")

if st.button("Score", type="primary", disabled=not posting_text.strip()):
    with st.spinner("Scoring..."):
        try:
            report = scorer.score(cv_text, posting_text)
        except scorer.ScoringError as e:
            st.error(str(e))
            st.stop()
    posting_id = db.add_posting(conn, title or "Untitled", posting_text, source=choice)
    st.session_state.run_id = db.add_run(conn, posting_id, report, CV_PATH.name, scorer.MODEL, PROMPT_VERSION)

# --- Results and review ---
run_id = st.session_state.get("run_id")
if run_id:
    report = db.get_report(conn, run_id)
    st.divider()
    st.metric("Fit score", f"{report.fit_score} / 100", report.fit_label, delta_color="off")

    st.subheader("Matched requirements")
    for m in report.matched_requirements:
        st.markdown(f"- **{m.requirement}**: {m.evidence}")

    with st.form("review"):
        verdicts = []  # (item_type, index, verdict, edited_text)

        st.subheader("Gaps")
        for i, g in enumerate(report.gaps):
            st.markdown(f"**{g.requirement}** ({g.severity.replace('_', ' ')}): {g.note}")
            v = st.radio("Is this gap right?", VERDICTS, index=None, horizontal=True, key=f"gap{i}")
            verdicts.append(("gap", i, v, None))

        st.subheader("CV bullet suggestions")
        for i, b in enumerate(report.bullet_suggestions):
            st.markdown(f"Original: {b.original}")
            edited = st.text_area("Suggested", value=b.suggested, key=f"bullet_text{i}", help=b.reason)
            v = st.radio("Verdict", VERDICTS, index=None, horizontal=True, key=f"bullet{i}")
            verdicts.append(("bullet", i, v, edited if v == "edit" else None))

        st.subheader("Cover letter points")
        for i, point in enumerate(report.cover_letter_points):
            edited = st.text_input(f"Point {i + 1}", value=point, key=f"cover_text{i}")
            v = st.radio("Verdict", VERDICTS, index=None, horizontal=True, key=f"cover{i}")
            verdicts.append(("cover_point", i, v, edited if v == "edit" else None))

        st.subheader("Overall")
        overall = st.radio("Is the score about right?", VERDICTS, index=None, horizontal=True, key="overall")
        note = st.text_input("Note (optional)")

        if st.form_submit_button("Save review"):
            saved = 0
            for item_type, i, v, edited in verdicts:
                if v:
                    db.add_review(conn, run_id, item_type, v, item_index=i, edited_text=edited)
                    saved += 1
            if overall:
                db.add_review(conn, run_id, "overall", overall, note=note or None)
                saved += 1
            st.success(f"Saved {saved} review(s).")

# --- History ---
st.divider()
st.subheader("Recent runs")
runs = db.list_runs(conn)
if runs:
    st.dataframe([dict(r) for r in runs], hide_index=True)
else:
    st.write("No runs yet.")
