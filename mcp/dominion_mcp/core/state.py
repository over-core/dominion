"""Pipeline state and signal management for dominion-mcp."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .config import (
    dominion_path,
    read_toml,
    read_toml_glob,
    read_toml_optional,
    write_toml,
    write_toml_locked,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_STEPS = ("idle", "discuss", "research", "plan", "execute", "audit", "review", "improve")
VALID_STATUSES = ("ready", "active", "blocked", "complete")
BLOCKER_LEVELS = ("task", "wave", "phase", "critical")


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------


def get_position(dom_root: Path) -> dict:
    """Read current pipeline position from state.toml.

    Returns a dict with keys: phase, step, wave, status, last_session, message.
    """
    state = read_toml_optional(dom_root / "state.toml") or {}
    pos = state.get("position", {})

    phase = pos.get("phase", 0)
    step = pos.get("step", "idle")
    status = pos.get("status", "ready")
    last_session = pos.get("last_session", "unknown")
    wave = pos.get("wave", 0)
    complexity_level = pos.get("complexity_level")

    if phase == 0:
        message = "Dominion initialized. No active phase."
    else:
        message = f"Phase {phase}, Step {step}. Status: {status}."

    result = {
        "phase": phase,
        "step": step,
        "wave": wave,
        "status": status,
        "last_session": last_session,
        "message": message,
    }
    if complexity_level:
        result["complexity_level"] = complexity_level
    return result


async def update_position(
    dom_root: Path,
    *,
    phase: int | None = None,
    step: str | None = None,
    wave: int | None = None,
    status: str | None = None,
    complexity_level: str | None = None,
) -> dict:
    """Update pipeline position fields.

    Validates step and status values against their allowed sets.
    Uses write_toml_locked for async safety. Returns the updated position dict.

    Raises ValueError for invalid step or status values.
    """
    if step is not None and step not in VALID_STEPS:
        raise ValueError(
            f"Invalid step '{step}'. Must be one of: {', '.join(VALID_STEPS)}"
        )
    if status is not None and status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}"
        )
    if complexity_level is not None and complexity_level not in (
        "trivial", "moderate", "complex", "major"
    ):
        raise ValueError(
            f"Invalid complexity_level '{complexity_level}'. "
            "Must be one of: trivial, moderate, complex, major"
        )

    state_path = dom_root / "state.toml"

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
        return state

    updated = await write_toml_locked(state_path, _update)
    return updated.get("position", {})


async def checkpoint(dom_root: Path) -> None:
    """Checkpoint session state.

    Sets last_session timestamp to current UTC time, clears the lock section,
    and resets status from 'active' to 'ready'. Uses write_toml_locked.
    """
    state_path = dom_root / "state.toml"
    now = datetime.now(timezone.utc).isoformat()

    def _update(state: dict) -> dict:
        if "position" not in state:
            state["position"] = {}
        state["position"]["last_session"] = now
        if "lock" in state:
            del state["lock"]
        if state["position"].get("status") == "active":
            state["position"]["status"] = "ready"
        return state

    await write_toml_locked(state_path, _update)


async def save_decision(
    dom_root: Path, task: str, text: str, tags: list[str] | None = None
) -> dict:
    """Record a decision in state.toml decisions list.

    Auto-increments the decision ID. Timestamps with UTC ISO format.
    Uses write_toml_locked. Returns the new decision dict.
    """
    state_path = dom_root / "state.toml"
    entry: dict = {}

    def _update(state: dict) -> dict:
        nonlocal entry
        existing = state.get("decisions", [])
        max_id = max((d.get("id", 0) for d in existing), default=0)
        new_id = max_id + 1

        entry = {
            "id": new_id,
            "phase": state.get("position", {}).get("phase", 0),
            "task": task,
            "agent": state.get("lock", {}).get("agent", "unknown"),
            "text": text,
            "tags": tags or [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        existing.append(entry)
        state["decisions"] = existing
        return state

    await write_toml_locked(state_path, _update)
    return entry


def get_decisions(
    dom_root: Path, tags: list[str] | None = None, phase: int | None = None
) -> list[dict]:
    """Search decisions log from state.toml.

    Optionally filter by tags (any overlap matches) and/or phase number.
    """
    state = read_toml_optional(dom_root / "state.toml") or {}
    items = state.get("decisions", [])

    if tags:
        tag_set = set(tags)
        items = [d for d in items if tag_set & set(d.get("tags", []))]
    if phase is not None:
        items = [d for d in items if d.get("phase") == phase]

    return items


async def defer_item(dom_root: Path, text: str) -> None:
    """Park an out-of-scope item in outstanding.deferred list.

    Uses write_toml_locked.
    """
    state_path = dom_root / "state.toml"

    def _update(state: dict) -> dict:
        if "outstanding" not in state:
            state["outstanding"] = {}
        if "deferred" not in state["outstanding"]:
            state["outstanding"]["deferred"] = []
        state["outstanding"]["deferred"].append(text)
        return state

    await write_toml_locked(state_path, _update)


def get_deferred(dom_root: Path) -> list[str]:
    """List deferred items from outstanding.deferred in state.toml."""
    state = read_toml_optional(dom_root / "state.toml") or {}
    return state.get("outstanding", {}).get("deferred", [])


# ---------------------------------------------------------------------------
# Signal management
# ---------------------------------------------------------------------------


async def raise_blocker(
    dom_root: Path, level: str, task_id: str, reason: str
) -> dict:
    """Raise a blocker signal.

    1. Validates level against BLOCKER_LEVELS.
    2. Writes signal file to .dominion/signals/blocker-{task_id}.toml.
    3. Updates state.toml: sets blocker field, sets status='blocked' for
       wave/phase/critical levels.

    Returns the signal data dict.
    Raises ValueError for invalid level.
    """
    if level not in BLOCKER_LEVELS:
        raise ValueError(
            f"Invalid blocker level '{level}'. Must be one of: {', '.join(BLOCKER_LEVELS)}"
        )

    now = datetime.now(timezone.utc).isoformat()
    signal_data = {
        "type": "blocker",
        "level": level,
        "task": task_id,
        "reason": reason,
        "raised_at": now,
    }

    signals_dir = dominion_path(dom_root, "signals")
    signals_dir.mkdir(parents=True, exist_ok=True)
    signal_path = signals_dir / f"blocker-{task_id}.toml"
    write_toml(signal_path, signal_data)

    # Update state.toml with blocker info
    state_path = dom_root / "state.toml"

    def _update(state: dict) -> dict:
        state["blocker"] = {"task": task_id, "level": level, "reason": reason}
        if level in ("wave", "phase", "critical"):
            state.setdefault("position", {})["status"] = "blocked"
        return state

    await write_toml_locked(state_path, _update)

    return signal_data


async def raise_warning(dom_root: Path, task_id: str, message: str) -> None:
    """Raise a warning signal (FYI, no halt).

    Writes to .dominion/signals/warning-{task_id}-{seq}.toml where seq
    is the count of existing warnings for this task plus one.
    """
    now = datetime.now(timezone.utc).isoformat()

    signals_dir = dominion_path(dom_root, "signals")
    signals_dir.mkdir(parents=True, exist_ok=True)

    existing = list(signals_dir.glob(f"warning-{task_id}-*.toml"))
    seq = len(existing) + 1

    signal_data = {
        "type": "warning",
        "task": task_id,
        "message": message,
        "raised_at": now,
    }

    signal_path = signals_dir / f"warning-{task_id}-{seq}.toml"
    write_toml(signal_path, signal_data)


def list_signals(dom_root: Path, affecting: str | None = None) -> list[dict]:
    """List current signals from .dominion/signals/ directory.

    Optionally filter by task_id via the affecting parameter.
    Each returned dict includes a '_file' key with the signal filename stem.
    """
    signals_dir = dominion_path(dom_root, "signals")
    signals = read_toml_glob(signals_dir)

    if affecting:
        signals = [s for s in signals if s.get("task") == affecting]

    return signals


async def resolve_signal(dom_root: Path, signal_ref: str) -> None:
    """Resolve and remove signal(s) matching signal_ref.

    signal_ref can be a filename (e.g. 'blocker-01-03.toml') or a task id
    (e.g. '01-03'). If a blocker was resolved, clears the blocker field from
    state.toml and sets status to 'active'.

    Raises ValueError if no matching signal is found.
    """
    signals_dir = dominion_path(dom_root, "signals")

    if signal_ref.endswith(".toml"):
        target = signals_dir / signal_ref
        targets = [target] if target.exists() else []
    else:
        targets = list(signals_dir.glob(f"*-{signal_ref}*.toml"))

    if not targets:
        raise ValueError(f"No signal found matching '{signal_ref}'")

    was_blocker = False
    for target in targets:
        data = read_toml(target)
        if data.get("type") == "blocker":
            was_blocker = True
        target.unlink()

    if was_blocker:
        state_path = dom_root / "state.toml"

        def _update(state: dict) -> dict:
            if "blocker" in state:
                del state["blocker"]
            state.setdefault("position", {})["status"] = "active"
            return state

        await write_toml_locked(state_path, _update)
