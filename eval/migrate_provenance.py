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
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ai_prescan import browser, fetch  # noqa: E402

GT = Path(__file__).with_name("ground_truth.json")


def fetch_provenance(url: str, _declared: str | None, now: datetime) -> dict:
    """Fetch through `ai_prescan.fetch`, so provenance is constructed in one place only.

    This script used to carry its own requests-based fetcher. That meant it never got the browser
    fallback, so the preflight failed whenever whoop.com's intermittent 403 landed — a fetch layer
    the rest of the system had already solved for. Duplicated retrieval logic is how two parts of
    one system end up disagreeing about what a source says.
    """
    result = fetch.fetch(url, now=now)
    if not result.ok:
        return {
            "canonical_url": url,
            "retrieved_at": now.isoformat(),
            "content_sha256": None,
            "currentness_status": "unknown",
            "source_published_at": None,
            "undated_reason": result.unavailable_reason,
            "fetch_error": result.unavailable_reason,
        }
    prov = result.provenance
    return {
        "canonical_url": str(prov.canonical_url),
        "retrieved_at": prov.retrieved_at.isoformat(),
        "content_sha256": prov.content_sha256,
        "authority_class": str(prov.authority_class),
        "source_published_at": prov.source_published_at.isoformat() if prov.source_published_at else None,
        "source_updated_at": None,
        "undated_reason": prov.undated_reason,
        "currentness_checked_at": prov.currentness_checked_at.isoformat() if prov.currentness_checked_at else None,
        "currentness_status": str(prov.currentness_status),
        "superseded_by": None,
        "next_review_at": prov.next_review_at.isoformat() if prov.next_review_at else None,
    }


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

    browser.install()   # blocked hosts get a real browser, same as a live scan
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
