"""Tests for core/events module — JSONL event emission and reading."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dominion_mcp.core.events import emit_event, read_events


@pytest.mark.asyncio
async def test_emit_event_creates_jsonl(dom_root: Path):
    """emit_event writes a valid JSON line with all required fields."""
    result = await emit_event(dom_root, "01", "step.started", step="research", role="researcher")

    events_file = dom_root / "phases" / "01" / "events.jsonl"
    assert events_file.exists()

    line = events_file.read_text().strip()
    parsed = json.loads(line)
    assert parsed["event"] == "step.started"
    assert parsed["phase"] == "01"
    assert parsed["step"] == "research"
    assert parsed["role"] == "researcher"
    assert "ts" in parsed
    # Return value matches what was written
    assert result == parsed


@pytest.mark.asyncio
async def test_emit_event_appends(dom_root: Path):
    """Multiple events append to the same file."""
    await emit_event(dom_root, "01", "step.started")
    await emit_event(dom_root, "01", "step.completed")

    events_file = dom_root / "phases" / "01" / "events.jsonl"
    lines = [l for l in events_file.read_text().strip().splitlines() if l]
    assert len(lines) == 2
    assert json.loads(lines[0])["event"] == "step.started"
    assert json.loads(lines[1])["event"] == "step.completed"


@pytest.mark.asyncio
async def test_emit_event_optional_fields(dom_root: Path):
    """Omitted optional fields are not present in the output."""
    result = await emit_event(dom_root, "01", "phase.started")

    assert "step" not in result
    assert "role" not in result
    assert "task_id" not in result
    assert "data" not in result
    # Required fields are present
    assert "ts" in result
    assert result["event"] == "phase.started"
    assert result["phase"] == "01"


@pytest.mark.asyncio
async def test_emit_event_creates_parent_dirs(dom_root: Path):
    """emit_event creates phase dir if it doesn't exist yet."""
    # Phase 99 doesn't exist in the fixture
    result = await emit_event(dom_root, "99", "phase.started")

    events_file = dom_root / "phases" / "99" / "events.jsonl"
    assert events_file.exists()
    assert result["phase"] == "99"


def test_read_events_returns_recent(dom_root: Path):
    """read_events returns the most recent N events in chronological order."""
    events_file = dom_root / "phases" / "01" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)

    # Write 5 events
    for i in range(5):
        entry = {"ts": f"2026-03-18T09:0{i}:00Z", "event": f"evt-{i}", "phase": "01"}
        events_file.open("a").write(json.dumps(entry) + "\n")

    # Read last 3
    result = read_events(dom_root, "01", limit=3)
    assert len(result) == 3
    # Chronological: most recent last
    assert result[0]["event"] == "evt-2"
    assert result[1]["event"] == "evt-3"
    assert result[2]["event"] == "evt-4"


def test_read_events_with_filter(dom_root: Path):
    """event_filter limits returned events to matching types."""
    events_file = dom_root / "phases" / "01" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)

    entries = [
        {"ts": "2026-03-18T09:00:00Z", "event": "step.started", "phase": "01"},
        {"ts": "2026-03-18T09:01:00Z", "event": "step.completed", "phase": "01"},
        {"ts": "2026-03-18T09:02:00Z", "event": "step.started", "phase": "01"},
        {"ts": "2026-03-18T09:03:00Z", "event": "task.assigned", "phase": "01"},
    ]
    for entry in entries:
        events_file.open("a").write(json.dumps(entry) + "\n")

    result = read_events(dom_root, "01", event_filter={"step.started"})
    assert len(result) == 2
    assert all(e["event"] == "step.started" for e in result)


def test_read_events_no_file(dom_root: Path):
    """read_events returns empty list when events.jsonl doesn't exist."""
    result = read_events(dom_root, "42")
    assert result == []
