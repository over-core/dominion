"""Tests for v0.3.0 core/filesystem module."""

from pathlib import Path

import pytest

from dominion_mcp.core.filesystem import (
    create_phase_dirs,
    create_task_dirs,
    read_status,
    write_status,
    read_output,
    write_output,
    read_summary,
    append_summary,
    write_claude_md,
    write_agent_claude_md,
    write_phase_claude_md,
    write_task_claude_md,
    scan_step_statuses,
    scan_task_statuses,
    count_summary_roles,
)


def test_create_phase_dirs(dom_root: Path):
    pipeline = ["research", "plan", "execute", "review"]
    phase_dir = create_phase_dirs(dom_root, "02", pipeline)

    assert phase_dir.exists()
    assert (phase_dir / "status").read_text() == "active"
    for step in pipeline:
        assert (phase_dir / step / "status").read_text() == "pending"
        assert (phase_dir / step / "output").is_dir()
    assert (phase_dir / "tasks").is_dir()


def test_create_task_dirs(dom_root: Path):
    (dom_root / "phases" / "01" / "tasks").mkdir(parents=True, exist_ok=True)
    task_dir = create_task_dirs(dom_root, "01", "fix-01")

    assert task_dir.exists()
    assert (task_dir / "output").is_dir()
    assert (task_dir / "status").read_text() == "active"


def test_read_status_missing():
    assert read_status(Path("/nonexistent/status")) == "pending"


def test_write_read_status(tmp_path: Path):
    path = tmp_path / "status"
    write_status(path, "complete")
    assert read_status(path) == "complete"


def test_write_status_invalid(tmp_path: Path):
    with pytest.raises(ValueError, match="Invalid status"):
        write_status(tmp_path / "status", "invalid")


def test_write_read_output(dom_root: Path):
    (dom_root / "phases" / "01" / "research" / "output").mkdir(parents=True, exist_ok=True)
    write_output(dom_root, "01", "research", "test.txt", "hello")
    assert read_output(dom_root, "01", "research", "test.txt") == "hello"


def test_read_output_missing(dom_root: Path):
    assert read_output(dom_root, "99", "research", "missing.txt") is None


@pytest.mark.asyncio
async def test_append_summary(dom_root: Path):
    (dom_root / "phases" / "01" / "research" / "output").mkdir(parents=True, exist_ok=True)
    await append_summary(dom_root, "01", "research", "researcher", "Found 3 issues.")
    await append_summary(dom_root, "01", "research", "security-auditor", "1 CVE found.")

    content = read_summary(dom_root, "01", "research")
    assert "## researcher" in content
    assert "## security-auditor" in content


def test_write_claude_md(dom_root: Path):
    (dom_root / "phases" / "01" / "research").mkdir(parents=True, exist_ok=True)
    path = write_claude_md(dom_root, "01", "research", "# Brief\nContent")
    assert path.exists()
    assert path.read_text() == "# Brief\nContent"


def test_write_agent_claude_md(dom_root: Path):
    path = write_agent_claude_md(dom_root, "01", "review", "security-auditor", "# Security Brief")
    assert path.exists()
    assert "agents/security-auditor/CLAUDE.md" in str(path)


def test_scan_step_statuses(dom_root_with_plan: Path):
    statuses = scan_step_statuses(dom_root_with_plan, "01", ["research", "plan", "execute", "review"])
    assert statuses["research"] == "complete"
    assert statuses["plan"] == "complete"
    assert statuses["execute"] == "pending"
    assert statuses["review"] == "pending"


def test_scan_task_statuses(dom_root_with_plan: Path):
    # Create some task dirs with status
    tasks_dir = dom_root_with_plan / "phases" / "01" / "tasks"
    t1 = tasks_dir / "01"
    t1.mkdir(parents=True)
    (t1 / "status").write_text("complete")
    t2 = tasks_dir / "02"
    t2.mkdir()
    (t2 / "status").write_text("active")

    statuses = scan_task_statuses(dom_root_with_plan, "01")
    assert statuses["01"] == "complete"
    assert statuses["02"] == "active"


def test_count_summary_roles(dom_root_with_plan: Path):
    roles = count_summary_roles(dom_root_with_plan, "01", "research")
    assert "researcher" in roles
