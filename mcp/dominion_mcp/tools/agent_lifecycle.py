"""Agent lifecycle tools — start, submit, signal, status."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ..server import mcp
from ..core.config import (
    current_phase,
    find_dominion_root,
    phase_path,
    read_toml,
    read_toml_optional,
    write_toml,
    write_toml_locked,
)
from ..core.memory import get_agent_memory
from ..core.methodology import assemble_methodology, get_budget, get_condition_signals
from ..core.panel import get_panel_context, get_step_panel_type
from ..core.state import get_position, raise_blocker, raise_warning

COMMUNICATION_DIRECTIVES: dict[str, str] = {
    "beginner": (
        "Explain reasoning at each step. Show output examples. "
        "Define technical terms. Annotate complex patterns."
    ),
    "intermediate": "Balanced detail. Explain non-obvious choices only.",
    "advanced": "Be terse. Reference method names. Skip obvious explanations.",
}

logger = logging.getLogger(__name__)

_cached_root: Path | None = None


def _get_root() -> Path:
    """Find and cache the .dominion/ root directory."""
    global _cached_root
    if _cached_root is None:
        _cached_root = find_dominion_root()
    return _cached_root


def _error(message: str) -> str:
    """Return a JSON error response."""
    return json.dumps({"error": message})


@mcp.tool()
async def agent_start(
    role: str,
    phase_id: int | None = None,
    task_id: str | None = None,
    mode: str | None = None,
    panel_topic: str | None = None,
) -> str:
    """Initialize agent session. Returns methodology, assignment, tools, constraints, memory.

    For panel mode: set mode="panel" with panel_topic to get multi-perspective
    facilitation context instead of single-agent methodology.
    """
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        # Panel mode: return combined perspectives + facilitation.
        if mode == "panel":
            pos = get_position(dom_root)
            step = pos.get("step", "discuss")
            decision_type = get_step_panel_type(step)
            topic = panel_topic or f"Phase {pos.get('phase', 0)} {step} discussion"
            panel_ctx = get_panel_context(dom_root, decision_type, topic)
            return json.dumps(panel_ctx)

        # Read agent TOML
        agent_path = dom_root / "agents" / role / "agent.toml"
        if not agent_path.exists():
            return _error(f"Agent '{role}' not found at {agent_path.name}")
        agent_toml = read_toml(agent_path)

        # Condition signals and model
        signals = get_condition_signals(dom_root)
        agent_section = agent_toml.get("agent", {})
        model = agent_section.get("model", "sonnet")

        # Assemble methodology
        methodology = assemble_methodology(dom_root, role, signals, model)

        # Token budget
        token_budget = get_budget(agent_toml)

        # Assignment from state
        state = read_toml_optional(dom_root / "state.toml") or {}
        pos = state.get("position", {})
        effective_phase = phase_id if phase_id is not None else pos.get("phase", 0)
        scope = pos.get("scope")

        # Read intent from phase directory if available
        intent = None
        if effective_phase:
            intent_path = phase_path(dom_root, effective_phase) / "intent.md"
            if intent_path.exists():
                intent = intent_path.read_text()

        # Agent memory
        memory = get_agent_memory(dom_root, role)

        # Tools from agent TOML
        tools = agent_toml.get("tools", [])

        # Hard stops from agent TOML [governance] section
        hard_stops = agent_toml.get("governance", {}).get("hard_stops", [])

        # Skill level communication directive
        skill_level = signals.get("user_skill_level")
        communication = COMMUNICATION_DIRECTIVES.get(skill_level or "")

        payload = {
            "methodology": methodology,
            "assignment": {
                "phase_id": effective_phase,
                "intent": intent,
                "scope": scope,
                "task_id": task_id,
            },
            "tools": tools,
            "constraints": {
                "hard_stops": hard_stops,
                "max_tokens": token_budget,
                "model": model,
            },
            "memory": memory,
        }

        if communication:
            payload["communication"] = communication

        return json.dumps(payload)

    except Exception as exc:
        logger.exception("agent_start failed for role=%s", role)
        return _error(f"agent_start failed: {exc}")


@mcp.tool()
async def agent_submit(
    role: str,
    artifact_type: str,
    content: str,
) -> str:
    """Submit work artifact. Validates, writes to .dominion/, updates state."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        # Parse content as JSON
        try:
            artifact_data = json.loads(content)
        except json.JSONDecodeError as exc:
            return _error(f"Invalid JSON in content: {exc}")

        # Determine current phase
        phase = current_phase(dom_root)
        if phase == 0:
            return _error("No active phase. Cannot submit artifact.")

        # Write artifact to phase directory
        p_path = phase_path(dom_root, phase)
        p_path.mkdir(parents=True, exist_ok=True)

        # Determine file extension based on artifact type
        if isinstance(artifact_data, dict):
            artifact_path = p_path / f"{artifact_type}.toml"
            write_toml(artifact_path, artifact_data)
        else:
            # Non-dict data: write as JSON
            artifact_path = p_path / f"{artifact_type}.json"
            artifact_path.write_text(json.dumps(artifact_data, indent=2))

        # Update state: mark role's step as complete
        state_path = dom_root / "state.toml"

        def _update(state: dict) -> dict:
            if "completed_steps" not in state:
                state["completed_steps"] = {}
            state["completed_steps"][role] = {
                "artifact": artifact_type,
                "phase": phase,
            }
            return state

        await write_toml_locked(state_path, _update)

        # Build handoff info
        handoff = {
            "status": "accepted",
            "artifact_type": artifact_type,
            "phase_id": phase,
            "written_to": str(artifact_path.relative_to(dom_root)),
            "role": role,
        }

        return json.dumps(handoff)

    except Exception as exc:
        logger.exception("agent_submit failed for role=%s", role)
        return _error(f"agent_submit failed: {exc}")


@mcp.tool()
async def agent_signal(
    role: str,
    signal_type: str,
    message: str | None = None,
) -> str:
    """Send signal: blocker, need-help, scope-change."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        msg = message or f"{role} raised {signal_type}"

        if signal_type == "blocker":
            signal_data = await raise_blocker(
                dom_root,
                level="task",
                task_id=role,
                reason=msg,
            )
            return json.dumps({"status": "blocker_raised", "signal": signal_data})

        elif signal_type == "need-help":
            await raise_warning(dom_root, task_id=role, message=msg)
            return json.dumps({
                "status": "warning_raised",
                "signal_type": "need-help",
                "message": msg,
            })

        elif signal_type == "scope-change":
            await raise_warning(dom_root, task_id=role, message=f"[scope-change] {msg}")
            return json.dumps({
                "status": "warning_raised",
                "signal_type": "scope-change",
                "message": msg,
            })

        else:
            return _error(
                f"Unknown signal type '{signal_type}'. "
                "Valid types: blocker, need-help, scope-change"
            )

    except Exception as exc:
        logger.exception("agent_signal failed for role=%s", role)
        return _error(f"agent_signal failed: {exc}")


@mcp.tool()
async def agent_status(role: str | None = None) -> str:
    """Current agent status, what's expected next."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        pos = get_position(dom_root)
        state = read_toml_optional(dom_root / "state.toml") or {}

        result: dict = {
            "position": pos,
        }

        # Include completed steps info
        completed = state.get("completed_steps", {})
        if role:
            result["role"] = role
            result["completed"] = completed.get(role)

            # Check if agent TOML exists
            agent_path = dom_root / "agents" / role / "agent.toml"
            result["agent_exists"] = agent_path.exists()
        else:
            result["completed_steps"] = completed

        # Include blocker info
        blocker = state.get("blocker")
        if blocker:
            result["blocker"] = blocker

        # Include lock info
        lock = state.get("lock")
        if lock:
            result["active_agent"] = lock

        return json.dumps(result)

    except Exception as exc:
        logger.exception("agent_status failed")
        return _error(f"agent_status failed: {exc}")
