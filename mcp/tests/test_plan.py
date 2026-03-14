"""Tests for dominion_mcp.core.plan module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dominion_mcp.core.plan import (
    compute_waves,
    get_plan,
    get_task,
    get_wave_tasks,
    validate_plan,
)


# ---------------------------------------------------------------------------
# get_plan
# ---------------------------------------------------------------------------


def test_get_plan_returns_plan_dict(dom_root_with_plan: Path) -> None:
    """get_plan returns the plan dict with tasks."""
    plan = get_plan(dom_root_with_plan)
    assert "tasks" in plan
    assert len(plan["tasks"]) == 3


def test_get_plan_raises_when_missing(dom_root: Path) -> None:
    """get_plan raises ValueError when plan.toml does not exist."""
    with pytest.raises(ValueError, match="File not found"):
        get_plan(dom_root)


# ---------------------------------------------------------------------------
# get_task
# ---------------------------------------------------------------------------


def test_get_task_finds_by_id(dom_root_with_plan: Path) -> None:
    """get_task returns the task dict matching the given ID."""
    task = get_task(dom_root_with_plan, "01-01")
    assert task is not None
    assert task["title"] == "Set up project structure"
    assert task["wave"] == 1


def test_get_task_returns_none_for_missing(dom_root_with_plan: Path) -> None:
    """get_task returns None when no task matches the ID."""
    task = get_task(dom_root_with_plan, "99-99")
    assert task is None


def test_get_task_finds_second_task(dom_root_with_plan: Path) -> None:
    """get_task finds the correct task among multiple."""
    task = get_task(dom_root_with_plan, "01-03")
    assert task is not None
    assert task["title"] == "Add API endpoints"
    assert task["wave"] == 2


# ---------------------------------------------------------------------------
# get_wave_tasks
# ---------------------------------------------------------------------------


def test_get_wave_tasks_wave1(dom_root_with_plan: Path) -> None:
    """get_wave_tasks returns all tasks assigned to wave 1."""
    tasks = get_wave_tasks(dom_root_with_plan, 1)
    assert len(tasks) == 2
    ids = {t["id"] for t in tasks}
    assert ids == {"01-01", "01-02"}


def test_get_wave_tasks_wave2(dom_root_with_plan: Path) -> None:
    """get_wave_tasks returns all tasks assigned to wave 2."""
    tasks = get_wave_tasks(dom_root_with_plan, 2)
    assert len(tasks) == 1
    assert tasks[0]["id"] == "01-03"


def test_get_wave_tasks_empty_wave(dom_root_with_plan: Path) -> None:
    """get_wave_tasks returns empty list for a wave with no tasks."""
    tasks = get_wave_tasks(dom_root_with_plan, 99)
    assert tasks == []


# ---------------------------------------------------------------------------
# compute_waves
# ---------------------------------------------------------------------------


def test_compute_waves_no_deps() -> None:
    """Tasks with no dependencies all get wave 1."""
    tasks = [
        {"id": "01-01", "depends_on": []},
        {"id": "01-02", "depends_on": []},
    ]
    waves = compute_waves(tasks)
    assert waves["01-01"] == 1
    assert waves["01-02"] == 1


def test_compute_waves_with_deps() -> None:
    """Tasks with dependencies get higher wave numbers."""
    tasks = [
        {"id": "01-01", "depends_on": []},
        {"id": "01-02", "depends_on": []},
        {"id": "01-03", "depends_on": ["01-01", "01-02"]},
    ]
    waves = compute_waves(tasks)
    assert waves["01-01"] == 1
    assert waves["01-02"] == 1
    assert waves["01-03"] == 2


def test_compute_waves_chain() -> None:
    """A chain of dependencies produces incrementing wave numbers."""
    tasks = [
        {"id": "01-01", "depends_on": []},
        {"id": "01-02", "depends_on": ["01-01"]},
        {"id": "01-03", "depends_on": ["01-02"]},
    ]
    waves = compute_waves(tasks)
    assert waves["01-01"] == 1
    assert waves["01-02"] == 2
    assert waves["01-03"] == 3


def test_compute_waves_circular_raises() -> None:
    """Circular dependencies raise ValueError."""
    tasks = [
        {"id": "01-01", "depends_on": ["01-02"]},
        {"id": "01-02", "depends_on": ["01-01"]},
    ]
    with pytest.raises(ValueError, match="Circular dependency"):
        compute_waves(tasks)


# ---------------------------------------------------------------------------
# validate_plan
# ---------------------------------------------------------------------------


def test_validate_plan_valid(dom_root_with_plan: Path) -> None:
    """validate_plan returns pass for well-formed plan."""
    plan = get_plan(dom_root_with_plan)
    checks = validate_plan(plan)
    statuses = {c["check"]: c["status"] for c in checks}
    assert statuses["task_id_format"] == "pass"
    assert statuses["no_circular_deps"] == "pass"
    assert statuses["file_ownership"] == "pass"
    assert statuses["dependency_refs"] == "pass"
    assert statuses["required_fields"] == "pass"
    assert statuses["wave_consistency"] == "pass"


def test_validate_plan_bad_id_format() -> None:
    """validate_plan fails on badly formatted task IDs."""
    plan = {"tasks": [{"id": "bad", "title": "T", "assigned_to": "dev", "depends_on": []}]}
    checks = validate_plan(plan)
    id_check = next(c for c in checks if c["check"] == "task_id_format")
    assert id_check["status"] == "fail"
    assert "bad format" in id_check["message"]


def test_validate_plan_missing_dep_ref() -> None:
    """validate_plan fails when a dependency references a non-existent task."""
    plan = {
        "tasks": [
            {"id": "01-01", "title": "T", "assigned_to": "dev", "depends_on": ["99-99"]},
        ]
    }
    checks = validate_plan(plan)
    dep_check = next(c for c in checks if c["check"] == "dependency_refs")
    assert dep_check["status"] == "fail"


def test_validate_plan_missing_required_fields() -> None:
    """validate_plan fails when tasks lack title or assigned_to."""
    plan = {"tasks": [{"id": "01-01", "depends_on": []}]}
    checks = validate_plan(plan)
    fields_check = next(c for c in checks if c["check"] == "required_fields")
    assert fields_check["status"] == "fail"
    assert "title" in fields_check["message"]


def test_validate_plan_token_budget_over() -> None:
    """validate_plan reports token budget violations."""
    plan = {
        "tasks": [
            {"id": "01-01", "title": "T", "assigned_to": "dev", "depends_on": [], "token_estimate": 200000},
        ]
    }
    checks = validate_plan(plan, max_tokens=150000)
    budget_check = next(c for c in checks if c["check"] == "token_budget")
    assert budget_check["status"] == "fail"
