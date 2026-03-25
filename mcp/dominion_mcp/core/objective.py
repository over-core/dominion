"""Objective management — multi-session feature tracking.

Objectives group related pipeline phases across sessions.
Stored in .dominion/objectives.toml (committed to git).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from .config import read_toml_optional, write_toml_locked
from .events import emit_event
from .state import get_phases, get_position


def _slugify(name: str) -> str:
    """Generate a slug ID from a name (lowercase, hyphens, max 30 chars)."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:30]


def read_objectives(dom_root: Path) -> list[dict]:
    """Read all objectives from objectives.toml."""
    data = read_toml_optional(dom_root / "objectives.toml")
    if not data:
        return []
    return data.get("objectives", [])


async def create_objective(dom_root: Path, name: str, description: str) -> dict:
    """Create a new objective."""
    obj_id = _slugify(name)
    now = datetime.now(timezone.utc).isoformat()

    entry = {
        "id": obj_id,
        "name": name,
        "status": "in-progress",
        "created": now,
        "completed": "",
        "phases": [],
        "summary": description,
    }

    def _update(data: dict) -> dict:
        objectives = data.get("objectives", [])
        # Check for duplicate
        for obj in objectives:
            if obj.get("id") == obj_id:
                return data  # Already exists, no-op
        objectives.append(entry)
        data["objectives"] = objectives
        return data

    await write_toml_locked(dom_root / "objectives.toml", _update)

    pos = get_position(dom_root)
    phase = pos.get("phase", "00")
    await emit_event(dom_root, phase=phase, event="objective_created",
                     data={"name": name, "id": obj_id})
    return entry


async def link_phase_to_objective(dom_root: Path, phase: str, objective_id: str) -> dict:
    """Add a phase to an objective's phases list."""
    found = {"found": False, "entry": {}}

    def _update(data: dict) -> dict:
        for obj in data.get("objectives", []):
            if obj.get("id") == objective_id:
                found["found"] = True
                found["entry"] = obj
                if phase not in obj.get("phases", []):
                    obj.setdefault("phases", []).append(phase)
                return data
        return data

    await write_toml_locked(dom_root / "objectives.toml", _update)

    if not found["found"]:
        return {"error": f"Objective '{objective_id}' not found."}

    await emit_event(dom_root, phase=phase, event="objective_phase_linked",
                     data={"objective_id": objective_id})
    return {"status": "linked", "objective_id": objective_id, "phase": phase}


def get_objective(dom_root: Path, objective_id: str | None = None) -> dict | list[dict]:
    """Get one objective (enriched) or all active objectives."""
    objectives = read_objectives(dom_root)

    if objective_id is None:
        # Return all active (not completed/abandoned)
        return [o for o in objectives if o.get("status") == "in-progress"]

    for obj in objectives:
        if obj.get("id") == objective_id:
            # Enrich with phase intents
            phases_info = []
            all_phases = get_phases(dom_root)
            phase_map = {p.get("id"): p for p in all_phases}
            for pid in obj.get("phases", []):
                phase_data = phase_map.get(pid, {})
                phases_info.append({
                    "id": pid,
                    "intent": phase_data.get("intent", ""),
                    "status": phase_data.get("status", "unknown"),
                })
            return {**obj, "phases_detail": phases_info}

    return {"error": f"Objective '{objective_id}' not found."}


async def complete_objective(dom_root: Path, objective_id: str, summary: str | None = None) -> dict:
    """Mark an objective as complete."""
    found = {"found": False}
    now = datetime.now(timezone.utc).isoformat()

    def _update(data: dict) -> dict:
        for obj in data.get("objectives", []):
            if obj.get("id") == objective_id:
                found["found"] = True
                obj["status"] = "complete"
                obj["completed"] = now
                if summary:
                    obj["summary"] = summary
                return data
        return data

    await write_toml_locked(dom_root / "objectives.toml", _update)

    if not found["found"]:
        return {"error": f"Objective '{objective_id}' not found."}

    pos = get_position(dom_root)
    phase = pos.get("phase", "00")
    await emit_event(dom_root, phase=phase, event="objective_completed",
                     data={"objective_id": objective_id})
    return {"status": "complete", "objective_id": objective_id}
