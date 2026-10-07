"""Score a CV against a job posting with the Claude API.

Usage:
    python -m src.scorer data/sample_postings/01_pm_fintech_payments.md [--cv data/fake_cv.md]
"""

import argparse
from pathlib import Path
from typing import Literal

import anthropic
from pydantic import BaseModel

from src.prompts import PROMPT_VERSION, SYSTEM_PROMPT, build_user_message

MODEL = "claude-opus-5-5"
DEFAULT_CV = Path(__file__).parent.parent / "data" / "fake_cv.md"


class Match(BaseModel):
    requirement: str
    evidence: str


class Gap(BaseModel):
    requirement: str
    severity: Literal["must_have", "nice_to_have"]
    note: str


class BulletSuggestion(BaseModel):
    original: str
    suggested: str
    reason: str


class FitReport(BaseModel):
    fit_score: int
    fit_label: Literal["high", "medium", "low"]
    matched_requirements: list[Match]
    gaps: list[Gap]
    bullet_suggestions: list[BulletSuggestion]
    cover_letter_points: list[str]


class ScoringError(Exception):
    pass


def score(cv_text: str, posting_text: str, client: anthropic.Anthropic | None = None) -> FitReport:
    client = client or anthropic.Anthropic()
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_message(cv_text, posting_text)}],
        output_format=FitReport,
        output_config={"effort": "medium"},
        # On a safety decline, the API retries on a fallback model in the same call.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        raise ScoringError("The model declined to score this posting.")
    if response.stop_reason == "max_tokens" or response.parsed_output is None:
        raise ScoringError(f"No usable result (stop_reason={response.stop_reason}).")
    return response.parsed_output


def main() -> None:
    from dotenv import load_dotenv

    parser = argparse.ArgumentParser(description="Score a CV against a job posting.")
    parser.add_argument("posting", type=Path, help="Path to a job posting text/markdown file")
    parser.add_argument("--cv", type=Path, default=DEFAULT_CV, help="Path to the CV (default: fake CV)")
    args = parser.parse_args()

    load_dotenv()
    report = score(args.cv.read_text(), args.posting.read_text())
    print(f"# model={MODEL} prompt={PROMPT_VERSION}")
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
