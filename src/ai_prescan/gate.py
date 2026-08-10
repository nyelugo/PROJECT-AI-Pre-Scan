"""The evidence gate.

Deterministic. No model involved — that is the point. It sits inside the research loop and decides
one of three things for every candidate claim: emit it, send the agent back for a better source, or
mark it undetermined.

The rules come from docs/architecture.md, and the one that matters most is rule 2: a recent
`retrieved_at` is not evidence of currentness. Fetching a superseded page today makes the copy fresh,
not the content. That is exactly how the AI Act's application dates were got wrong.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum

from .schemas import (
    ClaimTimeMode,
    Confidence,
    CurrentnessStatus,
    Evidence,
    Finding,
)


class GateOutcome(StrEnum):
    EMIT = "emit"
    RESEARCH_AGAIN = "research_again"
    UNDETERMINED = "undetermined"


@dataclass(frozen=True)
class GateVerdict:
    outcome: GateOutcome
    reason: str

    @property
    def passed(self) -> bool:
        return self.outcome is GateOutcome.EMIT


def _hash_matches(evidence: Evidence, known_hashes: dict[str, str] | None) -> bool:
    """A stable URL whose content hash changed is a silently edited page."""
    if not known_hashes:
        return True
    prior = known_hashes.get(str(evidence.provenance.canonical_url))
    return prior is None or prior == evidence.provenance.content_sha256


def evaluate(
    finding: Finding,
    *,
    search_exhausted: bool = False,
    known_hashes: dict[str, str] | None = None,
    now: datetime | None = None,
) -> GateVerdict:
    """Decide whether this finding may be emitted.

    `search_exhausted` distinguishes "go and look for a current source" from "we looked, and there
    is not one" — the difference between a retry and an honest undetermined.
    """
    now = now or datetime.now(timezone.utc)

    if not finding.evidence:
        return GateVerdict(
            GateOutcome.UNDETERMINED if search_exhausted else GateOutcome.RESEARCH_AGAIN,
            "no quoted evidence attached",
        )

    for ev in finding.evidence:
        prov = ev.provenance

        # Rule 4 — content changed under a stable URL. Re-ingest before trusting it again.
        if not _hash_matches(ev, known_hashes):
            return GateVerdict(
                GateOutcome.RESEARCH_AGAIN,
                f"content hash changed for {prov.canonical_url}; re-ingest before use",
            )

        if finding.claim_time_mode is ClaimTimeMode.HISTORICAL_EVENT:
            # Rule 1 — a dated, hashed source still proves what was announced at the time, even if
            # the page has since been superseded. What it cannot prove is present-day state.
            if prov.source_published_at is None:
                return GateVerdict(
                    GateOutcome.UNDETERMINED if search_exhausted else GateOutcome.RESEARCH_AGAIN,
                    "historical claim needs a source with a publication date",
                )
            continue

        # Rule 2 — current-state claims need a source checked as current, within its review window.
        if prov.currentness_status is CurrentnessStatus.SUPERSEDED:
            return GateVerdict(
                GateOutcome.RESEARCH_AGAIN,
                f"source superseded by {prov.superseded_by}; find the current source",
            )
        if prov.currentness_status is CurrentnessStatus.UNKNOWN:
            # Rule 3 — unknown is not a synonym for fine, however recently it was fetched.
            return GateVerdict(
                GateOutcome.UNDETERMINED if search_exhausted else GateOutcome.RESEARCH_AGAIN,
                "current-state claim from a source whose currentness was never established "
                "(retrieved_at does not prove the content was current)",
            )
        if prov.review_overdue(now):
            return GateVerdict(
                GateOutcome.UNDETERMINED if search_exhausted else GateOutcome.RESEARCH_AGAIN,
                "currentness check is overdue for a current-state claim",
            )

    return GateVerdict(GateOutcome.EMIT, "quoted evidence present and fit for the claim's time")


def apply(
    finding: Finding,
    verdict: GateVerdict,
) -> Finding:
    """Return the finding as the gate says it must be recorded.

    A blocked finding is never dropped — it is downgraded to undetermined with the reason kept, so
    the report can say what could not be established instead of quietly narrowing.
    """
    if verdict.passed:
        return finding
    return finding.model_copy(
        update={
            "confidence": Confidence.UNDETERMINED,
            "undetermined_reason": verdict.reason,
            "evidence": [],
        }
    )
