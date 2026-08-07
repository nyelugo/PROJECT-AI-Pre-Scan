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

### Set composition — 12 companies

| Band | Count | Purpose |
|---|---|---|
| Rich public footprint, multiple published AI systems | 4 | Can it find several, and rank the evidenced above the inferred? |
| Exactly one published AI system | 4 | Precision — does it find the real one without inventing three more? |
| Deliberately thin footprint, no published AI use | 4 | **The honesty band.** Correct output is few or no findings, most marked undetermined |

**The thin band is the most important and the easiest to omit.** Without it, a system that always
finds something scores well. It is the direct analogue of the negative test in the Week 5 LangGraph
lab, which proved the grounding check could actually fail rather than merely pass.

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
