"""Directory operations, status files, and output management for v0.3.0.

Manages the .dominion/phases/ directory tree: phase dirs, step dirs,
task dirs, status files (single-word text), and output files.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from .config import write_toml

# Per-file locks for concurrent summary appends (P-Thread safety).
_append_locks: dict[str, asyncio.Lock] = {}


# ---------------------------------------------------------------------------
# Phase directories
# ---------------------------------------------------------------------------


def create_phase_dirs(dom_root: Path, phase: str, pipeline: list[str]) -> Path:
    """Create the full phase directory tree.

    Creates phases/{phase}/ with:
    - CLAUDE.md placeholder
    - status file ("active")
    - Step directories per pipeline profile, each with output/ and status
    - tasks/ directory (populated later by prepare_task)

    Returns the phase directory path.
    """
    phase_dir = dom_root / "phases" / phase
    phase_dir.mkdir(parents=True, exist_ok=True)

    write_status(phase_dir / "status", "active")

    for step in pipeline:
        step_dir = phase_dir / step
        step_dir.mkdir(parents=True, exist_ok=True)
        (step_dir / "output").mkdir(exist_ok=True)
        write_status(step_dir / "status", "pending")

    # Tasks dir for execute step
    (phase_dir / "tasks").mkdir(exist_ok=True)

    return phase_dir


def create_task_dirs(dom_root: Path, phase: str, task_id: str) -> Path:
    """Create a task directory with output/ subdir and status file.

    Returns the task directory path.
    """
    task_dir = dom_root / "phases" / phase / "tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "output").mkdir(exist_ok=True)
    write_status(task_dir / "status", "active")
    return task_dir


# ---------------------------------------------------------------------------
# Status files — single-word text files
# ---------------------------------------------------------------------------

VALID_STATUSES = ("pending", "active", "complete", "blocked")


def read_status(path: Path) -> str:
    """Read a status file. Returns 'pending' if file doesn't exist."""
    if not path.exists():
        return "pending"
    return path.read_text().strip()


def write_status(path: Path, status: str) -> None:
    """Write a single-word status to a file."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {VALID_STATUSES}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(status)


# ---------------------------------------------------------------------------
# Output files
# ---------------------------------------------------------------------------


def read_output(dom_root: Path, phase: str, step: str, filename: str) -> str | None:
    """Read an output file from phases/{phase}/{step}/output/{filename}.

    Returns None if file doesn't exist.
    """
    path = dom_root / "phases" / phase / step / "output" / filename
    if not path.exists():
        return None
    return path.read_text()


def write_output(
    dom_root: Path, phase: str, step: str, filename: str, content: str
) -> Path:
    """Write content to phases/{phase}/{step}/output/{filename}.

    Creates parent dirs if needed. Returns the file path.
    """
    path = dom_root / "phases" / phase / step / "output" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def write_task_output(
    dom_root: Path, phase: str, task_id: str, filename: str, content: str
) -> Path:
    """Write content to phases/{phase}/tasks/{task_id}/output/{filename}."""
    path = dom_root / "phases" / phase / "tasks" / task_id / "output" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def write_output_toml(
    dom_root: Path, phase: str, step: str, filename: str, data: dict
) -> Path:
    """Write TOML data to an output file."""
    path = dom_root / "phases" / phase / step / "output" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    write_toml(path, data)
    return path


def write_task_output_toml(
    dom_root: Path, phase: str, task_id: str, filename: str, data: dict
) -> Path:
    """Write TOML data to a task output file."""
    path = dom_root / "phases" / phase / "tasks" / task_id / "output" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    write_toml(path, data)
    return path


# ---------------------------------------------------------------------------
# Summary files — append with locking for P-Thread concurrent writes
# ---------------------------------------------------------------------------


def read_summary(dom_root: Path, phase: str, step: str) -> str | None:
    """Read the summary.md for a step. Returns None if not found."""
    path = dom_root / "phases" / phase / step / "output" / "summary.md"
    if not path.exists():
        return None
    return path.read_text()


def read_task_summary(dom_root: Path, phase: str, task_id: str) -> str | None:
    """Read the summary.md for a task. Returns None if not found."""
    path = dom_root / "phases" / phase / "tasks" / task_id / "output" / "summary.md"
    if not path.exists():
        return None
    return path.read_text()


async def append_summary(
    dom_root: Path, phase: str, step: str, role: str, text: str
) -> Path:
    """Append a role's summary to the step's summary.md with async locking.

    Format: ## {role}\n{text}\n\n
    Uses per-file asyncio.Lock for P-Thread concurrent appends.
    """
    path = dom_root / "phases" / phase / step / "output" / "summary.md"
    return await _append_to_file(path, f"## {role}\n{text}\n\n")


async def append_task_summary(
    dom_root: Path, phase: str, task_id: str, role: str, text: str
) -> Path:
    """Append a role's summary to a task's summary.md."""
    path = dom_root / "phases" / phase / "tasks" / task_id / "output" / "summary.md"
    return await _append_to_file(path, f"## {role}\n{text}\n\n")


async def _append_to_file(path: Path, content: str) -> Path:
    """Append content to a file with per-file locking."""
    key = str(path.resolve())
    if key not in _append_locks:
        _append_locks[key] = asyncio.Lock()

    async with _append_locks[key]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(content)
    return path


# ---------------------------------------------------------------------------
# CLAUDE.md files
# ---------------------------------------------------------------------------


def write_claude_md(dom_root: Path, phase: str, step: str, content: str) -> Path:
    """Write CLAUDE.md for a step: phases/{phase}/{step}/CLAUDE.md."""
    path = dom_root / "phases" / phase / step / "CLAUDE.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def write_agent_claude_md(
    dom_root: Path, phase: str, step: str, role: str, content: str
) -> Path:
    """Write CLAUDE.md for a specific agent: phases/{phase}/{step}/agents/{role}/CLAUDE.md."""
    path = dom_root / "phases" / phase / step / "agents" / role / "CLAUDE.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def write_phase_claude_md(dom_root: Path, phase: str, content: str) -> Path:
    """Write CLAUDE.md for a phase: phases/{phase}/CLAUDE.md."""
    path = dom_root / "phases" / phase / "CLAUDE.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def write_task_claude_md(
    dom_root: Path, phase: str, task_id: str, content: str
) -> Path:
    """Write CLAUDE.md for a task: phases/{phase}/tasks/{task_id}/CLAUDE.md."""
    path = dom_root / "phases" / phase / "tasks" / task_id / "CLAUDE.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# Scanning utilities
# ---------------------------------------------------------------------------


def scan_step_statuses(dom_root: Path, phase: str, pipeline: list[str]) -> dict[str, str]:
    """Read status of all steps in a phase. Returns {step: status}."""
    result = {}
    for step in pipeline:
        status_path = dom_root / "phases" / phase / step / "status"
        result[step] = read_status(status_path)
    return result


def scan_task_statuses(dom_root: Path, phase: str) -> dict[str, str]:
    """Read status of all tasks in a phase. Returns {task_id: status}."""
    tasks_dir = dom_root / "phases" / phase / "tasks"
    if not tasks_dir.is_dir():
        return {}
    result = {}
    for task_dir in sorted(tasks_dir.iterdir()):
        if task_dir.is_dir():
            status_path = task_dir / "status"
            result[task_dir.name] = read_status(status_path)
    return result


def count_summary_roles(dom_root: Path, phase: str, step: str) -> list[str]:
    """Count role headers in a step's summary.md. Returns list of role names."""
    summary = read_summary(dom_root, phase, step)
    if not summary:
        return []
    roles = []
    for line in summary.splitlines():
        if line.startswith("## "):
            roles.append(line[3:].strip())
    return roles
