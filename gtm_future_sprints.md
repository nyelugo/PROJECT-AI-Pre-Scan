# Future GTM Sprints

**Project:** AI Pre-Scan · **Author:** Nnanyelugo Ahukannah

These are **post-MVP sprints — not work claimed as done.** The MVP is a single-company scan producing
an evidenced inventory and a discussion list. Everything below happens after that works.

**The MVP boundary, stated plainly:** the MVP scans one company on demand and produces two artefacts.
It has no accounts, no scheduling, no persistence between runs, and no customer. Each sprint below
adds exactly one of those, in the order that tests the riskiest assumption first.

---

## Sprint 1 — Adviser pilot

**Goal:** find out whether a compliance adviser will actually use a pre-scan before a client
conversation, and whether it changes what they do.

**Target buyer:** small compliance and accountancy firms in Ireland and the Netherlands, 3–15 staff,
with SME client lists. The operator is a partner or senior consultant who scopes engagements.

**Channel / motion:** direct outreach to 5 firms — founder-led, no product marketing. LinkedIn and
warm introductions through the bootcamp network. Each pilot runs as a working session: they name 10
clients, we return 10 pre-scans, they tell us what was wrong.

**Key deliverable:** a batch runner that accepts a list of company names and returns one report per
company, plus a structured feedback form capturing, per report, *what did we miss* and *what did we
claim that isn't true*.

**Success metric:** 3 of 5 firms run it across ≥10 clients each, and **≥1 firm states it changed what
they quoted or how they opened the client conversation.** A firm that finds it interesting but
changes nothing is a failure, not a soft pass.

**What this sprint is really testing:** that the discussion list — not the inventory — is the thing
they value. If they ignore the discussion list, the product thesis is wrong.

---

## Sprint 2 — Vendor-drift monitoring

**Goal:** convert a one-off scan into a recurring alert, on the one signal nobody else is positioned
to catch.

**Target buyer:** the firms that completed Sprint 1. Same operator, existing relationship, no new
acquisition motion.

**Channel / motion:** upsell inside the pilot. Scheduled re-scans across a client list, with a
digest delivered where the adviser already works — email, or Notion.

**Key deliverable:** scheduled re-scan with **delta reporting** — the report says what *changed*
since the last scan, not what is true today. The headline output is:

> *"Your client's applicant tracking vendor shipped AI CV ranking in a June update. They were out of
> scope in May. They are in scope now, and nobody at the company did anything."*

**Success metric:** **newly-detected systems per sweep** — how many findings appear that were not in
the previous scan and are confirmed real by the adviser. Plus retention past month 3, since a
monitoring product that isn't renewed didn't monitor anything worth paying for.

**Why this sprint and not more coverage:** the client changed nothing, so nobody at the client is
watching. The change arrived inside a product they already owned. This is the finding the
architecture is uniquely placed to make, and it recurs — which is what makes it a subscription rather
than a one-off sale.

---

## Sprint 3 — Internal inventory mode

**Goal:** replace the weakest input in the system — public evidence — with the client's own data,
once a relationship exists to make that possible.

**Target buyer:** end clients reached through the advisers in Sprints 1–2, brought in by their
adviser rather than sold to directly.

**Channel / motion:** adviser-led. The pre-scan is the wedge; this is what the adviser sells after
the first conversation lands.

**Key deliverable:** a second **research adapter** that reads a vendor list, procurement export or
SaaS-spend report instead of searching the public web. Classification, grounding, the discussion list
and the report all stay identical — only the evidence source changes, which is why the architecture
separates research from everything downstream.

**Success metric:** **systems found from internal data that public research missed.** This is
directly measurable by running both adapters on the same company, and it quantifies the value of the
upgrade in the only terms the buyer cares about.

**Honest risk:** if the number is small, public research was good enough and this sprint should not
ship. The metric is designed so that answer is visible rather than avoidable.

---

## What is deliberately not here

- **Multi-regime coverage.** Architecturally cheap (see `docs/scaling-and-durability.md`) but there is
  no evidence yet that anyone wants it. It follows demand from Sprint 1, not a roadmap.
- **Self-serve SaaS.** No account system, no billing, no marketing site until an adviser has paid for
  the service delivered by hand.
- **More AI features.** The product's constraint is trust in the findings, not the breadth of them.
