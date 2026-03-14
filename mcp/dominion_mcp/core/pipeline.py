"""Pipeline state machine -- 7 steps, 5 dispatch modes."""

from __future__ import annotations

from pathlib import Path

from .config import current_phase, phase_path as get_phase_path, read_toml_optional
from .state import get_position

PIPELINE_STEPS = ["discuss", "research", "plan", "execute", "audit", "review", "improve"]

DISPATCH_MODES: dict[str, str] = {
    "discuss": "inline",
    "research": "subagent",
    "plan": "subagent",
    "execute": "worktree",
    "audit": "multi_subagent",
    "review": "subagent",
    "improve": "panel",
}

STEP_AGENTS: dict[str, str | list[str]] = {
    "discuss": "orchestrator",  # inline, orchestrator handles
    "research": "researcher",
    "plan": "architect",
    "execute": "developer",
    "audit": ["quality-auditor", "security-auditor", "analyst"],
    "review": "reviewer",
    "improve": "orchestrator",  # panel, orchestrator facilitates
}

STEP_MODELS: dict[str, str] = {
    "research": "opus",
    "plan": "opus",
    "execute": "sonnet",  # default, can be overridden per task
    "audit": "sonnet",
    "review": "opus",
}


def get_next_action(dom_root: Path) -> dict:
    """Determine next pipeline action based on current state.

    Returns dict with:
    - action_type: "spawn_agent" | "multi_subagent" | "user_checkpoint" |
                   "panel" | "complete" | "inline" | "error"
    - step: current or next step name
    - agent_role: agent to spawn (if applicable)
    - agents: list of agents (for multi_subagent)
    - model: model to use
    - context: prompt context for agent
    """
    pos = get_position(dom_root)
    current_step = pos.get("step", "idle")
    status = pos.get("status", "ready")
    phase = pos.get("phase", 0)

    if phase == 0:
        return {
            "action_type": "error",
            "message": "No active phase. Run /dominion:onboard first.",
        }

    if status == "blocked":
        return {
            "action_type": "user_checkpoint",
            "step": current_step,
            "message": "Pipeline is blocked. Resolve blockers before continuing.",
        }

    if current_step == "improve" and status == "complete":
        return {
            "action_type": "complete",
            "step": "improve",
            "summary": f"Phase {phase} pipeline complete.",
        }

    # Find next step
    if current_step == "idle" or status == "complete":
        next_step = _next_step(current_step)
        if next_step is None:
            return {
                "action_type": "complete",
                "step": current_step,
                "summary": f"Phase {phase} pipeline complete.",
            }
    else:
        next_step = current_step

    mode = DISPATCH_MODES.get(next_step, "subagent")
    agents = STEP_AGENTS.get(next_step, "orchestrator")
    model = STEP_MODELS.get(next_step, "sonnet")

    if mode == "inline":
        return {"action_type": "inline", "step": next_step, "model": model}
    elif mode == "panel":
        return {"action_type": "panel", "step": next_step, "model": "opus"}
    elif mode == "multi_subagent":
        return {
            "action_type": "multi_subagent",
            "step": next_step,
            "agents": agents if isinstance(agents, list) else [agents],
            "model": model,
            "context": (
                f"Phase {phase}. "
                f"Call mcp__dominion__agent_start(role: '...', phase_id: {phase})"
            ),
        }
    elif mode == "worktree":
        agent_role = agents if isinstance(agents, str) else agents[0]
        return {
            "action_type": "spawn_agent",
            "step": next_step,
            "agent_role": agent_role,
            "model": model,
            "isolation": "worktree",
            "context": (
                f"Phase {phase}. "
                f"Call mcp__dominion__agent_start(role: '{agent_role}', phase_id: {phase})"
            ),
        }
    else:  # subagent
        agent_role = agents if isinstance(agents, str) else agents[0]
        return {
            "action_type": "spawn_agent",
            "step": next_step,
            "agent_role": agent_role,
            "model": model,
            "context": (
                f"Phase {phase}. "
                f"Call mcp__dominion__agent_start(role: '{agent_role}', phase_id: {phase})"
            ),
        }


def _next_step(current: str) -> str | None:
    """Get the next pipeline step after current. Returns None if at end."""
    if current == "idle":
        return PIPELINE_STEPS[0]
    try:
        idx = PIPELINE_STEPS.index(current)
        if idx + 1 < len(PIPELINE_STEPS):
            return PIPELINE_STEPS[idx + 1]
        return None
    except ValueError:
        return PIPELINE_STEPS[0]


def get_step_dispatch(dom_root: Path, step: str) -> dict:
    """Get dispatch info for a specific step.

    Returns: {mode, agent_role or agents, model, step, context}
    """
    if step not in PIPELINE_STEPS:
        raise ValueError(
            f"Invalid step '{step}'. Must be one of: {', '.join(PIPELINE_STEPS)}"
        )

    pos = get_position(dom_root)
    phase = pos.get("phase", 0)
    mode = DISPATCH_MODES[step]
    agents = STEP_AGENTS[step]
    model = STEP_MODELS.get(step, "sonnet")

    result: dict = {"mode": mode, "step": step, "model": model}

    if isinstance(agents, list):
        result["agents"] = agents
    else:
        result["agent_role"] = agents

    if mode not in ("inline", "panel"):
        agent_name = agents if isinstance(agents, str) else agents[0]
        result["context"] = (
            f"Phase {phase}. "
            f"Call mcp__dominion__agent_start(role: '{agent_name}', phase_id: {phase})"
        )

    return result


def get_pipeline_status(dom_root: Path) -> dict:
    """Get comprehensive pipeline status including health checks.

    Returns: {position, steps (with completion status), blocker, health}
    """
    pos = get_position(dom_root)
    current_step = pos.get("step", "idle")

    # Build step status list
    idx_current = (
        PIPELINE_STEPS.index(current_step) if current_step in PIPELINE_STEPS else -1
    )
    steps = []
    for step in PIPELINE_STEPS:
        idx_step = PIPELINE_STEPS.index(step)
        if idx_step < idx_current:
            status = "complete"
        elif idx_step == idx_current:
            status = pos.get("status", "active")
        else:
            status = "pending"
        steps.append({"step": step, "status": status, "mode": DISPATCH_MODES[step]})

    # Check for blockers
    state = read_toml_optional(dom_root / "state.toml") or {}
    blocker = state.get("blocker")

    # Basic health checks
    health = []
    if not (dom_root / "dominion.toml").exists():
        health.append(
            {"check": "config", "status": "fail", "message": "dominion.toml missing"}
        )
    if not (dom_root / "state.toml").exists():
        health.append(
            {"check": "state", "status": "fail", "message": "state.toml missing"}
        )
    if not health:
        health.append(
            {"check": "config", "status": "pass", "message": "Core config files present"}
        )

    return {
        "position": pos,
        "steps": steps,
        "blocker": blocker,
        "health": health,
    }


def get_phase_history(dom_root: Path, phase_id: int | None = None) -> dict:
    """Get history of what happened in a phase.

    Reads phase artifacts: research.toml, plan.toml, progress.toml,
    test-report.toml, review.toml, metrics.toml.
    """
    if phase_id is None:
        phase_id = current_phase(dom_root)

    p_path = get_phase_path(dom_root, phase_id)

    artifacts = {}
    for name in ["research", "plan", "progress", "test-report", "review", "metrics"]:
        artifact_path = p_path / f"{name}.toml"
        if artifact_path.exists():
            artifacts[name] = "present"
        else:
            artifacts[name] = "missing"

    return {"phase_id": phase_id, "artifacts": artifacts}


def get_help(dom_root: Path, question: str | None = None) -> dict:
    """Contextual help based on current pipeline state.

    Without question: return current position, what happened, what to do next.
    With question: return context for the LLM to answer.
    """
    pos = get_position(dom_root)
    current_step = pos.get("step", "idle")
    phase = pos.get("phase", 0)
    status = pos.get("status", "ready")

    next_step = _next_step(current_step) if status == "complete" else current_step

    result: dict = {
        "current_position": f"Phase {phase}, step: {current_step} ({status})",
    }

    if status == "complete" and next_step:
        result["what_to_do_next"] = f"Run /dominion:{next_step} to continue"
        result["available_commands"] = [f"/dominion:{next_step}", "/dominion:orchestrate"]
    elif status == "blocked":
        result["what_to_do_next"] = "Resolve blockers before continuing"
    elif current_step == "idle":
        result["what_to_do_next"] = "Run /dominion:discuss to start the pipeline"
    else:
        result["what_to_do_next"] = f"Step '{current_step}' is {status}"

    if question:
        result["question"] = question
        result["context_for_answer"] = (
            f"User is at phase {phase}, step {current_step}, status {status}."
        )

    return result
