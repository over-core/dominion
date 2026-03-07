"""Pipeline state management commands."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Optional

import typer

from ..core.config import dominion_path
from ..core.formatters import error, info, output, table
from ..core.readers import read_toml, read_toml_glob, write_toml

app = typer.Typer(help="Pipeline state management")

VALID_STEPS = ("idle", "discuss", "explore", "plan", "execute", "test", "review", "improve")
VALID_STATUSES = ("ready", "active", "blocked", "complete")


@app.command()
def resume(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Display current position for session start."""
    state = read_toml(dominion_path("state.toml"))
    pos = state.get("position", {})
    data = {
        "phase": pos.get("phase", 0),
        "step": pos.get("step", "idle"),
        "status": pos.get("status", "ready"),
        "last_session": pos.get("last_session", "unknown"),
    }
    if data["phase"] == 0:
        data["message"] = "Dominion initialized. No active phase."
    else:
        data["message"] = f"Phase {data['phase']}, Step {data['step']}. Status: {data['status']}."
    output(data, json)


@app.command()
def position(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show current position in compact form."""
    state = read_toml(dominion_path("state.toml"))
    pos = state.get("position", {})
    data = {
        "phase": pos.get("phase", 0),
        "step": pos.get("step", "idle"),
        "wave": pos.get("wave", 0),
        "status": pos.get("status", "ready"),
    }
    if json:
        output(data, json)
        return
    info(
        f"Phase {data['phase']} | Step: {data['step']} "
        f"| Wave: {data['wave']} | Status: {data['status']}"
    )


@app.command()
def update(
    phase: Annotated[Optional[int], typer.Option("--phase", help="Set phase number")] = None,
    step: Annotated[Optional[str], typer.Option("--step", help="Set step")] = None,
    wave: Annotated[Optional[int], typer.Option("--wave", help="Set current wave number")] = None,
    status: Annotated[Optional[str], typer.Option("--status", help="Set status")] = None,
) -> None:
    """Update pipeline position."""
    if step is not None and step not in VALID_STEPS:
        error(f"Invalid step '{step}'. Must be one of: {', '.join(VALID_STEPS)}")
        raise SystemExit(1)
    if status is not None and status not in VALID_STATUSES:
        error(f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}")
        raise SystemExit(1)

    path = dominion_path("state.toml")
    state = read_toml(path)

    if "position" not in state:
        state["position"] = {}

    pos = state["position"]
    updated: list[str] = []
    if phase is not None:
        pos["phase"] = phase
        updated.append(f"phase={phase}")
    if step is not None:
        pos["step"] = step
        updated.append(f"step={step}")
    if wave is not None:
        pos["wave"] = wave
        updated.append(f"wave={wave}")
    if status is not None:
        pos["status"] = status
        updated.append(f"status={status}")

    if not updated:
        error("No fields provided. Use --phase, --step, --wave, or --status.")
        raise SystemExit(1)

    write_toml(path, state)
    info(f"State updated: {', '.join(updated)}")


@app.command()
def decisions(
    tags: Annotated[Optional[str], typer.Option("--tags", help="Filter by tag")] = None,
    phase: Annotated[Optional[int], typer.Option("--phase", help="Filter by phase number")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Search decisions log."""
    state = read_toml(dominion_path("state.toml"))
    items = state.get("decisions", [])

    if tags:
        tag_set = {t.strip() for t in tags.split(",")}
        items = [d for d in items if tag_set & set(d.get("tags", []))]
    if phase is not None:
        items = [d for d in items if d.get("phase") == phase]

    if not items:
        info("No decisions found.")
        return

    columns = ["ID", "Phase", "Task", "Agent", "Text", "Tags"]
    rows = []
    for d in items:
        rows.append([
            f"D{d.get('id', '?')}",
            d.get("phase", ""),
            d.get("task", ""),
            d.get("agent", ""),
            d.get("text", ""),
            ", ".join(d.get("tags", [])),
        ])
    table("Decisions", columns, rows, json)


@app.command()
def blockers(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List active blockers."""
    state = read_toml(dominion_path("state.toml"))
    blocker_data = state.get("blocker", {})
    signals = read_toml_glob(dominion_path("signals"), "blocker-*.toml")

    items: list[dict] = []
    if blocker_data and blocker_data.get("task"):
        items.append({
            "source": "state",
            "task": blocker_data.get("task", ""),
            "level": blocker_data.get("level", ""),
            "reason": blocker_data.get("reason", ""),
        })
    for sig in signals:
        items.append({
            "source": "signal",
            "task": sig.get("task", ""),
            "level": sig.get("level", ""),
            "reason": sig.get("reason", ""),
        })

    if not items:
        info("No active blockers.")
        return

    columns = ["Source", "Task", "Level", "Reason"]
    rows = [[i["source"], i["task"], i["level"], i["reason"]] for i in items]
    table("Active Blockers", columns, rows, json)


@app.command()
def checkpoint() -> None:
    """Checkpoint current session state on session end."""
    path = dominion_path("state.toml")
    state = read_toml(path)

    now = datetime.now(timezone.utc).isoformat()
    if "position" not in state:
        state["position"] = {}
    state["position"]["last_session"] = now

    # Clear lock if present
    if "lock" in state:
        del state["lock"]

    # Reset active status to ready if no work in progress
    if state["position"].get("status") == "active":
        state["position"]["status"] = "ready"

    write_toml(path, state)
    info(f"Session checkpointed at {now}.")


@app.command()
def decision(
    task: Annotated[str, typer.Option("--task", help="Task ID context")],
    text: Annotated[str, typer.Option("--text", help="Decision description")],
    tags: Annotated[Optional[str], typer.Option("--tags", help="Comma-separated tags")] = None,
) -> None:
    """Record a significant decision during task execution."""
    path = dominion_path("state.toml")
    state = read_toml(path)

    existing = state.get("decisions", [])
    max_id = max((d.get("id", 0) for d in existing), default=0)
    new_id = max_id + 1

    entry: dict = {
        "id": new_id,
        "phase": state.get("position", {}).get("phase", 0),
        "task": task,
        "agent": state.get("lock", {}).get("agent", "unknown"),
        "text": text,
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    existing.append(entry)
    state["decisions"] = existing
    write_toml(path, state)
    info(f"Decision D{new_id} recorded for task {task}.")


@app.command()
def defer(
    text: Annotated[str, typer.Option("--text", help="Description of the deferred item")],
) -> None:
    """Park an out-of-scope item for later discussion."""
    path = dominion_path("state.toml")
    state = read_toml(path)

    if "outstanding" not in state:
        state["outstanding"] = {}
    if "deferred" not in state["outstanding"]:
        state["outstanding"]["deferred"] = []

    state["outstanding"]["deferred"].append(text)
    write_toml(path, state)
    info(f"Deferred: {text}. Will surface in next /dominion:discuss.")


@app.command()
def deferred(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List deferred items from [outstanding]."""
    state = read_toml(dominion_path("state.toml"))
    items = state.get("outstanding", {}).get("deferred", [])

    if not items:
        info("No deferred items.")
        return

    if json:
        output({"deferred": items}, json)
        return

    info("Deferred items:")
    for i, item in enumerate(items, 1):
        info(f"  {i}. {item}")
