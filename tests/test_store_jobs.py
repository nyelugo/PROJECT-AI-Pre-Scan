"""Persistence regressions for scan records shared by the worker and web routes."""

import json
from pathlib import Path

from ai_prescan import store_jobs
from ai_prescan.store_jobs import Scan


def test_save_keeps_the_previous_record_readable_until_atomic_replace(tmp_path, monkeypatch):
    """A report request during save must see complete JSON, never a truncated live file."""
    monkeypatch.setattr(store_jobs, "ROOT", tmp_path / "scans")
    store_jobs.save(Scan(id="race", company="Acme", status="running"))

    observed = {}
    real_replace = Path.replace

    def inspect_before_replace(source: Path, destination: Path):
        observed["live"] = store_jobs.get("race").status
        observed["pending"] = json.loads(source.read_text())["status"]
        return real_replace(source, destination)

    monkeypatch.setattr(Path, "replace", inspect_before_replace)
    store_jobs.save(Scan(id="race", company="Acme", status="done"))

    assert observed == {"live": "running", "pending": "done"}
    assert store_jobs.get("race").status == "done"
    assert list(store_jobs.ROOT.glob("*.tmp")) == []
