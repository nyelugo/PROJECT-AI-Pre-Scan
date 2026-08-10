"""The schemas encode rules the report spec states. Verify they actually bite."""

import pytest
from pydantic import ValidationError

from ai_prescan import fixtures
from ai_prescan.schemas import (
    Attestation, ClaimTimeMode, Confidence, Evidence, Finding, Report, SourceProvenance,
)


def test_undated_source_needs_a_stated_reason():
    with pytest.raises(ValidationError, match="undated_reason"):
        SourceProvenance(
            canonical_url="https://example.test/x", retrieved_at=fixtures.NOW,
            content_sha256="a" * 64, authority_class="company", source_published_at=None,
        )


def test_superseded_requires_a_replacement():
    with pytest.raises(ValidationError, match="superseded_by"):
        SourceProvenance(
            canonical_url="https://example.test/x", retrieved_at=fixtures.NOW,
            content_sha256="a" * 64, authority_class="company",
            source_published_at="2024-01-01", currentness_status="superseded",
        )


def test_evidenced_finding_cannot_have_no_evidence():
    with pytest.raises(ValidationError, match="no evidence"):
        Finding(
            system="x", what_it_does="y", claim_time_mode=ClaimTimeMode.CURRENT_STATE,
            attestation=Attestation.DEPLOYED, confidence=Confidence.EVIDENCED,
        )


def test_undetermined_finding_must_say_why():
    with pytest.raises(ValidationError, match="must say why"):
        Finding(
            system="x", what_it_does="y", claim_time_mode=ClaimTimeMode.CURRENT_STATE,
            attestation=Attestation.DEPLOYED, confidence=Confidence.UNDETERMINED,
        )


def test_truncated_quote_is_rejected():
    with pytest.raises(ValidationError, match="truncated"):
        Evidence(
            quote="This sentence was cut off right here...",
            provenance=SourceProvenance(
                canonical_url="https://example.test/x", retrieved_at=fixtures.NOW,
                content_sha256="a" * 64, authority_class="company",
                source_published_at="2024-01-01",
            ),
        )


def test_report_without_the_standing_question_is_invalid():
    with pytest.raises(ValidationError, match="standing modification question"):
        Report(company="X", scanned_at=fixtures.NOW, sources_consulted=1)
