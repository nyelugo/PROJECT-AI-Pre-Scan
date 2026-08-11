"""Render a Report to Markdown, following docs/report-spec.md section order.

The standing notice is assembled here and nowhere else, so no generation step can edit it.
"""

from __future__ import annotations

from .schemas import Confidence, Report

STANDING_NOTICE = (
    "This is a pre-scan of publicly available information. It identifies what a company "
    "**appears** to run and the questions worth asking. **It makes no assessment of legal risk, "
    "classification, or obligations**, and is not legal advice. Findings should be confirmed with "
    "the company and taken into a compliance determination — for the EU AI Act, the Future of Life "
    "Institute's compliance checker."
)


def cell(value) -> str:
    """Make free text safe for a markdown table cell.

    `system`, `what_it_does` and `vendor` come from extraction over scraped pages. An unescaped
    pipe — "Workday | Recruiting" — adds a column, shifting every later value one place left, so
    the report shows the wrong figure under every heading after it. A newline ends the table
    outright and the remaining rows render as raw pipe text.
    """
    return str(value if value not in (None, "") else "—").replace("|", "\\|").replace("\n", " ").strip()


def to_markdown(r: Report) -> str:
    out: list[str] = []
    ev = sum(1 for f in r.findings if f.confidence is Confidence.EVIDENCED)
    inf = sum(1 for f in r.findings if f.confidence is Confidence.INFERRED)

    out.append("# AI PRE-SCAN\n")
    out.append(
        f"**{r.company}**  ·  Scanned {r.scanned_at:%d %B %Y}  ·  "
        f"{r.sources_consulted} sources consulted  ·  scan {r.scan_version}\n"
    )

    out.append("\n## Summary\n")
    out.append(
        f"{len(r.findings)} candidate AI system(s) identified — {ev} evidenced, {inf} inferred, "
        f"{r.undetermined_count} undetermined. "
        f"{len(r.discussion)} question(s) could not be settled from public sources and are listed "
        "under *Questions to discuss*.\n"
    )

    if not r.findings:
        # An empty table with headers looks like a broken report rather than an honest one.
        out.append("\n## Inventory\n")
        out.append("No AI systems could be evidenced from public sources. That is a finding, not a "
                   "failure — see *What this scan could not see* below for what an external scan "
                   "cannot reach.\n")
    else:
        out.append("\n## Inventory\n")
        out.append("| System | What it does | Vendor | Role | Built/bought | Where used | "
                   "First evidenced | Confidence |")
        out.append("|---|---|---|---|---|---|---|---|")
        for f in r.findings:
            out.append(
                f"| {cell(f.system)} | {cell(f.what_it_does)} | {cell(f.vendor)} | "
                f"**{cell(f.role)}** | {cell(f.built_or_bought)} | {cell(f.where_used)} | "
                f"{cell(f.first_evidenced)} | **{cell(f.confidence)}** |"
            )

    if r.findings:
        out.append("\n## Per-system detail\n")
    for f in r.findings:
        out.append(f"### {f.system}\n")
        out.append(f"- **What it appears to do:** {f.what_it_does}")
        out.append(f"- **Role:** {f.role}")
        if f.evidence:
            for e in f.evidence:
                p = e.provenance
                dated = p.source_published_at or f"undated ({p.undated_reason})"
                out.append(
                    f"- **Evidence:** [{p.canonical_url}]({p.canonical_url})\n"
                    f"    - published: {dated} · retrieved: {p.retrieved_at:%Y-%m-%d} · "
                    f"currentness: {p.currentness_status}\n"
                    f"    - > {cell(e.quote)}"
                )
        else:
            out.append(f"- **Undetermined:** {f.undetermined_reason}")
        out.append("")

    out.append("\n## Questions to discuss with the client\n")
    for i, d in enumerate(r.discussion, 1):
        tag = " *(always asked)*" if d.standing else ""
        out.append(f"{i}. **{d.question}**{tag}\n\n    {d.why_it_matters}\n")

    out.append("\n## What this scan could not see\n")
    for b in r.blind_spots:
        out.append(f"- {b}")
    if r.unavailable_sources:
        out.append("\n**Sources unavailable during this scan:**")
        for u in r.unavailable_sources:
            out.append(f"- {u.label} — {u.reason}")

    out.append("\n## Method and notice\n")
    out.append(f"> {STANDING_NOTICE}\n")
    return "\n".join(out)
