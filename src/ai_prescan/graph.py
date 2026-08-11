"""The LangGraph skeleton.

Nodes and edges mirror docs/architecture.md. Phase 1 wires the shape and the loop-back; Phase 2
replaces the fixture research node with live tools. The structure that matters is already here:

    extract -> gate -> (research again | emit | undetermined) -> assemble

The gate is a routing decision, not a reporting step. That is why LangGraph is primary — a check
that can only observe cannot send the agent back for a better source.
"""

from __future__ import annotations

import operator
import re
from datetime import datetime, timezone
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from . import extract, fetch, fixtures, gate, store, tools
from .schemas import (
    Attestation,
    ClaimTimeMode,
    Confidence,
    DiscussionItem,
    Evidence,
    Finding,
    Report,
    UnavailableSource,
)

MAX_PAGES_PER_SCAN = 12

MAX_RESEARCH_PASSES = 3


class ScanState(TypedDict, total=False):
    company: str
    domain: str | None
    passes: int
    candidates: list[Finding]
    settled: list[Finding]          # replaced each pass, never accumulated
    needs_research: bool
    discussion: Annotated[list[DiscussionItem], operator.add]
    unavailable: Annotated[list[UnavailableSource], operator.add]
    sources_consulted: int
    report: Report
    use_fixtures: bool


def resolve_company(state: ScanState) -> dict:
    """Registry lookup. Fixture path asserts identity without a network call."""
    return {"passes": state.get("passes", 0), "sources_consulted": 0}


def research(state: ScanState) -> dict:
    """Gather candidates: search + news + registry, then fetch and extract from each page."""
    if state.get("use_fixtures", True):
        candidates = fixtures.candidate_findings()
        return {
            "candidates": candidates,
            "passes": state.get("passes", 0) + 1,
            "sources_consulted": sum(len(f.evidence) for f in candidates),
        }

    company = state["company"]
    # A domain supplied by the adviser beats anything we can infer. She knows her own clients, and
    # a bare name is ambiguous in ways that only show up as a confident report about the wrong
    # company — which on a list of forty looks exactly like a correct one.
    given = state.get("domain")
    ident = tools.Identity(query=company, domain=given, sources=["supplied by operator"]) \
        if given else tools.identity(company)
    found = tools.research_all(company, domain=ident.domain)
    unavailable = list(found.unavailable) + list(ident.unavailable)

    # Round-robin across queries rather than taking hits in order. Domain-scoped queries run first
    # and would otherwise consume the whole page budget with the company's own pages, so the
    # vendor-attestation queries — which find customer stories and case studies, the strongest
    # evidence class — never got a slot. That, not search coverage, is what capped recall.
    by_query: dict[str, list[str]] = {}
    for hit in found.hits:
        if hit.get("url"):
            by_query.setdefault(hit.get("query") or hit.get("tool", "other"), []).append(hit["url"])

    urls, seen = [], set()
    for rank in range(max((len(v) for v in by_query.values()), default=0)):
        for bucket in by_query.values():
            if rank < len(bucket) and bucket[rank] not in seen and len(urls) < MAX_PAGES_PER_SCAN:
                seen.add(bucket[rank])
                urls.append(bucket[rank])
        if len(urls) >= MAX_PAGES_PER_SCAN:
            break

    candidates: list[Finding] = []
    consulted = 0
    for url in urls:
        result = fetch.fetch(url)
        if not result.ok:
            # Named, not dropped. An unreadable source is a stated gap in the scan.
            unavailable.append(UnavailableSource(label=url, reason=result.unavailable_reason or "unreachable"))
            continue
        consulted += 1

        # Cheap deterministic filter before spending a model call: if the company is not named on
        # the page at all, the page cannot be evidence about it. Catches the bulk of name-collision
        # hits for nothing, and the model still judges subjecthood for the ones that survive.
        # A page on the company's own domain is about the company by construction. Otherwise the
        # name must appear, as a whole word, before a model call is worth making.
        on_own_domain = bool(ident.domain and ident.domain in result.url)
        if not on_own_domain and not _mentions(company, result.text):
            continue

        # Into the evidence store, so the gate checks claims against retrieved passages rather
        # than model memory, and so a later scan can diff against what this one saw.
        try:
            store.upsert(
                store.chunk_page(result.text, url=url,
                                 published=str(result.provenance.source_published_at or "")),
                store.scan_namespace(company),
            )
        except Exception as exc:  # noqa: BLE001 — a store outage must not end a scan
            unavailable.append(UnavailableSource(
                label="Evidence store (Pinecone)", reason=f"{type(exc).__name__} — passages not indexed"))

        try:
            outcome = extract.from_page(company, result.text, url)
        except Exception as exc:  # noqa: BLE001 - extraction failure must not end the scan
            unavailable.append(UnavailableSource(label=url, reason=f"extraction failed: {type(exc).__name__}"))
            continue

        for s_ in outcome.systems:
            # `asserts_current_use` is False for two different things: a third-party vendor
            # capability whose activation here is unpublished, and a dated announcement the company
            # made about its own system. Only the first should become undetermined. Collapsing both
            # (run 4) stripped the evidence off legitimate historical findings, cost recall
            # 0.556 -> 0.444, and did not move over-claiming at all. Reverted; the narrow version
            # needs a distinct signal from extraction and a run to verify, which is future work.
            mode = ClaimTimeMode.CURRENT_STATE if s_.asserts_current_use else ClaimTimeMode.HISTORICAL_EVENT
            candidates.append(Finding(
                system=s_.system,
                what_it_does=s_.what_it_does,
                vendor=s_.vendor,
                built_or_bought=s_.built_or_bought if s_.built_or_bought in
                    ("built", "bought", "resold", "unknown") else "unknown",
                where_used=s_.where_used,
                role=s_.role if s_.role in ("provider", "deployer") else "unknown",
                first_evidenced=_first_evidenced(result),
                claim_time_mode=mode,
                attestation=Attestation.DEPLOYED if s_.asserts_current_use else Attestation.CAPABILITY_PRESENT,
                confidence=Confidence.EVIDENCED,
                evidence=[Evidence(quote=s_.quote, provenance=result.provenance)],
            ))

    return {
        "candidates": _dedupe(candidates),
        "passes": state.get("passes", 0) + 1,
        "sources_consulted": consulted,
        "unavailable": unavailable,
    }


def _first_evidenced(result) -> str | None:
    """A date only counts when the page is plausibly *about* the announcement.

    A homepage carries a publication date that has nothing to do with when a feature shipped —
    Personio's root page is dated 2022 and was being attached to an assistant released years later.
    Since `first_evidenced` is what the Act's transition rules turn on, a confidently wrong date
    here is worse than no date at all.
    """
    prov = getattr(result, "provenance", None)
    if not prov or not prov.source_published_at:
        return None
    path = str(prov.canonical_url).split("://", 1)[-1]
    path = path[path.find("/"):] if "/" in path else "/"
    if len(path.strip("/")) < 8:          # site root or a bare section index
        return None
    return prov.source_published_at.isoformat()


def _mentions(company: str, page_text: str) -> bool:
    """Whole-word match on the company name.

    `\b` is not enough: a hyphen counts as a word boundary, so `\bGamma\b` happily matches inside
    "gamma-ray". Excluding word characters AND hyphens on both sides is what actually separates a
    company name from a compound that contains it.
    """
    return re.search(rf"(?<![\w-]){re.escape(company)}(?![\w-])", page_text, re.I) is not None


def _dedupe(findings: list[Finding]) -> list[Finding]:
    """One row per system. The same tool found on three pages is one system, not three."""
    best: dict[tuple[str, str | None], Finding] = {}
    for f in findings:
        key = (f.system.strip().lower(), (f.vendor or "").strip().lower() or None)
        prior = best.get(key)
        if prior is None or len(f.evidence) > len(prior.evidence):
            best[key] = f
        elif prior is not None:
            merged = list(prior.evidence) + [e for e in f.evidence if e not in prior.evidence]
            best[key] = prior.model_copy(update={"evidence": merged[:3]})
    return list(best.values())


def evidence_gate(state: ScanState) -> dict:
    """Apply the deterministic gate to every candidate.

    Two things this must not do. It must not drop a blocked finding — a finding that vanishes is
    indistinguishable from one never found. And it must not re-gate a finding that already arrived
    undetermined with a stated reason: capability-present is an honest conclusion from extraction,
    not a failure to find evidence, and overwriting its reason destroys the most useful thing in it.
    """
    exhausted = state.get("passes", 1) >= MAX_RESEARCH_PASSES
    settled: list[Finding] = []
    retry_wanted = False
    for finding in state.get("candidates", []):
        if finding.confidence is Confidence.UNDETERMINED and finding.undetermined_reason:
            settled.append(finding)          # already settled, and settled honestly
            continue
        verdict = gate.evaluate(finding, search_exhausted=exhausted)
        if verdict.outcome is gate.GateOutcome.RESEARCH_AGAIN:
            retry_wanted = True
        settled.append(gate.apply(finding, verdict))
    return {"settled": settled, "candidates": [], "needs_research": retry_wanted}


def _needs_another_pass(state: ScanState) -> str:
    """Route back only when the gate actually asked for a better source.

    Reading the gate's own verdict rather than inspecting reason strings — a router that pattern-
    matches on prose breaks the moment the prose changes, which it did.
    """
    if state.get("passes", 1) >= MAX_RESEARCH_PASSES:
        return "assemble"
    return "research" if state.get("needs_research") else "assemble"


def assemble(state: ScanState) -> dict:
    """Build the report. Validation happens in the schema, so an invalid report cannot be returned."""
    settled = state.get("settled", [])
    # A question that begins "for each tool identified" is absurd on a report that identified none.
    discussion: list[DiscussionItem] = [
        fixtures.MODIFICATION_QUESTION if settled else fixtures.NOTHING_FOUND_QUESTION
    ]
    for f in settled:
        if f.confidence is Confidence.UNDETERMINED and f.undetermined_reason:
            discussion.append(
                DiscussionItem(
                    question=f"On {f.system}: can you confirm whether this is in use, and since when?",
                    about_system=f.system,
                    why_it_matters=f.undetermined_reason,
                )
            )
    report = Report(
        company=state["company"],
        scanned_at=fixtures.NOW if state.get("use_fixtures", True) else datetime.now(timezone.utc),
        sources_consulted=state.get("sources_consulted", 0),
        findings=state.get("settled", []),
        discussion=discussion,
        unavailable_sources=state.get("unavailable", []),
        blind_spots=fixtures.BLIND_SPOTS,
    )
    return {"report": report}


def build() -> StateGraph:
    g = StateGraph(ScanState)
    g.add_node("resolve", resolve_company)
    g.add_node("research", research)
    g.add_node("gate", evidence_gate)
    g.add_node("assemble", assemble)

    g.add_edge(START, "resolve")
    g.add_edge("resolve", "research")
    g.add_edge("research", "gate")
    g.add_conditional_edges("gate", _needs_another_pass, {"research": "research", "assemble": "assemble"})
    g.add_edge("assemble", END)
    return g.compile()


def scan(company: str, *, domain: str | None = None, use_fixtures: bool = True) -> Report:
    result = build().invoke({"company": company, "domain": domain,
                             "use_fixtures": use_fixtures, "passes": 0})
    return result["report"]
