"""Objective tools — create, link, get, complete.

Tracks multi-session feature delivery across pipeline phases.
"""

from __future__ import annotations

from ..server import mcp
from ..core.config import find_dominion_root
from ..core.objective import (
    complete_objective as _complete,
    create_objective as _create,
    get_objective as _get,
    link_phase_to_objective as _link,
)


@mcp.tool()
async def create_objective(name: str, description: str) -> dict:
    """Create a new objective to track multi-session feature delivery.

    Args:
        name: Human-readable objective name (e.g., "Authentication Rewrite").
        description: Summary of what this objective delivers.
    """
    dom_root = find_dominion_root()
    return await _create(dom_root, name=name, description=description)


@mcp.tool()
async def link_phase_to_objective(phase: str, objective_id: str) -> dict:
    """Link a pipeline phase to an existing objective.

    Args:
        phase: Phase ID to link.
        objective_id: Objective slug ID.
    """
    dom_root = find_dominion_root()
    return await _link(dom_root, phase=phase, objective_id=objective_id)


@mcp.tool()
async def get_objective(objective_id: str | None = None) -> dict:
    """Get objective details. Without ID, returns all active objectives.

    Args:
        objective_id: Objective slug ID. Omit for all active.
    """
    dom_root = find_dominion_root()
    result = _get(dom_root, objective_id=objective_id)
    if isinstance(result, list):
        return {"objectives": result, "total": len(result)}
    return result


@mcp.tool()
async def complete_objective(objective_id: str, summary: str | None = None) -> dict:
    """Mark an objective as complete.

    Args:
        objective_id: Objective slug ID.
        summary: Optional final summary (overwrites existing).
    """
    dom_root = find_dominion_root()
    return await _complete(dom_root, objective_id=objective_id, summary=summary)
