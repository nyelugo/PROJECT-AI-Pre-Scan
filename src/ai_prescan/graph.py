"""The LangGraph skeleton.

Nodes and edges mirror docs/architecture.md. Phase 1 wires the shape and the loop-back; Phase 2
replaces the fixture research node with live tools. The structure that matters is already here:

    extract -> gate -> (research again | emit | undetermined) -> assemble

The gate is a routing decision, not a reporting step. That is why LangGraph is primary — a check
that can only observe cannot send the agent back for a better source.
"""

from __future__ import annotations

import operator
from datetime import datetime, timezone
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from . import fixtures, gate
from .schemas import (
    Confidence,
    DiscussionItem,
    Finding,
    Report,
    UnavailableSource,
)

MAX_RESEARCH_PASSES = 3


class ScanState(TypedDict, total=False):
    company: str
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
    """Gather candidates. Phase 1: fixtures. Phase 2: search + news + registry + fetch."""
    if not state.get("use_fixtures", True):
        raise NotImplementedError("live research lands in Phase 2")
    candidates = fixtures.candidate_findings()
    return {
        "candidates": candidates,
        "passes": state.get("passes", 0) + 1,
        "sources_consulted": sum(len(f.evidence) for f in candidates),
    }


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
    discussion: list[DiscussionItem] = [fixtures.STANDING_DISCUSSION]
    for f in state.get("settled", []):
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


def scan(company: str, *, use_fixtures: bool = True) -> Report:
    result = build().invoke({"company": company, "use_fixtures": use_fixtures, "passes": 0})
    return result["report"]
