"""Tool adapters. No network: what matters is that a missing key becomes a named unavailable
source rather than a crash or, worse, a silent omission."""

import ai_prescan.tools as tools


def test_missing_key_reports_unavailable_not_empty(monkeypatch):
    monkeypatch.delenv("SERPER_API_KEY", raising=False)
    r = tools.web_search("Acme Ltd")
    assert r.hits == []
    assert len(r.unavailable) == 1
    assert "SERPER_API_KEY" in r.unavailable[0].reason


def test_results_combine_and_keep_every_unavailable(monkeypatch):
    for k in ("SERPER_API_KEY", "NEWS_API_KEY", "OPENCORPORATES_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    r = tools.research_all("Acme Ltd")
    assert r.hits == []
    assert len(r.unavailable) == 3          # three tools, three stated gaps
    labels = {u.label for u in r.unavailable}
    assert len(labels) == 3
