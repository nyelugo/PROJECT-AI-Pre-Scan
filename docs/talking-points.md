# Project 3 — Talking Points

**AI System Discovery Agent** · Nnanyelugo Ahukannah · full proposal: `project3_proposal.md`

> The EU AI Act Compliance Checker says: *"Please complete this form for each individual AI system
> used in your organisation."* Most organisations don't have that list. This agent builds it.

---

## WHAT

An autonomous agent that takes **a company name** and returns an **evidenced inventory of the AI
systems that company runs** — what each system does, the vendor, whether it was built or bought,
where it's used, and when it first appears. Every row cites the source it came from, and anything
that can't be evidenced comes back **undetermined** rather than guessed. It produces facts, not
findings: no risk tiers, no obligations, no legal conclusions of any kind.

## WHY

The AI Act's high-risk obligations became applicable on 2 August 2026. Advisers are now being asked
by SME clients whether they're exposed — and every existing tool is per-system: the compliance
checker tells you to complete it *"for each individual AI system used in your organisation."*
Nobody has that list. Firms genuinely don't know what they run:
marketing bought a tool on a card, the ATS vendor shipped AI ranking in a June update nobody read.
So the question the deadline forces has no cheap answer, and it isn't a legal question — it's a
research question.

## HOW

LangGraph drives a research loop: search public sources → extract candidate systems with evidence →
follow up on named vendors → **deterministic grounding gate** decides whether to emit the row or
research again. n8n handles the trigger, scheduled sweeps across a client list, and delivery into
Notion. APIs: web search, news, company registry, OpenAI, Pinecone.

---

## The operator, concretely

**Maria runs a six-person compliance consultancy in Dublin. 40 SME clients.**

- She enters **a client's** company name — never her own.
- The agent researches **that client's** public footprint.
- She gets an evidenced inventory of that client's AI systems.
- She feeds each system into the deterministic compliance checker, which does the legal part.
- She walks into the meeting knowing what to ask, and can scope and quote the work.

Run across her client list, it tells her **which clients to approach first**.

**Why public sources:** she has no internal access to her client's systems. Published evidence is
all an outside assessor has.

---

## How it interfaces with the EU AI Act Compliance Checker

The Future of Life Institute's checker is free, deterministic, and good. **We feed it. We don't
compete with it and we don't reimplement it.**

It collects seven categories of information. The split is clean:

| The checker asks about | Who answers |
|---|---|
| Entity type (provider / deployer / distributor / …) | **Agent** — built in-house vs bought vs resold |
| System scope (professional vs personal use) | **Agent** |
| Operational context (sector, purpose, setting) | **Agent** |
| Market placement (placed on market / put into service) | **Agent** — internal use vs offered to customers |
| Risk classification (is it high-risk?) | **Checker** |
| GPAI / systemic risk status | **Checker** |
| Prohibited practices | **Checker** — agent supplies only the functional description |

Mechanically: the agent emits one **checker input sheet** per system, factual fields pre-filled and
each linked to its source. The output schema is designed backwards from the checker's inputs, so the
handoff is testable — a row is well-formed if it answers what the checker needs.

**Deliberately out of scope:** reimplementing the classification decision tree. That re-introduces
the legal-conclusion surface this project removes.

---

## Testing — and why it's a week, not a capstone

Every metric is checkable against public evidence. **No legal judgement is needed to score it.**

- **Recall** — of the systems we know a company runs, how many did it find?
- **False positives** — how many did it claim that they don't run?
- **Source-claim accuracy** — does the cited page actually say what the row asserts?
- **Honest-refusal rate** — how many findings correctly came back undetermined?
- **Checker-readiness** — do the rows answer every factual field the checker needs?

Target companies chosen so their AI use is independently verifiable — published case studies, vendor
customer lists, public job ads. Evaluation harness reused from the Week 5 lab.

---

## Likely questions

**"Doesn't the compliance checker already do this?"**
It does the half after this one. Its own instruction is *"complete this form for each individual AI
system used in your organisation"* — it assumes the list exists. Producing that list is the step
nobody covers, and it's what we supply.

**"Why an LLM instead of a deterministic path?"**
Classification *should* be deterministic and I'm not doing it — the checker's decision tree is the
right instrument. The part that isn't deterministic is reading a careers page, a product page and a
vendor changelog and inferring "they run automated CV ranking." That's unstructured evidence
extraction, which is exactly what a form can't do.

**"Aren't you giving legal advice?"**
No. No risk tiers, no obligations, no articles. It reports what a company appears to run, with
sources. The legal step is the checker's.

**"Isn't this your Week 5 lab again?"**
The lab was human-driven Q&A over the Act's text. This is an autonomous research agent whose subject
is a *company*, and it makes no claims about the law at all. Different problem, different output,
different failure modes.

**"Why not n8n primary like most of the cohort?"**
It's better for the ops half and I'm using it there. But the grounding gate has to sit inside the
loop and redirect the agent — a gate that can't redirect is just logging.

**"Does this need to be the capstone?"**
It did when it was making legal claims — validating those would be capstone-scale. Cutting them
means everything left is checkable against public evidence in a week.

---

## What I'd ask them

1. Any constraint on reusing infrastructure from a Week 5 lab?
2. Real named companies fine for the demo, or would they prefer synthetic profiles?
3. Is LangGraph-primary acceptable, or is there a cohort expectation toward n8n?
