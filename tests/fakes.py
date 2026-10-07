"""A stand-in for the Anthropic client so tests never call the real API."""

from types import SimpleNamespace

from src.scorer import FitReport, Gap, Match


def sample_report(**overrides) -> FitReport:
    data = dict(
        fit_score=72,
        fit_label="medium",
        matched_requirements=[Match(requirement="SQL", evidence="Listed in skills")],
        gaps=[Gap(requirement="Fintech experience", severity="nice_to_have", note="No payments roles")],
        bullet_suggestions=[],
        cover_letter_points=["Experiment-led onboarding work"],
    )
    data.update(overrides)
    return FitReport(**data)


class FakeClient:
    def __init__(self, report=None, stop_reason="end_turn"):
        self.calls = []
        response = SimpleNamespace(stop_reason=stop_reason, parsed_output=report)
        self.messages = SimpleNamespace(parse=self._parse(response))

    def _parse(self, response):
        def parse(**kwargs):
            self.calls.append(kwargs)
            return response
        return parse
