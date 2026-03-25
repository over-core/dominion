"""Tests for tools/monitoring module — get_feed pipeline observability."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from dominion_mcp.core.config import read_toml_optional, write_toml
from dominion_mcp.core.events import emit_event, read_events

from dominion_mcp.core.state import get_active_agents, register_active_agent
from dominion_mcp.tools.monitoring import (
    _check_agent_health,
    _check_pipeline_ready,
    _get_feed,
    _register_agent,
)


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


# ---------------------------------------------------------------------------
# register_agent
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_agent(dom_root: Path):
    """register_agent records agent in state.toml active_agents."""
    result = await _register_agent(dom_root, phase="01", step="research", role="researcher")

    assert result["agent_key"] == "researcher-research"
    assert result["role"] == "researcher"
    assert result["step"] == "research"

    agents = get_active_agents(dom_root)
    assert "researcher-research" in agents


@pytest.mark.asyncio
async def test_register_agent_with_task(dom_root: Path):
    """register_agent uses task_id in agent_key when provided."""
    result = await _register_agent(
        dom_root, phase="01", step="execute", role="developer", task_id="task-01"
    )

    assert result["agent_key"] == "developer-task-01"

    agents = get_active_agents(dom_root)
    assert "developer-task-01" in agents


# ---------------------------------------------------------------------------
# check_agent_health
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_agent_health_completed(dom_root_with_plan: Path):
    """Agent working on a complete step is detected as completed."""
    # Register agent for research step (which is complete in dom_root_with_plan)
    await register_active_agent(
        dom_root_with_plan,
        agent_key="researcher-research",
        phase="01",
        step="research",
        role="researcher",
    )

    result = await _check_agent_health(dom_root_with_plan, phase="01")

    assert len(result["completed"]) == 1
    assert result["completed"][0] == "researcher-research"
    # Should have been removed from active agents
    agents = get_active_agents(dom_root_with_plan)
    assert "researcher-research" not in agents


@pytest.mark.asyncio
async def test_check_agent_health_stalled(dom_root: Path):
    """Agent exceeding timeout is detected as stalled."""
    # Create research dir with active status so agent is not completed
    research_dir = dom_root / "phases" / "01" / "research"
    research_dir.mkdir(parents=True, exist_ok=True)
    (research_dir / "status").write_text("active")

    # Register agent, then manually backdate the spawned timestamp
    await register_active_agent(
        dom_root,
        agent_key="researcher-research",
        phase="01",
        step="research",
        role="researcher",
    )
    # Backdate spawned time to 30 minutes ago
    state = read_toml_optional(dom_root / "state.toml") or {}
    old_time = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    state["active_agents"]["researcher-research"]["spawned"] = old_time
    write_toml(dom_root / "state.toml", state)

    result = await _check_agent_health(dom_root, phase="01", timeout_minutes=15)

    assert len(result["stalled"]) == 1
    assert result["stalled"][0] == "researcher-research"
    assert len(result["healthy"]) == 0


# ---------------------------------------------------------------------------
# check_pipeline_ready
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_pipeline_ready_disabled(dom_root: Path):
    """Pipeline not ready when auto_continue is not enabled."""
    result = await _check_pipeline_ready(dom_root)

    assert result["ready"] is False
    assert "auto_continue" in result["reason"]


@pytest.mark.asyncio
async def test_check_pipeline_ready_enabled(dom_root: Path):
    """Pipeline ready when auto_continue is enabled and conditions met."""
    # Enable auto_continue in config
    config = read_toml_optional(dom_root / "config.toml") or {}
    config["auto"]["auto_continue"] = True
    write_toml(dom_root / "config.toml", config)

    result = await _check_pipeline_ready(dom_root)

    assert result["ready"] is True
    assert result["phase"] == "01"
    assert result["step"] == "research"
    assert result["wave"] == 0
    assert result["complexity"] == "moderate"


@pytest.mark.asyncio
async def test_submit_work_clears_active_agent(dom_root_with_plan: Path):
    """submit_work removes agent from active_agents after success."""
    import json
    # Register agent
    await _register_agent(dom_root_with_plan, phase="01", step="research", role="researcher")

    # Verify registered
    agents = get_active_agents(dom_root_with_plan)
    assert "researcher-research" in agents

    # Submit work via tool (monkey-patch find_dominion_root)
    import dominion_mcp.tools.submit as submit_mod
    original = submit_mod.find_dominion_root
    submit_mod.find_dominion_root = lambda: dom_root_with_plan
    try:
        content = json.dumps({"items": [{"severity": "medium", "category": "style", "description": "test", "file": "test.py"}]})
        result = await submit_mod.submit_work(phase="01", step="research", role="researcher", content=content, summary="Test findings")
    finally:
        submit_mod.find_dominion_root = original

    assert result["status"] == "accepted"

    # Verify cleared
    agents = get_active_agents(dom_root_with_plan)
    assert "researcher-research" not in agents


# ---------------------------------------------------------------------------
# check_agent_health — timeout disabled
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_agent_health_timeout_disabled(dom_root: Path):
    """Stall detection disabled when timeout_minutes=0."""
    research_dir = dom_root / "phases" / "01" / "research"
    research_dir.mkdir(parents=True, exist_ok=True)
    (research_dir / "status").write_text("active")

    await register_active_agent(
        dom_root, agent_key="researcher-research",
        phase="01", step="research", role="researcher",
    )
    state = read_toml_optional(dom_root / "state.toml") or {}
    old_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    state["active_agents"]["researcher-research"]["spawned"] = old_time
    write_toml(dom_root / "state.toml", state)

    result = await _check_agent_health(dom_root, phase="01", timeout_minutes=0)
    assert len(result["stalled"]) == 0
    assert len(result["healthy"]) == 1


# ---------------------------------------------------------------------------
# check_pipeline_ready — event emission
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_pipeline_ready_emits_event(dom_root: Path):
    """check_pipeline_ready emits pipeline_ready event when ready."""
    config = read_toml_optional(dom_root / "config.toml") or {}
    config["auto"]["auto_continue"] = True
    write_toml(dom_root / "config.toml", config)

    result = await _check_pipeline_ready(dom_root)
    assert result["ready"] is True

    events = read_events(dom_root, phase="01")
    ready_events = [e for e in events if e["event"] == "pipeline_ready"]
    assert len(ready_events) == 1
    assert ready_events[0]["data"]["next_step"] == "research"
