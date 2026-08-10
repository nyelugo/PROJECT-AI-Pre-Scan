"""Migrate eval/ground_truth.json onto the source-provenance contract.

The seed file predates the contract in docs/architecture.md. Every source must be re-fetched and
hashed; nothing may be back-filled from the top-level `_verified_on` date, because that date records
when a human looked, not whether the page was current.

    python eval/migrate_provenance.py            # dry run, reports what would change
    python eval/migrate_provenance.py --write     # rewrite ground_truth.json in place

Fetch failures are recorded, not hidden. A source we could not reach today is a source whose
currentness is unknown, and the preflight is supposed to reject it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

GT = Path(__file__).with_name("ground_truth.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

# How long a class of source stays trustworthy before it must be re-checked.
REVIEW_DAYS = {"company": 90, "vendor": 60, "registry": 180, "news": 365, "other": 60}

DATE_PATTERNS = [
    re.compile(rb'property=["\']article:published_time["\']\s+content=["\']([^"\']+)', re.I),
    re.compile(rb'name=["\']publish(?:ed)?[-_]?date["\']\s+content=["\']([^"\']+)', re.I),
    re.compile(rb'"datePublished"\s*:\s*"([^"]+)"', re.I),
    re.compile(rb"<time[^>]+datetime=[\"']([^\"']+)", re.I),
]


def authority_for(url: str, declared: str | None) -> str:
    if declared in REVIEW_DAYS:
        return declared
    host = url.split("/")[2].lower() if "://" in url else ""
    if "eur-lex" in host or "companieshouse" in host:
        return "registry"
    if any(h in host for h in ("irishtimes", "businesswire", "globenewswire")):
        return "news"
    return "vendor" if any(h in host for h in ("fin.ai", "teamtailor")) else "company"


@retry(
    retry=retry_if_exception_type(requests.RequestException),
    wait=wait_exponential_jitter(initial=1, max=8),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _get(url: str) -> requests.Response:
    return requests.get(url, headers={"User-Agent": UA}, timeout=30)


def published_date(body: bytes) -> str | None:
    for pat in DATE_PATTERNS:
        m = pat.search(body)
        if m:
            raw = m.group(1).decode("utf-8", "ignore")[:10]
            try:
                datetime.strptime(raw, "%Y-%m-%d")
                return raw
            except ValueError:
                continue
    return None


def fetch_provenance(url: str, declared_authority: str | None, now: datetime) -> dict:
    """Fetch once, hash the bytes, and record what the page itself says about its date."""
    authority = authority_for(url, declared_authority)
    prov: dict = {
        "canonical_url": url,
        "retrieved_at": now.isoformat(),
        "authority_class": authority,
        "content_sha256": None,
        "source_published_at": None,
        "source_updated_at": None,
        "undated_reason": None,
        "currentness_checked_at": None,
        "currentness_status": "unknown",
        "superseded_by": None,
        "next_review_at": None,
    }
    try:
        r = _get(url)
    except requests.RequestException as exc:
        prov["undated_reason"] = f"fetch failed: {type(exc).__name__}"
        prov["fetch_error"] = str(exc)[:200]
        return prov

    prov["http_status"] = r.status_code
    if r.status_code != 200:
        prov["undated_reason"] = f"fetch returned HTTP {r.status_code}"
        return prov

    prov["canonical_url"] = r.url  # after redirects
    prov["content_sha256"] = hashlib.sha256(r.content).hexdigest()
    pub = published_date(r.content)
    if pub:
        prov["source_published_at"] = pub
    else:
        prov["undated_reason"] = "page carries no machine-readable publication date"
    # Reaching the canonical URL and hashing what it serves today IS the currentness check.
    prov["currentness_checked_at"] = now.isoformat()
    prov["currentness_status"] = "current"
    prov["next_review_at"] = (now + timedelta(days=REVIEW_DAYS[authority])).isoformat()
    return prov


def claim_time_mode(system: dict) -> str:
    """A dated announcement evidences a historical event. Everything else asserts present state.

    Stated as a rule rather than decided per entry, so the classification is reviewable.
    """
    return "historical_event" if system.get("first_evidenced") else "current_state"


def iter_systems(data: dict):
    for band in ("rich_footprint", "single_system", "capability_present", "thin"):
        for company in data.get(band, []):
            for system in company.get("systems", []):
                yield band, company, system


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="rewrite ground_truth.json in place")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    data = json.loads(GT.read_text())
    cache: dict[str, dict] = {}
    rows, failures = [], 0

    for band, company, system in iter_systems(data):
        urls = [u for u in (system.get("source"), system.get("vendor_source"),
                            system.get("customer_source")) if u]
        if not urls:
            continue
        system["claim_time_mode"] = claim_time_mode(system)
        provs = []
        for url in urls:
            if url not in cache:
                cache[url] = fetch_provenance(url, system.get("authority_class"), now)
            provs.append(cache[url])
        system["source_provenance"] = provs[0] if len(provs) == 1 else provs

        ok = all(p["currentness_status"] == "current" for p in provs)
        failures += not ok
        rows.append((company["company"][:34], system["claim_time_mode"], "ok" if ok else
                     provs[0].get("undated_reason", "unreachable")[:40]))

    print(f"{'company':<36} {'claim mode':<18} provenance")
    print("-" * 84)
    for c, m, s in rows:
        print(f"{c:<36} {m:<18} {s}")
    print(f"\n{len(rows)} system entries · {len(cache)} unique sources · {failures} without usable provenance")

    if args.write:
        data["_provenance_migrated_at"] = now.isoformat()
        data["_migration_note"] = (
            "Provenance fetched by eval/migrate_provenance.py. Entries whose currentness_status is "
            "not 'current' fail the preflight and cannot back a current-state claim."
        )
        GT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"\nwrote {GT}")
    else:
        print("\ndry run — pass --write to apply")

    # Preflight mirrors the gate in src/ai_prescan/gate.py. Two rules, not one: a current-state
    # claim needs a source checked as current, and a historical claim needs a publication date.
    # Checking only the first is how an unusable historical source passes as fine.
    def _provs(system):
        sp = system.get("source_provenance")
        return sp if isinstance(sp, list) else [sp] if sp else []

    blocking: list[str] = []
    for _band, comp, system in iter_systems(data):
        provs = _provs(system)
        if not provs:
            continue
        mode = system.get("claim_time_mode")
        if mode == "current_state":
            if not all(p["currentness_status"] == "current" for p in provs):
                blocking.append(f"{comp['company']} (current-state source not established as current)")
        elif mode == "historical_event":
            if not any(p.get("source_published_at") for p in provs):
                blocking.append(f"{comp['company']} (historical claim with no publication date)")

    if blocking:
        print(f"\nPREFLIGHT FAIL — {len(blocking)} entr(y/ies) cannot back their claim:")
        for b in sorted(set(blocking)):
            print(f"  - {b}")
        return 1
    print("\nPREFLIGHT: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
