# AI Pre-Scan — Presentation Canon

This document is the source of truth for the presentation deck. It defines the visible slide copy,
visual intent, speaker notes, transitions and evidence sources. The main story is designed for a
**6 minute 20 second** delivery, with three appendix slides available for questions.

## Presentation brief

- **Objective:** make a first-time audience understand the missing pre-assessment step, trust the
  product boundary and remember the recurring vendor-drift opportunity.
- **Audience:** Ironhack reviewers and classmates seeing the project for the first time; secondarily,
  compliance advisers serving small and medium-sized businesses.
- **Desired outcome:** the audience can explain the product in one sentence, recognise why the
  evidence gate matters and see a credible path from the MVP to a recurring adviser workflow.
- **Primary message:** AI Pre-Scan turns a company name into an auditable first draft of candidate AI
  systems and the questions public evidence cannot settle.
- **Delivery rule:** show the product before explaining the stack. Do not claim legal classification,
  complete internal visibility, deterministic research quality or post-MVP capabilities as built.

## Visual system

- 16:9 white canvas, near-black typography and one electric-blue accent.
- Generous whitespace; one argument and one dominant composition per slide.
- Short, declarative headlines. No wall-of-text slides and no decorative stock imagery.
- Use native, editable PowerPoint shapes for diagrams, metrics and tables.
- Use real product/report captures only. If the live interface is unavailable, label the retained
  sample report as a pre-generated fallback rather than implying a live run.
- Retain the visual language of [`system-overview-slide.pptx`](system-overview-slide.pptx): blue
  section label, bold headline, restrained grey support copy and clear numbered flow.

## Main deck

### Slide 1 — AI Pre-Scan: the missing step before AI Act assessment

**Archetype:** `cover`

**Time:** 0:20

**Visible copy**

> AI PRE-SCAN<br>
> **The missing step before AI Act assessment**<br>
> Company name → evidence-backed first draft → focused client conversation

**Visual:** a single blue line runs from a company-name input on the left to a compact report card on
the right. The report card shows one quoted-evidence line and one `UNDETERMINED` tag.

**Speaker notes**

Every AI Act assessment begins with a list of the AI systems a company uses. AI Pre-Scan turns a
company name into an evidence-backed first draft and shows the adviser what still needs verification.
It does not make the legal decision.

**Transition:** The problem begins before the compliance form opens.

[Sources]

- docs/elevator-pitch.md
- README.md

[/Sources]

---

### Slide 2 — Compliance begins with an inventory most SMEs do not have

**Archetype:** `statement`

**Time:** 0:45

**Visible copy**

> **The checker asks:**<br>
> “Complete this form for each individual AI system used in your organisation.”

> **The SME asks:**<br>
> “Which systems are those?”

Small tools arrive through vendor updates, procurement and everyday employee use. The inventory is
often never created.

**Visual:** a clean two-column gap. On the left, a compliance-form card beginning with a system list.
On the right, an empty inventory sheet with three faint entry routes: vendor update, company card and
employee tool. A blue bracket between them is labelled **the missing step**.

**Speaker notes**

Most compliance tools sensibly assess one known system at a time. But that creates a hidden
assumption: someone has already found the systems. For many small companies, that inventory simply
does not exist. A recruitment platform adds an AI feature. Marketing buys a new tool. An employee
starts using a consumer assistant. None of those routes necessarily creates a central record. So,
when the checker asks for each individual AI system, the SME's honest answer may be: “Which systems
are those?” The compliance process begins with a blank page. AI Pre-Scan fills that missing step.

**Transition:** AI Pre-Scan creates a useful starting point before that meeting.

[Sources]

- docs/elevator-pitch.md
- docs/demo-plan.md

[/Sources]

---

### Slide 3 — One company name becomes an auditable first draft

**Archetype:** `statement`

**Time:** 0:45

**Visible copy**

> **1 · Research**<br>
> Public footprint, registry, careers, vendors and news

> **2 · Verify**<br>
> Exact quoted support + source currentness

> **3 · Hand off**<br>
> Candidate inventory + focused questions

**Footer:** Human review confirms the facts. A separate deterministic checker applies the law.

**Visual:** recreate the three-stage flow from the existing system-overview slide as native shapes.
The centre evidence gate is the strongest blue object. Unsupported findings peel downward into an
`UNDETERMINED` tray rather than continuing as claims.

**Speaker notes**

Here is the complete loop. First, the system resolves the company and searches its public footprint:
its own website, registry data, careers pages, vendor references and news. Second, it extracts
candidate systems, but every proposed finding must pass the evidence gate. The exact quote must be
present, the source must be traceable and the timing must fit the claim. Anything unsupported becomes
undetermined, not a fact. Third, the adviser receives a candidate inventory plus the questions the
public web cannot answer. Human review confirms the facts; a separate deterministic checker applies
the law.

**Transition:** The fastest way to understand that boundary is to see both kinds of output.

[Sources]

- docs/system-overview-slide.pptx
- docs/architecture.md
- docs/report-spec.md

[/Sources]

---

### Slide 4 — One name in; evidence and questions out

**Archetype:** `comparison-2col`

**Time:** 2:05

**Visible copy**

> **PERSONIO · PUBLIC EVIDENCE FOUND**<br>
> 3 candidate systems · 1 evidenced · 2 undetermined

> “AI Performance Summaries provide an AI-generated summary…”

> **BALLYMALOE FOODS · NO PUBLIC EVIDENCE FOUND**<br>
> 0 candidate systems · 1 question to discuss

> No public evidence is not the same as no AI use.

**Visual:** this is the live-demo stage, not a dense static slide. Begin with a large company-name
input and Scan button. After the run, use a split view: a cropped Personio report on the left with the
exact supporting sentence highlighted, and the correctly empty Ballymaloe report on the right. A
thin footer shows **live interface → retained sample fallback**.

**Speaker notes**

[Enter **Personio** and select **Scan**.]

I begin with only a company name. From here, I take my hands off the keyboard and let the workflow
run. It is resolving the organisation, researching its public footprint, extracting candidates and
checking each claim against the evidence.

[If the workflow loops back to research, point to it.]

This loop-back is intentional. The gate could not support a proposed claim, so the graph returned to
research instead of allowing a plausible-sounding statement into the report.

[Open the Personio result and point to the highlighted quote.]

For Personio, the report contains three candidate systems: one evidenced and two undetermined. The
important part is not the count; it is this exact sentence: “AI Performance Summaries provide an
AI-generated summary…” The adviser can inspect the support immediately, without treating the model's
wording as evidence. The two candidates whose current use could not be established are converted into
focused client questions.

[Switch to the Ballymaloe Foods result.]

Now compare that with Ballymaloe Foods. The scan found no public evidence, so it claimed zero
systems and produced one question to discuss. That does not mean the company uses no AI. It means an
external scan cannot see enough to make that claim. This is the honest result: evidence when evidence
exists, and a question when it does not.

[If the live run is unavailable, open the retained sample reports.]

These are pre-generated reports created through the same documented run path.

**Transition:** Those two reports are different because honesty is enforced before a finding ships.

[Sources]

- samples/personio.md
- samples/ballymaloe-foods.md
- docs/demo-plan.md

[/Sources]

---

### Slide 5 — Trust is enforced at the gate, not promised in the prompt

**Archetype:** `statement`

**Time:** 0:45

**Visible copy**

> **A finding ships only when:**

> exact quote ✓  source provenance ✓  currentness fit ✓

> **Otherwise:** research again → `UNDETERMINED` → client question

**Proof strip:** honest refusal **1.0** · thin-company false positives **0** · provenance violations
**0** across five evaluation runs

**Visual:** a horizontal gate. Three compact checks feed a blue pass lane; a failed check drops into
an amber `UNDETERMINED` lane. The proof strip is large and sparse along the bottom.

**Speaker notes**

This gate is the core trust mechanism. A model cannot ship a finding merely because it sounds
plausible. Three checks must pass: the exact quote exists in the fetched source, the provenance is
complete and the source is current enough for the claim being made. If any check fails, the workflow
researches again. If it still cannot support the claim, the result becomes undetermined and the
uncertainty becomes a client question. Across five evaluation runs, honest refusal stayed at one
hundred percent, thin-company false positives stayed at zero and provenance violations stayed at
zero. The trust comes from the gate, not from asking the model to be careful.

**Transition:** That gate also explains the stack choice.

[Sources]

- src/ai_prescan/gate.py
- eval/results.md
- docs/architecture.md

[/Sources]

---

### Slide 6 — LangGraph makes the evidence gate operational

**Archetype:** `statement`

**Time:** 0:45

**Visible copy**

> Research → extract → **evidence gate**

> **pass** → report<br>
> **retry** → research<br>
> **exhausted** → undetermined

**Delivery rail:** n8n files the finished report in Notion. It does not make decisions.

**Visual:** a compact loop diagram occupying two-thirds of the slide. The evidence gate is a blue
diamond with one arrow looping back to research and two arrows moving forward. A separate grey rail
below ends at a Notion report card and is labelled **delivery only**.

**Speaker notes**

LangGraph is the primary orchestration layer because the deterministic evidence gate has to sit
inside the decision loop. A supported finding moves forward to the report. A failed check sends the
workflow back to research. When the retry limit is reached, the claim becomes undetermined rather
than being forced through. n8n has a deliberately narrower role: it receives the finished report and
files it in Notion. It does not research, judge evidence or make compliance decisions. We verified
that delivery from the Notion API response itself, not merely from n8n reporting a successful run.

**Transition:** The same architecture points to a recurring product, not just a one-off scan.

[Sources]

- stack_decision.md
- docs/architecture.md
- workflows/README.md

[/Sources]

---

### Slide 7 — The recurring product is vendor-drift monitoring

**Archetype:** `ask`

**Time:** 0:55

**Visible copy**

> **POST-MVP PATH**

> MAY<br>
> Client's ATS has no evidenced AI ranking feature

> JUNE<br>
> Vendor ships AI CV ranking

> JULY ALERT<br>
> “The client's systems changed even though the client did nothing.”

**Close:** From a blank-page investigation to an auditable, recurring conversation.

**Visual:** a single three-point timeline with the July alert as the largest blue card. Under it, a
small commercial ladder reads **adviser pilot → confirmed drift alerts → retained monitoring**. Mark
the entire ladder clearly as future validation, not current traction.

**Speaker notes**

The MVP today is an on-demand scan of one company. The sharper post-MVP opportunity is vendor-drift
monitoring. Imagine that, in May, a client's recruitment system has no evidenced AI-ranking feature.
In June, the vendor adds AI CV ranking. By July, the adviser receives an alert: the client's system
landscape changed even though the client bought nothing and started no internal project. That change
signal can recur across an adviser portfolio. The commercial hypothesis is therefore simple: begin
with an adviser pilot, prove that the drift alerts are accurate and useful, then test retained
monitoring. That is future validation, not current traction. What is built today is the starting
point: AI Pre-Scan turns AI discovery from a blank-page investigation into an auditable, focused
conversation.

**Transition:** End here. Open the appendix only for questions.

[Sources]

- gtm_future_sprints.md
- docs/elevator-pitch.md

[/Sources]

## Appendix

### Slide 8 — The honesty controls pass; research quality still needs work

**Archetype:** `comparison-2col`

**Use:** evaluation questions

**Visible copy**

| Stable strengths | Measured limitations |
|---|---|
| Honest refusal: **1.0** | Recall: **0.444** vs 0.75 target |
| Thin-company false positives: **0** | Role correctness: **0.739** vs 0.90 |
| Provenance violations: **0** | Over-claim rate: **0.333** vs 0.10 |

> Identical code produced recall of **0.556** and **0.444**. One run cannot attribute a change to a
> configuration.

**Visual:** two balanced columns, green-neutral on the left and amber-neutral on the right. A small
variance line chart along the bottom shows runs 3 and 5 as identical-code points. Do not use red/green
alone; pair colour with pass/miss labels.

**Speaker notes**

The evaluation shows a clear split. The honesty controls are stable: unsupported claims are refused,
thin-company false positives are zero and provenance violations are zero. Discovery quality is not
yet at target. Recall is point four four four against point seven five. Role correctness is point
seven three nine against point nine. Over-claiming is point three three three against a maximum of
point one. We also saw identical code produce different recall across two runs. So one run cannot
prove that a configuration improved the system. The next evaluation step is repeated runs per
configuration, or a frozen page cache, before making tuning claims.

[Sources]

- eval/results.md
- docs/eval-plan.md

[/Sources]

---

### Slide 9 — Discovery finds facts; the checker applies the law

**Archetype:** `comparison-2col`

**Use:** scope and legal-boundary questions

**Visible copy**

> **AI PRE-SCAN**<br>
> Candidate systems · quoted evidence · provenance · unresolved questions

> **HUMAN + DETERMINISTIC CHECKER**<br>
> Confirm facts · classify risk · determine obligations

> **Never claimed:** complete internal visibility, legal advice or autonomous compliance decisions

**Visual:** two large, separate containers joined by a deliberate human-review checkpoint. The left
container contains a factual record; the right contains a rules tree. No arrow bypasses the human.

**Speaker notes**

The boundary is deliberate. AI Pre-Scan discovers and documents candidate facts from public
sources: possible systems, exact quoted evidence, provenance and unresolved questions. It does not
classify legal risk. An adviser first confirms the facts with the client; only then does a separate
deterministic checker apply the law and determine obligations. There is no path around that human
checkpoint. Internal tools, systems behind a login and employee use of consumer AI remain outside an
external scan's field of view. So the product never claims complete visibility, legal advice or an
autonomous compliance decision.

[Sources]

- README.md
- docs/report-spec.md
- docs/elevator-pitch.md

[/Sources]

---

### Slide 10 — The MVP is built, integrated and tested

**Archetype:** `bullets-4`

**Use:** technical-delivery questions

**Visible copy**

> **RUNS**  Browser UI + CLI from a company-name trigger

> **RESEARCHES**  Serper · NewsAPI · GLEIF · Wikidata

> **GROUNDS**  OpenAI extraction · Pinecone evidence store · deterministic gate

> **DELIVERS**  Markdown report · n8n → Notion

**Footer:** 12-company evaluation · two retained sample reports · offline test suite

**Visual:** four horizontal capability bands feeding one report card. Keep service names as plain
text; do not use unverified logos. A small boundary label marks scheduled sweeps and vendor-corpus
ingestion as **designed, not built**.

**Speaker notes**

The MVP is working end to end. A scan can begin in the browser or from the command line with a company
name. It researches across Serper, NewsAPI, GLEIF and Wikidata. OpenAI supports extraction, Pinecone
stores evidence and the deterministic gate decides whether a finding is supported. The output is a
Markdown report, which n8n can deliver into Notion. We evaluated twelve companies and retained two
sample reports as reproducible artefacts; they are not hand-edited showcase copy. The offline test
suite also passes. Scheduled sweeps and vendor-corpus ingestion are designed next steps, but they are
not part of the built MVP.

[Sources]

- README.md
- docs/architecture.md
- workflows/README.md
- eval/results.md
- samples/personio.md
- samples/ballymaloe-foods.md

[/Sources]

## Delivery checklist

- Rehearse the seven-slide main story to 6:20; appendix slides do not count toward the timed run.
- Pre-flight the live interface shortly before presenting.
- Keep the two retained sample reports open as an explicitly labelled fallback.
- Show one exact supporting sentence and one discussion question; do not read the full report.
- Do not expose environment variables or API-key values on screen.
- End on slide 7 and invite questions before opening the appendix.
