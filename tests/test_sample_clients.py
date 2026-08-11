"""The sample book. Real companies, verified domains, and a mix that demos both behaviours."""

import pytest

from ai_prescan import clients, sample_clients


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(clients, "PATH", tmp_path / "clients.json")


def test_every_sample_has_a_verified_domain():
    for s in sample_clients.SAMPLES:
        assert s.domain and "." in s.domain
        assert not s.domain.startswith(("http", "www."))     # stored the way scans need it


def test_clay_points_at_the_platform_not_the_country_singer():
    """Identity resolution returned claywalker.com for 'Clay'. That is the exact failure this
    project exists to catch, and it would have shipped inside the demo data."""
    clay = next(s for s in sample_clients.SAMPLES if s.name == "Clay")
    assert clay.domain == "clay.com"


def test_the_mix_demonstrates_restraint_as_well_as_capability():
    """A demo that only shows findings does not show the harder behaviour."""
    names = {s.name for s in sample_clients.SAMPLES}
    assert {"Personio", "WHOOP", "Matterport"} <= names          # produce findings
    assert {"Keogh's Crisps", "Barry's Tea", "Ballymaloe Foods"} <= names   # correctly produce none


def test_samples_load_into_the_book_with_domains_confirmed():
    added, skipped = clients.import_lines(sample_clients.as_import_lines())
    assert added == len(sample_clients.SAMPLES) and skipped == 0
    book = clients.all_clients()
    assert all(c.domain_status == "confirmed" for c in book)     # no unconfirmed identities
    assert clients.find_by_name("Clay").domain == "clay.com"


def test_loading_twice_does_not_duplicate():
    clients.import_lines(sample_clients.as_import_lines())
    added, skipped = clients.import_lines(sample_clients.as_import_lines())
    assert added == 0 and skipped == len(sample_clients.SAMPLES)
