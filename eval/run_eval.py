"""Run the 12-company evaluation.

Scores what is objectively checkable and refuses to invent the rest. Semantic judgement — does this
quoted passage genuinely support this claim — is not automated here, because using a model to grade
the output of a model tells you the two agree, not that either is right. That one is sampled by hand
and recorded separately.

    python eval/run_eval.py --dry     # show the plan and the cost estimate, scan nothing
    python eval/run_eval.py           # live: scans all 12 companies
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ai_prescan import browser, config, graph  # noqa: E402
from ai_prescan.schemas import Attestation, Confidence  # noqa: E402

GT = Path(__file__).with_name("ground_truth.json")
OUT_JSON = Path(__file__).with_name("results.json")
OUT_MD = Path(__file__).with_name("results.md")

# Generic on both sides. Leaving these in makes "AI Assistant" and "AI agent" look related when
# they share nothing but the vocabulary of the field.
STOP = {"the", "a", "an", "for", "and", "with", "in", "of", "on", "ai", "system", "systems",
        "artificial", "intelligence", "tool", "tools", "platform", "software", "powered",
        "based", "own", "product", "products", "solution", "service", "services"}


def tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if t and t not in STOP}


def finding_text(finding) -> str:
    """Everything the finding actually says, not just its title.

    The first version compared titles only, so a known 'Personio Assistant - AI-powered HR data
    assistant' and a found 'AI Assistant' shared one token against a threshold of two, and a correct
    find was scored as a miss. Recall came back 0.0 for the instrument, not for the system.
    """
    parts = [finding.system, finding.what_it_does or "", finding.vendor or ""]
    parts += [e.quote for e in finding.evidence]
    return " ".join(parts)


def matches(known: dict, finding) -> bool:
    """Vendor agreement, or the known system's distinctive words appearing in the finding."""
    kv, fv = tokens(known.get("vendor")), tokens(finding.vendor)
    if kv and fv and kv & fv:
        return True                                   # strongest signal: same maker

    blob = tokens(finding_text(finding))
    if kv and kv & blob:
        return True                                   # vendor named anywhere in the finding

    ks = tokens(known.get("system"))
    return bool(ks and len(ks & blob) >= 2)


def load_companies() -> list[dict]:
    data = json.loads(GT.read_text())
    out = []
    for band in ("rich_footprint", "single_system", "capability_present", "thin"):
        for c in data.get(band, []):
            out.append({"band": band, "company": c["company"], "systems": c.get("systems", []),
                        "expected_output": c.get("expected_output")})
    return out


def score_company(entry: dict, report) -> dict:
    band, findings = entry["band"], report.findings
    known = entry["systems"]
    emitted = [f for f in findings if f.confidence is not Confidence.UNDETERMINED]
    undetermined = [f for f in findings if f.confidence is Confidence.UNDETERMINED]

    row: dict = {
        "company": entry["company"], "band": band,
        "known": len(known), "findings": len(findings),
        "emitted": len(emitted), "undetermined": len(undetermined),
    }

    if band in ("rich_footprint", "single_system"):
        found = [k for k in known if any(matches(k, f) for f in findings)]
        row["found"] = len(found)
        row["recall"] = round(len(found) / len(known), 3) if known else None
        # Role correctness only counts where ground truth states a role.
        roled = [(k, f) for k in known if k.get("role")
                 for f in findings if matches(k, f)]
        row["role_checked"] = len(roled)
        row["role_correct"] = sum(1 for k, f in roled if f.role == k["role"])
    elif band == "capability_present":
        # Over-claiming means reporting THIS capability as deployed, not finding any other AI at
        # the company. The first version counted every deployed finding and divided by companies,
        # which produced a "rate" of 1.667 — a number that cannot be a rate, and a metric that
        # would have punished a correct find of unrelated AI.
        overclaimed = [
            k for k in known
            if any(matches(k, f) and f.attestation is Attestation.DEPLOYED for f in emitted)
        ]
        row["capability_items"] = len(known)
        row["overclaimed"] = len(overclaimed)
        row["correctly_undetermined"] = len(known) - len(overclaimed)
    else:  # thin
        row["false_positives"] = len(emitted)
        row["honest"] = len(emitted) == 0

    # Structural invariant: anything emitted must carry complete provenance. A violation is a bug
    # in the gate, not a quality shortfall.
    bad = [f.system for f in emitted
           if not f.evidence or any(not e.provenance.content_sha256 for e in f.evidence)]
    row["provenance_violations"] = len(bad)
    return row


def summarise(rows: list[dict]) -> dict:
    ident = [r for r in rows if r["band"] in ("rich_footprint", "single_system")]
    cap = [r for r in rows if r["band"] == "capability_present"]
    thin = [r for r in rows if r["band"] == "thin"]
    known = sum(r["known"] for r in ident) or 1
    return {
        "recall": round(sum(r.get("found", 0) for r in ident) / known, 3),
        "role_correct": round(
            sum(r.get("role_correct", 0) for r in ident)
            / max(sum(r.get("role_checked", 0) for r in ident), 1), 3),
        "over_claim_rate": round(
            sum(r.get("overclaimed", 0) for r in cap)
            / max(sum(r.get("capability_items", 0) for r in cap), 1), 3),
        "honest_refusal_rate": round(
            sum(1 for r in thin if r.get("honest")) / max(len(thin), 1), 3),
        "thin_band_false_positives": sum(r.get("false_positives", 0) for r in thin),
        "provenance_violations": sum(r["provenance_violations"] for r in rows),
        "total_findings": sum(r["findings"] for r in rows),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", help="scan one company by name substring")
    args = ap.parse_args()

    companies = load_companies()
    if args.only:
        companies = [c for c in companies if args.only.lower() in c["company"].lower()]

    if args.dry:
        for c in companies:
            print(f"{c['band']:<20} {c['company']}")
        print(f"\n{len(companies)} companies · ~12 pages each · roughly ${len(companies) * 0.16:.2f} "
              f"on gpt-4o extraction")
        return 0

    config.preflight(require_live=True)
    browser.install()

    rows, reports = [], {}
    for c in companies:
        name = c["company"].split(" (")[0]
        print(f"scanning {name} …", flush=True)
        try:
            report = graph.scan(name, use_fixtures=False)
        except Exception as exc:  # noqa: BLE001 — one company must not end the run
            print(f"  FAILED: {type(exc).__name__}: {exc}", flush=True)
            rows.append({"company": c["company"], "band": c["band"], "error": str(exc)[:200],
                         "known": len(c["systems"]), "findings": 0, "emitted": 0,
                         "undetermined": 0, "provenance_violations": 0})
            continue
        reports[name] = report
        row = score_company(c, report)
        rows.append(row)
        print(f"  {row['findings']} findings, {row['undetermined']} undetermined", flush=True)

    # Persist every report. Scoring and discarding made the first run undiagnosable: a recall of
    # 0.0 was indistinguishable from a broken matcher until the scans were repeated by hand.
    (Path(__file__).with_name("reports")).mkdir(exist_ok=True)
    for name, rep in reports.items():
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        Path(__file__).with_name("reports").joinpath(f"{slug}.json").write_text(
            rep.model_dump_json(indent=2) + "\n")

    summary = summarise(rows)
    stamp = datetime.now(timezone.utc).isoformat()
    OUT_JSON.write_text(json.dumps({"run_at": stamp, "rows": rows, "summary": summary}, indent=2) + "\n")

    md = ["# Evaluation results", "", f"Run {stamp}. Generated by `eval/run_eval.py`.", "",
          "| Metric | Value |", "|---|---|"]
    for k, v in summary.items():
        md.append(f"| {k.replace('_', ' ')} | {v} |")
    md += ["", "## Per company", "",
           "| Company | Band | Known | Findings | Emitted | Undetermined | Note |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        note = (f"recall {r['recall']}" if r.get("recall") is not None else
                "over-claimed" if r.get("overclaimed") else
                "honest" if r.get("honest") else
                r.get("error", "")[:40] or "")
        md.append(f"| {r['company'][:34]} | {r['band']} | {r.get('known','')} | {r['findings']} | "
                  f"{r['emitted']} | {r['undetermined']} | {note} |")
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"\nwrote {OUT_MD} and {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
