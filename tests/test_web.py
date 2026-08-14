"""The interface. Offline: no scans are run, the worker is never fed.

These test what Maria actually experiences — a queue she can see, history that survives, a report
she can read, and failures phrased in words rather than exception names.
"""

import json

import pytest
from fastapi.testclient import TestClient

from ai_prescan import clients, store_jobs, web
from ai_prescan.store_jobs import Scan


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(store_jobs, "ROOT", tmp_path / "scans")
    monkeypatch.setattr(clients, "PATH", tmp_path / "clients.json")


@pytest.fixture
def client(monkeypatch):
    # Nothing may reach the queue: these tests must never start a real scan.
    monkeypatch.setattr(web._work, "put", lambda item: None)
    return TestClient(web.app)


def test_an_empty_book_says_what_to_do_next(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "client book is empty" in r.text


def test_an_ad_hoc_paste_creates_one_scan_per_line(client, monkeypatch):
    created = []
    monkeypatch.setattr(web._work, "put", lambda item: created.append(item[0].company))
    r = client.post("/scan", data={"names": "Alpha Ltd\n\n  Beta Foods  \nGamma"},
                    follow_redirects=False)
    assert r.status_code == 303
    assert created == ["Alpha Ltd", "Beta Foods", "Gamma"]     # blanks dropped, whitespace trimmed


def test_history_survives_a_restart(client):
    """Scans persist to disk; the client page is where a client's history is shown."""
    c = clients.add("Kept Ltd")
    store_jobs.save(Scan(id="abc123", company="Kept Ltd", client_id=c.id, status="done",
                         findings=2, questions=1))
    assert store_jobs.get("abc123").company == "Kept Ltd"
    assert "abc123" in client.get(f"/client/{c.id}").text


def test_report_page_renders_markdown_as_html_not_raw(client):
    store_jobs.save(Scan(id="rep1", company="Acme", status="done",
                         markdown="## Inventory\n\n| A | B |\n|---|---|\n| 1 | 2 |\n"))
    body = client.get("/scan/rep1").text
    assert "<table>" in body and "<td>1</td>" in body
    assert "|---|---|" not in body                              # not shown raw


def test_report_renders_quotes_without_allowing_raw_html(client):
    """The safety escape must not turn Markdown's `>` marker into visible punctuation."""
    store_jobs.save(Scan(id="quotes", company="Acme", status="done", markdown=(
        "## Evidence\n\n- **Evidence:** [source](https://example.test)\n"
        "    - published: 2026-08-14\n"
        "    - > Exact quoted support from the source.\n\n"
        "## Method and notice\n\n> This is a pre-scan, not legal advice.\n\n"
        "<img src=x onerror=alert(1)>\n")))

    body = client.get("/scan/quotes").text

    assert body.count("<blockquote>") == 2
    assert "&gt; Exact quoted support" not in body
    assert "<img src=x" not in body
    assert "&lt;img src=x onerror=alert(1)&gt;" in body


def test_scans_stored_before_structured_questions_still_show_them(client):
    """Backward compatibility: history on disk predates question_items, and dropping the card for
    those scans would undo the persistence it was added to protect."""
    store_jobs.save(Scan(id="q1", company="Acme", status="done", markdown=(
        "## Inventory\n\nstuff\n\n"
        "## Questions to discuss with the client\n\n- Have you modified it?\n\n"
        "## What this scan could not see\n\n- things\n")))
    body = client.get("/scan/q1").text
    assert "Ask Acme" in body
    # the question block must appear before the full report card
    assert body.index("Have you modified it?") < body.index('class="card report"')


def test_failure_is_phrased_for_a_person(client):
    store_jobs.save(Scan(id="f1", company="Acme", status="failed",
                         error="The scan could not finish (TimeoutError). Nothing was reported."))
    body = client.get("/scan/f1").text
    assert "could not finish" in body
    assert "Traceback" not in body


def test_report_downloads_as_markdown(client):
    store_jobs.save(Scan(id="d1", company="Acme", status="done", markdown="# AI PRE-SCAN\n"))
    r = client.get("/scan/d1.md")
    assert r.status_code == 200 and r.text.startswith("# AI PRE-SCAN")
    assert r.headers["content-disposition"] == 'attachment; filename="acme-ai-prescan.md"'
    assert r.headers["x-content-type-options"] == "nosniff"


def test_missing_report_download_is_a_real_404(client):
    assert client.get("/scan/missing.md").status_code == 404


def test_summary_line_reads_in_plain_english():
    s = Scan(id="x", company="Acme", status="done", findings=1, undetermined=2, questions=3)
    assert s.summary_line() == "1 system · 2 undetermined · 3 questions to ask"


def test_unknown_scan_does_not_500(client):
    assert "no longer exists" in client.get("/scan/nope").text


def test_a_line_may_carry_the_client_domain():
    """A bare name is ambiguous — 'Gamma' matched a French entity in the registry and a Sony TV
    review in search. The adviser knows her clients' websites, so she can settle it herself."""
    assert web.parse_line("Acme Ltd") == ("Acme Ltd", None)
    assert web.parse_line("Acme Ltd, acme.ie") == ("Acme Ltd", "acme.ie")
    assert web.parse_line("Acme Ltd, https://www.acme.ie/") == ("Acme Ltd", "acme.ie")
    assert web.parse_line("Acme Ltd,   ") == ("Acme Ltd", None)


def test_supplied_domain_is_carried_onto_the_scan(client, monkeypatch):
    created = []
    monkeypatch.setattr(web._work, "put", lambda item: created.append(item[0]))
    client.post("/scan", data={"names": "Acme Ltd, acme.ie\nBeta Foods"}, follow_redirects=False)
    assert [(s.company, s.domain) for s in created] == [("Acme Ltd", "acme.ie"), ("Beta Foods", None)]


def test_the_book_shows_which_entity_a_client_resolves_to(client):
    clients.add("Acme Ltd", "acme.ie")
    assert "acme.ie" in client.get("/").text


def test_demo_mode_does_not_promise_a_website_lookup_it_will_never_run(client, monkeypatch):
    monkeypatch.setattr(web, "DEMO", True)
    clients.add("Northstar Research Ltd")
    body = client.get("/").text
    assert "Website required in demo" in body
    assert "looking up website" not in body


def test_demo_mode_refuses_to_report_on_a_company_outside_its_checked_corpus(client, monkeypatch):
    monkeypatch.setattr(web, "DEMO", True)
    scan = Scan(id="unknown-demo", company="Northstar Research Ltd")
    web._run_one(scan, None)
    assert scan.status == "failed"
    assert "no checked sample data" in scan.error
    assert scan.markdown == ""


def test_one_scan_lands_on_that_scan_but_a_batch_lands_on_the_book(client, monkeypatch):
    """Scanning one client is reactive — she is waiting for that answer. A batch is a sweep she
    comes back to. Sending both to the same place gets one of them wrong."""
    monkeypatch.setattr(web._work, "put", lambda item: None)

    one = client.post("/scan", data={"names": "Acme Ltd"}, follow_redirects=False)
    assert one.status_code == 303 and one.headers["location"].startswith("/scan/")

    many = client.post("/scan", data={"names": "Acme Ltd\nBeta Foods"}, follow_redirects=False)
    assert many.status_code == 303 and many.headers["location"] == "/"


def test_a_running_scan_says_what_it_is_doing(client):
    store_jobs.save(Scan(id="run1", company="Acme Ltd", status="running"))
    body = client.get("/scan/run1").text
    assert "Researching" in body
    assert "careers pages" in body          # tells her what is happening, not just that it is
    assert 'http-equiv="refresh"' in body   # and updates itself


def test_selecting_clients_scans_exactly_those(client, monkeypatch):
    a = clients.add("Alpha Ltd", "alpha.ie")
    clients.add("Beta Ltd")
    started = []
    monkeypatch.setattr(web._work, "put", lambda item: started.append(item[0]))
    client.post("/scan-selected", data={"client": [a.id]}, follow_redirects=False)
    assert [(s.company, s.domain, s.client_id) for s in started] == [("Alpha Ltd", "alpha.ie", a.id)]


def test_scan_every_client_covers_the_whole_book(client, monkeypatch):
    clients.add("Alpha Ltd"); clients.add("Beta Ltd"); clients.add("Gamma Ltd")
    started = []
    monkeypatch.setattr(web._work, "put", lambda item: started.append(item[0]))
    client.post("/scan-selected", data={"all": "1"}, follow_redirects=False)
    assert sorted(s.company for s in started) == ["Alpha Ltd", "Beta Ltd", "Gamma Ltd"]


def test_the_book_flags_never_scanned_and_overdue(client):
    clients.add("Fresh Ltd")
    body = client.get("/").text
    assert "Never scanned" in body and "never scanned" in body   # in the row and in the summary


def test_a_prospect_scan_does_not_join_the_book(client, monkeypatch):
    monkeypatch.setattr(web._work, "put", lambda item: None)
    client.post("/scan", data={"names": "Prospect Ltd"}, follow_redirects=False)
    assert clients.all_clients() == []


def test_client_page_offers_a_rescan(client):
    c = clients.add("Acme Ltd")
    body = client.get(f"/client/{c.id}").text
    assert "Scan now" in body                       # never scanned yet
    assert "vendor quietly adding AI" in body       # says why re-scanning matters


def _headings(body: str) -> list[str]:
    """Card headings in page order. Comparing raw string positions is unsafe — "Client book" is
    also the <title>, which precedes all body content and silently inverts the comparison."""
    import re
    return re.findall(r"<h2[^>]*>([^<]+)</h2>", body)


def test_an_empty_book_puts_adding_clients_first(client):
    """A new user should meet the thing they need, not an accordion under an empty table."""
    body = client.get("/").text
    assert _headings(body) == ["Add your clients", "Client book"]
    assert "client book is empty" in body


def test_a_populated_book_puts_the_list_first(client):
    """Once she has a book, the list she came to read is the first thing on the page."""
    clients.add("Acme Ltd", "acme.ie")
    assert _headings(client.get("/").text) == ["Client book", "Add clients"]


def test_filters_narrow_the_book(client):
    fresh = clients.add("Never Ltd")
    done = clients.add("Done Ltd")
    clients.record_scan(done.id, Scan(id="s", company="Done Ltd", status="done",
                                      finished_at="2026-08-11T09:00:00+00:00"))
    only_never = client.get("/?filter=never").text
    assert "Never Ltd" in only_never and "Done Ltd" not in only_never


def test_a_row_can_be_scanned_without_ticking_anything(client, monkeypatch):
    c = clients.add("Acme Ltd", "acme.ie")
    started = []
    monkeypatch.setattr(web._work, "put", lambda item: started.append(item[0]))
    r = client.post("/scan-selected", data={"scan_one": c.id}, follow_redirects=False)
    assert [s.company for s in started] == ["Acme Ltd"]
    assert r.headers["location"].startswith("/scan/")     # one client, so go to it


def test_a_row_scan_is_not_overridden_by_scan_all(client, monkeypatch):
    """Both controls live in one form; the row button must win over a stray 'all'."""
    a = clients.add("Alpha"); clients.add("Beta"); clients.add("Gamma")
    started = []
    monkeypatch.setattr(web._work, "put", lambda item: started.append(item[0]))
    client.post("/scan-selected", data={"scan_one": a.id, "all": "1"}, follow_redirects=False)
    assert [s.company for s in started] == ["Alpha"]


def test_the_report_is_printable(client):
    store_jobs.save(Scan(id="p1", company="Acme", status="done", markdown="## Inventory\n\nx\n"))
    body = client.get("/scan/p1").text
    assert "@media print" in body                      # she hands this to a client


def test_wide_inventory_is_contained_for_small_screens(client):
    store_jobs.save(Scan(id="mobile", company="Acme", status="done", markdown=(
        "## Inventory\n\n| A | B | C | D | E | F | G | H |\n"
        "|---|---|---|---|---|---|---|---|\n| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |\n")))
    body = client.get("/scan/mobile").text
    assert 'class="table-scroll"' in body
    assert 'aria-label="AI system inventory"' in body
    assert "@media(max-width:680px)" in body


def test_form_controls_have_labels(client):
    clients.add("Acme Ltd", "acme.ie")
    body = client.get("/").text
    assert 'for="client-lines"' in body
    assert 'for="prospect-names"' in body
    assert 'for="pickall"' in body
    assert "Select Acme Ltd" in body


def test_questions_and_their_reasons_are_not_sibling_bullets(client):
    """Three questions rendered as six bullets read as six questions. The reason must be visibly
    subordinate to the question it belongs to."""
    store_jobs.save(Scan(id="qq", company="Acme", status="done", markdown="## Inventory\n\nx\n",
        question_items=[
            {"question": "Have you modified it?", "why": "It changes the role.", "standing": True},
            {"question": "Is X in use?", "why": "The page carries no date.", "standing": False},
        ]))
    body = client.get("/scan/qq").text
    assert "<ol class='qs'>" in body
    assert body.count("<li>") == 2                       # two questions, not four bullets
    assert "class='why'" in body                          # reason is subordinate markup
    assert "Ask Acme — 2 questions" in body


def test_the_standing_question_is_tagged_not_duplicated(client):
    store_jobs.save(Scan(id="q2", company="Acme", status="done", markdown="x",
        question_items=[{"question": "Have you modified it?", "why": "Role.", "standing": True}]))
    body = client.get("/scan/q2").text
    assert "always asked" in body and body.count("<li>") == 1
