# Stack decision

**Primary: LangGraph. Secondary: n8n.**

## Why LangGraph is primary

The hard part of this problem is not calling tools in order — it is deciding, repeatedly, whether
what came back is good enough to report.

Every candidate finding passes a **deterministic evidence gate**: the claim must trace to a passage
quoted verbatim from the fetched page, and a claim about the company's *present state* needs a source
established as current, not merely retrieved recently. When either check fails the gate does not
record a warning — it **sends the agent back to research**, and only marks the finding `undetermined`
once the search is genuinely exhausted.

That is a state machine with a conditional edge, which is what LangGraph is for. The gate has to sit
*inside* the loop and control flow.

**Why n8n is secondary rather than primary.** n8n's agent node loops over tools perfectly well, but
the gate ends up outside the loop, where it can report a problem without correcting it. Since the
entire value of this product is refusing to state what it cannot evidence, a check that can only
observe is not the check this system needs. Choosing n8n as primary would have meant either weakening
the gate or reimplementing the loop inside a Code node — which is LangGraph with extra steps.

## Why it fits this industry problem

Compliance advisory rewards restraint over coverage. An adviser can act on a short list of evidenced
findings plus an honest list of open questions; she cannot act on a long list she has to re-verify,
and she is actively harmed by a confident claim about the wrong company. The architecture therefore
optimises for **provable refusal** — which is a control-flow property, not a prompt property.

The measurements bear that out. Across five evaluation runs, honest-refusal rate held at **1.0**,
thin-band false positives at **0**, and provenance violations at **0** — the metrics that depend on
the gate never moved, while the ones that depend on search coverage did. See
[`eval/results.md`](eval/results.md).

## What n8n actually does here

It owns the operational half, which it is genuinely better at:

- **Delivery.** The CLI posts a finished report to an n8n webhook, which creates a page in Notion.
  Built and verified — Notion's API returned the created page object.
  See [`workflows/n8n_report_delivery.json`](workflows/n8n_report_delivery.json).
- **Designed, not built:** scheduled sweeps across a client list. Stated as intent rather than
  implied as done.

## The honest boundary

A thin n8n webhook is explicitly permitted for a LangGraph-primary project, and that is exactly what
this is. The orchestration, the state, the branching and the gate are all in LangGraph
([`src/ai_prescan/graph.py`](src/ai_prescan/graph.py),
[`src/ai_prescan/gate.py`](src/ai_prescan/gate.py)); n8n does not make decisions.
