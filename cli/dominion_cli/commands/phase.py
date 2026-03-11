"""Phase lifecycle commands."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from ..core.config import current_phase, dominion_path, phase_path
from ..core.formatters import error, info, output, table
from ..core.readers import read_toml, read_toml_optional, write_toml

app = typer.Typer(help="Phase lifecycle management")


@app.command()
def init(
    number: Annotated[int, typer.Argument(help="Phase number")],
    title: Annotated[str, typer.Option("--title", help="Phase title")],
) -> None:
    """Create phase directory structure."""
    p = phase_path(number)
    p.mkdir(parents=True, exist_ok=True)
    (p / "summaries").mkdir(parents=True, exist_ok=True)

    # Update state.toml
    state_path = dominion_path("state.toml")
    state = read_toml(state_path)
    state.setdefault("position", {})
    state["position"]["phase"] = number
    state["position"]["step"] = "idle"
    state["position"]["status"] = "ready"
    write_toml(state_path, state)

    info(f"Phase {number} ({title}) initialized at {p}")


@app.command()
def status(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Current phase overview."""
    state = read_toml(dominion_path("state.toml"))
    pos = state.get("position", {})
    phase_num = pos.get("phase", 0)

    if phase_num == 0:
        info("No active phase.")
        return

    p = phase_path(phase_num)
    artifacts = {
        "research.toml": (p / "research.toml").exists(),
        "plan.toml": (p / "plan.toml").exists(),
        "progress.toml": (p / "progress.toml").exists(),
        "test-report.toml": (p / "test-report.toml").exists(),
        "review.toml": (p / "review.toml").exists(),
        "metrics.toml": (p / "metrics.toml").exists(),
    }

    data = {
        "phase": phase_num,
        "step": pos.get("step", "idle"),
        "status": pos.get("status", "ready"),
        "artifacts": {k: "exists" if v else "missing" for k, v in artifacts.items()},
    }

    if json:
        output(data, json_mode=True)
        return

    info(f"Phase {phase_num}")
    info(f"  Step: {data['step']} | Status: {data['status']}")
    info("  Artifacts:")
    for name, exists in artifacts.items():
        icon = "[green]exists[/green]" if exists else "[dim]missing[/dim]"
        info(f"    {name} [{icon}]")


@app.command()
def progress(
    number: Annotated[int, typer.Argument(help="Phase number")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Detailed progress for a phase."""
    p = phase_path(number)
    progress_data = read_toml_optional(p / "progress.toml")
    plan_data = read_toml_optional(p / "plan.toml")

    if not progress_data:
        info(f"No progress.toml for phase {number}.")
        return

    waves = progress_data.get("waves", [])
    plan_tasks = plan_data.get("tasks", []) if plan_data else []

    wave_info = []
    for w in waves:
        w_num = w.get("number", 0)
        w_status = w.get("status", "pending")
        w_tasks = w.get("tasks", [])
        complete = sum(1 for t in w_tasks if t.get("status") == "complete")
        total = len(w_tasks)
        blocked = [t.get("id", "?") for t in w_tasks if t.get("status") == "blocked"]

        wave_info.append({
            "number": w_num,
            "status": w_status,
            "tasks_complete": complete,
            "tasks_total": total,
            "blocked": blocked,
        })

    if json:
        output({"phase": number, "waves": wave_info}, json_mode=True)
        return

    info(f"Phase {number} Progress:")
    for w in wave_info:
        blocked_str = ""
        if w["blocked"]:
            blocked_str = f", {len(w['blocked'])} blocked"
        info(f"  Wave {w['number']}: {w['status']} ({w['tasks_complete']}/{w['tasks_total']} tasks{blocked_str})")
        for b in w["blocked"]:
            info(f"    Blocked: {b}")
