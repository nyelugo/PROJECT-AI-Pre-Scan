"""Pinecone: the vendor corpus and the per-scan evidence store.

Two namespaces in one index, because they have opposite lifecycles.

`vendor` is long-lived and shared across every scan. It answers the question public search answers
badly — *did this vendor ship AI into this product, and when* — and it is what the drift alert in
GTM sprint 2 diffs against. It gets better with every scan rather than being rebuilt.

`scan-<company>` is churn. Pages fetched during one scan, embedded so the evidence gate checks
claims against retrieved passages instead of model memory.

Embedding model and dimension are asserted on write, because a mismatch fails silently on the read
side — it returns neighbours from the wrong space rather than an error, which is the worst kind of
wrong.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass

from openai import OpenAI
from pinecone import Pinecone

from . import config

INDEX = os.getenv("AI_PRESCAN_INDEX", "ai-prescan")
EMBED_MODEL = "text-embedding-3-small"
DIMENSIONS = 1536
CHUNK_CHARS = 900
CHUNK_OVERLAP = 120

config.load()


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict


def chunk_page(text: str, *, url: str, published: str | None = None) -> list[Chunk]:
    """Fixed-size overlapping chunks. Overlap exists so a sentence split across a boundary is still
    retrievable whole — the quote must survive chunking or it cannot be verified later."""
    clean = re.sub(r"\s+", " ", text).strip()
    out: list[Chunk] = []
    step = CHUNK_CHARS - CHUNK_OVERLAP
    for i in range(0, max(len(clean), 1), step):
        piece = clean[i : i + CHUNK_CHARS]
        if len(piece) < 80:
            break
        cid = hashlib.sha256(f"{url}:{i}:{piece[:60]}".encode()).hexdigest()[:32]
        out.append(Chunk(cid, piece, {"url": url, "offset": i, "published": published or ""}))
    return out


def embed(texts: list[str], *, client: OpenAI | None = None) -> list[list[float]]:
    client = client or OpenAI()
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts, dimensions=DIMENSIONS)
    vectors = [d.embedding for d in resp.data]
    for v in vectors:
        # Asserted, not assumed. A dimension mismatch is silent on read and catastrophic in meaning.
        assert len(v) == DIMENSIONS, f"embedding dimension {len(v)} != {DIMENSIONS}"
    return vectors


def _index():
    return Pinecone(api_key=os.environ["PINECONE_API_KEY"]).Index(INDEX)


def upsert(chunks: list[Chunk], namespace: str, *, client: OpenAI | None = None) -> int:
    if not chunks:
        return 0
    vectors = embed([c.text for c in chunks], client=client)
    _index().upsert(
        vectors=[
            {"id": c.id, "values": v, "metadata": {**c.metadata, "text": c.text[:1500]}}
            for c, v in zip(chunks, vectors)
        ],
        namespace=namespace,
    )
    return len(chunks)


def query(text: str, namespace: str, *, top_k: int = 5, flt: dict | None = None,
          client: OpenAI | None = None) -> list[dict]:
    vector = embed([text], client=client)[0]
    res = _index().query(vector=vector, top_k=top_k, namespace=namespace,
                         include_metadata=True, filter=flt)
    return [
        {"score": m["score"], "text": m["metadata"].get("text", ""),
         "url": m["metadata"].get("url", ""), "published": m["metadata"].get("published", "")}
        for m in res.get("matches", [])
    ]


def scan_namespace(company: str) -> str:
    """Per-company namespace, unique even when the readable part is not.

    A slug alone collapsed any name without ASCII alphanumerics to the bare `scan-`, which every
    such company then shared, and truncation at 40 characters collided long registered names. One
    client's passages landing in another's store is silent and unrecoverable.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")[:32] or "x"
    digest = hashlib.sha256(company.strip().lower().encode()).hexdigest()[:8]
    return f"scan-{slug}-{digest}"


VENDOR_NAMESPACE = "vendor"
