"""Report creation and finalization commands."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import typer

from ..core.config import phase_path
from ..core.formatters import error, info
from ..core.readers import read_toml, read_toml_optional, write_toml

app = typer.Typer(help="Report management")


@app.command()
def create(
    report_type: Annotated[str, typer.Argument(metavar="TYPE", help="Report type: test-report | review")],
    phase: Annotated[int, typer.Argument(help="Phase number")],
) -> None:
    """Create test-report or review artifact."""
    valid_types = ("test-report", "review")
    if report_type not in valid_types:
        error(f"Invalid type '{report_type}'. Must be one of: {', '.join(valid_types)}")
        raise SystemExit(1)

    pp = phase_path(phase)
    pp.mkdir(parents=True, exist_ok=True)

    report_path = pp / f"{report_type}.toml"
    plan = read_toml_optional(pp / "plan.toml")

    # Initialize report structure
    report: dict = {
        "meta": {
            "type": report_type,
            "phase": phase,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "finalized_at": "",
        },
    }

    # Pre-populate from plan tasks
    if plan:
        tasks = plan.get("tasks", [])
        if report_type == "test-report":
            report["results"] = []
            for t in tasks:
                report["results"].append({
                    "task_id": t.get("id", ""),
                    "status": "pending",
                    "tests_passed": 0,
                    "tests_failed": 0,
                    "notes": "",
                })
        elif report_type == "review":
            report["items"] = []
            for t in tasks:
                report["items"].append({
                    "task_id": t.get("id", ""),
                    "status": "pending",
                    "findings": [],
                    "notes": "",
                })

    write_toml(report_path, report)
    info(f"Created {report_type} for phase {phase} at {report_path}")


@app.command()
def finalize(
    file: Annotated[str, typer.Argument(help="Path to report TOML file")],
) -> None:
    """Finalize a report."""
    from pathlib import Path

    path = Path(file)
    report = read_toml(path)

    # Validate completeness (check for empty required fields in results/items)
    meta = report.get("meta", {})
    if meta.get("finalized_at"):
        error("Report is already finalized.")
        raise SystemExit(1)

    results = report.get("results", report.get("items", []))
    pending = [r for r in results if r.get("status") == "pending"]
    if pending:
        error(f"{len(pending)} items still pending. Complete all items before finalizing.")
        raise SystemExit(1)

    meta["finalized_at"] = datetime.now(timezone.utc).isoformat()
    report["meta"] = meta
    write_toml(path, report)
    info(f"Report finalized at {meta['finalized_at']}.")
