"""Hand a finished report to n8n.

This is the seam between the two stacks, and it is deliberately thin. LangGraph does the research
and the deciding; n8n does the operational half — filing the report where the adviser already works,
and later, scheduling sweeps across a client list.

Delivery failure is reported, never silent, and never fatal: a report that was produced but not
filed is still a report. Losing it quietly would be the same class of error as a scan that drops a
source and reports a clean bill of health.
"""

from __future__ import annotations

from dataclasses import dataclass

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from .schemas import Confidence, Report

TIMEOUT = 30


@dataclass
class DeliveryResult:
    ok: bool
    status: int | None = None
    reason: str | None = None


def payload(report: Report, markdown: str) -> dict:
    """What n8n receives.

    Flat and named, so the workflow can map fields without expressions that reach into nested JSON —
    the same lesson as the Week 5 Telegram lab, where the mapping was the actual work.
    """
    return {
        "company": report.company,
        "scanned_at": report.scanned_at.isoformat(),
        "sources_consulted": report.sources_consulted,
        "findings_total": len(report.findings),
        "findings_evidenced": sum(
            1 for f in report.findings if f.confidence is Confidence.EVIDENCED
        ),
        "findings_undetermined": report.undetermined_count,
        "questions_for_client": len(report.discussion),
        "unavailable_sources": len(report.unavailable_sources),
        "scan_version": report.scan_version,
        "report_markdown": markdown,
    }


@retry(
    retry=retry_if_exception_type(requests.RequestException),
    wait=wait_exponential_jitter(initial=1, max=8),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _post(url: str, body: dict) -> requests.Response:
    return requests.post(url, json=body, timeout=TIMEOUT)


def deliver(report: Report, markdown: str, webhook_url: str) -> DeliveryResult:
    """POST the report to an n8n webhook. Never raises."""
    try:
        r = _post(webhook_url, payload(report, markdown))
    except requests.RequestException as exc:
        return DeliveryResult(False, None, f"{type(exc).__name__} after retries")
    if r.status_code >= 300:
        return DeliveryResult(False, r.status_code, f"n8n returned HTTP {r.status_code}")
    return DeliveryResult(True, r.status_code)
