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

Research on 7 Aug 2026 turned up a case more common than the one the set was designed around.

**Teamtailor publishes its own EU AI Act guidance.** It states its AI features sit in *"Co-pilot,
which can be used by any customer who chooses to activate it"*, and that *"some of our AI features
will fall under the act's definition of a high risk AI system, since they can materially influence
the outcome of decision making in the recruitment process."*

Its customer-stories page names twelve companies. **None of them mentions AI.**

So for every one of those companies, public evidence establishes: they use Teamtailor; Teamtailor
ships AI features it flags itself as potentially high-risk; the features are **opt-in**; and whether
this customer switched them on **is published nowhere.**

That is not an edge case. It is the ordinary shape of the problem, and it splits attestation into
three levels rather than two:

| Attestation | Meaning | Correct scan output |
|---|---|---|
| `deployed` | A named party states the system is in use | A finding |
| `capability-present` | Vendor confirmed, AI capability confirmed, activation unpublished | **`undetermined` + a discussion-list question** |
| absent | No published AI use | No finding |

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

---

## 2. Ground-truth format

`eval/ground_truth.json` — one entry per company:

```json
{
  "company": "Example Ltd",
  "jurisdiction": "IE",
  "band": "single-system",
  "known_systems": [
    {
      "system": "AI CV ranking in applicant tracking system",
      "vendor": "Example ATS",
      "source": "https://vendor.example/customers/example-ltd",
      "source_type": "vendor-case-study",
      "attested_date": "2026-06-11"
    }
  ],
  "known_absent": ["customer-facing chatbot"]
}
```

`known_absent` matters: it turns a claimed system into a **measurable** false positive rather than a
finding nobody can adjudicate.

---

## 3. Metrics

| Metric | Definition | Target |
|---|---|---|
| **Recall** | Known systems found ÷ known systems | ≥ 0.75 |
| **False-positive rate** | Findings contradicted by `known_absent` ÷ total findings | ≤ 0.10 |
| **Source-claim accuracy** | Findings whose quoted passage genuinely supports the claim ÷ findings | ≥ 0.95 |
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
- **Recall re-measured over time** as a decay detector: a fall against an unchanged ground-truth set
  means the research heuristics have rotted, not that the companies changed
  (`docs/scaling-and-durability.md`).

## 5. What this does not measure

- Whether any legal conclusion is correct — the system makes none.
- Whether the company is *actually* compliant.
- Internal AI with no public footprint, and employee use of consumer AI tools. Both are outside what
  any external scan can see, and the report says so rather than scoring itself against them.
