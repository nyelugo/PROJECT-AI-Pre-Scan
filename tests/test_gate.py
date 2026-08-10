"""The gate's job is to refuse. These tests prove it can."""

from datetime import date, datetime, timedelta, timezone

import pytest

from ai_prescan import fixtures, gate
from ai_prescan.schemas import ClaimTimeMode, Confidence, CurrentnessStatus


def _by_mode(mode):
    return [f for f in fixtures.candidate_findings() if f.claim_time_mode == mode]


def test_dated_historical_event_passes():
    f = _by_mode(ClaimTimeMode.HISTORICAL_EVENT)[0]
    assert gate.evaluate(f).passed


def test_current_state_claim_with_unknown_currentness_is_blocked():
    """The core rule: retrieved seconds ago, still not evidence of currentness."""
    f = _by_mode(ClaimTimeMode.CURRENT_STATE)[0]
    prov = f.evidence[0].provenance
    assert prov.currentness_status is CurrentnessStatus.UNKNOWN
    assert prov.retrieved_at == fixtures.NOW           # freshly fetched
    verdict = gate.evaluate(f, search_exhausted=True)
    assert not verdict.passed
    assert verdict.outcome is gate.GateOutcome.UNDETERMINED
    assert "retrieved_at does not prove" in verdict.reason


def test_blocked_finding_is_downgraded_not_dropped():
    f = _by_mode(ClaimTimeMode.CURRENT_STATE)[0]
    out = gate.apply(f, gate.evaluate(f, search_exhausted=True))
    assert out.confidence is Confidence.UNDETERMINED
    assert out.undetermined_reason
    assert out.evidence == []
    assert out.system == f.system      # the finding survives, the claim does not


def test_superseded_source_sends_the_agent_back():
    f = _by_mode(ClaimTimeMode.HISTORICAL_EVENT)[0]
    ev = f.evidence[0]
    bad = ev.provenance.model_copy(update={
        "currentness_status": CurrentnessStatus.SUPERSEDED,
        "superseded_by": "https://example.test/newer",
    })
    cur = f.model_copy(update={
        "claim_time_mode": ClaimTimeMode.CURRENT_STATE,
        "evidence": [ev.model_copy(update={"provenance": bad})],
    })
    assert gate.evaluate(cur).outcome is gate.GateOutcome.RESEARCH_AGAIN


def test_changed_content_hash_forces_reingest():
    f = _by_mode(ClaimTimeMode.HISTORICAL_EVENT)[0]
    url = str(f.evidence[0].provenance.canonical_url)
    verdict = gate.evaluate(f, known_hashes={url: "0" * 64})
    assert verdict.outcome is gate.GateOutcome.RESEARCH_AGAIN
    assert "hash changed" in verdict.reason


def test_overdue_currentness_check_fails_for_current_state():
    f = _by_mode(ClaimTimeMode.HISTORICAL_EVENT)[0]
    ev = f.evidence[0]
    stale = ev.provenance.model_copy(update={
        "next_review_at": fixtures.NOW - timedelta(days=1),
        "currentness_status": CurrentnessStatus.CURRENT,
    })
    cur = f.model_copy(update={
        "claim_time_mode": ClaimTimeMode.CURRENT_STATE,
        "evidence": [ev.model_copy(update={"provenance": stale})],
    })
    assert not gate.evaluate(cur, now=fixtures.NOW, search_exhausted=True).passed
