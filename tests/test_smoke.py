"""Phase 1 exit gate: a deterministic fixture run reaches a schema-valid structured report,
and every emitted finding carries provenance."""

from ai_prescan import render
from ai_prescan.graph import scan
from ai_prescan.schemas import Confidence, Report


def test_smoke_run_produces_a_valid_report():
    r = scan("Fitzgerald Recruitment Ltd")
    assert isinstance(r, Report)
    assert r.company == "Fitzgerald Recruitment Ltd"
    assert r.findings


def test_every_emitted_finding_carries_provenance():
    """The exit gate's actual wording. Anything with confidence above undetermined must be
    traceable to a quoted passage with full provenance."""
    for f in scan("Fitzgerald Recruitment Ltd").findings:
        if f.confidence is Confidence.UNDETERMINED:
            assert f.undetermined_reason
            continue
        assert f.evidence
        for e in f.evidence:
            p = e.provenance
            assert p.canonical_url and p.retrieved_at and p.content_sha256
            assert len(e.quote) >= 20


def test_the_unverifiable_claim_does_not_ship_as_a_finding():
    """The fixture set contains a current-state claim from an unchecked source. It must arrive
    as undetermined — this is the regression test for the mistake that started all this."""
    r = scan("Fitzgerald Recruitment Ltd")
    support = [f for f in r.findings if "support" in f.system.lower()][0]
    assert support.confidence is Confidence.UNDETERMINED
    assert "retrieved_at does not prove" in support.undetermined_reason


def test_run_is_deterministic():
    a, b = scan("Acme Ltd"), scan("Acme Ltd")
    assert a.model_dump_json() == b.model_dump_json()


def test_report_renders_with_the_standing_notice_intact():
    text = render.to_markdown(scan("Acme Ltd"))
    assert "makes no assessment of legal risk" in text
    assert "## Questions to discuss with the client" in text


def test_findings_are_not_duplicated_across_research_passes():
    """Regression: the settled list used an additive reducer, so every pass re-appended every
    finding and three candidates became nine. Caught by reading the report, not by the suite."""
    r = scan("Acme Ltd")
    assert len(r.findings) == 3
    assert len({f.system for f in r.findings}) == 3


def test_capability_present_keeps_its_own_reason():
    """Regression: a finding that arrives legitimately undetermined must not be re-gated. Its
    reason — vendor ships opt-in AI, activation unpublished — is the most useful line in the
    report, and gate.apply was overwriting it with 'no quoted evidence attached'."""
    r = scan("Acme Ltd")
    ats = [f for f in r.findings if "Applicant tracking" in f.system][0]
    assert "opt-in" in ats.undetermined_reason
    assert "no quoted evidence" not in ats.undetermined_reason


def test_discussion_list_has_no_duplicate_questions():
    r = scan("Acme Ltd")
    questions = [d.question for d in r.discussion]
    assert len(questions) == len(set(questions))


def test_capability_present_findings_keep_their_evidence():
    """Run 4 stripped evidence from every finding whose source was not a present-tense claim, to
    stop capability-present items being emitted as deployed. It caught legitimate dated
    announcements too, cost recall 0.556 -> 0.444, and left over-claiming unchanged. This pins the
    reverted behaviour: a finding with evidence keeps it."""
    for f in scan("Acme Ltd").findings:
        if f.confidence is not Confidence.UNDETERMINED:
            assert f.evidence, f"{f.system} lost its evidence"


def test_an_empty_report_asks_the_right_question():
    """Regression from a real report: a scan that found nothing still asked 'for each tool
    identified…', which presupposes findings it did not make. The useful question on an empty
    scan is a different question entirely."""
    from ai_prescan import fixtures, graph
    from ai_prescan.schemas import Report

    empty = graph.assemble({"company": "Nothing Found Ltd", "settled": [], "use_fixtures": True,
                            "sources_consulted": 9})["report"]
    assert isinstance(empty, Report) and not empty.findings
    q = empty.discussion[0].question
    assert "for each tool identified" not in q.lower()
    assert "What AI tools does the business actually use" in q


def test_a_report_with_findings_still_asks_about_modification():
    from ai_prescan import graph
    r = graph.scan("Acme Ltd")
    assert r.findings
    assert "renamed, rebranded" in r.discussion[0].question


def test_empty_inventory_says_so_instead_of_rendering_bare_headers():
    from ai_prescan import graph, render
    empty = graph.assemble({"company": "Nothing Found Ltd", "settled": [], "use_fixtures": True,
                            "sources_consulted": 9})["report"]
    text = render.to_markdown(empty)
    assert "No AI systems could be evidenced" in text
    assert "| System | What it does |" not in text      # no empty table
    assert "## Per-system detail" not in text           # no empty section
