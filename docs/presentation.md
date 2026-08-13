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

Every AI Act assessment starts with a basic input: the systems a company actually uses. AI Pre-Scan
builds the first draft of that input from public evidence, then shows the adviser exactly what still
needs to be verified.

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

Most compliance tools sensibly assess one known system at a time. The hidden assumption is that
someone has already found those systems. For a small company, that list may not exist: a recruitment
platform adds an AI feature, marketing buys a tool, or staff use a consumer assistant. So the first
meeting begins with a blank page.

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

The only input is a company name. The system resolves the company, searches its public footprint,
extracts candidate systems and checks every proposed finding against the retrieved passage and its
currentness. The outputs are an evidence-backed candidate inventory and the questions the public web
cannot answer. It stops before legal judgement.

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

Type a company name, press Scan and take your hands off the keyboard. Narrate one loop-back if it
appears: the gate could not support a claim, so the graph returned to research.

On Personio, do not read the inventory table. Land on the quoted sentence. The adviser can inspect
the support without opening the link. Then show the discussion questions for the two claims whose
current use could not be established.

Move to Ballymaloe Foods. The system found no public evidence and claimed no systems. That is the
honest result: it asks the client what an external scan cannot see. If the live run is unavailable,
open the retained sample reports and say that they were pre-generated through the documented run
path.

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

This is the trust mechanism. A model cannot emit a finding merely because it sounds plausible. The
quote has to exist in the fetched source, the provenance has to be complete and the source has to fit
the claim's time. If those checks fail, the graph researches again or turns the uncertainty into a
question. Across all five evaluation runs, the three honesty controls stayed stable.

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

LangGraph is primary because the deterministic gate must sit inside the loop, where it can redirect
the research rather than merely observe a bad result. n8n has a narrower job: receive the completed
report and file it in Notion. The delivery path was verified from the Notion API response, not just
from n8n reporting success.

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

The MVP is an on-demand single-company scan. The sharper post-MVP path is vendor-drift monitoring:
repeat the scan and report only what changed. A vendor can add AI to software the client already
owns, so the client's system landscape changes without a purchase or internal project. That signal
recurs, which is the subscription hypothesis to test with compliance advisers after the pilot.

Close on the product promise: AI Pre-Scan turns AI discovery from a blank-page investigation into an
auditable conversation.

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

The system is already strong at refusing unsupported claims, but it is not yet a high-recall
discovery engine. Recall, role correctness and over-claiming miss their targets. Retrieval variance
also means the evaluation needs repeated runs per configuration or a frozen page cache before it can
support tuning claims.

[Sources]

- eval/results.md
- docs/eval-plan.md

[/Sources]

---

### Slide 9 — Discovery establishes facts; the checker determines the law

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

AI Pre-Scan discovers and documents candidate facts from public sources. An adviser confirms those
facts, then a separate deterministic checker applies the law. Internal tools, anything behind a
login and employee use of consumer AI remain outside the external scan's field of view.

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

The MVP runs through both browser and command-line interfaces. It integrates public search, news and
company identity sources, uses OpenAI and Pinecone for extraction and evidence storage, enforces a
deterministic gate and can deliver the finished report through n8n into Notion. The retained samples
and evaluation results are generated artefacts, not hand-edited showcase copy. Scheduled sweeps and
vendor-corpus ingestion remain future work.

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
