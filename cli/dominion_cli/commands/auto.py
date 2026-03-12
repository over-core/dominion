"""Autonomy mode commands."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Optional

import typer

from ..core.config import dominion_path, project_root
from ..core.formatters import error, info, output, status_line, table
from ..core.readers import read_toml, write_toml

app = typer.Typer(help="Auto mode management")

DECISION_TYPES = ("replan", "skip", "retry", "split", "reorder")


@app.command()
def readiness(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Pre-flight check for auto mode."""
    dom = read_toml(dominion_path("dominion.toml"))
    state = read_toml(dominion_path("state.toml"))

    autonomy = dom.get("autonomy", {})
    if not autonomy:
        info("No autonomy config. Run /dominion:init or add [autonomy] to dominion.toml.")
        raise SystemExit(1)

    checks: list[dict] = []

    # Circuit breakers configured
    breakers = autonomy.get("circuit_breakers", {})
    max_tokens = breakers.get("max_tokens_per_task", 0)
    max_retries = breakers.get("max_retries", 0)
    if max_tokens > 0:
        checks.append({
            "name": "Circuit breakers",
            "status": "pass",
            "detail": f"configured ({max_tokens}/task, {max_retries} retries)",
        })
    else:
        checks.append({
            "name": "Circuit breakers",
            "status": "fail",
            "detail": "max_tokens_per_task not configured",
        })

    # MCP availability
    mcps = dom.get("mcps", {})
    installed = list(mcps.keys()) if isinstance(mcps, dict) else []
    warnings: list[str] = []

    # Check settings.local.json for permissions
    settings_path = project_root() / ".claude" / "settings.local.json"
    if settings_path.exists():
        import json as json_mod

        try:
            with open(settings_path) as f:
                settings = json_mod.load(f)
        except Exception:
            settings = {}
    else:
        settings = {}

    perms = settings.get("permissions", {}).get("allow", []) if settings else []
    approved = sum(1 for p in perms if any(m in p for m in installed)) if installed else 0

    if installed:
        checks.append({
            "name": "Permissions",
            "status": "pass" if approved > 0 else "warn",
            "detail": f"{approved}/{len(installed)} read tools pre-approved",
        })
    else:
        checks.append({"name": "Permissions", "status": "pass", "detail": "No MCPs configured"})

    # Overall readiness
    critical_fail = any(c["status"] == "fail" for c in checks)
    ready = "NO" if critical_fail else "YES"

    if json:
        output({
            "ready": ready == "YES",
            "checks": checks,
            "max_tokens_per_task": max_tokens,
            "max_retries": max_retries,
        }, json_mode=True)
        return

    status_line(checks, False)
    info(f"\n  Ready for auto mode: {ready}")


@app.command()
def decisions(
    session: Annotated[Optional[str], typer.Option("--session", help="Filter by session ID")] = None,
    phase: Annotated[Optional[int], typer.Option("--phase", help="Filter by phase number")] = None,
    reviewed: Annotated[Optional[str], typer.Option("--reviewed", help="Filter by review status")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List autonomous decisions from auto mode sessions."""
    state = read_toml(dominion_path("state.toml"))
    items = state.get("autonomous_decisions", [])

    if session:
        if session == "last" and items:
            last_session = items[-1].get("session_id")
            items = [d for d in items if d.get("session_id") == last_session]
        else:
            items = [d for d in items if d.get("session_id") == session]

    if phase is not None:
        items = [d for d in items if d.get("phase") == phase]

    if reviewed is not None:
        reviewed_bool = reviewed.lower() in ("true", "yes", "1")
        items = [d for d in items if d.get("reviewed") == reviewed_bool]

    if not items:
        info("No autonomous decisions recorded.")
        return

    columns = ["ID", "Phase", "Task", "Type", "Description", "Reviewed", "Outcome"]
    rows = []
    for d in items:
        rows.append([
            f"AD{d.get('id', '?')}",
            d.get("phase", ""),
            d.get("task", ""),
            d.get("type", ""),
            d.get("description", ""),
            "yes" if d.get("reviewed") else "no",
            d.get("outcome", ""),
        ])
    table("Autonomous Decisions", columns, rows, json)


@app.command()
def start() -> None:
    """Enter auto mode for the current session."""
    path = dominion_path("dominion.toml")
    dom = read_toml(path)
    dom.setdefault("autonomy", {})["mode"] = "auto"
    write_toml(path, dom)
    info("Auto mode enabled. Will revert on session end or auto stop.")


@app.command()
def stop() -> None:
    """Exit auto mode and return to interactive."""
    path = dominion_path("dominion.toml")
    dom = read_toml(path)
    dom.setdefault("autonomy", {})["mode"] = "interactive"
    write_toml(path, dom)
    info("Auto mode disabled. Returning to interactive mode.")


@app.command()
def log(
    task_id: Annotated[str, typer.Option("--task", help="Task ID")],
    decision_type: Annotated[str, typer.Option("--type", help="Decision type")],
    description: Annotated[str, typer.Option("--description", help="What was decided")],
    reason: Annotated[str, typer.Option("--reason", help="Why")],
) -> None:
    """Record an autonomous decision made without human input."""
    if decision_type not in DECISION_TYPES:
        error(f"Invalid type '{decision_type}'. Must be one of: {', '.join(DECISION_TYPES)}")
        raise SystemExit(1)

    path = dominion_path("state.toml")
    state = read_toml(path)

    existing = state.get("autonomous_decisions", [])
    max_id = max((d.get("id", 0) for d in existing), default=0)
    new_id = max_id + 1

    entry = {
        "id": new_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": state.get("position", {}).get("phase", 0),
        "task": task_id,
        "type": decision_type,
        "description": description,
        "reason": reason,
        "session_id": state.get("lock", {}).get("session_id", "unknown"),
        "reviewed": False,
        "outcome": "",
    }

    existing.append(entry)
    state["autonomous_decisions"] = existing
    write_toml(path, state)
    info(f"Autonomous decision AD{new_id} logged: {decision_type} for task {task_id}.")
