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
_Placeholder: e.g. Python + SQLite + Streamlit, Claude API for scoring, human-in-the-loop by design._

## What went wrong and what I changed
_Placeholder: to be filled in as the project evolves._

## Evaluation
_Placeholder: how scores are checked against hand-labelled expectations for the sample postings._

## Roadmap
_Placeholder: scoring script, SQLite schema, Streamlit interface, evaluation script._

## Setup
```bash
cp .env.example .env   # then add your Anthropic API key
```
