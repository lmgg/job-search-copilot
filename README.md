# Job Search Copilot

Paste a public job posting and get a fit score against a CV, a list of gaps, and suggested changes to CV bullets and a cover letter. A human reviews everything. The tool never applies for jobs.

> All data in this repo is fictional: a fake candidate CV (`data/fake_cv.md`) and made-up sample postings (`data/sample_postings/`).

## Problem and user
_Placeholder: who the user is (a job seeker applying to PM roles) and the pain of tailoring each application by hand._

## Goals and success metrics
_Placeholder: e.g. time to tailor one application, and how often the score agrees with a human rating._

## Scope and non-goals
_Placeholder: in scope are scoring, gaps and tailoring suggestions. Out of scope: auto-applying, scraping job boards, storing real personal data._

## How it works
_Placeholder: the loop used to build each feature._
1. **Define**: what a good output looks like.
2. **Test**: run it against the sample postings.
3. **Review**: a human checks the results.
4. **Refine**: adjust prompts, scoring or UI.

## Key design decisions
- **One API call per posting, structured output.** The scorer asks Claude for a `FitReport` that matches a Pydantic schema, so the app never parses free text.
- **No invented experience.** The prompt only allows rewrites grounded in the CV, and an honest gap is better than a hidden one.
- **Human review is the product.** Every gap, bullet and cover letter point gets an accept, edit or reject verdict, stored in SQLite. There is no apply button.
- **Versioned prompts.** Each run stores the model and `PROMPT_VERSION`, so evaluation results can be compared over time.
- _Placeholder: add the trade-offs you made and why._

## What went wrong and what I changed
_Placeholder: to be filled in as the project evolves._

## Evaluation
`src/evaluate.py` scores the fake CV against all 5 sample postings and compares the results with hand labels in `data/eval_labels.json`:
- **Label accuracy**: does the high, medium or low label match the expected one?
- **Expected-gap recall**: does the report name the gaps a human would expect (keyword match)?

Results: _placeholder until the first run (`python -m src.evaluate --write` saves them to `docs/eval_results.md`)._

## Roadmap
- [x] Scoring script (`src/scorer.py`)
- [x] SQLite schema (`src/db.py`)
- [x] Streamlit review interface (`app.py`)
- [x] Evaluation script (`src/evaluate.py`)
- [ ] First evaluation run and prompt refinement
- _Placeholder: what comes next._

## Setup and usage
```bash
pip install -r requirements.txt
cp .env.example .env                      # then add your Anthropic API key

python -m src.scorer data/sample_postings/04_pm_b2b_saas_data.md   # score one posting (prints JSON)
streamlit run app.py                      # review interface; data saved to data/copilot.db
python -m src.evaluate --write            # score all samples against the hand labels
python -m pytest                          # tests use a fake client, no API key needed
```
