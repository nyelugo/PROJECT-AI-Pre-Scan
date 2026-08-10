# Two-Minute Elevator Pitch

Read aloud. ~330 words, about two minutes at a measured pace. Delivery notes at the end — not to be
read out.

---

Eight days ago, on the second of August, the EU AI Act's high-risk rules became live.

They don't only bind the companies that build AI. They bind the ones that bought it.

So every small company now has a question to answer: which parts of this apply to us?

To answer that, you need to know what AI you actually run, in what role, and since when.

Almost no company knows.

Someone in marketing bought a tool on a company card. The recruitment system added AI CV ranking in a
vendor update nobody read. Nothing was decided. Nothing was written down.

Now, there are good compliance tools out there. The Future of Life Institute publishes a free one,
and it's genuinely well built. But read its opening instruction. It says: complete this form for each
individual AI system used in your organisation.

Every tool starts after the hard part. They all assume the list already exists.

I'm building the list.

You give it a company name. It researches that company's public footprint — website, careers pages,
named vendors, press — and it returns two things.

First, an inventory of the AI systems that company appears to run, where every row carries the
sentence it came from. Not a link. The sentence.

Second, a short list of questions to ask them, covering everything public evidence cannot settle.

It makes no legal judgement at all. No risk tiers, no obligations, no article numbers. It establishes
facts; the deterministic checker applies the law. That boundary is the entire design.

And when it can't evidence something, it says undetermined. It doesn't guess. An agent that always
finds something is an agent that fabricates.

It's built in LangGraph, because the check that asks "do I actually have evidence for this, or do I
go back and look again" has to live inside the loop, not watch from outside it.

Who pays for it? A compliance adviser with forty clients and no way to know which of them to worry
about. She runs it before the meeting — and walks in already knowing what to ask.

---

## Delivery notes

**Pace.** Around 330 words. Do not rush the short lines — they are short on purpose and they carry
the argument.

**Three deliberate pauses:**
- after *"Almost no company knows."*
- after *"They all assume the list already exists."*
- before *"I'm building the list."*

**The line to land hardest:** *"Not a link. The sentence."* It is the whole difference between this
and a plausible list, and it is the sentence a technical audience will remember.

**Do not apologise for the scope.** "It makes no legal judgement at all" is a strength, not a
limitation — deliver it as a design decision, because it is one.

**If running long, cut:** the LangGraph paragraph. The stack is the least interesting part to a mixed
audience and the first thing anyone will ask about anyway.

**If asked "isn't that what the checker does?"** — it does the step after this one. Its first
instruction assumes the inventory exists. This produces it.
