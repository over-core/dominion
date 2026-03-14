"""Phase and wave progress tracking."""

from __future__ import annotations

from pathlib import Path

from .config import (
    current_phase,
    phase_path,
    read_toml,
    read_toml_optional,
    write_toml,
    write_toml_locked,
)


async def create_wave(dom_root: Path, wave_num: int, phase: int | None = None) -> dict:
    """Create wave tracking entry in progress.toml.

    Pre-populates tasks from plan.toml for this wave number.
    Returns the created wave entry dict.
    """
    if phase is None:
        phase = current_phase(dom_root)

    pp = phase_path(dom_root, phase)
    progress_path = pp / "progress.toml"
    plan_path = pp / "plan.toml"

    plan = read_toml_optional(plan_path)

    wave_tasks = []
    if plan:
        for t in plan.get("tasks", []):
            if t.get("wave") == wave_num:
                wave_tasks.append({"id": t.get("id", ""), "status": "pending"})

    wave_entry = {
        "number": wave_num,
        "status": "pending",
        "tasks": wave_tasks,
    }

    def updater(data: dict) -> dict:
        if "waves" not in data:
            data["waves"] = []
        data["waves"].append(wave_entry)
        return data

    await write_toml_locked(progress_path, updater)
    return wave_entry


def get_wave_status(dom_root: Path, phase: int | None = None) -> dict:
    """Get current wave overview including task statuses.

    Returns dict with wave number, status, and task list with plan details.
    """
    from .config import dominion_path

    state = read_toml(dominion_path(dom_root, "state.toml"))
    pos = state.get("position", {})
    wave_num = pos.get("wave", 0)
    phase_num = pos.get("phase", 0) if phase is None else phase

    if phase_num == 0:
        return {"wave": 0, "status": "no_active_phase", "tasks": []}

    pp = phase_path(dom_root, phase_num)
    progress = read_toml_optional(pp / "progress.toml")
    plan = read_toml_optional(pp / "plan.toml")

    if not progress:
        return {"wave": wave_num, "status": "no_progress", "tasks": []}

    wave_data = None
    for w in progress.get("waves", []):
        if w.get("number") == wave_num:
            wave_data = w
            break

    if not wave_data:
        return {"wave": wave_num, "status": "not_found", "tasks": []}

    plan_tasks = {t["id"]: t for t in plan.get("tasks", [])} if plan else {}
    task_list = []
    for t in wave_data.get("tasks", []):
        tid = t.get("id", "")
        pt = plan_tasks.get(tid, {})
        task_list.append({
            "id": tid,
            "status": t.get("status", "pending"),
            "title": pt.get("title", ""),
        })

    return {
        "wave": wave_num,
        "status": wave_data.get("status", "pending"),
        "tasks": task_list,
    }


def check_merge_ready(dom_root: Path, wave_num: int, phase: int | None = None) -> tuple[bool, list[str]]:
    """Check if a wave is ready to merge (all tasks complete).

    Returns (ready, list_of_incomplete_task_ids).
    """
    if phase is None:
        phase = current_phase(dom_root)

    pp = phase_path(dom_root, phase)
    progress = read_toml(pp / "progress.toml")

    wave_data = None
    for w in progress.get("waves", []):
        if w.get("number") == wave_num:
            wave_data = w
            break

    if not wave_data:
        raise ValueError(f"Wave {wave_num} not found in progress.toml")

    tasks = wave_data.get("tasks", [])
    incomplete = [t.get("id", "?") for t in tasks if t.get("status") != "complete"]
    return len(incomplete) == 0, incomplete


async def merge_wave(dom_root: Path, wave_num: int, phase: int | None = None) -> None:
    """Mark wave as merged after verifying all tasks are complete.

    Raises ValueError if incomplete tasks exist.
    """
    if phase is None:
        phase = current_phase(dom_root)

    ready, incomplete = check_merge_ready(dom_root, wave_num, phase)
    if not ready:
        raise ValueError(
            f"Cannot merge wave {wave_num}: {len(incomplete)} tasks not complete: {incomplete}"
        )

    pp = phase_path(dom_root, phase)
    progress_path = pp / "progress.toml"

    def updater(data: dict) -> dict:
        for w in data.get("waves", []):
            if w.get("number") == wave_num:
                w["status"] = "merged"
                break
        return data

    await write_toml_locked(progress_path, updater)


async def init_phase(dom_root: Path, number: int, title: str) -> None:
    """Create phase directory structure and update state."""
    from .config import dominion_path

    pp = phase_path(dom_root, number)
    pp.mkdir(parents=True, exist_ok=True)
    (pp / "summaries").mkdir(parents=True, exist_ok=True)

    state_path = dominion_path(dom_root, "state.toml")

    def updater(data: dict) -> dict:
        data.setdefault("position", {})
        data["position"]["phase"] = number
        data["position"]["step"] = "idle"
        data["position"]["status"] = "ready"
        return data

    await write_toml_locked(state_path, updater)


def get_phase_status(dom_root: Path, phase: int | None = None) -> dict:
    """Get phase overview with artifact inventory.

    Returns dict with phase number, step, status, and artifact presence.
    """
    from .config import dominion_path

    state = read_toml(dominion_path(dom_root, "state.toml"))
    pos = state.get("position", {})
    phase_num = pos.get("phase", 0) if phase is None else phase

    if phase_num == 0:
        return {"phase": 0, "step": "idle", "status": "ready", "artifacts": {}}

    pp = phase_path(dom_root, phase_num)
    artifact_names = [
        "research.toml", "plan.toml", "progress.toml",
        "test-report.toml", "review.toml", "metrics.toml",
    ]
    artifacts = {name: (pp / name).exists() for name in artifact_names}

    return {
        "phase": phase_num,
        "step": pos.get("step", "idle"),
        "status": pos.get("status", "ready"),
        "artifacts": {k: "exists" if v else "missing" for k, v in artifacts.items()},
    }


def get_phase_progress(dom_root: Path, phase: int) -> dict:
    """Detailed progress for a phase with wave-by-wave breakdown.

    Returns dict with phase number and wave info list.
    """
    pp = phase_path(dom_root, phase)
    progress_data = read_toml_optional(pp / "progress.toml")

    if not progress_data:
        return {"phase": phase, "waves": []}

    wave_info = []
    for w in progress_data.get("waves", []):
        w_tasks = w.get("tasks", [])
        complete = sum(1 for t in w_tasks if t.get("status") == "complete")
        blocked = [t.get("id", "?") for t in w_tasks if t.get("status") == "blocked"]

        wave_info.append({
            "number": w.get("number", 0),
            "status": w.get("status", "pending"),
            "tasks_complete": complete,
            "tasks_total": len(w_tasks),
            "blocked": blocked,
        })

    return {"phase": phase, "waves": wave_info}


async def update_task_progress(
    dom_root: Path, task_id: str, status: str, summary: str | None = None,
    phase: int | None = None,
) -> None:
    """Update a specific task's status in progress.toml.

    Finds the task across all waves and updates its status.
    Raises ValueError if task not found.
    """
    if phase is None:
        phase = current_phase(dom_root)

    pp = phase_path(dom_root, phase)
    progress_path = pp / "progress.toml"

    def updater(data: dict) -> dict:
        found = False
        for w in data.get("waves", []):
            for t in w.get("tasks", []):
                if t.get("id") == task_id:
                    t["status"] = status
                    if summary:
                        t["summary"] = summary
                    found = True
                    break
            if found:
                break
        if not found:
            raise ValueError(f"Task {task_id} not found in progress.toml")
        return data

    await write_toml_locked(progress_path, updater)
