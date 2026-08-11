"""Scan history that survives a restart.

Maria has forty clients. A tool that forgets every scan when the process stops is a tool she has to
re-run to answer a question she already paid for. History is not a nicety here — it is the difference
between a demo and something with a client list behind it.

Stored as one JSON file per scan under `~/.ai-prescan/scans/`, outside the repository, because these
contain research about named companies and do not belong in version control.
"""

from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / ".ai-prescan" / "scans"
_lock = threading.Lock()


@dataclass
class Scan:
    id: str
    company: str
    domain: str | None = None
    status: str = "queued"                 # queued | running | done | failed
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str | None = None
    findings: int = 0
    evidenced: int = 0
    undetermined: int = 0
    questions: int = 0
    sources: int = 0
    unavailable: int = 0
    markdown: str = ""
    delivered: str | None = None
    error: str | None = None

    @property
    def elapsed(self) -> int:
        end = datetime.fromisoformat(self.finished_at) if self.finished_at else datetime.now(timezone.utc)
        return max(int((end - datetime.fromisoformat(self.started_at)).total_seconds()), 0)

    def summary_line(self) -> str:
        if self.status == "failed":
            return self.error or "failed"
        if self.status != "done":
            return "in progress"
        bits = [f"{self.findings} system{'s' if self.findings != 1 else ''}"]
        if self.undetermined:
            bits.append(f"{self.undetermined} undetermined")
        bits.append(f"{self.questions} question{'s' if self.questions != 1 else ''} to ask")
        return " · ".join(bits)


def _path(scan_id: str) -> Path:
    return ROOT / f"{scan_id}.json"


def save(scan: Scan) -> None:
    with _lock:
        ROOT.mkdir(parents=True, exist_ok=True)
        _path(scan.id).write_text(json.dumps(asdict(scan), indent=2))


def get(scan_id: str) -> Scan | None:
    p = _path(scan_id)
    if not p.exists():
        return None
    return Scan(**json.loads(p.read_text()))


def recent(limit: int = 50) -> list[Scan]:
    if not ROOT.exists():
        return []
    scans = []
    for p in ROOT.glob("*.json"):
        try:
            scans.append(Scan(**json.loads(p.read_text())))
        except Exception:  # noqa: BLE001 — one unreadable file must not hide the rest
            continue
    return sorted(scans, key=lambda s: s.started_at, reverse=True)[:limit]
