"""Configuration.

Keys live in the shared Ironhack store and are never copied into this repository, printed, or
written to logs. Presence is verified by length and a short hash fingerprint — enough to tell a
missing key from a wrong one without ever revealing a value.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

KEY_STORE = Path.home() / ".config/ironhack/.env.local"

REQUIRED = ("OPENAI_API_KEY", "PINECONE_API_KEY")
OPTIONAL = ("SERPER_API_KEY", "NEWS_API_KEY")


def load() -> None:
    """Load the shared key store. Absent file is not fatal — fixtures need no keys."""
    if KEY_STORE.exists():
        load_dotenv(KEY_STORE)


@dataclass(frozen=True)
class KeyStatus:
    name: str
    present: bool
    length: int
    fingerprint: str  # first 8 hex of sha256, never the value

    def __str__(self) -> str:
        return (
            f"{self.name}: present len={self.length} sha256:{self.fingerprint}"
            if self.present
            else f"{self.name}: MISSING"
        )


def key_status(name: str) -> KeyStatus:
    """Report presence without disclosure. Reads one named key, never the whole environment."""
    value = os.getenv(name)
    if not value:
        return KeyStatus(name, False, 0, "")
    return KeyStatus(name, True, len(value), hashlib.sha256(value.encode()).hexdigest()[:8])


def preflight(require_live: bool = False) -> list[KeyStatus]:
    """Check the keys the run will actually need.

    `require_live=False` is the fixture path: the graph runs end to end with no network and no keys,
    which is what makes the Phase 1 smoke test deterministic.
    """
    load()
    statuses = [key_status(n) for n in (*REQUIRED, *OPTIONAL)]
    if require_live:
        missing = [s.name for s in statuses if s.name in REQUIRED and not s.present]
        if missing:
            raise RuntimeError(
                f"missing required keys: {', '.join(missing)} — expected in {KEY_STORE}"
            )
    return statuses
