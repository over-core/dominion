"""Data write tools — progress, blockers, decisions, memory."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ..server import mcp
from ..core.config import find_dominion_root
from ..core.memory import save_agent_memory
from ..core.progress import update_task_progress
from ..core.state import raise_blocker, resolve_signal, save_decision

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
async def update_progress(
    task_id: str,
    status: str,
    summary: str | None = None,
) -> str:
    """Progress tracking during execution."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        await update_task_progress(dom_root, task_id, status, summary=summary)
        return json.dumps({
            "status": "updated",
            "task_id": task_id,
            "new_status": status,
            "summary": summary,
        })

    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        logger.exception("update_progress failed for task=%s", task_id)
        return _error(f"update_progress failed: {exc}")


@mcp.tool()
async def add_blocker(description: str, severity: str) -> str:
    """Register a pipeline blocker."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        # Map severity to blocker level
        level_map = {
            "low": "task",
            "medium": "wave",
            "high": "phase",
            "critical": "critical",
            # Also accept raw level names
            "task": "task",
            "wave": "wave",
            "phase": "phase",
        }
        level = level_map.get(severity)
        if level is None:
            return _error(
                f"Invalid severity '{severity}'. "
                "Valid: low, medium, high, critical, task, wave, phase"
            )

        # Use a generated task_id based on description hash
        task_id = f"blocker-{abs(hash(description)) % 10000:04d}"

        signal_data = await raise_blocker(dom_root, level, task_id, description)
        return json.dumps({"status": "blocker_raised", "signal": signal_data})

    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        logger.exception("add_blocker failed")
        return _error(f"add_blocker failed: {exc}")


@mcp.tool()
async def resolve_blocker(blocker_id: str) -> str:
    """Mark blocker as resolved."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        await resolve_signal(dom_root, blocker_id)
        return json.dumps({
            "status": "resolved",
            "blocker_id": blocker_id,
        })

    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        logger.exception("resolve_blocker failed for id=%s", blocker_id)
        return _error(f"resolve_blocker failed: {exc}")


@mcp.tool()
async def save_decision(
    title: str,
    decision: str,
    rationale: str,
) -> str:
    """ADR-style decision record."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        text = f"{decision}\n\nRationale: {rationale}"
        entry = await save_decision(dom_root, task=title, text=text)
        return json.dumps({"status": "saved", "decision": entry})

    except Exception as exc:
        logger.exception("save_decision failed")
        return _error(f"save_decision failed: {exc}")


@mcp.tool()
async def save_memory(
    role: str,
    type: str,
    content: str,
) -> str:
    """Save agent-specific memory for future sessions."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        valid_types = ("correction", "preference", "discovery")
        if type not in valid_types:
            return _error(
                f"Invalid memory type '{type}'. Valid: {', '.join(valid_types)}"
            )

        await save_agent_memory(
            dom_root,
            role=role,
            memory_type=type,
            content=content,
            source=role,
        )
        return json.dumps({
            "status": "saved",
            "role": role,
            "type": type,
        })

    except Exception as exc:
        logger.exception("save_memory failed for role=%s", role)
        return _error(f"save_memory failed: {exc}")
