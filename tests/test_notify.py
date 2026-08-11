"""Delivery to n8n. No network — what matters is the payload shape and that failure is not silent."""

import requests

from ai_prescan import notify
from ai_prescan.graph import scan


def _report():
    return scan("Acme Ltd")


def test_payload_is_flat_and_named():
    """n8n maps fields far more easily from a flat object than from nested JSON — the mapping was
    the actual work in the Week 5 Telegram lab."""
    r = _report()
    body = notify.payload(r, "# report")
    assert set(body) >= {"company", "scanned_at", "findings_total", "findings_undetermined",
                         "questions_for_client", "report_markdown"}
    assert all(not isinstance(v, (dict, list)) for v in body.values())
    assert body["company"] == "Acme Ltd"
    assert body["findings_undetermined"] == r.undetermined_count


def test_delivery_failure_is_reported_not_raised(monkeypatch):
    def boom(url, body):
        raise requests.ConnectionError("no route")
    monkeypatch.setattr(notify, "_post", boom)
    res = notify.deliver(_report(), "# report", "https://n8n.test/webhook/x")
    assert res.ok is False and "ConnectionError" in res.reason


def test_non_2xx_is_a_failure(monkeypatch):
    class R:
        status_code = 500
    monkeypatch.setattr(notify, "_post", lambda url, body: R())
    res = notify.deliver(_report(), "# report", "https://n8n.test/webhook/x")
    assert res.ok is False and res.status == 500


def test_success_path(monkeypatch):
    class R:
        status_code = 200
    monkeypatch.setattr(notify, "_post", lambda url, body: R())
    assert notify.deliver(_report(), "# report", "https://n8n.test/webhook/x").ok
