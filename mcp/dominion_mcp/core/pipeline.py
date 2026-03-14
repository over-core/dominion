"""Pipeline state machine -- 7 steps, 5 dispatch modes, complexity-adaptive."""

from __future__ import annotations

from pathlib import Path

from .complexity import get_dispatch_override, get_effective_steps, refine_complexity
from .config import current_phase, phase_path as get_phase_path, read_toml_optional
from .correction import assess_verdict, get_correction_action
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


def get_active_steps(dom_root: Path) -> list[str]:
    """Return the effective step list based on current complexity level."""
    pos = get_position(dom_root)
    complexity = pos.get("complexity_level")
    return get_effective_steps(complexity)


def get_next_action(dom_root: Path) -> dict:
    """Determine next pipeline action based on current state.

    Adapts pipeline depth to complexity level, applies dispatch overrides
    for major complexity, and integrates course correction verdicts after
    review/audit steps.

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
    complexity = pos.get("complexity_level")

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

    active_steps = get_effective_steps(complexity)
    last_step = active_steps[-1] if active_steps else "improve"

    if current_step == last_step and status == "complete":
        return {
            "action_type": "complete",
            "step": last_step,
            "summary": f"Phase {phase} pipeline complete.",
        }

    # Find next step.
    if current_step == "idle" or status == "complete":
        # Post-research refinement: upgrade complexity if warranted.
        if current_step == "research" and status == "complete":
            refine_complexity(dom_root)

        # Course correction after review or audit.
        if current_step in ("review", "audit") and status == "complete":
            verdict = assess_verdict(dom_root)
            if verdict["verdict"] != "go":
                correction = get_correction_action(dom_root, verdict)
                if correction["action"] in ("halt", "auto_fix"):
                    return {
                        "action_type": "user_checkpoint",
                        "step": current_step,
                        "message": correction["reason"],
                        "verdict": verdict,
                        "correction": correction,
                    }

        next_step = _next_step(current_step, active_steps)
        if next_step is None:
            return {
                "action_type": "complete",
                "step": current_step,
                "summary": f"Phase {phase} pipeline complete.",
            }
    else:
        next_step = current_step

    # Check for complexity-driven dispatch overrides.
    mode = get_dispatch_override(complexity, next_step) or DISPATCH_MODES.get(
        next_step, "subagent"
    )
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


def _next_step(current: str, steps: list[str] | None = None) -> str | None:
    """Get the next pipeline step after current. Returns None if at end.

    Uses ``steps`` if provided, otherwise defaults to full PIPELINE_STEPS.
    """
    effective = steps if steps is not None else PIPELINE_STEPS
    if current == "idle":
        return effective[0] if effective else None
    try:
        idx = effective.index(current)
        if idx + 1 < len(effective):
            return effective[idx + 1]
        return None
    except ValueError:
        return effective[0] if effective else None


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
    complexity = pos.get("complexity_level")

    mode = get_dispatch_override(complexity, step) or DISPATCH_MODES[step]
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
    active_steps = get_active_steps(dom_root)

    # Build step status list
    idx_current = (
        active_steps.index(current_step) if current_step in active_steps else -1
    )
    steps = []
    for step in active_steps:
        idx_step = active_steps.index(step)
        if idx_step < idx_current:
            step_status = "complete"
        elif idx_step == idx_current:
            step_status = pos.get("status", "active")
        else:
            step_status = "pending"
        mode = get_dispatch_override(pos.get("complexity_level"), step) or DISPATCH_MODES.get(step, "subagent")
        steps.append({"step": step, "status": step_status, "mode": mode})

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
    for name in [
        "research", "plan", "progress", "test-report",
        "security-findings", "performance-report",
        "review", "metrics",
    ]:
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

    active_steps = get_active_steps(dom_root)
    next_step = _next_step(current_step, active_steps) if status == "complete" else current_step

    # Build what_just_happened from phase artifacts.
    what_happened = None
    tip = None
    if phase and current_step != "idle":
        p_path = get_phase_path(dom_root, phase)
        if current_step == "research" and status == "complete":
            research = read_toml_optional(p_path / "research.toml") or {}
            findings = research.get("findings", [])
            high = sum(1 for f in findings if f.get("severity") == "high")
            what_happened = f"Researcher found {len(findings)} finding(s), {high} high severity"
            if high:
                tip = "High-severity findings detected — Architect will route accordingly"
        elif current_step == "review" and status == "complete":
            review = read_toml_optional(p_path / "review.toml") or {}
            verdict = review.get("verdict", "unknown")
            what_happened = f"Review verdict: {verdict}"
        elif current_step == "audit" and status == "complete":
            test_report = read_toml_optional(p_path / "test-report.toml")
            sec_findings = read_toml_optional(p_path / "security-findings.toml")
            parts = []
            if test_report:
                parts.append("test-report submitted")
            if sec_findings:
                parts.append("security findings submitted")
            what_happened = ", ".join(parts) if parts else "Audit step complete"

    result: dict = {
        "current_position": f"Phase {phase}, step: {current_step} ({status})",
    }

    if what_happened:
        result["what_just_happened"] = what_happened
    if tip:
        result["tip"] = tip

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
