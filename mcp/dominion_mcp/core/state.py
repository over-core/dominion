"""Pipeline state management for v0.3.0.

Manages state.toml: position, circuit breaker, completed tasks, phases array,
decisions. All writes use async locking for safety.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .config import (
    read_toml_optional,
    write_toml,
    write_toml_locked,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_STEPS = ("idle", "discuss", "research", "plan", "execute", "review")
VALID_STATUSES = ("ready", "active", "blocked", "complete")
CIRCUIT_BREAKER_STATES = ("closed", "open", "half_open")


# ---------------------------------------------------------------------------
# Read state
# ---------------------------------------------------------------------------


def get_position(dom_root: Path) -> dict:
    """Read current pipeline position from state.toml.

    Returns dict with: phase, step, wave, status, complexity_level, last_session.
    Returns idle state if state.toml doesn't exist.
    """
    state = read_toml_optional(dom_root / "state.toml") or {}
    pos = state.get("position", {})

    return {
        "phase": pos.get("phase", "00"),
        "step": pos.get("step", "idle"),
        "wave": pos.get("wave", 0),
        "status": pos.get("status", "ready"),
        "complexity_level": pos.get("complexity_level"),
        "last_session": pos.get("last_session"),
    }


def get_circuit_breaker(dom_root: Path) -> dict:
    """Read circuit breaker state from state.toml."""
    state = read_toml_optional(dom_root / "state.toml") or {}
    cb = state.get("circuit_breaker", {})
    return {
        "state": cb.get("state", "closed"),
        "retry_count": cb.get("retry_count", 0),
        "iteration_count": cb.get("iteration_count", 0),
        "last_findings_hash": cb.get("last_findings_hash", ""),
        "same_finding_count": cb.get("same_finding_count", 0),
    }


def get_phases(dom_root: Path) -> list[dict]:
    """Read [[phases]] array from state.toml."""
    state = read_toml_optional(dom_root / "state.toml") or {}
    return state.get("phases", [])


def get_decisions(dom_root: Path, phase: str | None = None) -> list[dict]:
    """Read [[decisions]] from state.toml. Optionally filter by phase."""
    state = read_toml_optional(dom_root / "state.toml") or {}
    decisions = state.get("decisions", [])
    if phase is not None:
        decisions = [d for d in decisions if d.get("phase") == phase]
    return decisions


def get_completed_tasks(dom_root: Path) -> dict:
    """Read [completed_tasks] from state.toml."""
    state = read_toml_optional(dom_root / "state.toml") or {}
    return state.get("completed_tasks", {})


# ---------------------------------------------------------------------------
# Update position
# ---------------------------------------------------------------------------


async def update_position(
    dom_root: Path,
    *,
    phase: str | None = None,
    step: str | None = None,
    wave: int | None = None,
    status: str | None = None,
    complexity_level: str | None = None,
) -> dict:
    """Update pipeline position fields in state.toml.

    Validates step and status values. Uses write_toml_locked.
    Returns the updated position dict.
    """
    if step is not None and step not in VALID_STEPS:
        raise ValueError(f"Invalid step '{step}'. Must be one of: {', '.join(VALID_STEPS)}")
    if status is not None and status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}")

    state_path = dom_root / "state.toml"
    now = datetime.now(timezone.utc).isoformat()

    def _update(state: dict) -> dict:
        if "position" not in state:
            state["position"] = {}
        pos = state["position"]
        if phase is not None:
            pos["phase"] = phase
        if step is not None:
            pos["step"] = step
        if wave is not None:
            pos["wave"] = wave
        if status is not None:
            pos["status"] = status
        if complexity_level is not None:
            pos["complexity_level"] = complexity_level
        pos["last_session"] = now
        return state

    updated = await write_toml_locked(state_path, _update)
    return updated.get("position", {})


# ---------------------------------------------------------------------------
# Phase management
# ---------------------------------------------------------------------------


async def add_phase(
    dom_root: Path, phase_id: str, intent: str, complexity: str
) -> dict:
    """Add a new phase to [[phases]] array and update position."""
    state_path = dom_root / "state.toml"
    now = datetime.now(timezone.utc).isoformat()
    entry: dict = {}

    def _update(state: dict) -> dict:
        nonlocal entry
        if "phases" not in state:
            state["phases"] = []

        # Mark any active phase as abandoned
        for p in state["phases"]:
            if p.get("status") == "active":
                p["status"] = "abandoned"

        entry = {
            "id": phase_id,
            "intent": intent,
            "status": "active",
            "complexity": complexity,
            "started": now,
        }
        state["phases"].append(entry)

        # Clear completed_tasks for new phase
        state["completed_tasks"] = {}

        return state

    await write_toml_locked(state_path, _update)
    return entry


async def update_phase_status(dom_root: Path, phase_id: str, status: str) -> None:
    """Update a phase's status in [[phases]] array."""
    state_path = dom_root / "state.toml"

    def _update(state: dict) -> dict:
        for p in state.get("phases", []):
            if p.get("id") == phase_id:
                p["status"] = status
                break
        return state

    await write_toml_locked(state_path, _update)


def next_phase_id(dom_root: Path) -> str:
    """Determine next phase ID (zero-padded) from existing phases."""
    phases = get_phases(dom_root)
    if not phases:
        return "01"
    max_id = max(int(p.get("id", "0")) for p in phases)
    return f"{max_id + 1:02d}"


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------


async def update_circuit_breaker(
    dom_root: Path,
    *,
    state_val: str | None = None,
    retry_count: int | None = None,
    iteration_count: int | None = None,
    last_findings_hash: str | None = None,
    same_finding_count: int | None = None,
) -> dict:
    """Update circuit breaker fields in state.toml."""
    state_path = dom_root / "state.toml"

    def _update(state: dict) -> dict:
        if "circuit_breaker" not in state:
            state["circuit_breaker"] = {
                "state": "closed",
                "retry_count": 0,
                "iteration_count": 0,
                "last_findings_hash": "",
                "same_finding_count": 0,
            }
        cb = state["circuit_breaker"]
        if state_val is not None:
            cb["state"] = state_val
        if retry_count is not None:
            cb["retry_count"] = retry_count
        if iteration_count is not None:
            cb["iteration_count"] = iteration_count
        if last_findings_hash is not None:
            cb["last_findings_hash"] = last_findings_hash
        if same_finding_count is not None:
            cb["same_finding_count"] = same_finding_count
        return state

    updated = await write_toml_locked(state_path, _update)
    return updated.get("circuit_breaker", {})


# ---------------------------------------------------------------------------
# Completed tasks
# ---------------------------------------------------------------------------


async def mark_task_complete(dom_root: Path, task_id: str, phase: str, step: str) -> None:
    """Add a task to [completed_tasks] in state.toml."""
    state_path = dom_root / "state.toml"

    def _update(state: dict) -> dict:
        if "completed_tasks" not in state:
            state["completed_tasks"] = {}
        state["completed_tasks"][task_id] = {"phase": phase, "step": step}
        return state

    await write_toml_locked(state_path, _update)


# ---------------------------------------------------------------------------
# Decisions (v0.3.0: dual-write to state.toml + decisions.md)
# ---------------------------------------------------------------------------


async def save_decision(
    dom_root: Path,
    phase: str,
    title: str,
    decision: str,
    rationale: str,
    tags: list[str] | None = None,
) -> dict:
    """Record a decision in state.toml [[decisions]] and .dominion/decisions.md.

    Auto-increments ID. Returns the new decision dict.
    """
    state_path = dom_root / "state.toml"
    now = datetime.now(timezone.utc).isoformat()
    entry: dict = {}

    def _update(state: dict) -> dict:
        nonlocal entry
        existing = state.get("decisions", [])
        max_id = max((d.get("id", 0) for d in existing), default=0)
        new_id = max_id + 1

        entry = {
            "id": new_id,
            "phase": phase,
            "title": title,
            "decision": decision,
            "rationale": rationale,
            "tags": tags or [],
            "timestamp": now,
        }
        existing.append(entry)
        state["decisions"] = existing
        return state

    await write_toml_locked(state_path, _update)

    # Dual-write to decisions.md (committed, human-readable)
    decisions_md = dom_root / "decisions.md"
    tag_str = ", ".join(tags) if tags else ""
    date_str = now[:10]  # YYYY-MM-DD

    md_entry = (
        f"\n## {entry['id']}. {title} (Phase {phase})\n"
        f"**Decision:** {decision}\n"
        f"**Rationale:** {rationale}\n"
        f"**Tags:** {tag_str} | **Date:** {date_str}\n"
    )

    if decisions_md.exists():
        with open(decisions_md, "a") as f:
            f.write(md_entry)
    else:
        with open(decisions_md, "w") as f:
            f.write("# Architectural Decisions\n")
            f.write(md_entry)

    return entry
