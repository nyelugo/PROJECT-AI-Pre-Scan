# Demo Plan — 5 to 7 minutes

Rubric outcome 5 asks the demo to cover **autonomy, the report, the stack rationale and the GTM
path**. Nothing else earns time.

**The one idea to land:** every AI Act tool starts by asking which AI systems you run. Nobody can
answer. This builds that answer, and admits what it cannot.

---

## Running order

| # | Beat | Time | What is on screen |
|---|---|---|---|
| 1 | The gap | 0:45 | The compliance checker, on its own instruction: *"complete this form for each individual AI system used in your organisation"* |
| 2 | Trigger | 0:30 | A company name goes in. Hands off the keyboard |
| 3 | Autonomy | 1:30 | The graph running — searching, extracting, the gate sending it back |
| 4 | The report | 1:30 | Inventory with quoted evidence, then the discussion list |
| 5 | The honest run | 0:45 | Second report, thin-footprint company — mostly `undetermined` |
| 6 | Stack | 0:45 | The gate, in code, inside the loop |
| 7 | GTM | 0:45 | Sprint 2: the vendor-drift alert |

**Total 6:30.** Leaves room to slow down without overrunning.

---

## Beat notes

**1 — The gap.** Open on the checker, not on my project. Show its instruction and let it make the
argument: this tool is good, free and deterministic, and it assumes a list nobody has. *"So I built
the step before it."*

**3 — Autonomy.** The point is that nobody touches anything. Say the trigger was the only input, and
narrate one loop-back out loud — *"it couldn't evidence that claim, so it went back to research"* —
because that is the whole architecture visible in one moment.

**4 — The report.** Land on a **quoted passage**, not the table. *"Every row carries the sentence it
came from, so the adviser can check a finding without opening the link."* Then the discussion list:
*"and this is what the adviser actually walks in with — the questions public evidence can't settle."*

**5 — The honest run.** Do not skip this to save time. A second report where the system finds little
and says so is the strongest thing in the demo, because everyone else's agent will find something
about everything. *"This company publishes nothing about AI use. A system that found four things here
would be lying."*

**6 — Stack.** Show the gate as code, inside the loop. *"That's why LangGraph is primary — the gate
has to redirect the agent, not just report on it. n8n triggers it and delivers the report, which is
what n8n is better at."* One sentence on the trade-off, then move.

**7 — GTM.** One sprint, not three. Sprint 2, because it is the sharpest: *"your client's ATS vendor
shipped AI CV ranking in June. They were out of scope in May, they're in scope now, and nobody at the
company did anything."* Then: that recurs, which is what makes it a subscription. Point at
`gtm_future_sprints.md` for the rest.

---

## Deliberately not shown

- Repo tour and code walkthrough beyond beat 6
- The full report, read out — one section, one quote
- All three GTM sprints
- Anything the system does not yet do

## Preparation

**Commands, in order, so nothing is improvised on screen:**

```bash
# Beat 2-3 — show the interface, not the terminal. Type a company name, hands off the keyboard.
python -m ai_prescan.web        # http://127.0.0.1:8000

# Terminal fallback if the browser misbehaves on the day
PYTHONPATH=src python -m ai_prescan "Personio" --live --out /tmp/demo.md

# Beat 5 — the honest run, pre-generated so a thin scan does not eat 90 seconds of airtime.
open samples/ballymaloe-foods.md
```

- **Both sample reports are already in the repo** (`samples/`), generated through the documented run
  path and unedited. If the live run fails, narrate the pre-generated Personio one and say so — no
  silent recovery.
- **Pre-flight the live run on the same company** shortly before presenting. Scans are not
  deterministic: search results move, and one host in the evaluation set blocks scripted fetches
  intermittently.
- **Nothing on screen may show a key value**, including terminal output and environment dumps. The
  CLI prints key presence as length plus hash fingerprint, which is safe to show and worth showing.
- The demo company is publicly listed or clearly public-facing, and every claim shown is one the
  company or its vendor published themselves.

## The numbers to have ready

From `eval/results.md`, in case a reviewer asks what "it works" means:

- **Honest refusal 1.0, thin-band false positives 0, provenance violations 0** — constant across all
  five runs, on 64+ findings each time. Those three are the ones to quote.
- **Recall 0.444 and role correctness 0.739** both miss target, and both vary run to run on
  identical code. Say that plainly if asked; the honest version is stronger than a number.
- **The finding worth volunteering:** runs 3 and 5 used the same code and gave recall 0.556 and
  0.444. A single run cannot support a claim about a configuration — which I learned by making
  exactly that mistake and having the next run contradict me.

## Likely questions

**"Doesn't the checker already do this?"** It does the step after. Its instruction assumes the
inventory exists; this produces it.

**"Are you giving legal advice?"** No — no risk tiers, no obligations, no articles. Facts and
questions. The determination is the checker's.

**"How do you know it works?"** Twelve companies with published AI use as ground truth, including
four with none, so honest refusal is measured rather than assumed. `docs/eval-plan.md`.

**"What breaks first?"** Research decay. A scan is a snapshot with a shelf life of weeks, which is
why the product is monitoring rather than assessment — and why Sprint 2 is the delta, not the scan.
