"""External research tools.

Each adapter reports its own availability. A missing key is not a crash and not a silent skip — it
becomes an `UnavailableSource` that the report names, because a scan that quietly loses a source and
reports a clean bill of health is the worst output this system can produce.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from .schemas import UnavailableSource

TIMEOUT = 30


@dataclass
class ToolResult:
    """Hits, plus an explicit account of anything that did not run."""

    hits: list[dict] = field(default_factory=list)
    unavailable: list[UnavailableSource] = field(default_factory=list)

    def __add__(self, other: ToolResult) -> ToolResult:
        return ToolResult(self.hits + other.hits, self.unavailable + other.unavailable)


@retry(
    retry=retry_if_exception_type(requests.RequestException),
    wait=wait_exponential_jitter(initial=1, max=8),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _post(url: str, **kw) -> requests.Response:
    return requests.post(url, timeout=TIMEOUT, **kw)


@retry(
    retry=retry_if_exception_type(requests.RequestException),
    wait=wait_exponential_jitter(initial=1, max=8),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _get(url: str, **kw) -> requests.Response:
    return requests.get(url, timeout=TIMEOUT, **kw)


def _missing(label: str, key: str) -> ToolResult:
    return ToolResult(unavailable=[UnavailableSource(
        label=label, reason=f"{key} not set in the shared key store — source not consulted"
    )])


def web_search(company: str, *, limit: int = 10) -> ToolResult:
    """Serper. Queries are shaped to find the footprint, not opinions about the sector."""
    key = os.getenv("SERPER_API_KEY")
    if not key:
        return _missing("Web search (Serper)", "SERPER_API_KEY")

    queries = [
        f'"{company}" careers OR jobs (AI OR "machine learning" OR automation)',
        f'"{company}" (software OR platform OR vendor OR "powered by")',
        f'"{company}" site:*.com "AI"',
    ]
    hits: list[dict] = []
    try:
        for q in queries:
            r = _post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": key, "Content-Type": "application/json"},
                json={"q": q, "num": limit},
            )
            if r.status_code != 200:
                return ToolResult(hits, [UnavailableSource(
                    label="Web search (Serper)", reason=f"HTTP {r.status_code}")])
            for item in r.json().get("organic", []):
                hits.append({"tool": "search", "title": item.get("title"),
                             "url": item.get("link"), "snippet": item.get("snippet"), "query": q})
    except requests.RequestException as exc:
        return ToolResult(hits, [UnavailableSource(
            label="Web search (Serper)", reason=f"{type(exc).__name__} after retries")])
    return ToolResult(hits)


def news(company: str, *, limit: int = 20) -> ToolResult:
    """NewsAPI. Vendor announcements and deployment coverage — where dates actually live."""
    key = os.getenv("NEWS_API_KEY")
    if not key:
        return _missing("News (NewsAPI)", "NEWS_API_KEY")
    try:
        r = _get(
            "https://newsapi.org/v2/everything",
            params={"q": f'"{company}" AND (AI OR "artificial intelligence")',
                    "pageSize": limit, "sortBy": "publishedAt", "language": "en"},
            headers={"X-Api-Key": key},
        )
        if r.status_code != 200:
            return ToolResult(unavailable=[UnavailableSource(
                label="News (NewsAPI)", reason=f"HTTP {r.status_code}")])
        hits = [{"tool": "news", "title": a.get("title"), "url": a.get("url"),
                 "snippet": a.get("description"), "published_at": a.get("publishedAt")}
                for a in r.json().get("articles", [])]
    except requests.RequestException as exc:
        return ToolResult(unavailable=[UnavailableSource(
            label="News (NewsAPI)", reason=f"{type(exc).__name__} after retries")])
    return ToolResult(hits)


def registry(company: str) -> ToolResult:
    """OpenCorporates. Confirms the organisation exists and fixes its jurisdiction.

    Identity matters more than it looks: 'Barry's Tea' in the evaluation set exists to catch a scan
    that matches a name instead of an organisation.
    """
    key = os.getenv("OPENCORPORATES_API_KEY")
    if not key:
        return _missing("Company registry (OpenCorporates)", "OPENCORPORATES_API_KEY")
    try:
        r = _get("https://api.opencorporates.com/v0.4/companies/search",
                 params={"q": company, "api_token": key, "per_page": 5})
        if r.status_code != 200:
            return ToolResult(unavailable=[UnavailableSource(
                label="Company registry (OpenCorporates)", reason=f"HTTP {r.status_code}")])
        hits = [{"tool": "registry", "name": c["company"].get("name"),
                 "jurisdiction": c["company"].get("jurisdiction_code"),
                 "number": c["company"].get("company_number"),
                 "url": c["company"].get("opencorporates_url"),
                 "status": c["company"].get("current_status")}
                for c in r.json().get("results", {}).get("companies", [])]
    except requests.RequestException as exc:
        return ToolResult(unavailable=[UnavailableSource(
            label="Company registry (OpenCorporates)", reason=f"{type(exc).__name__} after retries")])
    return ToolResult(hits)


def research_all(company: str) -> ToolResult:
    """Run every tool. Availability is reported per tool, never assumed."""
    return web_search(company) + news(company) + registry(company)
