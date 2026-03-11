"""Rollback and history commands — registered as top-level commands in app.py."""

from __future__ import annotations

from ..core.config import phase_path
from ..core.formatters import error, info, output
from ..core.readers import read_toml_optional


def rollback(
    to_wave: int | None = None,
    task: str | None = None,
    to_phase: int | None = None,
) -> None:
    """Roll back to a safe boundary."""
    provided = sum(1 for x in (to_wave, task, to_phase) if x is not None)
    if provided != 1:
        error("Exactly one of --to-wave, --task, or --to-phase must be provided.")
        raise SystemExit(1)

    if to_wave is not None:
        info(f"Rollback to wave {to_wave} boundary requested.")
        info("This will revert all commits after wave merge commit.")
        info("Note: Actual git revert operations must be performed by the agent.")
        info(f"Agent should run: git revert to wave {to_wave} merge commit")
    elif task is not None:
        info(f"Rollback of task {task} requested.")
        info("This will revert commits for the single task.")
        info(f"Agent should run: git revert for task {task} commits")
    elif to_phase is not None:
        info(f"Rollback to phase {to_phase} start requested.")
        info("This will revert to the commit at phase start.")
        info(f"Agent should run: git revert to phase {to_phase} start commit")


def show_history(
    phase: int,
    json: bool = False,
) -> None:
    """Show commit map for a phase."""
    pp = phase_path(phase)
    progress = read_toml_optional(pp / "progress.toml")

    if not progress:
        info(f"No progress.toml for phase {phase}.")
        return

    waves = progress.get("waves", [])
    if not waves:
        info(f"No waves recorded for phase {phase}.")
        return

    if json:
        wave_data = []
        for w in waves:
            wave_entry = {
                "number": w.get("number", 0),
                "status": w.get("status", ""),
                "merge_commit": w.get("merge_commit", ""),
                "tasks": [],
            }
            for t in w.get("tasks", []):
                wave_entry["tasks"].append({
                    "id": t.get("id", ""),
                    "commits": t.get("commits", []),
                })
            wave_data.append(wave_entry)
        output({"phase": phase, "waves": wave_data}, json_mode=True)
        return

    info(f"Phase {phase} History:")
    for w in waves:
        w_num = w.get("number", 0)
        w_status = w.get("status", "")
        merge = w.get("merge_commit", "")
        merge_str = f" (merged: {merge[:7]})" if merge else ""
        status_str = f" ({w_status})" if w_status != "merged" else ""
        info(f"  Wave {w_num}{merge_str}{status_str}")
        for t in w.get("tasks", []):
            tid = t.get("id", "")
            commits = t.get("commits", [])
            commit_str = ", ".join(c[:7] for c in commits) if commits else "no commits"
            info(f"    {tid}: {commit_str}")
