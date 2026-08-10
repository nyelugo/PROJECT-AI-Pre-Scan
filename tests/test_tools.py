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
    """Identity resolution is its own step now, so research_all covers search and news. What must
    hold is that every tool which did not run is named — none may be silently skipped."""
    for k in ("SERPER_API_KEY", "NEWS_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    r = tools.research_all("Acme Ltd")
    assert r.hits == []
    assert len(r.unavailable) == 2
    assert len({u.label for u in r.unavailable}) == 2


def test_registry_name_match_must_be_the_same_entity():
    """GLEIF returns a French company called GAMMA for 'Gamma', and a Personio Foundation for
    'Personio'. A name-filter hit is not identity, and recording it would look like confirmation."""
    assert tools._same_entity("Personio", "Personio SE & Co. KG")
    assert not tools._same_entity("Personio", "Personio Foundation")
    assert not tools._same_entity("Keogh's Crisps", "Keogh Holdings")


def test_identity_is_resolved_only_by_a_domain():
    """An LEI obtained by name matching must not vouch for identity on its own."""
    ident = tools.Identity(query="Gamma", lei="123", legal_name="GAMMA")
    assert not ident.resolved
    assert tools.Identity(query="Gamma", domain="gamma.app").resolved
