# What went wrong, and where it is guarded

A router, not a retelling. Each lesson is enforced next to the code or document it constrains — that
is where a maintainer meets it at the moment it matters. This page exists so the set is findable,
because the reasoning otherwise lives in fifty commit messages that nobody reads.

**If you change one of these areas, read the linked file first.**

---

## The defect that mattered most

**Every fetched page was marked `current` because the fetch returned HTTP 200.** Circular — a
superseded page serves fine today. Across every evaluation run, 68 of 68 evidence items were
`current`, so two of the evidence gate's three rules had never executed in production. The safeguard
named in [`stack_decision.md`](stack_decision.md) as the reason for choosing LangGraph was inert.

One of the project's own tests was holding it in place, asserting that a page published in 2024 and
fetched in 2026 was current.

→ Guarded in [`src/ai_prescan/fetch.py`](src/ai_prescan/fetch.py) (what counts as a currency signal)
and [`tests/test_fetch_extract.py`](tests/test_fetch_extract.py) (`test_a_200_does_not_make_stale_content_current`).

**The correction had to be corrected too.** Requiring a publication date everywhere produced a
Personio report with four findings and none evidenced — honest and useless. A live page on the
company's own domain is a present-tense assertion by the company about itself, and counts.
→ [`docs/architecture.md`](docs/architecture.md), *What counts as a currency signal*.

---

## Recurring: the tool doing the thing it exists to prevent

Entity ambiguity produced a wrong-company result five separate times — a TV review for "Gamma", an
unrelated French entity from the registry for the same name, and a country singer for "Clay",
*inside the sample data meant to demonstrate the system working*.

→ [`src/ai_prescan/sample_clients.py`](src/ai_prescan/sample_clients.py) (why every sample domain is
verified by fetching it), [`src/ai_prescan/tools.py`](src/ai_prescan/tools.py) (`_same_entity`, and
why a registry name-match is not identity), [`src/ai_prescan/graph.py`](src/ai_prescan/graph.py)
(host comparison, not substring).

---

## More defects were in the measurement than in the system

- A recall score of **0.0** was a broken comparison function, not a broken scanner.
- An **over-claim rate of 1.667** — a rate above one, which should have stopped work on sight.
- Two evaluation runs on **identical code** gave materially different numbers, invalidating a
  confident diagnosis already written down.

→ [`docs/eval-plan.md`](docs/eval-plan.md) §3b (measurement variance, and what the suite can and
cannot support) and [`eval/results.md`](eval/results.md) (all five runs, not just the last).

**Consequence adopted:** every scored report is persisted to `eval/reports/`, because a number that
cannot be drilled into cannot be trusted. The first run's 0.0 took a manual re-scan to diagnose
precisely because the runner discarded what it scored.

---

## Claims outrunning code

n8n was described in the present tense across three documents with no artefact in the repository. A
retrieval store was documented as grounding the evidence gate while being written and never read.

→ [`docs/architecture.md`](docs/architecture.md) marks each component *built* or *designed*.
[`workflows/README.md`](workflows/README.md) records the n8n path being verified against the
destination API rather than the workflow's own success indicator — which reports on itself.

---

## How the defects were actually found

Not by the test suite. It was green through nearly all of this.

1. **Reading the generated output** as a reader, not checking that it existed. Found triplicated
   findings, a question asking about tools the report had just said it could not find, and a
   client-facing rationale that was really an internal diagnostic.
2. **Cloning into an empty directory** and running only the documented commands. The first one
   failed immediately — a missing package install that never showed up locally because of a habit.
3. **A component-by-component audit**, run deliberately rather than after tripping over something.
   It found the currency defect above, which nothing else had.

→ Method retained in [`docs/project-build-plan.md`](docs/project-build-plan.md).

---

## Known and open

Recorded rather than carried quietly:

- **The research loop re-runs identical queries** rather than refining them, so a retry cannot find
  a better source — 3× the spend for the same candidates.
- **The evaluation numbers predate the currency fix.** They describe an earlier pipeline. Stated in
  [`eval/results.md`](eval/results.md); a re-run is roughly $2 and 25 minutes.
- **Findings are replaced per research pass, not accumulated**, so one evidenced on an early pass can
  be lost if a later pass does not re-find it.
- **The vendor corpus is a namespace with no writer**, and the per-scan store has no reader. The
  per-scan store now holds only validated passages rather than whole pages, with a purge before each
  scan — that fixed a privacy defect, not the missing reader, which is still open.
- **No processor agreements or transfer mechanism** for OpenAI and Pinecone, both US. Required
  before any real client use; surfaced by a GDPR self-audit of this project, not by a test.

---

## The one line worth keeping

A green test suite is a claim about the tests. It was green while the central safeguard did nothing,
while the download button led nowhere, and while a confirm button silently started scans instead.
