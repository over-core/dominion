"""Pipeline tools — next action, dispatch, status, history, help."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ..server import mcp
from ..core.complexity import COMPLEXITY_LEVELS
from ..core.config import find_dominion_root
from ..core.pipeline import (
    get_help,
    get_next_action,
    get_phase_history,
    get_pipeline_status,
    get_step_dispatch,
)
from ..core.state import update_position

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
async def pipeline_next(complexity_level: str | None = None) -> str:
    """Returns next action: spawn_agent, user_checkpoint, panel, or complete.

    Optionally set complexity_level during the discuss step to adapt pipeline
    depth. Valid levels: trivial, moderate, complex, major.
    """
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        if complexity_level is not None:
            if complexity_level not in COMPLEXITY_LEVELS:
                return _error(
                    f"Invalid complexity_level '{complexity_level}'. "
                    f"Valid levels: {', '.join(COMPLEXITY_LEVELS)}"
                )
            await update_position(dom_root, complexity_level=complexity_level)

        result = get_next_action(dom_root)
        return json.dumps(result)
    except Exception as exc:
        logger.exception("pipeline_next failed")
        return _error(f"pipeline_next failed: {exc}")


@mcp.tool()
async def step_dispatch(step: str) -> str:
    """Returns dispatch mode and agent(s) for a specific step."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        result = get_step_dispatch(dom_root, step)
        return json.dumps(result)
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        logger.exception("step_dispatch failed for step=%s", step)
        return _error(f"step_dispatch failed: {exc}")


@mcp.tool()
async def phase_status() -> str:
    """Current phase, step, active agents, blockers, validation health."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        result = get_pipeline_status(dom_root)
        return json.dumps(result)
    except Exception as exc:
        logger.exception("phase_status failed")
        return _error(f"phase_status failed: {exc}")


@mcp.tool()
async def phase_history(phase_id: int | None = None) -> str:
    """What happened in previous phases."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        result = get_phase_history(dom_root, phase_id)
        return json.dumps(result)
    except Exception as exc:
        logger.exception("phase_history failed")
        return _error(f"phase_history failed: {exc}")


@mcp.tool()
async def help(question: str | None = None) -> str:
    """Contextual guidance — current position, next steps, available commands."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        result = get_help(dom_root, question)
        return json.dumps(result)
    except Exception as exc:
        logger.exception("help failed")
        return _error(f"help failed: {exc}")
