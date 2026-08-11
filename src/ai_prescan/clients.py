"""The client book.

Maria advises forty companies. Every version of this tool before now started by asking her to type
a client's name, which is fine once and absurd forty times — and it threw the answer away, so
nothing accumulated. A client is a standing record here: added once, scanned repeatedly, with the
history attached.

That also unlocks the question the tool exists to answer at portfolio scale — *which of my clients
should I worry about first* — which cannot be asked of a text box.

Stored under `~/.ai-prescan/clients.json`, outside the repository, because a consultant's client
list is not something to commit to a public repo.
"""

from __future__ import annotations

import json
import re
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PATH = Path.home() / ".ai-prescan" / "clients.json"
_lock = threading.Lock()

STALE_AFTER_DAYS = 30      # a scan is a snapshot; after a month it is a historical document


@dataclass
class Client:
    id: str
    name: str
    domain: str | None = None
    # confirmed = Maria typed or approved it · suggested = we resolved it, unreviewed
    # unknown    = we could not resolve one, and every scan of this client is weaker for it
    domain_status: str = "unknown"
    notes: str = ""
    added_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Denormalised from the latest scan so the book can be sorted without loading every report.
    last_scan_id: str | None = None
    last_scanned_at: str | None = None
    last_findings: int = 0
    last_undetermined: int = 0
    last_questions: int = 0
    scan_count: int = 0

    @property
    def days_since_scan(self) -> int | None:
        if not self.last_scanned_at:
            return None
        delta = datetime.now(timezone.utc) - datetime.fromisoformat(self.last_scanned_at)
        return delta.days

    @property
    def is_stale(self) -> bool:
        d = self.days_since_scan
        return d is not None and d >= STALE_AFTER_DAYS

    @property
    def never_scanned(self) -> bool:
        return self.last_scanned_at is None

    @property
    def identity_warning(self) -> str | None:
        """Never let a missing or unreviewed domain be silent.

        The domain is the strongest control in the pipeline — a page on the client's own site is
        about that client by construction. Without one, findings rest on name matching, and a
        report about the wrong company is indistinguishable from a right one.
        """
        if self.domain_status == "confirmed":
            return None
        if self.domain_status == "suggested":
            return f"Website not confirmed — we think it is {self.domain}. Check it."
        return "No website — findings rest on the name alone and may be about another company."

    def status(self) -> str:
        """One phrase for the book. Never scanned is the most actionable state, so it says so."""
        if self.never_scanned:
            return "Never scanned"
        d = self.days_since_scan
        when = "today" if d == 0 else "yesterday" if d == 1 else f"{d} days ago"
        return f"Scanned {when}" + (" — due a re-scan" if self.is_stale else "")

    def triage_rank(self) -> tuple:
        """Sort order for 'who do I look at first'.

        Never scanned outranks everything: an unknown client is a bigger risk to an adviser than a
        known one with findings. Then stale, then most undetermined, then most found.
        """
        return (0 if self.never_scanned else 1,
                0 if self.is_stale else 1,
                -self.last_undetermined,
                -self.last_findings,
                self.name.lower())


def _read() -> dict[str, dict]:
    if not PATH.exists():
        return {}
    try:
        return json.loads(PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _write(data: dict[str, dict]) -> None:
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(data, indent=2))


def all_clients() -> list[Client]:
    return sorted((Client(**c) for c in _read().values()), key=lambda c: c.triage_rank())


def get(client_id: str) -> Client | None:
    raw = _read().get(client_id)
    return Client(**raw) if raw else None


def find_by_name(name: str) -> Client | None:
    key = name.strip().lower()
    return next((c for c in all_clients() if c.name.lower() == key), None)


def clean_domain(value: str | None) -> str | None:
    if not value:
        return None
    d = value.strip().lower()
    d = re.sub(r"^https?://", "", d).removeprefix("www.").rstrip("/")
    return d.split("/")[0] or None


def add(name: str, domain: str | None = None, notes: str = "") -> Client | None:
    """Add a client. Returns None if the name is blank or already in the book.

    A domain given here is treated as confirmed — Maria knows her own clients. Without one the
    client is queued for resolution rather than left quietly ambiguous.
    """
    name = name.strip()
    if not name or find_by_name(name):
        return None
    dom = clean_domain(domain)
    client = Client(id=uuid.uuid4().hex[:10], name=name, domain=dom,
                    domain_status="confirmed" if dom else "unknown", notes=notes.strip())
    with _lock:
        data = _read()
        data[client.id] = asdict(client)
        _write(data)
    return client


def update(client_id: str, **fields) -> Client | None:
    with _lock:
        data = _read()
        if client_id not in data:
            return None
        if "domain" in fields:
            fields["domain"] = clean_domain(fields["domain"])
        data[client_id].update({k: v for k, v in fields.items() if v is not None})
        _write(data)
        return Client(**data[client_id])


def remove(client_id: str) -> bool:
    with _lock:
        data = _read()
        if client_id not in data:
            return False
        del data[client_id]
        _write(data)
        return True


def record_scan(client_id: str, scan) -> None:
    """Fold a finished scan into the client's standing record."""
    with _lock:
        data = _read()
        if client_id not in data:
            return
        c = data[client_id]
        c["last_scan_id"] = scan.id
        c["last_scanned_at"] = scan.finished_at or datetime.now(timezone.utc).isoformat()
        c["last_findings"] = scan.findings
        c["last_undetermined"] = scan.undetermined
        c["last_questions"] = scan.questions
        c["scan_count"] = c.get("scan_count", 0) + 1
        _write(data)


def import_lines(text: str) -> tuple[int, int]:
    """Bulk add from pasted lines: `Name` or `Name, domain.com`.

    Returns (added, skipped). Skipped means blank or already present — onboarding forty clients
    should not fail because three were already there.
    """
    added = skipped = 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        name, _, domain = line.partition(",")
        if add(name, domain):
            added += 1
        else:
            skipped += 1
    return added, skipped


def needs_domain() -> list[Client]:
    """Clients whose identity is not settled. Resolved in the background, reviewed by Maria."""
    return [c for c in all_clients() if c.domain_status == "unknown"]


def suggest_domain(client_id: str, domain: str | None) -> None:
    """Record a resolved domain as a suggestion — never as fact. She confirms it."""
    if domain:
        update(client_id, domain=domain, domain_status="suggested")
    else:
        update(client_id, domain_status="unresolved")


def confirm_domain(client_id: str, domain: str | None = None) -> Client | None:
    return update(client_id, **({"domain": domain} if domain else {}), domain_status="confirmed")
