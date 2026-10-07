# Changelog

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
