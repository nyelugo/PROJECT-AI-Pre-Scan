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
    assert p.currentness_status is CurrentnessStatus.CURRENT
    assert p.next_review_at > NOW
    assert "AI assistant to triage" in r.text
    assert "ignore()" not in r.text          # script contents stripped


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
