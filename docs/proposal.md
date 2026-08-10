# Project 3 Proposal — AI Pre-Scan

**Author:** Nnanyelugo Ahukannah
**Cohort:** AC-FT-26-07-06
**Project type:** Autonomous Company Research & Report Generation Agent
**Industry:** Regulatory compliance advisory

> The EU AI Act Compliance Checker instructs users to *"complete this form for each individual
> AI system used in your organisation."* Most organisations cannot produce that list.
> This agent builds it — as a pre-scan, plus the short list of items the client must be asked.

---

## 1. The operator, the input, and the flow

**The operator is an external compliance adviser.** Maria runs a six-person compliance consultancy
in Dublin with 40 SME clients. The AI Act is being phased in — the Digital Omnibus moved high-risk
obligations to **2 December 2027**, and rules for AI embedded in regulated products to 2 August 2028
([Commission timeline](https://digital-strategy.ec.europa.eu/en/faqs/navigating-ai-act)) — and
clients are already asking whether they are exposed. Each answer currently costs her a discovery call
plus hours of digging, so she cannot answer at the scale of her client list.

**The delay does not remove the work; it front-loads it.** An inventory is the long-lead item, it
takes longest to assemble, and it is needed before any determination can begin.

**The input is a third party's company name** — a client's or a prospect's, never her own. Say
`Fitzgerald Recruitment Ltd`.

**The flow:**

1. Maria submits the client's company name.
2. The agent researches **that client's** public footprint — website, product and pricing pages,
   careers listings, publicly named vendors, press coverage, funding announcements.
3. It returns an evidenced inventory of the AI systems that client appears to run.
4. Maria takes each identified system into the **EU AI Act Compliance Checker** (section 4), which
   performs the legal classification.
5. She walks into the client meeting already knowing what to ask about, and can scope and quote the
   engagement — a two-hour job or a two-week one.

Run across her whole client list, it also tells her **which clients to approach first**.

**Why public sources are the right instrument here:** Maria has no internal access to her client's
systems. Published evidence is all she has, and it is exactly what an outside assessor works from.

## 2. What it produces

One row per candidate system, each traceable to a source:

| Field | Example | Notes |
|---|---|---|
| System | AI CV ranking within applicant tracking system | What it appears to do |
| Evidence | careers page URL + vendor changelog URL | Every row cites a source that passes the provenance and claim-time currentness contract in `docs/architecture.md` |
| Vendor | *named third-party ATS* | Or "built in-house" where evidenced |
| Built or bought | Bought | Factual basis for the role question |
| Where used | Recruitment / hiring | Operational context, not a legal category |
| Offered to customers? | No — internal use only | Factual basis for the market-placement question |
| First evidenced | June 2026 | Earliest date the evidence supports |
| Confidence | Evidenced / Inferred / **Undetermined** | Undetermined is a first-class outcome |

### 2.2 Second output: the discussion list

The inventory is only half the deliverable. The agent also emits **a short list of items to discuss
with the client** — every question the checker needs that public evidence cannot settle, phrased so
the client can answer it.

This is the operating model the facilitator named on review: **run it as a pre-scan, then hand the
company a list of things to talk through.** Rather than opening with "tell me about your AI", the
adviser opens with *"you appear to use this named tool for CV ranking — have you rebranded it,
changed what you use it for, or modified it?"* Specific, short, and answerable by someone who has
never read the Act.

The discovery call is not replaced. It is **scoped** — which is worth more, because it is the part
the adviser bills for and the part a client can actually engage with.

**"Undetermined" is never guessed away.** An agent that always finds something is an agent that
fabricates. A partial but honest inventory beats what the company has today, which is nothing.

## 3. What it explicitly does not do

- **No risk classification.** It does not say whether a system is high-risk.
- **No obligations.** It does not tell anyone which articles apply to them.
- **No legal conclusions of any kind**, and nothing that reads as legal advice.

It establishes **facts**. A deterministic tool applies the law. This boundary is the design, not a
disclaimer bolted on afterwards.

## 4. How it interfaces with the EU AI Act Compliance Checker

The Future of Life Institute publishes a free
[EU AI Act Compliance Checker](https://artificialintelligenceact.eu/assessment/eu-ai-act-compliance-checker/)
— a deterministic questionnaire mapping a described system to role-based obligations. It is good, it
is free, and its logic is a decision tree rather than an LLM, which is the correct way to classify.

**This project feeds that tool. It does not compete with it or reimplement it.**

### 4.1 The tree, walked end to end (verified 10 August 2026)

I completed the form for the deployer path rather than inferring it. Questions in order:

| # | Question | Input |
|---|---|---|
| 0 | *"Is my system an 'AI System' according to the EU AI Act?"* — Article 3(1) definition | informational |
| 1 | *"Which kind of entity is your organisation?"* | Provider / Deployer / Distributor / Importer / Product manufacturer / Authorised representative |
| 2 | *"System modifications — do you perform any of the following actions?"* | rebrand · change intended purpose · substantial modification · none |
| 3 | *"High-risk AI system: Annex I"* | 7 sectors, then 13 product categories, then a third-party conformity-assessment Yes/No |
| 4 | *"High-risk AI system: Annex III"* | 8 categories incl. **Employment, workers management** · none |
| 5 | *High-risk technicalities* — Article 6(3) | Yes / No |
| 6 | *"Scope"* | **adaptive** — a deployer sees only 3 of the 6 options |
| 7 | *"Excluded systems"* | military · third-country law enforcement · R&D · open source · personal use · none |
| 8 | *"Prohibited systems"* | 8 practices · none |
| 9 | *"Transparent systems"* | **adaptive** — a deployer sees 4 of 5 |
| 10 | *"Are you a body governed by 'public law', or a private entity providing public services?"* | Yes / No |

**Two findings that shape this project:**

**The form is adaptive by entity type.** Scope and Transparency present different options to a
deployer than to a provider, so entity type must be resolved first — it changes the questions, not
just the answers.

**The tree never asks when a system was deployed.** There is no date input anywhere. Article 111(2)
grandfathering — systems already on the market are caught only if significantly modified after the
application date — sits entirely outside the checker's scope. The inventory's `first evidenced`
field therefore carries information the checker cannot derive, which an adviser needs and would
otherwise miss.

**The cut-off date itself must be re-read against the amended text**, not the original Regulation:
the Digital Omnibus moved the application dates, and the transitional provisions reference them. See
the corpus warning in `docs/architecture.md`.

### 4.2 The split: facts vs determinations

| Checker question | Who answers | Notes |
|---|---|---|
| Entity type | **Agent** | Built in-house vs bought vs resold — evidenced |
| Annex III category | **Agent** | What domain the system operates in |
| Scope | **Agent** | Establishment and EU presence, from the registry |
| Excluded systems | **Agent** | Open-source / R&D / personal use, where evidenced |
| Transparent systems | **Agent** | Functional description — does it generate synthetic content? |
| Public body / public services | **Agent** | From the company registry |
| GPAI status | **Agent** | From the vendor and model in use |
| Prohibited practices | **Agent supplies description only** | The determination is the checker's |
| **Is it high-risk (Art. 6)** | **Checker** | Never the agent |
| **Art. 6(3) technicalities** | **Checker** | Judgement, not fact |
| **System modifications** | **Neither — undetermined by design** | See below |

### 4.3 What public research honestly cannot answer

**Question 2, system modifications, is not publicly researchable.** Whether a company rebranded a
bought system, repurposed it, or substantially modified it is internal and rarely visible. It is
also the highest-stakes question in the tree: any of those turns a deployer into a **provider**
(Article 25), which replaces a short obligation list with a long one.

The agent therefore returns it as **undetermined, always**, and says so explicitly.

That is not a weakness — it is the sharpest thing the product does. The agent reduces a broad
discovery call to the two or three questions public evidence genuinely cannot settle. Instead of
"tell me about your AI," the adviser asks: *"you use this named tool for CV ranking — have you
rebranded it, changed what you use it for, or modified it?"* That is a two-minute conversation with
a client who can actually answer it.

### 4.4 Verification of the Week 5 defect

Completing the walkthrough as a private Irish recruitment firm deploying AI CV ranking returns:
**Article 6 high-risk**, **Article 26 deployer obligations**, and **Article 4 AI literacy** — and
**no Article 27**, because question 10 gates it on being a public body or public-service provider.

That is independent confirmation of the residual defect in the Week 5 prototype, which asserted an
Article 27 FRIA duty for exactly this case. The filtered run's other outputs — Article 26 and
Article 4 — were correct.

**Deliberately out of scope:** reimplementing this decision tree. It exists, it is deterministic, and
rebuilding it would re-introduce the legal-conclusion surface this project removes.

## 5. Why this needs an agent rather than a script

Three properties rule out a fixed pipeline:

- **Conditional research depth.** Finding a named vendor creates new work: check whether that vendor
  shipped AI features, and when. A company with no named vendors needs a different path entirely.
- **Unstructured evidence extraction.** Inferring "they run automated CV ranking" from a careers
  page, a product page and a changelog is not deterministic — it is the one genuinely fuzzy part of
  the problem, and the reason a form cannot do it.
- **An evidence gate inside the loop.** Every claim must trace to a quoted source, and every
  current-state claim must use a source whose provenance metadata says it is current. When either
  check fails, the agent goes back and researches rather than emitting the finding.

## 6. Primary stack: LangGraph

**LangGraph is primary. n8n is secondary, for triggering and delivery.**

The evidence gate is deterministic code that must sit *inside* the research loop and control flow —
emit the finding, or send the agent back to research. It checks quoted support and source currentness
for the claim's time. That is a state machine. n8n's agent node loops over tools, but the gate ends up
outside the loop, where it can report a problem without correcting it.
Since the entire value of this product is refusing to state what it cannot evidence, the gate has to
be able to redirect the agent, not merely observe it.

n8n keeps what it is genuinely better at: the trigger, scheduled re-runs across a client list, and
delivering finished inventories into Notion or Airtable. Both are already wired from Week 5 labs.

## 7. APIs

| API | Role |
|---|---|
| Web search (Serper or Bing) | Locate the company's public footprint |
| News API (NewsAPI or Guardian) | Vendor announcements, deployments, incidents |
| Company registry (Companies House / OpenCorporates) | Confirm identity, size, sector |
| OpenAI | Evidence extraction and embeddings |
| Pinecone | Vector store for the vendor corpus and retrieved company evidence |

Auth methods, rate limits and free-tier ceilings documented before build.

### 7.1 Model choice and budget

Week 5 established that on this problem **cost is not the binding constraint — accuracy is.** A full
question answered end to end cost ≈ $0.0007, roughly 30x under the target, which made the interesting
question "what would a better model buy?" rather than "can we afford this?"

That conclusion sets the model policy here:

| Stage | Model | Why |
|---|---|---|
| Evidence extraction from pages | **The stronger general model** | The one genuinely fuzzy step. Inferring "they run automated CV ranking" from a careers page and a changelog is where errors originate, so it gets the better model |
| Query and classification scaffolding | Small model | Mechanical, high volume, no judgement |
| Embeddings | `text-embedding-3-small`, 1536 | Unchanged from Week 5; the corpus and the eval harness both assume it |

**Estimated cost per company researched:** roughly 20–30 extraction calls over retrieved pages.
On a small model that is ≈ $0.03 per company; on the stronger model ≈ $0.40–0.50. Even the expensive
path leaves room for hundreds of evaluation runs inside the provisioned budget.

**So the eval set is sized by what is useful, not by what is affordable** — enough target companies
to make recall and false-positive rates meaningful, re-run on every material change to the research
loop rather than once at the end. Spending the provision on repeated measurement is the highest-value
use of it, because the measurement is what the whole project rests on.

## 8. How it is tested

Every metric is checkable against public evidence. **No legal judgement is required to score this
system**, which is precisely what the narrowed scope buys.

| Metric | Question it answers |
|---|---|
| Recall on a seeded set | Of the AI systems we know a company runs, how many did it find? |
| False-positive rate | How many systems did it claim that the company does not run? |
| Source-claim accuracy | Does the cited page actually say what the row asserts? |
| Honest-refusal rate | Proportion of findings correctly marked undetermined |
| Checker-readiness | Proportion of rows that answer every factual field the checker needs |

Target companies are chosen so their AI use is independently verifiable — published case studies,
vendor customer lists, public job ads. The evaluation harness from the Week 5 lab is reused; the
same method there moved correct-article retrieval from 8/10 to 10/10 and is what caught the defect
that prompted the fix.

## 9. Ethics and data

Publicly listed or clearly public-facing companies only, using published sources. The subject of
research is the **organisation**, not any individual — no personal data is collected, and named
individuals encountered in sources are not recorded. Output is an inventory of facts with sources,
carrying no legal determination. Any company used for demonstration can be swapped for a synthetic
profile.

## 10. Future GTM sprints

| Sprint | Audience | Channel | Success metric |
|---|---|---|---|
| **1 — Adviser pilot** | Small compliance / accountancy firms | Direct outreach to 5 firms | 3 firms run it across ≥10 clients each; ≥1 says it changed what they quoted |
| **2 — Client-list sweep** | The same firms | Existing relationship | Scheduled re-runs; measured by newly-detected systems per sweep — a vendor shipping an AI feature is a new finding, not a re-run |
| **3 — Internal inventory mode** | Clients engaged via sprints 1–2 | Existing relationship | Swap the research adapter from public search to the client's vendor list and procurement export. Metric: systems found internally that public research missed |

## 11. Risks

| Risk | Mitigation |
|---|---|
| Agent claims a system the company does not run | False-positive rate is a headline metric; evidence gate blocks unsupported findings |
| Thin public footprint, agent pads the inventory | "Undetermined" is a first-class outcome and is measured |
| Source is stale, superseded, or silently changed | Provenance metadata and content hashes feed the deterministic evidence gate; an unknown or overdue currentness check degrades to `undetermined` |
| Reads as legal advice | No classification, no obligations, no articles cited. The boundary is structural |
| Search API cost or rate limits | Per-company cost measured before scaling, using the Week 5 costing method |
| Company modified a bought system, silently becoming a provider | Publicly undetectable. Always returned as undetermined and surfaced as a required client question (4.3) |
