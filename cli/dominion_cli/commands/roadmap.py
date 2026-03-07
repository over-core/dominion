"""Roadmap display commands."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from ..core.config import dominion_path
from ..core.formatters import info, output, table
from ..core.readers import read_toml, read_toml_optional

app = typer.Typer(help="Roadmap overview")


@app.command()
def show(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Display roadmap summary."""
    roadmap_path = dominion_path("roadmap.toml")
    roadmap = read_toml_optional(roadmap_path)

    if not roadmap:
        info("No roadmap.toml found.")
        return

    state = read_toml_optional(dominion_path("state.toml")) or {}
    current = state.get("position", {}).get("phase", 0)

    project_name = roadmap.get("project", {}).get("name", "")
    phases = roadmap.get("phases", [])

    columns = ["Phase", "Title", "Status"]
    rows = []
    for p in phases:
        num = p.get("number", 0)
        title = p.get("title", "")
        if num < current:
            status = "complete"
        elif num == current:
            status = "in-progress"
        else:
            status = "upcoming"
        rows.append([num, title, status])

    if json:
        output({
            "project": project_name,
            "total_phases": len(phases),
            "current_phase": current,
            "phases": [{"number": r[0], "title": r[1], "status": r[2]} for r in rows],
        }, json_mode=True)
        return

    if project_name:
        info(f"Roadmap: {project_name}")
    info(f"  Phases: {len(phases)}, Current: {current}")
    table("Phases", columns, rows, False)


@app.command()
def phases(
    phase: Annotated[Optional[int], typer.Option("--phase", help="Show details for a specific phase")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List phases with objectives and status."""
    roadmap = read_toml(dominion_path("roadmap.toml"))
    state = read_toml_optional(dominion_path("state.toml")) or {}
    current = state.get("position", {}).get("phase", 0)

    items = roadmap.get("phases", [])
    if phase is not None:
        items = [p for p in items if p.get("number") == phase]

    if not items:
        info("No phases found.")
        return

    if json:
        phase_data = []
        for p in items:
            num = p.get("number", 0)
            status = "complete" if num < current else ("in-progress" if num == current else "upcoming")
            phase_data.append({
                "number": num,
                "title": p.get("title", ""),
                "objectives": p.get("objectives", []),
                "success_criteria": p.get("success_criteria", []),
                "status": status,
            })
        output({"phases": phase_data}, json_mode=True)
        return

    for p in items:
        num = p.get("number", 0)
        title = p.get("title", "")
        status = "complete" if num < current else ("in-progress" if num == current else "upcoming")
        info(f"Phase {num}: {title}")
        objectives = p.get("objectives", [])
        if objectives:
            info("  Objectives:")
            for o in objectives:
                info(f"    - {o}")
        criteria = p.get("success_criteria", [])
        if criteria:
            info("  Success Criteria:")
            for c in criteria:
                info(f"    - {c}")
        info(f"  Status: {status}")
        info("")
