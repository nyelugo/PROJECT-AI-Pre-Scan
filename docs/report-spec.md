# Report Specification

*Define the report before the tools.* This is what the system produces, what "good" means for the
buyer, and what it must never do. Written before any code so the tools serve the report rather than
the report being whatever the tools happened to return.

**Reader:** a compliance adviser about to meet a client. She has five minutes with it in the taxi.

**Format:** Markdown, 2–4 pages. Rendered to PDF for client handover.

---

## Structure

### 1. Header block

```
AI PRE-SCAN
Fitzgerald Recruitment Ltd  ·  Companies House 0123456
Scanned 10 August 2026  ·  41 sources consulted  ·  scan v1
```

Date is load-bearing: a scan is a snapshot with a shelf life of weeks, and the reader must see how
old it is.

### 2. Summary — one paragraph, no bullets

What was found, how much is uncertain, and the single thing most worth attention. Written so it can
be read aloud.

> Four candidate AI systems were identified, three of them evidenced and one inferred. The most
> significant is AI-assisted CV ranking inside the company's applicant tracking system, which appears
> to have arrived in a vendor product update in June 2026 rather than through a purchasing decision.
> Six questions could not be settled from public sources and are listed in section 5.

### 3. The inventory

One row per candidate system.

| System | What it does | Vendor | Built/bought | Where used | First evidenced | Confidence |
|---|---|---|---|---|---|---|

**Confidence is three-valued and never blank:** `Evidenced` (a source states it), `Inferred` (the
source implies it), `Undetermined` (public evidence does not settle it).

### 4. Per-system detail

For each row, on its own short block:

- **What it appears to do** — functional description, no regime vocabulary
- **Evidence** — the source URL, its publication or update date when available, retrieval date,
  currentness status, and **a quoted passage**, so the reader can check the claim without opening the
  link
- **Who it affects, and how** — does it make or assist a decision about identifiable people?
- **What we could not establish about this system**

The quoted passage is not decoration. It is what separates this from a plausible list, and it is what
the source-claim accuracy metric measures.

### 5. Questions to discuss with the client

The second deliverable, and for the adviser the most valuable page. Each question is specific,
answerable by a non-expert, and tied to the system it concerns.

> **On the applicant tracking system:** have you renamed, rebranded, or white-labelled it? Have you
> changed what you use it for since you bought it? Has anyone configured or retrained the ranking?
> *(Any yes may change the company's role from deployer to provider, which changes its obligations
> substantially.)*

Standing entry, always present: **the modification question**, because it is the highest-stakes item
in a compliance determination and is invisible from outside.

### 6. What this scan could not see

Named explicitly rather than left as silence:

- Internal tools with no public footprint
- Employee use of consumer AI tools — leaves no external trace
- Anything behind a login
- Systems evidenced only in sources published before the scan window

A scan that lists its blind spots is more useful than one that implies it has none.

### 7. Method and standing notice

Sources searched, date range, currentness checks that were overdue or unresolved, and the fixed
notice:

> This is a pre-scan of publicly available information. It identifies what a company **appears** to
> run and the questions worth asking. **It makes no assessment of legal risk, classification, or
> obligations**, and is not legal advice. Findings should be confirmed with the company and taken
> into a compliance determination — for the EU AI Act, the Future of Life Institute's compliance
> checker.

---

## What "good" means

| Good | Not good |
|---|---|
| Every claim traceable to a quoted source | Claims that are true but unsourced |
| Current-state claims backed by a source checked as current | A recently retrieved but superseded source treated as current |
| "Undetermined" appearing where evidence is thin | A full-looking report with nothing marked uncertain |
| Discussion questions a non-expert can answer | "Do you use high-risk AI systems?" |
| Blind spots stated | Silence implying completeness |
| Readable in five minutes | A raw API dump with headings |

## Hard rules

1. **No regime vocabulary in findings.** Not "high-risk", not "Annex III", not article numbers.
   Functional description only — that is also what keeps the schema regime-neutral.
2. **No empty confidence values.** Every row is classified, including as undetermined.
3. **No claim without a quoted passage.** If the passage cannot be quoted, the finding does not ship.
4. **No current-state claim from an unchecked source.** `unknown`, `superseded`, or overdue evidence
   becomes `undetermined`; a recent retrieval timestamp does not override that rule.
5. **The standing notice is not editable** by any generation step.

## Two sample reports

The deliverable requires at least two, generated on **different target companies** — one with a rich
public footprint and one deliberately thin, so the reports demonstrate that `undetermined` behaves
correctly rather than only that the happy path works.
