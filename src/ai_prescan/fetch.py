"""Fetching, with provenance attached at the point of retrieval.

Provenance is built here and nowhere else. If a caller could construct a source record without
fetching, the contract would be advisory; building it only on a real response makes it structural.

Some hosts block scripted fetches outright — whoop.com returns 403 to any header combination while
serving a browser normally. Those are recorded as unavailable and named in the report. A host we
cannot read is not a host with nothing to say.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Callable

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from .schemas import AuthorityClass, CurrentnessStatus, SourceProvenance

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Upgrade-Insecure-Requests": "1",
}

REVIEW_DAYS = {
    AuthorityClass.COMPANY: 90,
    AuthorityClass.VENDOR: 60,
    AuthorityClass.REGISTRY: 180,
    AuthorityClass.NEWS: 365,
    AuthorityClass.OTHER: 60,
}

_DATE_PATTERNS = [
    re.compile(rb'property=["\']article:published_time["\']\s+content=["\']([^"\']+)', re.I),
    re.compile(rb'"datePublished"\s*:\s*"([^"]+)"', re.I),
    re.compile(rb"<time[^>]+datetime=[\"']([^\"']+)", re.I),
]
_TAGS = re.compile(rb"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
_MARKUP = re.compile(rb"<[^>]+>")

# Set by the host application when a browser-backed fetcher is available.
# Signature: (url) -> tuple[str, bytes] | None  ->  (final_url, content)
browser_fetch: Callable[[str], tuple[str, bytes] | None] | None = None


@dataclass
class FetchResult:
    url: str
    ok: bool
    provenance: SourceProvenance | None = None
    text: str = ""
    unavailable_reason: str | None = None


def _published(body: bytes) -> date | None:
    for pat in _DATE_PATTERNS:
        m = pat.search(body)
        if m:
            raw = m.group(1).decode("utf-8", "ignore")[:10]
            try:
                return datetime.strptime(raw, "%Y-%m-%d").date()
            except ValueError:
                continue
    return None


def to_text(body: bytes) -> str:
    stripped = _MARKUP.sub(b" ", _TAGS.sub(b" ", body))
    return re.sub(r"\s+", " ", stripped.decode("utf-8", "ignore")).strip()


def classify(url: str) -> AuthorityClass:
    host = url.split("/")[2].lower() if "://" in url else ""
    if any(h in host for h in ("eur-lex", "companieshouse", "opencorporates")):
        return AuthorityClass.REGISTRY
    if any(h in host for h in ("irishtimes", "businesswire", "globenewswire", "reuters", "ft.com")):
        return AuthorityClass.NEWS
    if any(h in host for h in ("fin.ai", "teamtailor", "intercom.com")):
        return AuthorityClass.VENDOR
    return AuthorityClass.COMPANY


@retry(
    retry=retry_if_exception_type(requests.RequestException),
    wait=wait_exponential_jitter(initial=1, max=8),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _get(url: str) -> requests.Response:
    return requests.get(url, headers=HEADERS, timeout=30)


def fetch(url: str, *, now: datetime | None = None) -> FetchResult:
    """Retrieve a page and build its provenance. Never raises — failure is data."""
    now = now or datetime.now(timezone.utc)
    final_url, content = url, None

    try:
        r = _get(url)
        if r.status_code == 200 and r.content and r.content.strip():
            final_url, content = r.url, r.content
        elif r.status_code in (401, 403, 429) and browser_fetch is not None:
            got = browser_fetch(url)          # blocked to scripts, readable in a browser
            # Test the content, not the tuple. ("url", b"") is truthy, and an empty body was being
            # hashed and shipped as a source attesting to nothing — the sha256 of "" with
            # provenance attached. A Cloudflare interstitial at HTTP 200 does the same.
            if got and got[1] and got[1].strip():
                final_url, content = got
        if content is None:
            status = r.status_code
            if status == 200:
                reason = "HTTP 200 but the page returned no readable content"
            elif status in (401, 403, 429):
                reason = (f"HTTP {status} — host blocks scripted fetches"
                          + ("; the browser fallback could not read it either"
                             if browser_fetch is not None else
                             " and no browser fetcher is configured"))
            else:
                reason = f"HTTP {status}"
            return FetchResult(url, False, unavailable_reason=reason)
    except requests.RequestException as exc:
        return FetchResult(url, False, unavailable_reason=f"{type(exc).__name__} after retries")

    authority = classify(final_url)
    pub = _published(content)

    # A 200 proves the page is *served* now. It does not prove the content is current — the
    # superseded EU AI Act text returns 200 today. Treating retrieval as a currentness check was
    # circular, and it silently disabled two of the gate's three rules: across every evaluation
    # report, 68 of 68 evidence items were stamped `current`, so the SUPERSEDED and UNKNOWN
    # branches had never executed in production.
    #
    # Currency now needs a positive signal from the source itself: a date inside the review window
    # for this class of source. Without one the status is `unknown`, which is not a failure — it
    # routes present-tense claims to `undetermined` and a question, which is the designed outcome.
    window = timedelta(days=REVIEW_DAYS[authority])
    dated_recently = bool(pub and (now.date() - pub) <= window)
    status = CurrentnessStatus.CURRENT if dated_recently else CurrentnessStatus.UNKNOWN

    prov = SourceProvenance(
        canonical_url=final_url,
        retrieved_at=now,
        content_sha256=hashlib.sha256(content).hexdigest(),
        authority_class=authority,
        source_published_at=pub,
        undated_reason=None if pub else "page carries no machine-readable publication date",
        currentness_checked_at=now if dated_recently else None,
        currentness_status=status,
        next_review_at=(now + window) if dated_recently else None,
    )
    return FetchResult(final_url, True, provenance=prov, text=to_text(content))
