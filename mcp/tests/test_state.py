"""Tests for v0.3.0 dominion_mcp.core.state module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dominion_mcp.core.config import read_toml
from dominion_mcp.core.state import (
    get_circuit_breaker,
    get_completed_tasks,
    get_decisions,
    get_phases,
    get_position,
    mark_task_complete,
    next_phase_id,
    add_phase,
    save_decision,
    update_circuit_breaker,
    update_phase_status,
    update_position,
)


# -- get_position -----------------------------------------------------------


def test_get_position_with_state(dom_root: Path):
    pos = get_position(dom_root)
    assert pos["phase"] == "01"
    assert pos["step"] == "research"
    assert pos["status"] == "active"
    assert pos["complexity_level"] == "moderate"


def test_get_position_no_state(tmp_path: Path):
    dom = tmp_path / ".dominion"
    dom.mkdir()
    pos = get_position(dom)
    assert pos["phase"] == "00"
    assert pos["step"] == "idle"


# -- update_position --------------------------------------------------------


@pytest.mark.asyncio
async def test_update_position(dom_root: Path):
    pos = await update_position(dom_root, step="plan", status="active")
    assert pos["step"] == "plan"
    assert pos["status"] == "active"


@pytest.mark.asyncio
async def test_update_position_invalid_step(dom_root: Path):
    with pytest.raises(ValueError, match="Invalid step"):
        await update_position(dom_root, step="nonexistent")


@pytest.mark.asyncio
async def test_update_position_invalid_status(dom_root: Path):
    with pytest.raises(ValueError, match="Invalid status"):
        await update_position(dom_root, status="invalid")


# -- phases ------------------------------------------------------------------


def test_get_phases(dom_root: Path):
    phases = get_phases(dom_root)
    assert len(phases) == 1
    assert phases[0]["id"] == "01"
    assert phases[0]["intent"] == "Add rate limiting"


def test_next_phase_id(dom_root: Path):
    assert next_phase_id(dom_root) == "02"


def test_next_phase_id_empty(tmp_path: Path):
    dom = tmp_path / ".dominion"
    dom.mkdir()
    assert next_phase_id(dom) == "01"


@pytest.mark.asyncio
async def test_add_phase(dom_root: Path):
    entry = await add_phase(dom_root, "02", "Add OAuth2", "complex")
    assert entry["id"] == "02"
    assert entry["complexity"] == "complex"

    phases = get_phases(dom_root)
    assert len(phases) == 2
    # Previous active phase should be abandoned
    assert phases[0]["status"] == "abandoned"
    assert phases[1]["status"] == "active"


@pytest.mark.asyncio
async def test_update_phase_status(dom_root: Path):
    await update_phase_status(dom_root, "01", "complete")
    phases = get_phases(dom_root)
    assert phases[0]["status"] == "complete"


# -- circuit breaker ---------------------------------------------------------


def test_get_circuit_breaker(dom_root: Path):
    cb = get_circuit_breaker(dom_root)
    assert cb["state"] == "closed"
    assert cb["retry_count"] == 0
    assert cb["same_finding_count"] == 0


@pytest.mark.asyncio
async def test_update_circuit_breaker(dom_root: Path):
    cb = await update_circuit_breaker(
        dom_root, state_val="open", retry_count=2, same_finding_count=1
    )
    assert cb["state"] == "open"
    assert cb["retry_count"] == 2
    assert cb["same_finding_count"] == 1


# -- completed tasks ---------------------------------------------------------


@pytest.mark.asyncio
async def test_mark_task_complete(dom_root: Path):
    await mark_task_complete(dom_root, "01", "01", "execute")
    tasks = get_completed_tasks(dom_root)
    assert "01" in tasks
    assert tasks["01"]["phase"] == "01"


# -- decisions ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_decision(dom_root: Path):
    entry = await save_decision(
        dom_root, "01", "auth-approach", "Use OAuth2", "Standards-based", ["security"]
    )
    assert entry["id"] == 1
    assert entry["title"] == "auth-approach"

    # Verify dual-write to decisions.md
    decisions_md = dom_root / "decisions.md"
    assert decisions_md.exists()
    content = decisions_md.read_text()
    assert "auth-approach" in content
    assert "OAuth2" in content


@pytest.mark.asyncio
async def test_save_multiple_decisions(dom_root: Path):
    await save_decision(dom_root, "01", "first", "A", "Because", [])
    await save_decision(dom_root, "01", "second", "B", "Also", ["arch"])

    decisions = get_decisions(dom_root)
    assert len(decisions) == 2
    assert decisions[0]["id"] == 1
    assert decisions[1]["id"] == 2


def test_get_decisions_filter_by_phase(dom_root: Path):
    decisions = get_decisions(dom_root, phase="99")
    assert len(decisions) == 0
