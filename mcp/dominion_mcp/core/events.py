"""JSONL event emission for pipeline observability.

Appends structured events to .dominion/phases/{phase}/events.jsonl
for monitoring and debugging pipeline execution.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

# Per-file locks for concurrent event appends (P-Thread safety).
_event_locks: dict[str, asyncio.Lock] = {}


async def emit_event(
    dom_root: Path,
    phase: str,
    event: str,
    *,
    step: str | None = None,
    role: str | None = None,
    task_id: str | None = None,
    data: dict | None = None,
) -> dict:
    """Append one JSON event line to phases/{phase}/events.jsonl.

    Creates parent dirs if needed.  Uses per-file asyncio.Lock so
    concurrent P-Thread agents writing to the same phase are safe.

    Returns the event dict that was written.
    """
    entry: dict = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "phase": phase,
    }
    if step is not None:
        entry["step"] = step
    if role is not None:
        entry["role"] = role
    if task_id is not None:
        entry["task_id"] = task_id
    if data is not None:
        entry["data"] = data

    path = dom_root / "phases" / phase / "events.jsonl"

    key = str(path.resolve())
    if key not in _event_locks:
        _event_locks[key] = asyncio.Lock()

    async with _event_locks[key]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    return entry


def read_events(
    dom_root: Path,
    phase: str,
    limit: int = 20,
    event_filter: set[str] | None = None,
) -> list[dict]:
    """Read up to *limit* most recent events from phases/{phase}/events.jsonl.

    Returns events in chronological order (oldest first among the
    returned slice).  When *event_filter* is provided only events whose
    ``event`` field is in the set are included.

    Returns an empty list when the file does not exist.
    """
    path = dom_root / "phases" / phase / "events.jsonl"
    if not path.exists():
        return []

    events: list[dict] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        if event_filter is not None and entry.get("event") not in event_filter:
            continue
        events.append(entry)

    # Return the most recent `limit` in chronological order.
    return events[-limit:]
