"""Contracts for AI Pre-Scan.

These are the schemas the whole system is gated on. Two ideas do the work:

`claim_time_mode` — a historical event ("this vendor announced a feature on this date") and a
current-state claim ("this company runs this system now") need different evidence, even from the
same page. Conflating them is how a superseded source produces a confident wrong answer.

`SourceProvenance` — a retrieval timestamp proves when a copy was fetched, not that it was current
when fetched. That distinction is the one that caught us out on the AI Act's application dates, so
it is enforced in the types rather than left to discipline.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class Confidence(StrEnum):
    EVIDENCED = "Evidenced"      # a source states it
    INFERRED = "Inferred"        # the source implies it
    UNDETERMINED = "Undetermined"  # public evidence does not settle it


class ClaimTimeMode(StrEnum):
    HISTORICAL_EVENT = "historical_event"
    CURRENT_STATE = "current_state"


class CurrentnessStatus(StrEnum):
    CURRENT = "current"
    SUPERSEDED = "superseded"
    UNKNOWN = "unknown"


class AuthorityClass(StrEnum):
    COMPANY = "company"
    VENDOR = "vendor"
    REGISTRY = "registry"
    NEWS = "news"
    OTHER = "other"


class Attestation(StrEnum):
    DEPLOYED = "deployed"
    CAPABILITY_PRESENT = "capability-present"
    ATTESTED_ABSENT = "attested-absent"
    NO_PUBLISHED_USE = "no-published-use"


class SourceProvenance(BaseModel):
    """Everything needed to decide whether a source may support a given claim.

    Deliberately strict: `source_published_at` may be null, but only with a stated reason, so a
    missing date is a recorded fact rather than a silent gap.
    """

    canonical_url: HttpUrl
    retrieved_at: datetime
    content_sha256: str = Field(min_length=64, max_length=64)
    authority_class: AuthorityClass
    currentness_checked_at: datetime | None = None
    currentness_status: CurrentnessStatus = CurrentnessStatus.UNKNOWN
    source_published_at: date | None = None
    source_updated_at: date | None = None
    undated_reason: str | None = None
    superseded_by: HttpUrl | None = None
    next_review_at: datetime | None = None

    @field_validator("content_sha256")
    @classmethod
    def _hex(cls, v: str) -> str:
        int(v, 16)  # raises if not hex
        return v.lower()

    @model_validator(mode="after")
    def _dates_accounted_for(self) -> SourceProvenance:
        if self.source_published_at is None and not self.undated_reason:
            raise ValueError(
                "source_published_at is null and no undated_reason given — an undated source is a "
                "recorded fact, not an omission"
            )
        if self.currentness_status is CurrentnessStatus.SUPERSEDED and self.superseded_by is None:
            raise ValueError("currentness_status is 'superseded' but superseded_by is not set")
        return self

    def review_overdue(self, now: datetime | None = None) -> bool:
        """True when the currentness check has expired, or was never made."""
        if self.next_review_at is None or self.currentness_checked_at is None:
            return True
        return (now or datetime.now(timezone.utc)) > self.next_review_at


class Evidence(BaseModel):
    """A quoted passage plus the provenance of the page it came from.

    `quote` is mandatory and non-trivial. The report spec's rule is that a claim without a quotable
    passage does not ship, so there is no way to construct evidence that omits it.
    """

    quote: str = Field(min_length=20)
    provenance: SourceProvenance

    @field_validator("quote")
    @classmethod
    def _not_placeholder(cls, v: str) -> str:
        if v.strip().endswith("..."):
            raise ValueError("quote is truncated; store the full supporting sentence")
        return v.strip()


class Finding(BaseModel):
    """One candidate AI system, or one honest failure to establish it."""

    system: str
    what_it_does: str
    vendor: str | None = None
    built_or_bought: Literal["built", "bought", "resold", "unknown"] = "unknown"
    where_used: str | None = None
    role: Literal["provider", "deployer", "unknown"] = "unknown"
    offered_to_customers: bool | None = None
    first_evidenced: str | None = None
    claim_time_mode: ClaimTimeMode
    attestation: Attestation
    confidence: Confidence
    evidence: list[Evidence] = Field(default_factory=list)
    undetermined_reason: str | None = None

    @model_validator(mode="after")
    def _confidence_matches_evidence(self) -> Finding:
        if self.confidence is Confidence.UNDETERMINED:
            if not self.undetermined_reason:
                raise ValueError("an undetermined finding must say why")
        elif not self.evidence:
            raise ValueError(
                f"confidence is {self.confidence} with no evidence — every non-undetermined "
                "finding carries at least one quoted passage"
            )
        return self


class DiscussionItem(BaseModel):
    """A question for the client, because public evidence cannot settle it."""

    question: str
    about_system: str | None = None
    why_it_matters: str
    standing: bool = False  # always asked, regardless of what the scan found


class UnavailableSource(BaseModel):
    """A source the scan could not reach. Named in the report rather than silently dropped."""

    label: str
    reason: str


class Report(BaseModel):
    company: str
    scanned_at: datetime
    sources_consulted: int
    findings: list[Finding] = Field(default_factory=list)
    discussion: list[DiscussionItem] = Field(default_factory=list)
    unavailable_sources: list[UnavailableSource] = Field(default_factory=list)
    blind_spots: list[str] = Field(default_factory=list)
    scan_version: str = "v1"

    @model_validator(mode="after")
    def _standing_question_present(self) -> Report:
        """The modification question is the highest-stakes item in a determination and is invisible
        from outside, so the report spec makes it a standing entry. Enforced, not remembered."""
        if not any(d.standing for d in self.discussion):
            raise ValueError("report is missing the standing modification question")
        return self

    @property
    def undetermined_count(self) -> int:
        return sum(1 for f in self.findings if f.confidence is Confidence.UNDETERMINED)
