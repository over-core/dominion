"""Data read tools — config, style, plan, progress, knowledge, roadmap."""

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
    validate_file_path,
)
from ..core.knowledge import get_knowledge_file, search_knowledge
from ..core.plan import get_plan, get_task
from ..core.progress import get_phase_progress

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
async def get_config(section: str | None = None) -> str:
    """dominion.toml contents (optionally filtered by section)."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        config_path = dom_root / "dominion.toml"
        data = read_toml_optional(config_path)
        if data is None:
            return _error("dominion.toml not found")

        if section:
            filtered = data.get(section)
            if filtered is None:
                return _error(f"Section '{section}' not found in dominion.toml")
            return json.dumps({section: filtered})

        return json.dumps(data)

    except Exception as exc:
        logger.exception("get_config failed")
        return _error(f"get_config failed: {exc}")


@mcp.tool()
async def get_style(section: str | None = None) -> str:
    """style.toml contents (conventions, patterns)."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        style_path = dom_root / "style.toml"
        data = read_toml_optional(style_path)
        if data is None:
            return _error("style.toml not found")

        if section:
            filtered = data.get(section)
            if filtered is None:
                return _error(f"Section '{section}' not found in style.toml")
            return json.dumps({section: filtered})

        return json.dumps(data)

    except Exception as exc:
        logger.exception("get_style failed")
        return _error(f"get_style failed: {exc}")


@mcp.tool()
async def get_plan(
    phase_id: int | None = None,
    task_id: str | None = None,
) -> str:
    """plan.toml — tasks, waves, criteria. Returns full plan or single task."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        if task_id:
            task = get_task(dom_root, task_id, phase=phase_id)
            if task is None:
                return _error(f"Task '{task_id}' not found in plan")
            return json.dumps(task)
        else:
            plan = get_plan(dom_root, phase=phase_id)
            return json.dumps(plan)

    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        logger.exception("get_plan failed")
        return _error(f"get_plan failed: {exc}")


@mcp.tool()
async def get_progress(phase_id: int | None = None) -> str:
    """progress.toml — task completion status."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        phase = phase_id if phase_id is not None else current_phase(dom_root)
        if phase == 0:
            return json.dumps({"phase": 0, "waves": [], "message": "No active phase"})

        result = get_phase_progress(dom_root, phase)
        return json.dumps(result)

    except Exception as exc:
        logger.exception("get_progress failed")
        return _error(f"get_progress failed: {exc}")


@mcp.tool()
async def get_knowledge(file: str) -> str:
    """Specific knowledge file contents."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        validate_file_path(file)
        content = get_knowledge_file(dom_root, file)
        return json.dumps({"file": file, "content": content})

    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        logger.exception("get_knowledge failed for file=%s", file)
        return _error(f"get_knowledge failed: {exc}")


@mcp.tool()
async def search_knowledge(query: str) -> str:
    """Search across knowledge index."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        results = search_knowledge(dom_root, query)
        return json.dumps({"query": query, "results": results})

    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:
        logger.exception("search_knowledge failed for query=%s", query)
        return _error(f"search_knowledge failed: {exc}")


@mcp.tool()
async def get_roadmap() -> str:
    """roadmap.toml — milestones and phases."""
    try:
        dom_root = _get_root()
    except ValueError:
        return _error("Run /dominion:onboard first — .dominion/ not found")

    try:
        roadmap_path = dom_root / "roadmap.toml"
        data = read_toml_optional(roadmap_path)
        if data is None:
            return _error("roadmap.toml not found")

        return json.dumps(data)

    except Exception as exc:
        logger.exception("get_roadmap failed")
        return _error(f"get_roadmap failed: {exc}")
