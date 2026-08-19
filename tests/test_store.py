"""Chunking and dimension safety. No network — the rules are what is under test."""

import pytest

from ai_prescan import store


def test_chunks_overlap_so_a_split_sentence_survives():
    text = " ".join(f"word{i}" for i in range(400))
    chunks = store.chunk_page(text, url="https://example.test/x")
    assert len(chunks) > 1
    a, b = chunks[0].text, chunks[1].text
    assert a[-50:] in " ".join([a, b])          # tail of one appears in the pair
    assert all(c.metadata["url"] == "https://example.test/x" for c in chunks)


def test_chunk_ids_are_stable_and_unique():
    text = " ".join(f"word{i}" for i in range(400))
    first = store.chunk_page(text, url="https://example.test/x")
    again = store.chunk_page(text, url="https://example.test/x")
    assert [c.id for c in first] == [c.id for c in again]
    assert len({c.id for c in first}) == len(first)


def test_short_page_produces_no_fragment_chunks():
    assert store.chunk_page("too short", url="https://example.test/x") == []


def test_namespace_is_readable_and_unique():
    ns = store.scan_namespace("Keogh's Crisps (Ireland)")
    assert ns.startswith("scan-keogh-s-crisps-ireland-")     # still readable
    assert store.scan_namespace("Keogh's Crisps (Ireland)") == ns   # and stable


def test_namespaces_never_collide_between_different_companies():
    """A slug alone collapsed every name without ASCII alphanumerics to a shared `scan-`, and
    truncated long registered names to the same 40 characters. One client's evidence landing in
    another client's store is silent and unrecoverable."""
    names = ["Acme Ltd", "acme-ltd", "ACME  LTD!", "北京智源", "株式会社ソニー", "!!!",
             "Northern Ireland Advanced Composites and Engineering Centre Belfast",
             "Northern Ireland Advanced Composites and Engineering Centre Derry"]
    assert len({store.scan_namespace(n) for n in names}) == len(names)


def test_embedding_dimension_is_asserted(monkeypatch):
    """A dimension mismatch fails silently on read — it returns neighbours from the wrong space.
    It must fail loudly on write instead."""
    class _Bad:
        class embeddings:
            @staticmethod
            def create(**kw):
                class R: data = [type("D", (), {"embedding": [0.0] * 512})()]
                return R()
    with pytest.raises(AssertionError, match="512"):
        store.embed(["x"], client=_Bad())


def test_passage_chunk_survives_whole_and_is_not_re_cut():
    """A quote is the unit the gate validated. `chunk_page` would drop anything under 80 chars and
    re-cut longer ones at fixed boundaries; a stored passage must match what shipped in the report."""
    quote = "Personio added an AI-assisted candidate summary to its recruiting module."
    chunks = store.chunk_passage(quote, url="https://example.test/changelog")
    assert len(chunks) == 1
    assert chunks[0].text == quote
    assert chunks[0].metadata["url"] == "https://example.test/changelog"


def test_short_passage_is_kept_where_a_short_page_would_be_dropped():
    short = "AI CV ranking is enabled."
    assert store.chunk_page(short, url="https://example.test/x") == []      # page rule drops it
    assert len(store.chunk_passage(short, url="https://example.test/x")) == 1  # passage rule keeps it


def test_passage_ids_are_stable_and_distinguish_sources():
    quote = "The platform now ships an AI screening assistant."
    a = store.chunk_passage(quote, url="https://a.test/p")[0].id
    again = store.chunk_passage(quote, url="https://a.test/p")[0].id
    b = store.chunk_passage(quote, url="https://b.test/p")[0].id
    assert a == again          # same passage, same vector — re-storing does not duplicate
    assert a != b              # same words from a different source are different evidence


def test_blank_passage_stores_nothing():
    assert store.chunk_passage("   ", url="https://example.test/x") == []


def test_purge_targets_the_company_namespace_and_survives_an_absent_one(monkeypatch):
    """Purge is called before every live scan, including the first one for a company, when there is
    no namespace to delete. That must not raise."""
    called: list[str] = []
    monkeypatch.setattr(store, "delete_namespace", lambda ns: called.append(ns))
    store.purge_scan("Keogh's Crisps (Ireland)")
    assert called == [store.scan_namespace("Keogh's Crisps (Ireland)")]

    def _boom(ns):
        raise RuntimeError("namespace not found")
    monkeypatch.setattr(store, "delete_namespace", _boom)
    store.purge_scan("Never Scanned Ltd")     # must not raise
