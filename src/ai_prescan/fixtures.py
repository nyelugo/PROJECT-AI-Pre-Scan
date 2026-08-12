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


def _demo_evidenced(
    *,
    system: str,
    what_it_does: str,
    vendor: str,
    role: str,
    built_or_bought: str,
    where_used: str,
    quote: str,
    url: str,
    authority: AuthorityClass,
    published: date | None = None,
    first_evidenced: str | None = None,
    historical: bool = False,
) -> Finding:
    """Build one evidence-backed item from the checked demo corpus."""
    return Finding(
        system=system,
        what_it_does=what_it_does,
        vendor=vendor,
        role=role,
        built_or_bought=built_or_bought,
        where_used=where_used,
        first_evidenced=first_evidenced,
        claim_time_mode=(ClaimTimeMode.HISTORICAL_EVENT if historical
                         else ClaimTimeMode.CURRENT_STATE),
        attestation=Attestation.DEPLOYED,
        confidence=Confidence.EVIDENCED,
        evidence=[Evidence(
            quote=quote,
            provenance=_prov(url, published=published, status=CurrentnessStatus.CURRENT,
                             checked=NOW, authority=authority,
                             undated_reason=(None if published else
                                             "page carries no machine-readable publication date")),
        )],
    )


def _demo_undetermined(
    *, system: str, what_it_does: str, vendor: str, where_used: str,
    reason: str, role: str = "deployer",
) -> Finding:
    return Finding(
        system=system,
        what_it_does=what_it_does,
        vendor=vendor,
        built_or_bought="bought",
        where_used=where_used,
        role=role,
        claim_time_mode=ClaimTimeMode.CURRENT_STATE,
        attestation=Attestation.CAPABILITY_PRESENT,
        confidence=Confidence.UNDETERMINED,
        undetermined_reason=reason,
    )


def _demo_identity(company: str, domain: str | None) -> str | None:
    """Resolve only an exact checked demo identity; a conflicting domain yields no data."""
    names = {
        "personio": "personio", "whoop": "whoop", "matterport": "matterport",
        "gamma": "gamma", "clay": "clay", "rocket money": "rocket-money",
        "colten care": "colten-care", "liseberg": "liseberg", "rebeldot": "rebeldot",
        "keogh's crisps": "keoghs", "keogh's crisps (keogh's farm)": "keoghs",
        "barry's tea": "barrys-tea", "ballymaloe foods": "ballymaloe",
    }
    domains = {
        "personio.de": "personio", "whoop.com": "whoop", "matterport.com": "matterport",
        "gamma.app": "gamma", "clay.com": "clay", "rocketmoney.com": "rocket-money",
        "coltencare.co.uk": "colten-care", "liseberg.com": "liseberg",
        "rebeldot.com": "rebeldot", "keoghs.ie": "keoghs", "barrystea.ie": "barrys-tea",
        "ballymaloefoods.ie": "ballymaloe",
    }
    by_name = names.get(" ".join(company.lower().split()))
    if not domain:
        return by_name
    clean = domain.lower().removeprefix("https://").removeprefix("http://")
    clean = clean.removeprefix("www.").split("/", 1)[0]
    by_domain = domains.get(clean)
    return by_name if by_name and by_name == by_domain else None


def demo_supported(company: str, domain: str | None = None) -> bool:
    """Whether the fixed browser demo has checked data for this exact identity."""
    return _demo_identity(company, domain) is not None


def demo_case(company: str, domain: str | None = None) -> tuple[list[Finding], int]:
    """Company-scoped fixed data for the browser demo.

    Returning no findings for an unknown or mismatched identity is deliberate. Reusing a persuasive
    fixture from another company is worse than an empty report because it looks trustworthy.
    """
    identity = _demo_identity(company, domain)
    if identity == "personio":
        return [
            _demo_evidenced(
                system="Fin — AI agent for customer support",
                what_it_does="Supports customer-service teams and recommends improvements",
                vendor="Intercom", role="deployer", built_or_bought="bought",
                where_used="Customer support",
                quote=("What stood out about Fin was its ability to show us where the problems are, "
                       "recommend improvements, and continuously get better over time."),
                url="https://fin.ai/", authority=AuthorityClass.VENDOR,
            ),
            _demo_evidenced(
                system="Personio Assistant — AI-powered HR data assistant",
                what_it_does="Answers HR questions and surfaces workforce insights",
                vendor="Personio (own product)", role="provider", built_or_bought="built",
                where_used="Personio HR platform", authority=AuthorityClass.COMPANY,
                quote=("Turn complex HR data into confident decisions. Ask Personio Assistant any "
                       "question and get AI-powered insights in seconds - all with privacy built in."),
                url="https://www.personio.com/product/assistant/",
            ),
        ], 2
    if identity == "whoop":
        return [
            _demo_evidenced(
                system="Fin — AI agent for customer support",
                what_it_does="Handles customer-support conversations",
                vendor="Intercom", role="deployer", built_or_bought="bought",
                where_used="Customer support", quote="I needed control — and Fin gave me that.",
                url="https://fin.ai/", authority=AuthorityClass.VENDOR,
            ),
            _demo_evidenced(
                system="WHOOP Coach — generative AI coaching on member biometric data",
                what_it_does="Generates individualised coaching responses from biometric data",
                vendor="WHOOP (own product), built on OpenAI GPT-4", role="provider",
                built_or_bought="built", where_used="Consumer product", historical=True,
                first_evidenced="2023-09-26", published=date(2023, 9, 26),
                quote=("WHOOP Coach takes an in-depth knowledge of a WHOOP member's goals, their "
                       "unique biometric data, and the latest performance science and generates "
                       "highly individualized, conversational responses to their health and "
                       "fitness questions"),
                url=("https://www.whoop.com/us/en/thelocker/"
                     "whoop-unveils-the-new-whoop-coach-powered-by-openai/"),
                authority=AuthorityClass.COMPANY,
            ),
        ], 2
    if identity == "matterport":
        return [
            _demo_evidenced(
                system="Fin for Salesforce — AI agent for customer support",
                what_it_does="Automates support while integrating with Salesforce",
                vendor="Intercom", role="deployer", built_or_bought="bought",
                where_used="Customer support", authority=AuthorityClass.VENDOR,
                quote=("Fin for Salesforce has been a game-changer. Fin's seamless integration "
                       "meant no disruption to our existing setup, leading to faster customer responses."),
                url="https://fin.ai/",
            ),
            _demo_evidenced(
                system="Cortex AI — automated 3D digital twin generation",
                what_it_does="Creates digital twins automatically with computer vision and deep learning",
                vendor="Matterport (own product)", role="provider", built_or_bought="built",
                where_used="Matterport digital-twin platform", authority=AuthorityClass.COMPANY,
                quote=("Cortex AI, is powered by AI and fully automated, allowing us to create "
                       "thousands of digital twins daily without human intervention."),
                url="https://matterport.com/cortex-ai",
            ),
        ], 2

    single = {
        "gamma": ("Fin — AI agent for customer support", "Gamma customer support"),
        "clay": ("Fin — AI agent across in-app chat, Slack and email", "Clay customer support"),
        "rocket-money": ("Fin — AI agent for customer support", "Rocket Money customer support"),
    }
    if identity in single:
        system, where = single[identity]
        return [_demo_undetermined(
            system=system, what_it_does="Handles customer-support conversations",
            vendor="Intercom", where_used=where,
            reason=("The fixed demo corpus identifies the vendor relationship but does not carry "
                    "a quotable passage strong enough to evidence the deployment."),
        )], 1

    if identity in {"colten-care", "liseberg", "rebeldot"}:
        return [_demo_undetermined(
            system="Teamtailor Co-pilot — opt-in AI features in an applicant tracking system",
            what_it_does="Adds optional AI assistance to recruitment workflows",
            vendor="Teamtailor", where_used="Recruitment",
            reason=("Vendor and customer relationship are documented, but the vendor states the "
                    "AI features are opt-in and this customer's activation is published nowhere."),
        )], 2

    # Thin-footprint companies produce an honest empty report. Browser callers reject unknown
    # identities before scanning; this lower-level fallback still cannot leak another company.
    return [], 1 if identity in {"keoghs", "barrys-tea", "ballymaloe"} else 0


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
