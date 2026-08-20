# Data protection record

**Status:** first-pass, maintained by the builder · **Last reviewed:** 20 August 2026
**Scope:** AI Pre-Scan as built — local operation, no hosted backend, no external users.

This is the accountability record for AI Pre-Scan. It exists because an external GDPR audit of this
project (Vittal Navale, 19 August 2026) correctly marked the lawful basis as *"cannot determine —
no LIA appears anywhere"*. The assessment had been written, but it lived in a coursework submission
rather than in this repository. **Compliance reasoning stored where an auditor will not look is
indistinguishable from compliance reasoning never done**, and an auditor is right to mark it absent.

It is not legal advice, not a DPIA, and not a certification. Items marked **TBD — legal review** are
flagged deliberately rather than guessed.

---

## 1. Does this system process personal data?

**Yes, incidentally.** Nothing about individuals is sought: the subject of research is the
organisation. But public pages carry names, job titles, quotes and bylines, and those pages are
fetched and read. Since 19 August only **gate-validated passages** are stored rather than whole
pages, which narrows the exposure without eliminating it — a quote from a public source can still
name someone.

## 2. Records of processing

| # | Data category | Source | Purpose | Retention | Outside EEA? |
|---|---|---|---|---|---|
| 1 | Names, titles, quotes and bylines inside fetched pages | Public web via Serper / news API | Extract candidate AI systems from source text | Not persisted — pages are read in memory and discarded | **Yes** — OpenAI |
| 2 | Validated evidence passages, embedded | Derived from (1) | Evidence-gate verification and later diffing | Until the next scan of that company; `purge_scan` runs before every live scan | **Yes** — Pinecone, OpenAI |
| 3 | Vendor announcement and changelog text | Public web | Persistent cross-company vendor corpus — **designed, not built** | Indefinite by design if built | **Yes** — Pinecone |
| 4 | Quoted evidence inside a finished report | Derived from (1) | Report delivery and filing | **Indefinite once filed — see open item O1** | **Yes** — Notion via n8n |
| 5 | Company name, scan metadata, finished report | Operator input and system output | Local scan history (`store_jobs`) | **None defined — see open item O2** | No — local disk |
| 6 | Adviser's client list, including the free-text `notes` field | Typed by the operator | Client-book management | None defined | No — local disk |
| 7 | Source text and generated reports | Public web | Evaluation, ground truth, two committed sample reports | Indefinite, irreversible in git history | **Yes** — GitHub |

Row 6 exists because the same external audit found it and this project's own self-assessment had
not: `Client.notes` is unstructured and operator-controlled, which is exactly where a contact
person's name ends up.

## 3. Lawful basis, and the legitimate interests assessment

| Purpose | Basis | Justification |
|---|---|---|
| Extract candidate systems (row 1) | **Art 6(1)(f)** legitimate interests | An adviser cannot apply the AI Act without knowing which systems a client runs; the data is already public |
| Evidence-gate verification (row 2) | **Art 6(1)(f)** | Checking claims against retrieved text is what stops the system fabricating |
| Vendor corpus (row 3) | **TBD — legal review** | A cross-company, indefinite corpus is a different purpose from a single scan; needs an Art 6(4) compatibility assessment before it is built |
| Report delivery (row 4) | **Art 6(1)(f)**, or contract if operated for a client | Filing a report the adviser commissioned |
| Local scan history (row 5) | **Art 6(1)(f)** | Re-open a prior scan without re-running it |
| Client book (row 6) | **Art 6(1)(f)** | Operating the adviser's own client list |
| Evaluation and samples (row 7) | **Art 6(1)(f)** | Honest measurement; published samples verified free of personal data |

### The three-part LIA — rows 1 and 2

**1. Legitimate interest?** Yes, concretely. An external adviser cannot assess a client's AI Act
position without an inventory, and small companies frequently have none. The system is built to
refuse rather than invent when evidence is absent.

**2. Necessary?** Reading public pages and quoting the passages that evidence a finding: yes — there
is no less intrusive way to establish what a company publishes about its own tooling. **Storing
whole fetched pages was not necessary**, and that failure was the reason this assessment first
concluded the basis was unsatisfied in practice. Fixed on 19 August (`3eee7f6`): only the validated
passage and its provenance are stored.

**3. Does the individual's interest override?** With minimisation in place, no — the data is public,
the processing is not directed at the individual, no decision is made about them, and nothing is
published about them. Two conditions keep it that way: retention must stay bounded, and the transfers
in open item O3 must be documented. Without those, the balance tips the other way.

## 4. Roles and processors

| Entity | Role | DPA / mechanism |
|---|---|---|
| The builder (today) | **Controller** — chose purposes and means for development and evaluation | — |
| A subscribing adviser (if hosted) | **Controller**; the builder would become a **processor** | Would require Art 28 agreement. **Hosting model undecided** — see O4 |
| OpenAI | Processor — extraction and embeddings | **None. Required.** |
| Pinecone | Processor — vector storage | **None. Required.** |
| Notion / n8n | Processors — report delivery and filing | **None. Required**, and previously unnamed in this project's own documentation |
| Serper, news API | Independent controllers — sources, not processors | Their terms govern reuse |
| GLEIF, Wikidata | Independent controllers — public registries | GLEIF returns entity records, not officers |
| GitHub | Processor — repository hosting | Vendor terms |

## 5. Transfers

OpenAI, Pinecone, Notion and GitHub are US-based. Mechanism would be the EU–US Data Privacy Framework
where the entity is certified, otherwise SCCs plus a transfer impact assessment. **None is documented
today** (O3).

## 6. Article 35(1) threshold assessment

**Recorded position, agreed with the external auditor on 20 August 2026.**

Criteria that apply now: **innovative technology** (LLM extraction plus vector retrieval) and
**matching or combining datasets** (search, news, registry and vendor sources joined per company).
**Cross-border transfer** is arguable while the transfers remain undocumented.

Criteria that do **not** apply: no evaluation or scoring of people, no automated decision-making with
significant effects, no systematic monitoring of individuals, no special-category data at scale, no
large-scale processing, no vulnerable data subjects.

**Conclusion: a full DPIA is not required at present scale**, because no individual is assessed. It
**becomes a precondition for scheduled re-scans** — the GTM sprint 2 feature — because repeated,
automated research about the same companies over time, naming the same individuals repeatedly, is
systematic monitoring in a way a one-off scan is not. That trigger, rather than a date, is what
should prompt the DPIA.

## 7. Article 14 and data subject rights

**Article 14 applies** — the data is not obtained from the data subject. The disproportionate-effort
exemption in Art 14(5)(b) is arguable on these facts and is where this most likely lands, but it must
be **reasoned and recorded**, not assumed. Not yet done (O5).

| Right | Position |
|---|---|
| **Access (Art 15)** | Partially serviceable. Passages are keyed by company, not person, so a complete "all data about this individual" search is not possible today |
| **Erasure (Art 17)** | Serviceable for the research store — `delete_namespace` and `purge_scan` exist since 19 August. **Not serviceable for a delivered report already filed to Notion** (O1) |
| **Objection (Art 21)** | No mechanism, and no notice, so the right cannot be exercised in practice. Linked to Art 14 above |

## 8. Open items

| # | Item | Owner | Trigger |
|---|---|---|---|
| **O1** | No retention period or deletion route for a report once filed to Notion — the purge covers the store I built and not the copy I sent | Builder | Before any real client report is filed |
| **O2** | No retention schedule for the local job store; exclusion from git is source-control hygiene, not a control | Builder | Before external use |
| **O3** | No transfer mechanism or Art 28 agreement for OpenAI, Pinecone or Notion — stated candidly in `proposal.md` §9 but with no owner or date until now | Builder → counsel | Before the first real client scan |
| **O4** | Hosting model undecided; it determines whether a processor relationship exists at all | Builder | Part of GTM sprint 1 planning |
| **O5** | Art 14 reasoning not recorded | Builder → counsel | Before external use |
| **O6** | No minimisation guidance on the `Client.notes` free-text field | Builder | Cheap; do with the next UI change |
| **O7** | Art 6(4) compatibility assessment for the vendor corpus | Builder → counsel | Before the corpus is built |

## Provenance of this record

Sections 2–7 were first written as a GDPR self-audit on 19 August 2026 and are reproduced here as
the canonical record. Rows and items **O1** and **O6**, and the sprint-2 trigger in section 6, come
from the external peer audit by Vittal Navale — findings this project's own self-assessment did not
reach.
