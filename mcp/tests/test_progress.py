"""Tests for dominion_mcp.core.progress module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dominion_mcp.core.progress import (
    check_merge_ready,
    get_phase_progress,
    get_phase_status,
    get_wave_status,
    update_task_progress,
)


# ---------------------------------------------------------------------------
# get_wave_status
# ---------------------------------------------------------------------------


def test_get_wave_status_returns_data(dom_root_with_plan: Path) -> None:
    """get_wave_status returns wave data with tasks."""
    status = get_wave_status(dom_root_with_plan)
    assert "wave" in status
    assert "tasks" in status
    assert status["wave"] == 2  # fixture state.toml has wave=2


def test_get_wave_status_task_details(dom_root_with_plan: Path) -> None:
    """get_wave_status includes task IDs and statuses."""
    status = get_wave_status(dom_root_with_plan)
    task_ids = {t["id"] for t in status["tasks"]}
    assert "01-03" in task_ids


# ---------------------------------------------------------------------------
# get_phase_status
# ---------------------------------------------------------------------------


def test_get_phase_status_returns_structure(dom_root_with_plan: Path) -> None:
    """get_phase_status returns artifact inventory."""
    status = get_phase_status(dom_root_with_plan)
    assert status["phase"] == 1
    assert "artifacts" in status
    assert "plan.toml" in status["artifacts"]
    assert status["artifacts"]["plan.toml"] == "exists"


def test_get_phase_status_artifacts(dom_root_with_plan: Path) -> None:
    """get_phase_status reports missing artifacts correctly."""
    status = get_phase_status(dom_root_with_plan)
    # research.toml doesn't exist in fixture
    assert status["artifacts"]["research.toml"] == "missing"
    # progress.toml does exist
    assert status["artifacts"]["progress.toml"] == "exists"


# ---------------------------------------------------------------------------
# get_phase_progress
# ---------------------------------------------------------------------------


def test_get_phase_progress_wave_breakdown(dom_root_with_plan: Path) -> None:
    """get_phase_progress returns wave-by-wave breakdown."""
    progress = get_phase_progress(dom_root_with_plan, 1)
    assert progress["phase"] == 1
    assert len(progress["waves"]) == 2


def test_get_phase_progress_task_counts(dom_root_with_plan: Path) -> None:
    """get_phase_progress reports correct task counts per wave."""
    progress = get_phase_progress(dom_root_with_plan, 1)
    wave1 = next(w for w in progress["waves"] if w["number"] == 1)
    assert wave1["tasks_total"] == 2
    assert wave1["tasks_complete"] == 1  # 01-01 is complete


def test_get_phase_progress_empty_phase(dom_root: Path) -> None:
    """get_phase_progress returns empty waves for a phase without progress."""
    progress = get_phase_progress(dom_root, 1)
    assert progress["waves"] == []


# ---------------------------------------------------------------------------
# check_merge_ready
# ---------------------------------------------------------------------------


def test_check_merge_ready_not_ready(dom_root_with_plan: Path) -> None:
    """check_merge_ready returns False with incomplete task IDs."""
    ready, incomplete = check_merge_ready(dom_root_with_plan, 1)
    assert ready is False
    assert "01-02" in incomplete


def test_check_merge_ready_wave2_not_ready(dom_root_with_plan: Path) -> None:
    """check_merge_ready for wave 2 returns False (task pending)."""
    ready, incomplete = check_merge_ready(dom_root_with_plan, 2)
    assert ready is False
    assert "01-03" in incomplete


# ---------------------------------------------------------------------------
# update_task_progress
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_task_progress_changes_status(dom_root_with_plan: Path) -> None:
    """update_task_progress updates a task's status."""
    await update_task_progress(dom_root_with_plan, "01-02", "complete")
    # Verify it changed
    ready, incomplete = check_merge_ready(dom_root_with_plan, 1)
    assert ready is True
    assert incomplete == []


@pytest.mark.asyncio
async def test_update_task_progress_raises_for_unknown_task(dom_root_with_plan: Path) -> None:
    """update_task_progress raises ValueError for non-existent task."""
    with pytest.raises(ValueError, match="Task 99-99 not found"):
        await update_task_progress(dom_root_with_plan, "99-99", "complete")
