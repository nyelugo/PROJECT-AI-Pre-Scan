"""Fetching and extraction. Network calls are stubbed; the rules are what is under test."""

from datetime import datetime, timezone

import ai_prescan.fetch as fetch
from ai_prescan.extract import _quote_is_in_page
from ai_prescan.schemas import CurrentnessStatus

NOW = datetime(2026, 8, 10, tzinfo=timezone.utc)
PAGE = (b'<html><head><meta property="article:published_time" content="2024-03-05T09:00:00Z">'
        b"</head><body><script>ignore()</script><p>We use an AI assistant to triage "
        b"incoming support tickets across chat and email.</p></body></html>")


class _Resp:
    def __init__(self, status, content=b"", url="https://example.test/x"):
        self.status_code, self.content, self.url = status, content, url


def test_successful_fetch_builds_full_provenance(monkeypatch):
    monkeypatch.setattr(fetch, "_get", lambda url: _Resp(200, PAGE, url))
    r = fetch.fetch("https://example.test/x", now=NOW)
    assert r.ok
    p = r.provenance
    assert p.content_sha256 and len(p.content_sha256) == 64
    assert str(p.source_published_at) == "2024-03-05"
    assert "AI assistant to triage" in r.text
    assert "ignore()" not in r.text          # script contents stripped


def test_a_200_does_not_make_stale_content_current(monkeypatch):
    """This test previously asserted the opposite, and in doing so pinned the project's worst
    defect in place. Fetching a page proves it is served now, not that its content is current —
    the superseded EU AI Act text returns 200 today. Across every evaluation report, 68 of 68
    evidence items were stamped `current`, so two of the gate's three rules had never run."""
    monkeypatch.setattr(fetch, "_get", lambda url: _Resp(200, PAGE, url))
    p = fetch.fetch("https://example.test/x", now=NOW).provenance
    assert p.source_published_at.year == 2024 and NOW.year == 2026   # older than the review window
    assert p.currentness_status is CurrentnessStatus.UNKNOWN
    assert p.currentness_checked_at is None and p.next_review_at is None


def test_a_recently_dated_page_is_current(monkeypatch):
    """Currency needs a positive signal from the source, and a fresh date is one."""
    recent = PAGE.replace(b"2024-03-05T09:00:00Z", b"2026-08-01T09:00:00Z")
    monkeypatch.setattr(fetch, "_get", lambda url: _Resp(200, recent, url))
    p = fetch.fetch("https://example.test/x", now=NOW).provenance
    assert p.currentness_status is CurrentnessStatus.CURRENT
    assert p.next_review_at > NOW


def test_an_undated_page_cannot_support_a_present_tense_claim(monkeypatch):
    """The common case: most company pages carry no date. That is not a failure — it routes a
    current-state claim to `undetermined` and a question, which is the designed outcome."""
    from ai_prescan import gate
    from ai_prescan.schemas import (Attestation, ClaimTimeMode, Confidence, Evidence, Finding)

    monkeypatch.setattr(fetch, "_get",
                        lambda url: _Resp(200, b"<html><body>We use an AI assistant daily.</body></html>", url))
    prov = fetch.fetch("https://example.test/undated", now=NOW).provenance
    assert prov.currentness_status is CurrentnessStatus.UNKNOWN

    claim = Finding(system="AI assistant", what_it_does="handles support",
                    claim_time_mode=ClaimTimeMode.CURRENT_STATE,
                    attestation=Attestation.DEPLOYED, confidence=Confidence.EVIDENCED,
                    evidence=[Evidence(quote="We use an AI assistant daily for support triage.",
                                       provenance=prov)])
    verdict = gate.evaluate(claim, search_exhausted=True)
    assert not verdict.passed
    assert verdict.outcome is gate.GateOutcome.UNDETERMINED


def test_blocked_host_is_unavailable_not_silently_dropped(monkeypatch):
    monkeypatch.setattr(fetch, "_get", lambda url: _Resp(403, b"", url))
    monkeypatch.setattr(fetch, "browser_fetch", None)
    r = fetch.fetch("https://www.whoop.com/blocked", now=NOW)
    assert not r.ok
    assert r.provenance is None
    assert "403" in r.unavailable_reason and "browser" in r.unavailable_reason


def test_browser_fallback_is_used_when_configured(monkeypatch):
    monkeypatch.setattr(fetch, "_get", lambda url: _Resp(403, b"", url))
    monkeypatch.setattr(fetch, "browser_fetch", lambda url: (url, PAGE))
    r = fetch.fetch("https://www.whoop.com/blocked", now=NOW)
    assert r.ok and r.provenance.content_sha256


def test_undated_page_records_a_reason(monkeypatch):
    monkeypatch.setattr(fetch, "_get", lambda url: _Resp(200, b"<html><body>no date here</body></html>", url))
    r = fetch.fetch("https://example.test/y", now=NOW)
    assert r.provenance.source_published_at is None
    assert r.provenance.undated_reason


def test_quote_verification_rejects_a_paraphrase():
    page = "We use an AI assistant to triage incoming support tickets across chat and email."
    assert _quote_is_in_page("We use an AI assistant to triage incoming support tickets", page)
    # plausible, adjacent, and not what the page says
    assert not _quote_is_in_page("We deploy AI to automatically rank and score job applicants", page)


def test_company_name_must_match_as_a_whole_word():
    """Regression from a live run: searching 'Gamma' returned a Sony TV review, and the scan
    reported Google Gemini as Gamma's AI system. Substring matching is how that happens."""
    from ai_prescan.graph import _mentions
    assert _mentions("Gamma", "Gamma is a presentation tool used by teams.")
    assert not _mentions("Gamma", "The detector measures gamma-ray emissions.")
    assert not _mentions("Gamma", "Sony's new TV includes Google Gemini.")


def test_duplicate_systems_collapse_to_one_row():
    from ai_prescan.graph import _dedupe
    from ai_prescan import fixtures
    f = fixtures.candidate_findings()[0]
    assert len(_dedupe([f, f.model_copy(), f.model_copy()])) == 1


def test_quote_must_show_ai_behaviour():
    """Prompt-only control failed: 'Personio Whistleblowing, a centralised solution for anonymous
    reporting' kept being reported because it sat in an AI-titled press release. Asking the model
    not to was not enough, so the check is deterministic."""
    from ai_prescan.extract import _quote_shows_ai
    assert not _quote_shows_ai(
        "Personio Whistleblowing is a centralised solution for anonymous reporting that enables "
        "people to safely and anonymously report wrongdoing.")
    assert _quote_shows_ai("upgraded with an HR focused, AI-powered chatbot")
    assert _quote_shows_ai("automatically ranks applicants against the role requirements")
    assert _quote_shows_ai("provides an AI-generated summary of continuous feedback")
