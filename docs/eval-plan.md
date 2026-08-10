# Evaluation Plan

The claim this project makes is that it finds AI systems a company runs, accurately, and admits when
it cannot. That claim has to be measured, not asserted — and every metric here is checkable against
public evidence, with **no legal judgement required**. That is what the narrowed scope bought.

Method carried over from the Week 5 lab, where measuring a stated assumption moved correct-article
retrieval from 8/10 to 10/10 and exposed a defect the prototype would otherwise have shipped.

---

## 1. Building ground truth

The hard part of this evaluation is not the metrics — it is knowing the right answer.

**Selection rule: only companies that have published their own AI use.** Ground truth comes from the
company's or vendor's own words, never from inference. Acceptable sources, in order of strength:

1. **Vendor case-study and customer pages** — the vendor names the customer and describes the AI
   feature deployed. Strongest, because two parties attest to it.
2. **The company's own announcements** — press releases, engineering blogs, product pages stating
   they use an AI tool.
3. **Job advertisements** written by the company naming the tool or the capability.
4. **Regulatory or annual filings** mentioning AI systems in use.

Excluded: journalism inferring AI use, aggregator sites, and anything the company has not itself
confirmed. If we cannot point at the company's or vendor's own words, it is not ground truth — it is
a guess, and grading against a guess measures nothing.

### The finding that reshaped this set

Research on 10 August 2026 turned up a case more common than the one the set was designed around.

**Teamtailor publishes its own EU AI Act guidance.** It states its AI features sit in *"Co-pilot,
which can be used by any customer who chooses to activate it"*, and that *"some of our AI features
will fall under the act's definition of a high risk AI system, since they can materially influence
the outcome of decision making in the recruitment process."*

Its customer-stories page names twelve companies. **None of them mentions AI.**

So for every one of those companies, public evidence establishes: they use Teamtailor; Teamtailor
ships AI features it flags itself as potentially high-risk; the features are **opt-in**; and whether
this customer switched them on **is published nowhere.**

That is not an edge case. It is the ordinary shape of the problem, and it splits attestation into
four levels rather than two:

| Attestation | Meaning | Correct scan output |
|---|---|---|
| `deployed` | A named party states the system is in use | A finding |
| `capability-present` | Vendor confirmed, AI capability confirmed, activation unpublished | **`undetermined` + a discussion-list question** |
| `attested-absent` | The company has publicly said it has not adopted AI | No finding |
| `no-published-use` | A documented search found no published AI use | No finding |

**A scan that reports a Teamtailor customer as running AI CV ranking is wrong — even though the
guess would often be right.** Guessing right for the wrong reason is the failure this project exists
to avoid, and `capability-present` is where it will happen. The set therefore grades it explicitly.

It also validates the vendor corpus in `docs/architecture.md` with a real first document: the
Teamtailor page states the provider/deployer split, names the model family, and carries dates. That
is precisely the corpus entry the `first evidenced` field depends on.

### Set composition — 12 companies

| Band | Count | Purpose |
|---|---|---|
| Rich public footprint, multiple published AI systems | 3 | Can it find several, and rank the evidenced above the inferred? |
| Exactly one published AI system | 3 | Precision — does it find the real one without inventing three more? |
| **Capability-present** — known vendor with opt-in AI, activation unpublished | 3 | **The trap band.** Correct output is `undetermined` plus a question, not a finding |
| Deliberately thin footprint, no published AI use | 3 | **The honesty band.** Correct output is few or no findings, most marked undetermined |

**The thin and capability bands are the most important and the easiest to omit.** Without them, a
system that always finds something scores well, and one that guesses right for the wrong reason is
indistinguishable from one that knows. They are the direct analogue of the negative test in the Week
5 LangGraph lab, which proved the grounding check could actually fail rather than merely pass.

### Publication rule

The ground-truth file is committed **only where every entry cites the company's or vendor's own
public statement.** This repository is public, and asserting that a named company runs a particular
AI system is a claim about a real organisation. Citing their own words is fair; publishing an
inference is not. Any entry not meeting that bar stays local and is excluded from the committed set.

### The four failure modes the thin band actually catches

The thin band was built by searching for real companies and documenting what came back empty. Three
of the four traps below were not designed — they were found, and they are more realistic than
anything invented at a desk.

| Trap | Where | What fails |
|---|---|---|
| **Non-AI digital transformation** | Keogh's Crisps adopted an ERP system in 2019 with touchscreens, weighing and mobile scanning | A scan that reads "digital transformation" as AI |
| **Name collision** | Searching Barry's Tea surfaces "Barry the Chatbot" — an AI chatbot built for **DPD**, a different company | Entity resolution. Matching a name instead of an organisation |
| **Sector contamination** | Ballymaloe Foods returns a wall of "AI in the food industry" commentary naming no one | Attributing an industry trend to a specific company |
| **Attested absence** | Keogh's CEO on record: *"AI is not adding massive value to manufacturing at our level just yet"* | A scan that cannot represent a company having actively declined |

**Keogh's Crisps is the strongest single entry in the set** — a public denial from the named CEO,
sitting next to a genuine near-miss in the same company's history. Getting it right requires both
restraint and the ability to tell technology adoption from AI adoption.

The capability band adds two more of its own: RebelDot builds software for clients, so its marketing
is saturated with AI vocabulary that says nothing about what it deploys on its own staff; and
Liseberg's sector returns articles about Disney and Legoland using AI, and about Liseberg not at all.

---

## 2. Ground-truth format

`eval/ground_truth.json` groups companies by band. Each system carries the source it was verified
from, the attestation level, and the provenance needed to tell a historical source from evidence of
current state.

```json
{
  "company": "WHOOP",
  "systems": [{
    "system": "WHOOP Coach — generative AI coaching on member biometric data",
    "vendor": "WHOOP (own product), built on OpenAI GPT-4",
    "role": "provider",
    "attestation": "deployed",
    "claim_time_mode": "historical_event",
    "source": "https://www.whoop.com/us/en/thelocker/whoop-unveils-the-new-whoop-coach-powered-by-openai/",
    "source_provenance": {
      "canonical_url": "https://www.whoop.com/us/en/thelocker/whoop-unveils-the-new-whoop-coach-powered-by-openai/",
      "retrieved_at": "2026-08-10T10:00:00Z",
      "source_published_at": "2023-09-26",
      "source_updated_at": null,
      "content_sha256": "<sha256 of fetched content>",
      "authority_class": "company",
      "currentness_checked_at": "2026-08-10T10:00:00Z",
      "currentness_status": "current",
      "superseded_by": null,
      "next_review_at": "<derived from source-class policy>"
    },
    "first_evidenced": "2023-09-26",
    "quote": "WHOOP Coach takes an in-depth knowledge of a WHOOP member's goals, their unique biometric data..."
  }]
}
```

Three fields carry most of the weight. **`quote`** makes source-claim accuracy scoreable — a grader
reads it against the finding rather than judging plausibility. **`role`** separates provider from
deployer, which is the checker's first question and the thing the Week 5 prototype got wrong.
**`claim_time_mode`** declares whether the finding is a historical event or a current-state claim.
**`source_provenance`** makes currentness scoreable: `retrieved_at` alone is insufficient, and the
evaluation loader rejects a current-state item without a content hash, currentness check and status.

**Migration result (10 August 2026).** `eval/migrate_provenance.py` re-fetched and hashed every
source. 11 of 12 system entries now carry a content hash; **the preflight correctly fails on one.**

`whoop.com` returns **HTTP 403** to a scripted fetch while serving the page normally to a real
browser — the same block hit during research. So the WHOOP historical claim has no publication date
from a re-fetch, and the preflight refuses it rather than reusing the date a human read earlier.
That is the rule working: *nothing may be back-filled from what someone remembers seeing.*

The fix is a Phase 2 requirement, now evidenced rather than assumed: **the fetch layer needs a
browser-backed fallback for bot-blocked hosts**, and any host it cannot reach must degrade to
`undetermined` rather than silently vanish from the scan.

The seed file predates this contract. It must be migrated by re-fetching and hashing each
source before the first baseline run; missing values must not be invented from the top-level
`_verified_on` date.

Thin-band entries carry a `trap` field naming the specific way a scan is expected to fail on them,
and `search_documented` recording the query and date that came back empty. An absence is only
evidence if the search for it is on record.

---

## 3. Metrics

| Metric | Definition | Target |
|---|---|---|
| **Recall** | Known systems found ÷ known systems | ≥ 0.75 |
| **False-positive rate** | Findings contradicted by `known_absent` ÷ total findings | ≤ 0.10 |
| **Source-claim accuracy** | Findings whose quoted passage genuinely supports the claim ÷ findings | ≥ 0.95 |
| **Source-currentness validity** | Findings whose source provenance satisfies the rule for the claim's time ÷ findings | 1.00 |
| **Honest-refusal rate** (thin band) | Correctly `undetermined` ÷ items with no public evidence | ≥ 0.90 |
| **Over-claim rate** (capability band) | Capability-present items reported as deployed findings ÷ capability-present items | ≤ 0.10 |
| **Checker-readiness** | Rows answering every factual field the checker needs ÷ rows | ≥ 0.90 |

**Source-claim accuracy is the one that matters most.** A finding with a real URL attached that does
not actually say what the row claims is the fluent-and-wrong failure — the same defect found in Week
5, where every citation existed and two did not support their claims. It is scored by reading the
quoted passage, which is exactly why the report spec requires the passage to be quoted rather than
merely linked.

**Recall is deliberately not set near 1.0.** Some published AI use is genuinely unreachable within a
scan budget, and a system tuned to find everything will invent things. Recall trading against
false-positive rate is the real curve; measuring only one of them hides it.

---

## 4. Cadence

- **On every material change to the research loop**, not once at the end. The Week 5 provision has
  ample room for this — roughly $0.40–0.50 per company on the stronger model, so a full 12-company
  run costs around $5 at the expensive end and cents on the small model.
- **A baseline run before any tuning**, so improvement is measured rather than felt.
- **A provenance preflight before every baseline**, rejecting current-state ground truth whose
  currentness check is overdue or whose stored content hash no longer matches.
- **Recall re-measured over time** as a decay detector: a fall against an unchanged ground-truth set
  means the research heuristics have rotted, not that the companies changed
  (`docs/scaling-and-durability.md`).

## 5. What this does not measure

- Whether any legal conclusion is correct — the system makes none.
- Whether the company is *actually* compliant.
- Internal AI with no public footprint, and employee use of consumer AI tools. Both are outside what
  any external scan can see, and the report says so rather than scoring itself against them.
