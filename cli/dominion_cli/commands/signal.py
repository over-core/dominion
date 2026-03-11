"""Signal management commands (blockers and warnings)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Optional

import typer

from ..core.config import dominion_path
from ..core.formatters import error, info, output, table
from ..core.readers import read_toml, read_toml_glob, write_toml

app = typer.Typer(help="Signal management (blockers and warnings)")

BLOCKER_LEVELS = ("task", "wave", "phase", "critical")


@app.command()
def blocker(
    level: Annotated[str, typer.Option("--level", help="Blocker level: task | wave | phase | critical")],
    task_id: Annotated[str, typer.Option("--task", help="Task id that raised the blocker")],
    reason: Annotated[str, typer.Option("--reason", help="Human-readable reason")],
) -> None:
    """Raise a blocker signal."""
    if level not in BLOCKER_LEVELS:
        error(f"Invalid level '{level}'. Must be one of: {', '.join(BLOCKER_LEVELS)}")
        raise SystemExit(1)

    now = datetime.now(timezone.utc).isoformat()
    signal_data = {
        "type": "blocker",
        "level": level,
        "task": task_id,
        "reason": reason,
        "raised_at": now,
    }

    signals_dir = dominion_path("signals")
    signals_dir.mkdir(parents=True, exist_ok=True)
    signal_path = signals_dir / f"blocker-{task_id}.toml"
    write_toml(signal_path, signal_data)

    # Update state.toml
    state_path = dominion_path("state.toml")
    state = read_toml(state_path)
    state["blocker"] = {"task": task_id, "level": level, "reason": reason}
    if level in ("wave", "phase", "critical"):
        state.setdefault("position", {})["status"] = "blocked"
    write_toml(state_path, state)

    info(f"Blocker raised: {task_id} ({level}) — {reason}")


@app.command()
def warning(
    task_id: Annotated[str, typer.Option("--task", help="Task id raising the warning")],
    message: Annotated[str, typer.Option("--message", help="Warning message")],
) -> None:
    """Raise a warning signal (FYI, no halt)."""
    now = datetime.now(timezone.utc).isoformat()

    signals_dir = dominion_path("signals")
    signals_dir.mkdir(parents=True, exist_ok=True)

    # Find next sequence number for this task
    existing = list(signals_dir.glob(f"warning-{task_id}-*.toml"))
    seq = len(existing) + 1

    signal_data = {
        "type": "warning",
        "task": task_id,
        "message": message,
        "raised_at": now,
    }

    signal_path = signals_dir / f"warning-{task_id}-{seq}.toml"
    write_toml(signal_path, signal_data)

    info(f"Warning raised: {task_id} — {message}")


@app.command(name="list")
def list_signals(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
    affecting: Annotated[Optional[str], typer.Option("--affecting", help="Filter by task id")] = None,
) -> None:
    """List current signals."""
    signals = read_toml_glob(dominion_path("signals"))

    if affecting:
        signals = [s for s in signals if s.get("task") == affecting]

    if not signals:
        info("No active signals.")
        return

    columns = ["Type", "Task", "Level", "Message/Reason"]
    rows = []
    for s in signals:
        sig_type = s.get("type", "")
        task_id = s.get("task", "")
        level = s.get("level", "—")
        msg = s.get("reason", s.get("message", ""))
        rows.append([sig_type, task_id, level, msg])

    table("Active Signals", columns, rows, json)


@app.command()
def resolve(
    signal_file: Annotated[str, typer.Argument(help="Signal file name or task id")],
) -> None:
    """Resolve and remove a signal."""
    signals_dir = dominion_path("signals")

    # Find matching signal file(s)
    if signal_file.endswith(".toml"):
        target = signals_dir / signal_file
        targets = [target] if target.exists() else []
    else:
        # Match by task id
        targets = list(signals_dir.glob(f"*-{signal_file}*.toml"))

    if not targets:
        error(f"No signal found matching '{signal_file}'.")
        raise SystemExit(1)

    was_blocker = False
    for target in targets:
        data = read_toml(target)
        if data.get("type") == "blocker":
            was_blocker = True
        target.unlink()
        info(f"Removed {target.name}")

    # If a blocker was resolved, update state.toml
    if was_blocker:
        state_path = dominion_path("state.toml")
        state = read_toml(state_path)
        if "blocker" in state:
            del state["blocker"]
        state.setdefault("position", {})["status"] = "active"
        write_toml(state_path, state)
        info("Blocker cleared. Status set to active.")
