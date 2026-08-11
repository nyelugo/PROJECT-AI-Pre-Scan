"""Controlled fixtures for the Phase 1 smoke run.

Deterministic, offline, and drawn from sources already verified in eval/ground_truth.json. Three
candidates chosen because they exercise three different gate paths rather than three variations of
success:

  1. a dated historical event that should be emitted
  2. a current-state claim from a source whose currentness was never checked — must be blocked,
     even though it was retrieved seconds ago
  3. a capability-present case where the vendor ships opt-in AI and activation is unpublished

The second is the whole point. It is the shape of the mistake that produced the wrong AI Act dates.
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta, timezone

from .schemas import (
    Attestation,
    AuthorityClass,
    ClaimTimeMode,
    Confidence,
    CurrentnessStatus,
    DiscussionItem,
    Evidence,
    Finding,
    SourceProvenance,
)

NOW = datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _prov(url: str, *, published: date | None, status: CurrentnessStatus,
          checked: datetime | None, review_days: int | None = 30,
          authority: AuthorityClass = AuthorityClass.COMPANY,
          undated_reason: str | None = None) -> SourceProvenance:
    return SourceProvenance(
        canonical_url=url,
        retrieved_at=NOW,
        content_sha256=_sha(url),
        authority_class=authority,
        currentness_checked_at=checked,
        currentness_status=status,
        source_published_at=published,
        undated_reason=undated_reason,
        next_review_at=(NOW + timedelta(days=review_days)) if review_days else None,
    )


def candidate_findings() -> list[Finding]:
    """Pre-gate candidates. Confidence here is what extraction proposed, not what will ship."""
    return [
        # 1. Historical event, dated and hashed — should pass.
        Finding(
            system="WHOOP Coach — generative AI coaching on member biometric data",
            what_it_does="Generates individualised coaching responses from member biometric data",
            vendor="WHOOP (own product), built on OpenAI GPT-4",
            built_or_bought="built",
            where_used="Consumer product",
            role="provider",
            offered_to_customers=True,
            first_evidenced="2023-09-26",
            claim_time_mode=ClaimTimeMode.HISTORICAL_EVENT,
            attestation=Attestation.DEPLOYED,
            confidence=Confidence.EVIDENCED,
            evidence=[
                Evidence(
                    quote=(
                        "WHOOP Coach takes an in-depth knowledge of a WHOOP member's goals, their "
                        "unique biometric data, and the latest performance science and generates "
                        "highly individualized, conversational responses to their health and "
                        "fitness questions"
                    ),
                    provenance=_prov(
                        "https://www.whoop.com/us/en/thelocker/whoop-unveils-the-new-whoop-coach-powered-by-openai/",
                        published=date(2023, 9, 26),
                        status=CurrentnessStatus.CURRENT,
                        checked=NOW,
                    ),
                )
            ],
        ),
        # 2. Current-state claim, freshly retrieved, currentness NEVER established — must be blocked.
        Finding(
            system="Customer support AI agent",
            what_it_does="Handles inbound support conversations",
            vendor="Unnamed vendor",
            built_or_bought="bought",
            where_used="Customer service",
            role="deployer",
            claim_time_mode=ClaimTimeMode.CURRENT_STATE,
            attestation=Attestation.DEPLOYED,
            confidence=Confidence.EVIDENCED,
            evidence=[
                Evidence(
                    quote=(
                        "Our support team uses an AI assistant to respond to common customer "
                        "questions around the clock across chat and email."
                    ),
                    provenance=_prov(
                        "https://example-company.test/support-overview",
                        published=None,
                        undated_reason="page carries no publication or update date",
                        status=CurrentnessStatus.UNKNOWN,
                        checked=None,
                        review_days=None,
                    ),
                )
            ],
        ),
        # 3. Capability present, activation unpublished — undetermined by design, not by failure.
        Finding(
            system="Applicant tracking system with opt-in AI features",
            what_it_does=(
                "Vendor ships AI features the vendor itself flags as potentially decision-"
                "influencing in recruitment; activation by this customer is not published"
            ),
            vendor="Teamtailor",
            built_or_bought="bought",
            where_used="Recruitment",
            role="deployer",
            claim_time_mode=ClaimTimeMode.CURRENT_STATE,
            attestation=Attestation.CAPABILITY_PRESENT,
            confidence=Confidence.UNDETERMINED,
            undetermined_reason=(
                "Vendor confirmed and AI capability confirmed, but the vendor states the features "
                "are opt-in and this customer's activation is published nowhere"
            ),
        ),
    ]


MODIFICATION_QUESTION = DiscussionItem(
    question=(
        "For each tool identified: have you renamed, rebranded or white-labelled it? Have you "
        "changed what you use it for since you bought it? Has anyone configured or retrained it?"
    ),
    why_it_matters=(
        "Any yes may change the company's role from deployer to provider, which changes its "
        "obligations substantially. It is invisible from outside, so it is always asked."
    ),
    standing=True,
)

# Asked when the scan found nothing. "For each tool identified" is nonsense on an empty report,
# and the useful question changes completely: the point is no longer how a tool was modified, it is
# that public evidence cannot see inside the business at all.
NOTHING_FOUND_QUESTION = DiscussionItem(
    question=(
        "We found no public evidence of AI systems in use. What AI tools does the business "
        "actually use — including anything bought on a card, anything added to a tool you "
        "already had, and anything staff use day to day?"
    ),
    why_it_matters=(
        "No public evidence is not the same as nothing. Internal tools, anything behind a login, "
        "and staff use of consumer AI leave no external trace at all, so this is the one question "
        "an outside scan can never answer for you."
    ),
    standing=True,
)

BLIND_SPOTS = [
    "Internal tools with no public footprint",
    "Employee use of consumer AI tools — leaves no external trace",
    "Anything behind a login",
    "Systems evidenced only in sources published before the scan window",
]
