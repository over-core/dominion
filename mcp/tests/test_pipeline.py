"""Tests for dominion_mcp.core.pipeline module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dominion_mcp.core.pipeline import (
    PIPELINE_STEPS,
    get_help,
    get_next_action,
    get_pipeline_status,
    get_step_dispatch,
)


# ---------------------------------------------------------------------------
# PIPELINE_STEPS
# ---------------------------------------------------------------------------


def test_pipeline_steps_count() -> None:
    """PIPELINE_STEPS has exactly 7 entries."""
    assert len(PIPELINE_STEPS) == 7


def test_pipeline_steps_order() -> None:
    """PIPELINE_STEPS has the correct order."""
    assert PIPELINE_STEPS == [
        "discuss", "research", "plan", "execute", "audit", "review", "improve"
    ]


# ---------------------------------------------------------------------------
# get_next_action
# ---------------------------------------------------------------------------


def test_get_next_action_execute_step(dom_root: Path) -> None:
    """get_next_action returns spawn_agent for active execute step."""
    # Fixture has step=execute, status=active
    action = get_next_action(dom_root)
    assert action["action_type"] == "spawn_agent"
    assert action["step"] == "execute"
    assert action["agent_role"] == "developer"


def test_get_next_action_no_phase(tmp_path: Path) -> None:
    """get_next_action returns error when no phase is active."""
    dom = tmp_path / ".dominion"
    dom.mkdir()
    (dom / "state.toml").write_text('[position]\nphase = 0\nstep = "idle"\nstatus = "ready"\n')
    action = get_next_action(dom)
    assert action["action_type"] == "error"


def test_get_next_action_blocked(dom_root: Path) -> None:
    """get_next_action returns user_checkpoint when pipeline is blocked."""
    # Manually set blocked status
    from dominion_mcp.core.config import write_toml, read_toml
    state = read_toml(dom_root / "state.toml")
    state["position"]["status"] = "blocked"
    write_toml(dom_root / "state.toml", state)

    action = get_next_action(dom_root)
    assert action["action_type"] == "user_checkpoint"


# ---------------------------------------------------------------------------
# get_step_dispatch
# ---------------------------------------------------------------------------


def test_get_step_dispatch_research(dom_root: Path) -> None:
    """get_step_dispatch for research returns subagent mode with researcher."""
    dispatch = get_step_dispatch(dom_root, "research")
    assert dispatch["mode"] == "subagent"
    assert dispatch["agent_role"] == "researcher"


def test_get_step_dispatch_audit(dom_root: Path) -> None:
    """get_step_dispatch for audit returns multi_subagent with agents list."""
    dispatch = get_step_dispatch(dom_root, "audit")
    assert dispatch["mode"] == "multi_subagent"
    assert isinstance(dispatch["agents"], list)
    assert "quality-auditor" in dispatch["agents"]
    assert "security-auditor" in dispatch["agents"]


def test_get_step_dispatch_discuss(dom_root: Path) -> None:
    """get_step_dispatch for discuss returns inline mode."""
    dispatch = get_step_dispatch(dom_root, "discuss")
    assert dispatch["mode"] == "inline"


def test_get_step_dispatch_improve(dom_root: Path) -> None:
    """get_step_dispatch for improve returns panel mode."""
    dispatch = get_step_dispatch(dom_root, "improve")
    assert dispatch["mode"] == "panel"


def test_get_step_dispatch_invalid_step(dom_root: Path) -> None:
    """get_step_dispatch raises ValueError for an invalid step."""
    with pytest.raises(ValueError, match="Invalid step"):
        get_step_dispatch(dom_root, "invalid_step")


# ---------------------------------------------------------------------------
# get_pipeline_status
# ---------------------------------------------------------------------------


def test_get_pipeline_status_returns_structure(dom_root: Path) -> None:
    """get_pipeline_status returns position, steps, blocker, health."""
    status = get_pipeline_status(dom_root)
    assert "position" in status
    assert "steps" in status
    assert "blocker" in status
    assert "health" in status


def test_get_pipeline_status_step_count(dom_root: Path) -> None:
    """get_pipeline_status returns 7 steps."""
    status = get_pipeline_status(dom_root)
    assert len(status["steps"]) == 7


def test_get_pipeline_status_marks_completed_steps(dom_root: Path) -> None:
    """Steps before current step are marked complete."""
    status = get_pipeline_status(dom_root)
    step_map = {s["step"]: s["status"] for s in status["steps"]}
    # Fixture is at execute step, so discuss/research/plan should be complete
    assert step_map["discuss"] == "complete"
    assert step_map["research"] == "complete"
    assert step_map["plan"] == "complete"
    assert step_map["execute"] == "active"
    assert step_map["audit"] == "pending"


def test_get_pipeline_status_health_pass(dom_root: Path) -> None:
    """Health checks pass for well-formed fixture."""
    status = get_pipeline_status(dom_root)
    health_statuses = [h["status"] for h in status["health"]]
    assert "fail" not in health_statuses


# ---------------------------------------------------------------------------
# get_help
# ---------------------------------------------------------------------------


def test_get_help_returns_position(dom_root: Path) -> None:
    """get_help returns current position info."""
    result = get_help(dom_root)
    assert "current_position" in result
    assert "Phase 1" in result["current_position"]
    assert "execute" in result["current_position"]


def test_get_help_with_question(dom_root: Path) -> None:
    """get_help includes question context when question is provided."""
    result = get_help(dom_root, question="What should I do next?")
    assert "question" in result
    assert "context_for_answer" in result


# ---------------------------------------------------------------------------
# execute_wave dispatch
# ---------------------------------------------------------------------------


def test_execute_wave_dispatch(dom_root_with_plan: Path) -> None:
    """Execute step with plan.toml returns execute_wave with task list."""
    from dominion_mcp.core.config import read_toml, write_toml

    # Set position to execute step, wave 1
    state_path = dom_root_with_plan / "state.toml"
    state = read_toml(state_path)
    state["position"]["step"] = "execute"
    state["position"]["status"] = "active"
    state["position"]["wave"] = 1
    write_toml(state_path, state)

    result = get_next_action(dom_root_with_plan)
    assert result["action_type"] == "execute_wave"
    assert result["wave"] == 1
    assert len(result["tasks"]) >= 1
    assert result["tasks"][0]["isolation"] == "worktree"
    assert "task_id" in result["tasks"][0]
    assert "agent_role" in result["tasks"][0]
    assert "context" in result["tasks"][0]


def test_execute_wave_includes_task_ids(dom_root_with_plan: Path) -> None:
    """Wave tasks have correct task IDs from plan.toml."""
    from dominion_mcp.core.config import read_toml, write_toml

    state_path = dom_root_with_plan / "state.toml"
    state = read_toml(state_path)
    state["position"]["step"] = "execute"
    state["position"]["status"] = "active"
    state["position"]["wave"] = 1
    write_toml(state_path, state)

    result = get_next_action(dom_root_with_plan)
    task_ids = {t["task_id"] for t in result["tasks"]}
    # Wave 1 in conftest: 01-01 is complete, 01-02 is active (pending)
    assert "01-02" in task_ids
    assert "01-01" not in task_ids  # Already complete, filtered out


def test_execute_wave_no_plan_falls_back(dom_root: Path) -> None:
    """Execute step without plan.toml falls back to single spawn_agent."""
    from dominion_mcp.core.config import read_toml, write_toml

    state_path = dom_root / "state.toml"
    state = read_toml(state_path)
    state["position"]["step"] = "execute"
    state["position"]["status"] = "active"
    write_toml(state_path, state)

    result = get_next_action(dom_root)
    assert result["action_type"] == "spawn_agent"
    assert result.get("isolation") == "worktree"
