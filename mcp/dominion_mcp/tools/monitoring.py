"""Monitoring tools — get_feed, register_agent, check_agent_health, check_pipeline_ready.

Provides pipeline observability and agent health tracking.
"""

from __future__ import annotations

from pathlib import Path

from ..server import mcp
from ..core.config import find_dominion_root
from ..core.events import read_events
from ..core.state import get_position


async def _get_feed(
    dom_root: Path,
    phase: str | None = None,
    limit: int = 20,
    event_filter: str | None = None,
) -> dict:
    """Internal: return recent events. Testable without MCP context."""
    if phase is None:
        pos = get_position(dom_root)
        phase = pos.get("phase", "01")

    filter_set = None
    if event_filter:
        filter_set = {t.strip() for t in event_filter.split(",")}

    events = read_events(dom_root, phase=phase, limit=limit, event_filter=filter_set)
    return {"events": events, "total": len(events)}


@mcp.tool()
async def get_feed(
    phase: str | None = None,
    limit: int = 20,
    event_filter: str | None = None,
) -> dict:
    """Return recent events from the pipeline feed.

    Args:
        phase: Phase ID. Defaults to current phase.
        limit: Maximum events to return (default 20).
        event_filter: Comma-separated event types to filter by.
    """
    dom_root = find_dominion_root()
    return await _get_feed(dom_root, phase=phase, limit=limit, event_filter=event_filter)
