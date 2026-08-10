"""Evidence extraction.

The one genuinely fuzzy step: reading a careers page, a product page and a changelog and inferring
"they run automated CV ranking". Everything downstream is deterministic, so this is where the
stronger model is spent — accuracy is the binding constraint here, not cost.

Two rules the prompt cannot be trusted to keep on its own, so they are enforced in code afterwards:
a quote must be present, and it must actually appear in the page text. A model that paraphrases a
source into something more convenient is the failure mode this whole project is built against.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

MODEL = os.getenv("AI_PRESCAN_EXTRACT_MODEL", "gpt-4o")
MAX_PAGE_CHARS = 12_000


class ExtractedSystem(BaseModel):
    system: str = Field(description="What the AI system is, in plain functional terms")
    what_it_does: str
    vendor: str | None = None
    built_or_bought: str = "unknown"
    where_used: str | None = None
    quote: str = Field(description="Verbatim sentence from the page that supports this")
    asserts_current_use: bool = Field(
        description="True if the page says the company uses this now; False if it reports a "
                    "past announcement or a vendor capability rather than this company's use"
    )
    company_is_subject: bool = Field(
        description="True ONLY if this page is about the target company and attributes this system "
                    "to it. False if the page is about a different organisation that merely shares "
                    "or contains the company's name, or if the system belongs to someone else."
    )


class Extraction(BaseModel):
    systems: list[ExtractedSystem] = Field(default_factory=list)


SYSTEM_PROMPT = """You identify AI systems a specific company appears to use, from one web page.

The single most important judgement is whether this page is about the target company at all. Pages
are retrieved by name search, so many will be about entirely different organisations that happen to
share a word with the company name, or about a vendor's product rather than this company's use.

Rules:
- Only report a system if the page itself supports it. Never infer from the industry or from what
  similar companies do.
- Set company_is_subject to false when the page is about a different organisation, even if it
  discusses AI in detail. A page about another company's product is not evidence about this one.
- `quote` must be copied verbatim from the page. Do not paraphrase, shorten, or tidy it.
- If the page describes a vendor's capability rather than this company using it, still report it,
  but set asserts_current_use to false.
- If the page shows no AI system for this company, return an empty list. An empty list is a correct
  and common answer.
- Do not report the company's own AI products as systems it deploys internally unless the page says
  it uses them internally."""


@dataclass
class ExtractionOutcome:
    systems: list[ExtractedSystem]
    rejected: list[str]        # quotes that failed verification, kept for the trace


def _normalise(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower())


def _quote_is_in_page(quote: str, page_text: str) -> bool:
    """Verify the quote actually appears. Tolerates whitespace and punctuation, nothing more."""
    q, p = _normalise(quote), _normalise(page_text)
    q = re.sub(r"\s+", " ", q).strip()
    p = re.sub(r"\s+", " ", p)
    if len(q) < 20:
        return False
    return q in p


def from_page(company: str, page_text: str, url: str, *, client: OpenAI | None = None) -> ExtractionOutcome:
    """Extract candidate systems from one page, then verify every quote against that page."""
    client = client or OpenAI()
    text = page_text[:MAX_PAGE_CHARS]

    completion = client.chat.completions.parse(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Company: {company}\nPage URL: {url}\n\nPage text:\n{text}"},
        ],
        response_format=Extraction,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        return ExtractionOutcome([], ["model returned no parsable extraction"])

    kept, rejected = [], []
    for s in parsed.systems:
        if not s.company_is_subject:
            # The page is about someone else. This is the name-collision failure, and it is the
            # most common one when pages are retrieved by name search.
            rejected.append(f"not about {company}: {s.system}")
            continue
        if not _quote_is_in_page(s.quote, text):
            # A quote that is not in the page is a fabrication, however plausible the finding.
            rejected.append(f"quote not found in page: {s.quote[:60]}")
            continue
        kept.append(s)
    return ExtractionOutcome(kept, rejected)
