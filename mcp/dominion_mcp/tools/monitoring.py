"""Monitoring tools — get_feed, register_agent, check_agent_health, check_pipeline_ready.

Provides pipeline observability and agent health tracking.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..core.config import find_dominion_root, read_toml_optional
from ..core.events import emit_event, read_events
from ..core.filesystem import read_status
from ..core.state import (
    get_active_agents,
    get_circuit_breaker,
    get_position,
    register_active_agent,
    remove_active_agent,
)
from ..server import mcp


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


# ---------------------------------------------------------------------------
# register_agent
# ---------------------------------------------------------------------------


async def _register_agent(
    dom_root: Path,
    phase: str,
    step: str,
    role: str,
    task_id: str | None = None,
) -> dict:
    """Internal: register an agent and emit agent_spawned event."""
    agent_key = f"{role}-{task_id}" if task_id else f"{role}-{step}"
    result = await register_active_agent(
        dom_root,
        agent_key=agent_key,
        phase=phase,
        step=step,
        role=role,
        task_id=task_id,
    )
    await emit_event(
        dom_root,
        phase=phase,
        event="agent_spawned",
        step=step,
        role=role,
        task_id=task_id,
    )
    return result


@mcp.tool()
async def register_agent(
    phase: str,
    step: str,
    role: str,
    task_id: str | None = None,
) -> dict:
    """Register an agent spawn for health tracking.

    Args:
        phase: Phase ID the agent is working in.
        step: Pipeline step (research, plan, execute, review).
        role: Agent role (researcher, developer, etc.).
        task_id: Optional task ID for execute-step agents.
    """
    dom_root = find_dominion_root()
    return await _register_agent(dom_root, phase=phase, step=step, role=role, task_id=task_id)


# ---------------------------------------------------------------------------
# check_agent_health
# ---------------------------------------------------------------------------


async def _check_agent_health(
    dom_root: Path,
    phase: str,
    timeout_minutes: int | None = None,
) -> dict:
    """Internal: check health of all active agents in a phase.

    For each active agent:
    - If step/task status is "complete" → completed, remove from active
    - If elapsed > timeout → stalled, emit agent_stalled event
    - Otherwise → healthy
    """
    if timeout_minutes is None:
        config = read_toml_optional(dom_root / "config.toml") or {}
        timeout_minutes = config.get("auto", {}).get("agent_timeout_minutes", 15)

    agents = get_active_agents(dom_root)
    now = datetime.now(timezone.utc)

    healthy: list[str] = []
    stalled: list[str] = []
    completed: list[str] = []

    for agent_key, info in agents.items():
        if info.get("phase") != phase:
            continue

        # Determine status path
        task_id = info.get("task_id", "")
        step = info.get("step", "")
        if task_id:
            status_path = dom_root / "phases" / phase / "tasks" / task_id / "status"
        else:
            status_path = dom_root / "phases" / phase / step / "status"

        status = read_status(status_path)

        if status == "complete":
            completed.append(agent_key)
            await remove_active_agent(dom_root, agent_key)
            continue

        # Check elapsed time
        spawned_str = info.get("spawned", "")
        if spawned_str:
            spawned = datetime.fromisoformat(spawned_str)
            elapsed_seconds = (now - spawned).total_seconds()
            if timeout_minutes > 0 and elapsed_seconds > timeout_minutes * 60:
                stalled.append(agent_key)
                await emit_event(
                    dom_root,
                    phase=phase,
                    event="agent_stalled",
                    step=step,
                    role=info.get("role", ""),
                    task_id=task_id or None,
                    data={"agent_key": agent_key, "duration_seconds": int(elapsed_seconds)},
                )
                continue

        healthy.append(agent_key)

    return {"healthy": healthy, "stalled": stalled, "completed": completed}


@mcp.tool()
async def check_agent_health(
    phase: str | None = None,
    timeout_minutes: int | None = None,
) -> dict:
    """Check health of all active agents — find stalled or completed agents.

    Args:
        phase: Phase ID. Defaults to current phase.
        timeout_minutes: Override timeout (default from config or 15 min).
    """
    dom_root = find_dominion_root()
    if phase is None:
        pos = get_position(dom_root)
        phase = pos.get("phase", "01")
    return await _check_agent_health(dom_root, phase=phase, timeout_minutes=timeout_minutes)


# ---------------------------------------------------------------------------
# check_pipeline_ready
# ---------------------------------------------------------------------------


async def _check_pipeline_ready(dom_root: Path) -> dict:
    """Internal: check if pipeline is ready for autonomous continuation.

    Checks: auto_continue enabled, circuit_breaker closed, status active,
    step not idle.
    """
    config = read_toml_optional(dom_root / "config.toml") or {}
    auto_continue = config.get("auto", {}).get("auto_continue", False)

    if not auto_continue:
        return {"ready": False, "reason": "auto_continue is not enabled in config"}

    cb = get_circuit_breaker(dom_root)
    if cb["state"] != "closed":
        return {"ready": False, "reason": f"circuit_breaker is {cb['state']}"}

    pos = get_position(dom_root)
    if pos["status"] != "active":
        return {"ready": False, "reason": f"pipeline status is {pos['status']}"}

    if pos["step"] == "idle":
        return {"ready": False, "reason": "pipeline step is idle"}

    result = {
        "ready": True,
        "reason": "pipeline ready for autonomous continuation",
        "phase": pos["phase"],
        "step": pos["step"],
        "wave": pos["wave"],
    }
    await emit_event(dom_root, phase=pos["phase"], event="pipeline_ready",
                     step=pos["step"], data={"next_step": pos["step"]})
    return result


@mcp.tool()
async def check_pipeline_ready() -> dict:
    """Check if the pipeline is ready for autonomous continuation.

    Verifies auto_continue config, circuit breaker, and pipeline status.
    """
    dom_root = find_dominion_root()
    return await _check_pipeline_ready(dom_root)
