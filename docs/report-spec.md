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

| System | What it does | Vendor | Role | Built/bought | Where used | First evidenced | Confidence |
|---|---|---|---|---|---|---|---|

**Role is in the table, not buried in the detail.** Provider and deployer carry different
obligations, it is the first thing the compliance checker asks, and it is the field the Week 5
prototype got wrong. A reader skimming one row should see it.

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

**The standing question depends on what was found**, because one question cannot serve both cases:

- **Systems found** → the modification question. Renaming, repurposing or retraining a bought tool
  can turn a deployer into a provider, and it is invisible from outside.
- **Nothing found** → *"What AI tools does the business actually use?"* Asking "for each tool
  identified" on a report that identified none is absurd, and the useful question has changed: the
  point is no longer how a tool was modified, it is that public evidence cannot see inside the
  business at all.

**Empty sections are not rendered.** An inventory table with headers and no rows reads as a broken
report rather than an honest one, so a scan with no findings says so in a sentence and points at the
blind-spots section.

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

## Identity before findings

A report is only about the company its evidence is about. Where the client's website is confirmed,
that domain anchors the scan. Where it is only suggested or missing, the findings rest on name
matching and are weaker for it — which the interface states rather than implies.

## Hard rules

1. **No regime vocabulary in findings.** Not "high-risk", not "Annex III", not article numbers.
   Functional description only — that is also what keeps the schema regime-neutral.
2. **No empty confidence values.** Every row is classified, including as undetermined.
3. **No claim without a quoted passage.** If the passage cannot be quoted, the finding does not ship.
4. **The quote must show the system doing something AI does.** Being named in an AI-titled article
   is not being an AI system — "Personio Whistleblowing, a centralised solution for anonymous
   reporting" was reported for exactly that reason. Asking the prompt not to did not work; the check
   is deterministic and runs on the quote, not on the model's summary of it.
5. **A date is only taken from a page plausibly about the announcement.** A homepage's publication
   date has nothing to do with when a feature shipped, and `first evidenced` is what the Act's
   transition rules turn on — a confidently wrong date there is worse than none.
6. **No current-state claim from an unchecked source.** `unknown`, `superseded`, or overdue evidence
   becomes `undetermined`; a recent retrieval timestamp does not override that rule.
7. **The standing notice is not editable** by any generation step.

## Two sample reports

The deliverable requires at least two, generated on **different target companies** — one with a rich
public footprint and one deliberately thin, so the reports demonstrate that `undetermined` behaves
correctly rather than only that the happy path works.
