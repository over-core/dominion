"""Improvement proposal management commands."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from ..core.config import dominion_path
from ..core.formatters import error, info, output, table
from ..core.readers import read_toml, write_toml

app = typer.Typer(help="Improvement proposal management")

VALID_STATUSES = ("pending", "accepted", "rejected", "rolled-back")
VALID_APPLIED_BY = ("direct", "pipeline", "structural")


@app.command(name="list")
def list_improvements(
    status_filter: Annotated[Optional[str], typer.Option("--status", help="Filter by status")] = None,
    phase: Annotated[Optional[int], typer.Option("--phase", help="Filter by phase")] = None,
    type_filter: Annotated[Optional[str], typer.Option("--type", help="Filter by type")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List improvement proposals from improvements.toml."""
    improvements = read_toml(dominion_path("improvements.toml"))
    items = improvements.get("proposals", [])

    if status_filter:
        items = [i for i in items if i.get("status") == status_filter]
    if phase is not None:
        items = [i for i in items if i.get("phase") == phase]
    if type_filter:
        items = [i for i in items if i.get("type") == type_filter]

    # Sort by phase (newest first), then by ID
    items.sort(key=lambda x: (-x.get("phase", 0), x.get("id", "")))

    if not items:
        info("No improvement proposals found.")
        return

    columns = ["ID", "Phase", "Type", "Title", "Status"]
    rows = []
    for i in items:
        rows.append([
            i.get("id", ""),
            i.get("phase", ""),
            i.get("type", ""),
            i.get("title", ""),
            i.get("status", ""),
        ])
    table("Improvement Proposals", columns, rows, json)


@app.command()
def show(
    id: Annotated[str, typer.Argument(help="Proposal ID (e.g., P1)")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show details of a single improvement proposal."""
    improvements = read_toml(dominion_path("improvements.toml"))
    items = improvements.get("proposals", [])

    match = next((i for i in items if i.get("id") == id), None)
    if not match:
        info(f"Proposal {id} not found.")
        raise SystemExit(1)

    data = {
        "id": match.get("id"),
        "phase": match.get("phase", ""),
        "type": match.get("type", ""),
        "title": match.get("title", ""),
        "evidence": match.get("evidence", []),
        "reason": match.get("reason", ""),
        "status": match.get("status", ""),
        "applied_at": match.get("applied_at", ""),
        "applied_by": match.get("applied_by", ""),
    }

    if json:
        output(data, json_mode=True)
        return

    info(f"Proposal {data['id']}: {data['title']}")
    info(f"  Phase: {data['phase']} | Type: {data['type']} | Status: {data['status']}")
    if data["reason"]:
        info(f"  Reason: {data['reason']}")
    if data["evidence"]:
        info("  Evidence:")
        for e in data["evidence"]:
            info(f"    - {e}")
    if data["applied_at"]:
        info(f"  Applied at: {data['applied_at']}")
    if data["applied_by"]:
        info(f"  Applied by: {data['applied_by']}")


@app.command(name="update")
def update_improvement(
    id: Annotated[str, typer.Argument(help="Proposal ID (e.g., P1)")],
    status: Annotated[Optional[str], typer.Option("--status", help="New status")] = None,
    applied_at: Annotated[Optional[str], typer.Option("--applied-at", help="Commit hash")] = None,
    applied_by: Annotated[Optional[str], typer.Option("--applied-by", help="Apply method")] = None,
) -> None:
    """Update a proposal's status and apply metadata."""
    if status and status not in VALID_STATUSES:
        error(f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}")
        raise SystemExit(1)
    if applied_by and applied_by not in VALID_APPLIED_BY:
        error(f"Invalid applied_by '{applied_by}'. Must be one of: {', '.join(VALID_APPLIED_BY)}")
        raise SystemExit(1)

    path = dominion_path("improvements.toml")
    improvements = read_toml(path)
    items = improvements.get("proposals", [])

    match = next((i for i in items if i.get("id") == id), None)
    if not match:
        info(f"Proposal {id} not found.")
        raise SystemExit(1)

    changed: list[str] = []
    if status:
        match["status"] = status
        changed.append(f"status={status}")
    if applied_at:
        match["applied_at"] = applied_at
        changed.append(f"applied_at={applied_at}")
    if applied_by:
        match["applied_by"] = applied_by
        changed.append(f"applied_by={applied_by}")

    if not changed:
        error("No fields to update. Use --status, --applied-at, or --applied-by.")
        raise SystemExit(1)

    write_toml(path, improvements)
    info(f"Proposal {id} updated: {', '.join(changed)}.")
