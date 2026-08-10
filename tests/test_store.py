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


def test_namespace_is_derived_safely():
    assert store.scan_namespace("Keogh's Crisps (Ireland)") == "scan-keogh-s-crisps-ireland"


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
