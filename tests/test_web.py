"""The interface. Offline: no scans are run, the worker is never fed.

These test what Maria actually experiences — a queue she can see, history that survives, a report
she can read, and failures phrased in words rather than exception names.
"""

import json

import pytest
from fastapi.testclient import TestClient

from ai_prescan import store_jobs, web
from ai_prescan.store_jobs import Scan


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(store_jobs, "ROOT", tmp_path / "scans")


@pytest.fixture
def client(monkeypatch):
    # Nothing may reach the queue: these tests must never start a real scan.
    monkeypatch.setattr(web._work, "put", lambda item: None)
    return TestClient(web.app)


def test_dashboard_loads_with_no_history(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "No scans yet" in r.text


def test_a_pasted_client_list_creates_one_scan_per_line(client, monkeypatch):
    created = []
    monkeypatch.setattr(web._work, "put", lambda item: created.append(item[0].company))
    r = client.post("/scan", data={"names": "Alpha Ltd\n\n  Beta Foods  \nGamma"},
                    follow_redirects=False)
    assert r.status_code == 303
    assert created == ["Alpha Ltd", "Beta Foods", "Gamma"]     # blanks dropped, whitespace trimmed


def test_history_survives_a_restart(client):
    store_jobs.save(Scan(id="abc123", company="Kept Ltd", status="done", findings=2, questions=1))
    assert store_jobs.get("abc123").company == "Kept Ltd"      # read back from disk
    assert "Kept Ltd" in client.get("/").text


def test_report_page_renders_markdown_as_html_not_raw(client):
    store_jobs.save(Scan(id="rep1", company="Acme", status="done",
                         markdown="## Inventory\n\n| A | B |\n|---|---|\n| 1 | 2 |\n"))
    body = client.get("/scan/rep1").text
    assert "<table>" in body and "<td>1</td>" in body
    assert "|---|---|" not in body                              # not shown raw


def test_questions_are_lifted_above_the_report(client):
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


def test_summary_line_reads_in_plain_english():
    s = Scan(id="x", company="Acme", status="done", findings=1, undetermined=2, questions=3)
    assert s.summary_line() == "1 system · 2 undetermined · 3 questions to ask"


def test_unknown_scan_does_not_500(client):
    assert "no longer exists" in client.get("/scan/nope").text
