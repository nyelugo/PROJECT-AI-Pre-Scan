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
- Slide 1 is both the cover and the opening thesis; do not add a separate cover slide.
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

- The EU AI Act addresses risks from AI systems through a risk-based approach.

- Before a company can assess what rules apply, it must know which AI systems it uses.

- AI Pre-Scan turns a company name into an evidence-backed first draft of that inventory.

- [Pause.]

**Transition:** The problem begins before the compliance form opens.

[Sources]

- docs/elevator-pitch.md
- README.md
- European Commission, “AI Act”: https://digital-strategy.ec.europa.eu/en/factpages/ai-act

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

- Most compliance tools assess one known system at a time.

- That assumes someone has already found the systems.

- For many SMEs, that inventory does not exist.

- AI can arrive through a vendor update, a team purchase or an employee tool.

- So, when the checker asks for each individual AI system, the SME may honestly ask: “Which systems
  are those?”

- [Pause.]

- AI Pre-Scan fills that missing step.

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

> **3 · Review**<br>
> Candidate inventory + focused questions

**Footer:** Human review confirms the facts. A separate deterministic checker applies the law.

**Visual:** recreate the three-stage flow from the existing system-overview slide as native shapes.
The centre evidence gate is the strongest blue object. Unsupported findings peel downward into an
`UNDETERMINED` tray rather than continuing as claims.

**Speaker notes**

- The only input is a company name.

- First, the system maps the public footprint: registry, website, careers, vendor references and news.

- Second, every candidate finding must pass the evidence gate.

- The exact quote must exist, the source must be traceable and the timing must fit the claim.

- Unsupported findings become undetermined, not facts.

- Third, the adviser receives a candidate inventory plus focused client questions.

- Human review confirms the facts; a separate deterministic checker applies the law.

- [Pause.]

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

- [Enter **Personio** and select **Scan**.]

- I begin with only a company name.

- From here, I take my hands off the keyboard while the workflow researches, extracts and checks the
  evidence.

- [If the workflow loops back to research, point to it.]

- That loop-back is intentional: the gate could not support a claim, so the workflow researched again.

- [Open the Personio result and point to the highlighted quote.]

- Personio has three candidates: one evidenced and two undetermined.

- The key is this exact supporting sentence—not the model's wording.

- The two unresolved candidates become focused client questions.

- [Switch to the Ballymaloe Foods result.]

- Here, the scan found no public evidence, so it claimed zero systems and produced one question.

- No public evidence does not mean no AI use; it means the external scan cannot make that claim.

- [If the live run is unavailable, open the retained sample reports.]

- These reports were generated through the same documented run path.

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

> exact quote ✓  traceable source ✓  current enough ✓

> **Otherwise:** research again → `UNDETERMINED` → client question

**Proof strip:** unsupported claims refused **1.0** · false claims on thin-data companies **0** ·
missing source details **0** across five evaluation runs

**Visual:** a horizontal gate. Three compact checks feed a blue pass lane; a failed check drops into
an amber `UNDETERMINED` lane. The proof strip is large and sparse along the bottom.

**Speaker notes**

- This gate is the trust mechanism.

- A finding ships only when all three checks pass.

- One: the exact quote exists in the fetched source.

- Two: the source is traceable, with complete identity and retrieval details.

- Three: the source is current enough for the claim.

- If a check fails, the workflow researches again.

- If support still cannot be found, the result becomes undetermined and the uncertainty becomes a
  client question.

- Across five runs: unsupported claims refused, **1.0**; false claims on thin-data companies, **0**;
  missing source details, **0**.

- [Pause.]

- The trust comes from the gate, not from asking the model to be careful.

**Transition:** That gate also explains the stack choice.

[Sources]

- src/ai_prescan/gate.py
- eval/results.md
- docs/architecture.md

[/Sources]

---

### Slide 6 — LangGraph runs the full evidence loop

**Archetype:** `statement`

**Time:** 0:45

**Visible copy**

> **INSIDE LANGGRAPH**

> Research → extract → **evidence gate**

> **pass → report** → supported facts + questions<br>
> **retry → research**<br>
> **no retries left** → undetermined

**Outside LangGraph:** n8n files the finished report in Notion. It does not make decisions.

**Visual:** a thin blue outline creates a real boundary labelled **INSIDE LANGGRAPH**. It contains
research, extraction, the evidence gate, report routing, the retry path and the undetermined stop.
The dashed retry arrow reconnects directly to the Research block. A separate grey rail below sits
outside the outline, ends at a Notion report card and is labelled **OUTSIDE LANGGRAPH**.

**Speaker notes**

- The blue outline is the LangGraph boundary.

- Inside it are research, extraction, the evidence gate, retry state and report routing.

- LangGraph keeps the deterministic evidence gate inside that workflow loop.

- If the evidence checks pass, supported facts and questions move to the report.

- If a check fails and retries remain, the workflow researches again.

- If no retries remain, the claim becomes undetermined.

- Nothing is forced through.

- The grey rail sits outside LangGraph: n8n only files the finished report in Notion.

- n8n does not research, judge evidence or make compliance decisions.

- We verified delivery from the Notion API response—not only from an n8n success message.

**Transition:** The same architecture points to a recurring product, not just a one-off scan.

[Sources]

- stack_decision.md
- docs/architecture.md
- workflows/README.md

[/Sources]

---

### Slide 7 — Vendor updates can change a client's AI inventory

**Archetype:** `ask`

**Time:** 0:55

**Visible copy**

> **POST-MVP · VENDOR DRIFT**

> MAY<br>
> Client already uses the ATS · no evidenced AI ranking

> JUNE<br>
> Vendor adds AI CV ranking · no new client purchase

> JULY ALERT<br>
> Inventory changed · alert the adviser

**Close:** Turn a blank-page scan into an auditable, recurring conversation.

**Visual:** a single three-point timeline with the July alert as the largest blue card. Under it, a
small commercial ladder reads **adviser pilot → validate drift alerts → retained monitoring**. Mark
the entire ladder clearly as future validation, not current traction.

**Speaker notes**

- The MVP today is an on-demand scan of one company.

- The post-MVP opportunity is vendor-drift monitoring.

- In May, the client already uses an ATS, but no AI-ranking feature is evidenced.

- In June, the vendor adds AI CV ranking; the client buys nothing new.

- In July, the adviser receives an alert: the client's AI inventory changed.

- That change signal can recur across an adviser portfolio.

- The commercial test is: adviser pilot, validate useful drift alerts, then test retained monitoring.

- This is future validation—not current traction.

- [Pause.]

- AI Pre-Scan can turn a blank-page scan into an auditable, recurring conversation.

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
| Unsupported claims refused: **1.0** | Expected systems found: **0.444** vs 0.75 target |
| False claims on thin-data companies: **0** | Correct role labels: **0.739** vs 0.90 |
| Missing source details: **0** | Unsupported use claims: **0.333** vs 0.10 |

> Same code, different recall: one run is not evidence of improvement.

**Visual:** two balanced columns, green-neutral on the left and amber-neutral on the right. A small
variance line chart along the bottom shows runs 3 and 5 as identical-code points. Do not use red/green
alone; pair colour with pass/miss labels.

**Speaker notes**

- The evaluation shows a clear split.

- The honesty controls are stable: honest refusal is **1.0**; thin-company false positives are **0**;
  provenance violations are **0**.

- Discovery quality is not yet at target.

- Recall—how many expected systems were found—is **0.444** against a **0.75** target.

- Role correctness—whether company roles were labelled correctly—is **0.739** against **0.90**.

- The over-claim rate—unsupported claims of current use—is **0.333** against a maximum of **0.10**.

- The same code produced recall of **0.556** and **0.444** in two runs.

- [Pause.]

- One run cannot prove an improvement; use repeated runs or a frozen page cache before tuning claims.

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

- The boundary is deliberate.

- AI Pre-Scan establishes candidate facts from public sources: systems, quoted evidence, provenance
  and unresolved questions.

- It does not classify legal risk.

- An adviser confirms the facts with the client at the human-review checkpoint.

- Only then does a separate deterministic checker classify risk and determine obligations.

- Internal tools, systems behind a login and employee use of consumer AI remain outside the external
  scan's field of view.

- [Pause.]

- The product never claims complete visibility, legal advice or an autonomous compliance decision.

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

> **FINDS EVIDENCE**  Serper · NewsAPI · GLEIF · Wikidata

> **VERIFIES**  OpenAI extraction · Pinecone evidence store · deterministic gate

> **DELIVERS**  Markdown report · n8n → Notion

**Footer:** 12-company evaluation · two retained sample reports · offline test suite

**Visual:** four horizontal capability bands feeding one report card. Keep service names as plain
text; do not use unverified logos. A small boundary label marks scheduled sweeps and vendor-corpus
ingestion as **designed, not built**.

**Speaker notes**

- The MVP works end to end.

- It runs in the browser or from the command line with a company-name trigger.

- It finds evidence through Serper, NewsAPI, GLEIF and Wikidata.

- OpenAI supports extraction, Pinecone stores evidence and the deterministic gate verifies each
  finding.

- The output is a Markdown report; n8n can deliver it into Notion.

- The evidence base includes a twelve-company evaluation, two retained sample reports and **104**
  passing offline tests.

- The retained samples are generated artefacts—not hand-edited showcase copy.

- [Pause.]

- Scheduled sweeps and vendor-corpus ingestion are designed next steps, not part of the built MVP.

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
