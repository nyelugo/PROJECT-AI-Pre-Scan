"""The client book — the thing that makes this a tool for forty clients rather than a text box."""

import pytest

from ai_prescan import clients
from ai_prescan.store_jobs import Scan


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(clients, "PATH", tmp_path / "clients.json")


def test_a_client_is_added_once_and_kept():
    c = clients.add("Acme Ltd", "https://www.acme.ie/")
    assert c.domain == "acme.ie"                      # normalised, so it matches what search needs
    assert clients.get(c.id).name == "Acme Ltd"
    assert [x.name for x in clients.all_clients()] == ["Acme Ltd"]


def test_the_same_client_is_not_added_twice():
    clients.add("Acme Ltd")
    assert clients.add("  acme ltd  ") is None
    assert len(clients.all_clients()) == 1


def test_a_whole_list_imports_in_one_paste():
    added, skipped = clients.import_lines(
        "Acme Ltd, acme.ie\n\nBeta Foods\nAcme Ltd\n   \nGamma, gamma.app")
    assert (added, skipped) == (3, 1)                 # blank lines ignored, duplicate skipped
    assert clients.find_by_name("Gamma").domain == "gamma.app"


def test_never_scanned_clients_come_first():
    """An unknown client is a bigger risk to an adviser than a known one with findings."""
    old = clients.add("Scanned Ltd")
    clients.record_scan(old.id, Scan(id="s1", company="Scanned Ltd", status="done",
                                     findings=3, undetermined=1,
                                     finished_at="2026-08-11T09:00:00+00:00"))
    clients.add("Unknown Ltd")
    assert [c.name for c in clients.all_clients()][0] == "Unknown Ltd"


def test_more_unresolved_outranks_more_found():
    a = clients.add("Many Findings")
    b = clients.add("Many Unknowns")
    now = "2026-08-11T09:00:00+00:00"
    clients.record_scan(a.id, Scan(id="a", company="a", status="done", findings=9,
                                   undetermined=0, finished_at=now))
    clients.record_scan(b.id, Scan(id="b", company="b", status="done", findings=1,
                                   undetermined=4, finished_at=now))
    assert [c.name for c in clients.all_clients()][0] == "Many Unknowns"


def test_a_scan_updates_the_standing_record():
    c = clients.add("Acme Ltd")
    clients.record_scan(c.id, Scan(id="s9", company="Acme Ltd", status="done", findings=2,
                                   undetermined=1, questions=3,
                                   finished_at="2026-08-11T09:00:00+00:00"))
    again = clients.get(c.id)
    assert (again.last_findings, again.last_undetermined, again.scan_count) == (2, 1, 1)
    assert again.last_scan_id == "s9"


def test_a_stale_scan_says_so():
    c = clients.add("Acme Ltd")
    clients.record_scan(c.id, Scan(id="s", company="Acme Ltd", status="done",
                                   finished_at="2026-01-01T00:00:00+00:00"))
    assert clients.get(c.id).is_stale
    assert "re-scan" in clients.get(c.id).status()


def test_never_scanned_is_stated_plainly():
    assert clients.add("Acme Ltd").status() == "Never scanned"


def test_removing_a_client_leaves_the_book_consistent():
    c = clients.add("Acme Ltd")
    assert clients.remove(c.id) and clients.all_clients() == []
    assert clients.remove(c.id) is False


def test_a_supplied_website_is_trusted_but_a_missing_one_is_not_silent():
    """'Optional' must never mean 'no consequence'. The domain is the strongest control there is,
    and a client without one is more likely to produce a confident report about someone else."""
    typed = clients.add("Acme Ltd", "acme.ie")
    assert typed.domain_status == "confirmed" and typed.identity_warning is None

    blank = clients.add("Beta Foods")
    assert blank.domain_status == "unknown"
    assert "may be about another company" in blank.identity_warning


def test_a_resolved_domain_is_a_suggestion_not_a_fact():
    c = clients.add("Beta Foods")
    clients.suggest_domain(c.id, "betafoods.ie")
    again = clients.get(c.id)
    assert again.domain == "betafoods.ie"
    assert again.domain_status == "suggested"
    assert "not confirmed" in again.identity_warning     # still flagged until she looks


def test_confirming_settles_it():
    c = clients.add("Beta Foods")
    clients.suggest_domain(c.id, "betafoods.ie")
    assert clients.confirm_domain(c.id).identity_warning is None


def test_confirming_can_correct_a_wrong_suggestion():
    c = clients.add("Gamma")
    clients.suggest_domain(c.id, "gamma-ray-detectors.com")   # plausible, wrong company
    fixed = clients.confirm_domain(c.id, "gamma.app")
    assert fixed.domain == "gamma.app" and fixed.domain_status == "confirmed"


def test_unresolvable_is_distinct_from_not_yet_tried():
    c = clients.add("Obscure Ltd")
    assert "looking" not in (c.identity_warning or "")     # 'unknown' = not yet tried
    clients.suggest_domain(c.id, None)
    assert clients.get(c.id).domain_status == "unresolved"


def test_clients_awaiting_resolution_are_queryable():
    clients.add("Has One", "x.ie")
    clients.add("Needs One")
    assert [c.name for c in clients.needs_domain()] == ["Needs One"]
