# Scaling and Durability

Two questions this project has to answer to be more than a one-regime, one-moment tool: **can it
cover other AI regimes?** and **what stops it going stale?**

This document is design intent, not implemented behaviour. Nothing here is built yet.

---

## 1. Scaling to other regimes

The architecture already separates **research** from **determination**. Research — what AI a company
runs, from which vendor, in what domain, since when — is regime-agnostic. The EU AI Act, a US state
regime, a sectoral regulator or an insurer's questionnaire all need the same underlying facts and
differ only in how they carve them up.

So one research pass can serve many regimes. **The expensive half is shared; the cheap half is what
multiplies.**

### The rule that makes this true

> **Store functional facts. Derive regime categories.**

| Don't store | Store |
|---|---|
| `Annex III point 4` | `ranks job applicants` · `affects hiring decisions` · `about identifiable individuals` |
| `high-risk` | `vendor-supplied` · `deployed June 2026` · `human reviews output: unknown` |

Recording `Annex III point 4` bakes the EU into the data permanently. Recording what the system
*does* makes Annex III point 4 a derivation — and so is Colorado's "consequential decision" test, and
so is any future regime's taxonomy.

Break this rule and every new regime is a fork. Keep it and a new regime is an **adapter**: a mapping
from the core schema to that regime's question set, plus its determinator. That is a table, not a
rebuild.

### What each regime needs from the core schema

Each adapter needs three things, none of which touch the research loop:

1. A **field mapping** from core facts to that regime's inputs.
2. A **determinator** — the deterministic tool or decision tree that applies that regime's law.
3. An **undetermined set** — the questions public evidence cannot settle, which become that regime's
   discussion list.

The EU adapter is the first one, and its undetermined set is currently: *has the company rebranded,
repurposed or substantially modified a bought system?* (Article 25).

### The commercial consequence

An adviser with clients in more than one jurisdiction runs **one scan**, not three. That is the
argument for the layered design, and it only exists if the core schema stays regime-neutral from the
first commit — which is why this document exists before the code does.

---

## 2. What can go stale, and which of it matters

### Legal drift — largely neutralised

Because the project makes **no legal claims**, amendments, guidance, delegated acts and harmonised
standards are not its problem. The determinator owns the law; when the FLI checker updates its tree,
this project inherits the change for free.

This was a consequence of narrowing scope after review, not a designed-for benefit — but it is real,
and it insulates the project from the fastest-moving part of the domain.

### Determinator dependency — manageable

If the checker changes its questions or disappears, what breaks is a **mapping**, not the product,
because the fact schema is owned here. Cost of that failure is one adapter update.

### Research decay — the real risk

Websites are rewritten, vendors rename and merge, search behaviour shifts, and companies adopt AI
continuously. **A scan is a snapshot with a shelf life measured in weeks.**

The response is not better research. It is accepting what the product actually is:

> **This is monitoring, not assessment. The delta is worth more than the scan.**

The highest-value output the system can produce is not the first inventory. It is:

> *"Your client's ATS vendor shipped AI CV ranking in a June update. They were out of scope in May.
> They are in scope now, and nobody at the company did anything."*

Nobody is watching that vector, because the client changed nothing — the change arrived inside a
product they already owned. That is the finding this architecture is uniquely placed to make, and it
recurs, which is what makes it a subscription rather than a one-off.

### Detecting decay rather than discovering it late

The evaluation set doubles as a decay detector. Recall measured against companies whose AI use is
independently verifiable should be stable over time; **a fall in recall means the research heuristics
have decayed**, not that the companies changed. Re-running the eval on a schedule turns silent rot
into a visible signal — the same discipline that caught the retrieval defect in the Week 5 lab.

---

## 3. The relevance risk worth naming

By 2028, near enough every SaaS product will ship AI features. At that point an inventory of "AI
systems" degenerates into an inventory of all software, and the signal disappears.

**The durable framing is not *find the AI*. It is *find the AI that makes or assists consequential
decisions about people*.** That is what every regime actually regulates, present and future, and it
survives ubiquity. Framing the product around detection rather than consequence would date it.

The core schema should therefore treat *"what decision does this affect, about whom, with what human
involvement"* as its primary axis, and *"is it AI"* as a qualifier.

### The one that could undercut it

If vendors begin publishing machine-readable AI declarations — which the Act's transparency direction
pushes toward — external research becomes both easier and less differentiated. The defensible
position then is not discovery but the **cross-vendor, cross-regime, time-series view**: what a whole
client portfolio runs, how it changed, and what that means under more than one regime at once.

Worth tracking as a signal rather than planning around today.
