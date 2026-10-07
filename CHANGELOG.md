# Changelog

## v0.3 (2026-10-07)
- Added `app.py` (Streamlit): pick a sample or paste a public posting, score it, then accept, edit or reject each gap, bullet rewrite and cover letter point.
- Every run and review is saved to SQLite; a "Recent runs" table shows history.
- No apply or send button, by design.
- Added a Streamlit `AppTest` that runs the full flow with a stubbed scorer.

## v0.2 (2026-10-07)
- Added `src/db.py`: SQLite tables for `postings`, `runs` and `reviews`, using only the standard library.
- Each run stores the model and prompt version so results can be compared over time.
- Reviews record a human verdict (accept, edit, reject) per gap, bullet, cover letter point or overall.

## v0.1 (2026-10-07)
- Added `src/scorer.py`: one Claude API call returns a validated `FitReport` (score, label, matches, gaps, bullet rewrites, cover letter points).
- Prompt lives in `src/prompts.py` with a `PROMPT_VERSION`; it forbids inventing experience.
- Refusals and truncated output raise `ScoringError` instead of returning partial data.
- Tests use a fake client, so they never call the API.

## v0 (2026-10-07)
- Scaffolded the project: `src/`, `data/`, `docs/`, `tests/`.
- Added `.gitignore` (excludes `.env`, `*.db`, real CV files) and `.env.example`.
- Added a fake candidate CV and 5 fictional product manager job postings.
- Added a README skeleton.
