"""Pinecone: the vendor corpus and the per-scan evidence store.

Two namespaces in one index, because they have opposite lifecycles.

`vendor` is long-lived and shared across every scan. It answers the question public search answers
badly — *did this vendor ship AI into this product, and when* — and it is what the drift alert in
GTM sprint 2 diffs against. It gets better with every scan rather than being rebuilt.

`scan-<company>` is churn. **Validated evidence passages only — never whole pages.** A fetched page
carries names, titles and quoted people who are not the subject of the research; the passage that
supports a finding is what the gate validated and what ships in the report, and it is all this
namespace needs. Storing the page instead was collecting personal data the system never reads back,
which is the least justifiable kind. The namespace is purged at the start of each scan of the same
company, so evidence persists only for the life of the most recent scan.

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


def chunk_passage(quote: str, *, url: str, published: str | None = None) -> list[Chunk]:
    """One chunk from one validated evidence passage.

    Deliberately not `chunk_page`. That function fixed-size-chunks a whole document and drops
    anything under 80 characters, which would silently discard a short quote — and a quote is the
    unit the gate validated, so it must survive storage whole rather than be re-cut.
    """
    clean = re.sub(r"\s+", " ", quote).strip()
    if not clean:
        return []
    cid = hashlib.sha256(f"{url}:passage:{clean[:120]}".encode()).hexdigest()[:32]
    return [Chunk(cid, clean, {"url": url, "offset": 0, "published": published or ""})]


def delete_namespace(namespace: str) -> None:
    """Remove every vector in a namespace.

    The store had no deletion path of any kind: no vector delete, no purge, no expiry. That made
    retention "forever, by omission" and made an erasure request unanswerable without destroying
    the whole index.
    """
    _index().delete(delete_all=True, namespace=namespace)


def purge_scan(company: str) -> None:
    """Drop the evidence namespace for one company. Safe to call when nothing is stored."""
    try:
        delete_namespace(scan_namespace(company))
    except Exception:  # noqa: BLE001 — an absent namespace is the expected case, not an error
        pass


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
