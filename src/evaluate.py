"""Run the scorer on every sample posting and compare with hand labels.

Usage:
    python -m src.evaluate [--write]   # --write saves the table to docs/eval_results.md
"""

import argparse
import json
import re
from datetime import date
from pathlib import Path

from src import scorer
from src.prompts import PROMPT_VERSION

ROOT = Path(__file__).parent.parent
LABELS = ROOT / "data" / "eval_labels.json"
POSTINGS = ROOT / "data" / "sample_postings"
RESULTS = ROOT / "docs" / "eval_results.md"


def found_gaps(expected: dict[str, list[str]], report: scorer.FitReport) -> dict[str, bool]:
    """For each expected gap, True if any keyword starts a word in a reported gap ("payment" matches "payments")."""
    reported = " ".join(f"{g.requirement} {g.note}" for g in report.gaps).lower()
    return {
        name: any(re.search(rf"\b{re.escape(k)}", reported) for k in keywords)
        for name, keywords in expected.items()
    }


def evaluate_one(name: str, label: dict, report: scorer.FitReport) -> dict:
    gaps = found_gaps(label["expected_gaps"], report)
    return {
        "posting": name,
        "score": report.fit_score,
        "label": report.fit_label,
        "expected_label": label["expected_label"],
        "label_ok": report.fit_label == label["expected_label"],
        "gaps_found": sum(gaps.values()),
        "gaps_expected": len(gaps),
        "missed_gaps": [g for g, ok in gaps.items() if not ok],
    }


def summarize(results: list[dict]) -> dict:
    expected = sum(r["gaps_expected"] for r in results)
    return {
        "label_accuracy": sum(r["label_ok"] for r in results) / len(results),
        "gap_recall": sum(r["gaps_found"] for r in results) / expected if expected else 1.0,
    }


def to_markdown(results: list[dict], summary: dict) -> str:
    lines = [
        f"# Evaluation results ({date.today()}, model `{scorer.MODEL}`, prompt `{PROMPT_VERSION}`)",
        "",
        f"- Label accuracy: {summary['label_accuracy']:.0%}",
        f"- Expected-gap recall: {summary['gap_recall']:.0%}",
        "",
        "| Posting | Score | Label | Expected | Gaps found | Missed |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        mark = "" if r["label_ok"] else " ✗"
        lines.append(
            f"| {r['posting']} | {r['score']} | {r['label']}{mark} | {r['expected_label']} "
            f"| {r['gaps_found']}/{r['gaps_expected']} | {', '.join(r['missed_gaps']) or '-'} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    from dotenv import load_dotenv

    parser = argparse.ArgumentParser(description="Evaluate the scorer against hand labels.")
    parser.add_argument("--write", action="store_true", help=f"Save results to {RESULTS.relative_to(ROOT)}")
    args = parser.parse_args()

    load_dotenv()
    labels = {k: v for k, v in json.loads(LABELS.read_text()).items() if not k.startswith("_")}
    cv_text = scorer.DEFAULT_CV.read_text()

    results = []
    for name, label in labels.items():
        print(f"Scoring {name}...")
        report = scorer.score(cv_text, (POSTINGS / name).read_text())
        results.append(evaluate_one(name, label, report))

    markdown = to_markdown(results, summarize(results))
    print(markdown)
    if args.write:
        RESULTS.write_text(markdown)
        print(f"Saved to {RESULTS}")


if __name__ == "__main__":
    main()
