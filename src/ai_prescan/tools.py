"""External research tools.

Each adapter reports its own availability. A missing key is not a crash and not a silent skip — it
becomes an `UnavailableSource` that the report names, because a scan that quietly loses a source and
reports a clean bill of health is the worst output this system can produce.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from . import config
from .schemas import UnavailableSource

TIMEOUT = 30

# Load the shared key store on import. Without this, only the CLI has keys, and every other entry
# point silently reports every tool as unconfigured — a wiring fault that looks exactly like a
# missing key, which is the most misleading failure this module could have.
config.load()


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


def web_search(company: str, *, domain: str | None = None, limit: int = 10) -> ToolResult:
    """Serper. Queries are shaped to find the footprint, not opinions about the sector.

    When the company's own domain is known, the first two queries are scoped to it. Pages on the
    company's own site are about the company by construction, which is far stronger evidence than a
    name match anywhere on the web.
    """
    key = os.getenv("SERPER_API_KEY")
    if not key:
        return _missing("Web search (Serper)", "SERPER_API_KEY")

    scope = f" site:{domain}" if domain else ""
    queries = [
        f'"{company}"{scope} careers OR jobs (AI OR "machine learning" OR automation)',
        f'"{company}"{scope} (software OR platform OR vendor OR "powered by")',
        f'"{company}" ("uses" OR "deployed" OR "implemented") (AI OR "artificial intelligence")',
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


WIKIDATA_UA = "AI-Pre-Scan/0.1 (Ironhack bootcamp project; github.com/nyelugo/PROJECT-AI-Pre-Scan)"


@dataclass
class Identity:
    """Who the company actually is, and where its own words live.

    `domain` is the most valuable field in the whole pipeline. A page on the company's own domain is
    about the company by construction, which is the cheapest possible answer to the name-collision
    problem that produced a Sony TV review for a company called Gamma.
    """

    query: str
    legal_name: str | None = None
    jurisdiction: str | None = None
    status: str | None = None
    lei: str | None = None
    domain: str | None = None
    sources: list[str] = field(default_factory=list)
    unavailable: list[UnavailableSource] = field(default_factory=list)

    @property
    def resolved(self) -> bool:
        """Only a domain counts.

        An LEI obtained by matching a name is not identity — GLEIF returns a French entity called
        GAMMA for a query of "Gamma", and a Personio Foundation for "Personio". Treating either as
        confirmation would move the name-collision failure into the identity layer, where it would
        then vouch for everything downstream.
        """
        return bool(self.domain)


def _gleif(company: str, ident: Identity) -> None:
    """GLEIF — free, keyless, global. Legal identity for registered entities."""
    try:
        r = _get("https://api.gleif.org/api/v1/lei-records",
                 params={"filter[entity.legalName]": company, "page[size]": 1})
        if r.status_code != 200:
            ident.unavailable.append(UnavailableSource(label="Registry (GLEIF)", reason=f"HTTP {r.status_code}"))
            return
        data = r.json().get("data", [])
        if not data:
            return                      # no LEI is normal for an SME, not a failure
        attrs = data[0]["attributes"]
        entity = attrs["entity"]
        if not _same_entity(company, entity["legalName"]["name"]):
            # A name-filter hit is not the same company. Recording it would be worse than
            # recording nothing, because it would look like confirmation.
            return
        ident.legal_name = entity["legalName"]["name"]
        ident.jurisdiction = entity.get("jurisdiction")
        ident.status = entity.get("status")
        ident.lei = attrs.get("lei")
        ident.sources.append("https://api.gleif.org/api/v1/lei-records")
    except requests.RequestException as exc:
        ident.unavailable.append(UnavailableSource(label="Registry (GLEIF)", reason=f"{type(exc).__name__} after retries"))


def _wikidata_domain(company: str, ident: Identity) -> None:
    """Wikidata — free, keyless, needs a descriptive User-Agent. Sparse for SMEs, exact when present."""
    try:
        hits = _get("https://www.wikidata.org/w/api.php", headers={"User-Agent": WIKIDATA_UA},
                    params={"action": "wbsearchentities", "search": company, "language": "en",
                            "format": "json", "limit": 1, "type": "item"}).json().get("search", [])
        if not hits:
            return
        qid = hits[0]["id"]
        claims = _get(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json",
                      headers={"User-Agent": WIKIDATA_UA}).json()["entities"][qid]["claims"]
        site = claims.get("P856", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value")
        if site:
            ident.domain = ident.domain or _host(site)
            ident.sources.append(f"https://www.wikidata.org/wiki/{qid}")
    except (requests.RequestException, KeyError, IndexError, ValueError):
        pass                            # sparse coverage is expected; absence is not an outage


def _serper_domain(company: str, ident: Identity) -> None:
    """Serper's knowledge graph names an official site for many SMEs that Wikidata never lists."""
    key = os.getenv("SERPER_API_KEY")
    if not key or ident.domain:
        return
    try:
        r = _post("https://google.serper.dev/search",
                  headers={"X-API-KEY": key, "Content-Type": "application/json"},
                  json={"q": f"{company} official website", "num": 5})
        if r.status_code != 200:
            return
        body = r.json()
        site = (body.get("knowledgeGraph") or {}).get("website")
        if not site and body.get("organic"):
            site = body["organic"][0].get("link")
        if site:
            ident.domain = _host(site)
            ident.sources.append("https://google.serper.dev/search")
    except requests.RequestException:
        pass


_SUFFIXES = re.compile(
    r"\b(se|ag|gmbh|ltd|limited|plc|inc|incorporated|llc|l\.l\.c|bv|b\.v|nv|n\.v|ab|as|a/s|oy|"
    r"sa|s\.a|sas|sarl|spa|s\.p\.a|kg|co|company|holdings?|group|international)\b|[.,&]",
    re.I,
)


def _norm_name(name: str) -> str:
    return re.sub(r"\s+", " ", _SUFFIXES.sub(" ", name)).strip().lower()


def _same_entity(query: str, legal_name: str) -> bool:
    """Accept a registry record only when the names match once corporate suffixes are removed.

    Deliberately strict. "Personio" and "Personio Foundation" are different organisations, and
    treating the second as the first is exactly the error this check exists to stop.
    """
    return _norm_name(query) == _norm_name(legal_name)


def _host(url: str) -> str | None:
    if "://" not in url:
        return None
    return url.split("/")[2].lower().removeprefix("www.")


def identity(company: str) -> Identity:
    """Resolve who this company is and which domain is theirs.

    Replaces OpenCorporates, which is not free. GLEIF and Wikidata are keyless; Serper is already
    provisioned. Between them they cover legal identity and the official domain without new spend.
    """
    ident = Identity(query=company)
    _gleif(company, ident)
    _wikidata_domain(company, ident)
    _serper_domain(company, ident)
    if not ident.resolved:
        ident.unavailable.append(UnavailableSource(
            label="Company identity",
            reason="no official domain could be resolved — findings rest on name matching alone "
                   "and are weaker for it"))
    return ident


def research_all(company: str, domain: str | None = None) -> ToolResult:
    """Run every tool. Availability is reported per tool, never assumed."""
    return web_search(company, domain=domain) + news(company)
