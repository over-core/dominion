"""Tests for tools/monitoring module — get_feed pipeline observability."""

from __future__ import annotations

from pathlib import Path

import pytest

from dominion_mcp.core.events import emit_event
from dominion_mcp.tools.monitoring import _get_feed


@pytest.mark.asyncio
async def test_get_feed_returns_recent_events(dom_root: Path):
    """get_feed returns recently emitted events with total count."""
    await emit_event(dom_root, "01", "step.started", step="research", role="researcher")
    await emit_event(dom_root, "01", "step.completed", step="research", role="researcher")

    result = await _get_feed(dom_root, phase="01")

    assert result["total"] == 2
    assert len(result["events"]) == 2
    assert result["events"][0]["event"] == "step.started"
    assert result["events"][1]["event"] == "step.completed"


@pytest.mark.asyncio
async def test_get_feed_with_filter(dom_root: Path):
    """get_feed filters events when event_filter comma-separated string is provided."""
    await emit_event(dom_root, "01", "step.started", step="research")
    await emit_event(dom_root, "01", "task.assigned", role="developer")
    await emit_event(dom_root, "01", "step.completed", step="research")

    result = await _get_feed(dom_root, phase="01", event_filter="step.started,step.completed")

    assert result["total"] == 2
    assert all(e["event"] in {"step.started", "step.completed"} for e in result["events"])


@pytest.mark.asyncio
async def test_get_feed_empty(dom_root: Path):
    """get_feed returns empty result when no events exist."""
    result = await _get_feed(dom_root, phase="01")

    assert result["total"] == 0
    assert result["events"] == []
