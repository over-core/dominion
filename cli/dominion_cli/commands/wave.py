"""Wave tracking commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ..core.config import current_phase, dominion_path, phase_path
from ..core.formatters import error, info, output, table
from ..core.readers import read_toml, read_toml_optional, write_toml

app = typer.Typer(help="Wave tracking and management")


@app.command()
def create(
    number: Annotated[int, typer.Argument(help="Wave number")],
) -> None:
    """Create wave tracking entry in progress.toml."""
    p = current_phase()
    pp = phase_path(p)
    progress_path = pp / "progress.toml"
    plan_path = pp / "plan.toml"

    progress = read_toml_optional(progress_path) or {"waves": []}
    plan = read_toml_optional(plan_path)

    # Get tasks for this wave from plan
    wave_tasks = []
    if plan:
        for t in plan.get("tasks", []):
            if t.get("wave") == number:
                wave_tasks.append({"id": t.get("id", ""), "status": "pending"})

    wave_entry = {
        "number": number,
        "status": "pending",
        "tasks": wave_tasks,
    }

    if "waves" not in progress:
        progress["waves"] = []
    progress["waves"].append(wave_entry)
    write_toml(progress_path, progress)

    info(f"Wave {number} created with {len(wave_tasks)} tasks.")


@app.command(name="status")
def wave_status(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Current wave overview."""
    state = read_toml(dominion_path("state.toml"))
    pos = state.get("position", {})
    wave_num = pos.get("wave", 0)
    phase_num = pos.get("phase", 0)

    if phase_num == 0:
        info("No active phase.")
        return

    pp = phase_path(phase_num)
    progress = read_toml_optional(pp / "progress.toml")
    plan = read_toml_optional(pp / "plan.toml")

    if not progress:
        info("No progress.toml found.")
        return

    # Find current wave
    wave_data = None
    for w in progress.get("waves", []):
        if w.get("number") == wave_num:
            wave_data = w
            break

    if not wave_data:
        info(f"Wave {wave_num} not found in progress.")
        return

    tasks = wave_data.get("tasks", [])
    plan_tasks = {t["id"]: t for t in plan.get("tasks", [])} if plan else {}

    if json:
        task_list = []
        for t in tasks:
            tid = t.get("id", "")
            pt = plan_tasks.get(tid, {})
            task_list.append({
                "id": tid,
                "status": t.get("status", "pending"),
                "title": pt.get("title", ""),
            })
        output({"wave": wave_num, "status": wave_data.get("status", ""), "tasks": task_list}, json_mode=True)
        return

    info(f"Wave {wave_num}: {wave_data.get('status', 'unknown')}")
    info("  Tasks:")
    for t in tasks:
        tid = t.get("id", "")
        status = t.get("status", "pending")
        title = plan_tasks.get(tid, {}).get("title", "")
        info(f"    {tid}  [{status}]  {title}")


@app.command()
def merge() -> None:
    """Trigger wave merge protocol."""
    p = current_phase()
    pp = phase_path(p)
    progress_path = pp / "progress.toml"
    progress = read_toml(progress_path)

    state = read_toml(dominion_path("state.toml"))
    wave_num = state.get("position", {}).get("wave", 0)

    wave_data = None
    for w in progress.get("waves", []):
        if w.get("number") == wave_num:
            wave_data = w
            break

    if not wave_data:
        error(f"Wave {wave_num} not found.")
        raise SystemExit(1)

    tasks = wave_data.get("tasks", [])
    complete = [t for t in tasks if t.get("status") == "complete"]
    incomplete = [t for t in tasks if t.get("status") != "complete"]

    if incomplete:
        error(f"Cannot merge: {len(incomplete)} tasks not complete.")
        for t in incomplete:
            info(f"  {t.get('id', '?')}: {t.get('status', 'unknown')}")
        raise SystemExit(1)

    # Mark wave as merged
    wave_data["status"] = "merged"

    write_toml(progress_path, progress)
    info(f"Wave {wave_num} merged ({len(complete)} tasks).")
    info("Note: Git merge operations should be performed by the agent.")
