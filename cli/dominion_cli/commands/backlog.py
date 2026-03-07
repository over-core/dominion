"""Backlog management commands."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from ..core.config import current_phase, dominion_path
from ..core.formatters import error, info, output, table
from ..core.readers import read_toml, read_toml_optional, write_toml

app = typer.Typer(help="Backlog capture and management")


@app.command()
def add(
    text: Annotated[str, typer.Argument(help="Backlog item text")],
    tags: Annotated[Optional[str], typer.Option("--tags", help="Comma-separated tags")] = None,
) -> None:
    """Capture an idea during work."""
    path = dominion_path("backlog.toml")
    backlog = read_toml_optional(path) or {"items": []}

    items = backlog.get("items", [])
    max_id = max((i.get("id", 0) for i in items), default=0)
    new_id = max_id + 1

    entry = {
        "id": new_id,
        "text": text,
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
        "phase": current_phase(),
        "status": "open",
        "priority": "medium",
    }

    items.append(entry)
    backlog["items"] = items
    write_toml(path, backlog)
    info(f"Backlog item {new_id} added: {text}")


@app.command(name="list")
def list_backlog(
    status_filter: Annotated[Optional[str], typer.Option("--status", help="Filter by status")] = None,
    tags: Annotated[Optional[str], typer.Option("--tags", help="Filter by tag")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """View all backlog items."""
    path = dominion_path("backlog.toml")
    backlog = read_toml(path)
    items = backlog.get("items", [])

    if status_filter:
        items = [i for i in items if i.get("status") == status_filter]
    if tags:
        tag_set = {t.strip() for t in tags.split(",")}
        items = [i for i in items if tag_set & set(i.get("tags", []))]

    if not items:
        info("No backlog items found.")
        return

    columns = ["ID", "Phase", "Priority", "Tags", "Text"]
    rows = []
    for i in items:
        rows.append([
            i.get("id", ""),
            i.get("phase", ""),
            i.get("priority", ""),
            ", ".join(i.get("tags", [])),
            i.get("text", ""),
        ])
    table("Backlog", columns, rows, json)


@app.command()
def suggest(
    phase: Annotated[Optional[int], typer.Option("--phase", help="Target phase number")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Smart suggestions for planning."""
    path = dominion_path("backlog.toml")
    backlog = read_toml(path)
    items = backlog.get("items", [])

    # Filter to open items
    open_items = [i for i in items if i.get("status") == "open"]

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    open_items.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))

    if not open_items:
        info("No open backlog items to suggest.")
        return

    columns = ["ID", "Priority", "Tags", "Text"]
    rows = []
    for i in open_items[:10]:  # Top 10 suggestions
        rows.append([
            i.get("id", ""),
            i.get("priority", ""),
            ", ".join(i.get("tags", [])),
            i.get("text", ""),
        ])
    table("Suggested Items", columns, rows, json)
