"""Output formatting: Rich for humans, JSON for agents."""

from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
err_console = Console(stderr=True)


def output(data: dict[str, Any], json_mode: bool) -> None:
    """Output a dict as JSON or as Rich key-value pairs."""
    if json_mode:
        _print_json(data)
        return
    for key, value in data.items():
        if key.startswith("_"):
            continue
        label = key.replace("_", " ").title()
        console.print(f"  [bold]{label}:[/bold] {value}")


def table(
    title: str,
    columns: list[str],
    rows: list[list[Any]],
    json_mode: bool,
) -> None:
    """Render a table as Rich or JSON array of objects."""
    if json_mode:
        keys = [c.lower().replace(" ", "_") for c in columns]
        json_rows = []
        for row in rows:
            json_rows.append(dict(zip(keys, row)))
        _print_json(json_rows)
        return

    t = Table(title=title, show_lines=False)
    for col in columns:
        t.add_column(col)
    for row in rows:
        t.add_row(*[str(cell) for cell in row])
    console.print(t)


def panel(title: str, content: str, json_mode: bool) -> None:
    """Render a panel as Rich or JSON object."""
    if json_mode:
        _print_json({"title": title, "content": content})
        return
    console.print(Panel(content, title=title))


def status_line(checks: list[dict[str, Any]], json_mode: bool) -> None:
    """Format pass/fail/warn check results.

    Each check: {"name": str, "status": "pass"|"warn"|"fail", "detail": str}
    """
    if json_mode:
        passed = sum(1 for c in checks if c["status"] == "pass")
        warnings = sum(1 for c in checks if c["status"] == "warn")
        failed = sum(1 for c in checks if c["status"] == "fail")
        _print_json({
            "checks": checks,
            "summary": {"passed": passed, "warnings": warnings, "failed": failed},
        })
        return

    passed = 0
    warnings = 0
    failed = 0
    for check in checks:
        status = check["status"]
        name = check["name"]
        detail = check.get("detail", "")
        if status == "pass":
            icon = "[green][PASS][/green]"
            passed += 1
        elif status == "warn":
            icon = "[yellow][WARN][/yellow]"
            warnings += 1
        else:
            icon = "[red][FAIL][/red]"
            failed += 1
        detail_str = f" {detail}" if detail else ""
        console.print(f"  {icon} {name}{detail_str}")

    console.print()
    console.print(f"  {passed} passed, {warnings} warnings, {failed} failed")


def success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]{message}[/green]")


def error(message: str) -> None:
    """Print an error message to stderr."""
    err_console.print(f"[red]Error:[/red] {message}")


def info(message: str) -> None:
    """Print an informational message."""
    console.print(message)


def _print_json(data: Any) -> None:
    """Print JSON to stdout."""
    json.dump(data, sys.stdout, indent=2, default=str)
    print()
