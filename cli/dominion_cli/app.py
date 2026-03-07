"""Main Typer application — assembles all command groups."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from . import __version__

from .commands import (
    agents,
    auto,
    backlog,
    data,
    doc,
    history,
    improve,
    knowledge,
    metrics,
    phase,
    plan,
    profile,
    release,
    report,
    research,
    roadmap,
    security,
    signal,
    state,
    style,
    validate,
    wave,
    zone,
)

def _version_callback(value: bool) -> None:
    if value:
        print(f"dominion-cli {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="dominion-cli",
    no_args_is_help=True,
)


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", help="Show version and exit.", callback=_version_callback, is_eager=True),
    ] = None,
) -> None:
    """Dominion AI development methodology CLI — data access layer for .dominion/ TOML files."""

# --- Command groups (two-word commands: "state resume", "plan task", etc.) ---
app.add_typer(state.app, name="state")
app.add_typer(plan.app, name="plan")
app.add_typer(agents.app, name="agents")
app.add_typer(signal.app, name="signal")
app.add_typer(validate.app, name="validate")
app.add_typer(knowledge.app, name="knowledge")
app.add_typer(phase.app, name="phase")
app.add_typer(wave.app, name="wave")
app.add_typer(research.app, name="research")
app.add_typer(report.app, name="report")
app.add_typer(backlog.app, name="backlog")
app.add_typer(metrics.app, name="metrics")
app.add_typer(auto.app, name="auto")
app.add_typer(zone.app, name="zone")
app.add_typer(profile.app, name="profile")
app.add_typer(release.app, name="release")
app.add_typer(doc.app, name="doc")
app.add_typer(roadmap.app, name="roadmap")
app.add_typer(style.app, name="style")
app.add_typer(security.app, name="security")
app.add_typer(improve.app, name="improve")
app.add_typer(data.app, name="data")

# --- "project" sub-group (project summary) ---
project_app = typer.Typer(help="Project overview")


@project_app.command(name="summary")
def project_summary_cmd(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """One-paragraph project overview."""
    knowledge.project_summary(json=json)


app.add_typer(project_app, name="project")

# --- "claim" sub-group (claim status) ---
claim_app = typer.Typer(help="Claim provenance")


@claim_app.command(name="status")
def claim_status_cmd(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show brownfield claim provenance for this project."""
    profile.claim_status(json=json)


app.add_typer(claim_app, name="claim")

# --- Top-level commands (single-word: "rollback", "history") ---


@app.command(name="rollback")
def rollback_cmd(
    to_wave: Annotated[Optional[int], typer.Option("--to-wave", help="Roll back to wave boundary")] = None,
    task: Annotated[Optional[str], typer.Option("--task", help="Revert single task")] = None,
    to_phase: Annotated[Optional[int], typer.Option("--to-phase", help="Roll back entire phase")] = None,
) -> None:
    """Roll back to a safe boundary."""
    history.rollback(to_wave=to_wave, task=task, to_phase=to_phase)


@app.command(name="history")
def history_cmd(
    phase_num: Annotated[int, typer.Option("--phase", help="Phase number")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show commit map for a phase."""
    history.show_history(phase=phase_num, json=json)


if __name__ == "__main__":
    app()
