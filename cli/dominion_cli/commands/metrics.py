"""Metrics display and tracking commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ..core.config import dominion_path, phase_path
from ..core.formatters import error, info, output, table
from ..core.readers import read_toml, read_toml_optional, write_toml

app = typer.Typer(help="Metrics and measurement")


@app.command()
def show(
    phase: Annotated[int, typer.Option("--phase", help="Phase number")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Display metrics for a phase."""
    pp = phase_path(phase)
    metrics = read_toml(pp / "metrics.toml")

    quality = metrics.get("quality", {})
    process = metrics.get("process", {})

    data = {
        "phase": phase,
        "quality": {
            "tests_added": quality.get("tests_added", 0),
            "tests_passing": quality.get("tests_passing", 0),
            "linter_warnings": quality.get("linter_warnings", 0),
            "coverage_delta": quality.get("coverage_delta", ""),
            "review_findings_high": quality.get("review_findings_high", 0),
            "review_findings_medium": quality.get("review_findings_medium", 0),
            "review_findings_low": quality.get("review_findings_low", 0),
            "acceptance_passed": quality.get("acceptance_passed", 0),
            "acceptance_total": quality.get("acceptance_total", 0),
        },
        "process": {
            "tasks_completed": process.get("tasks_completed", 0),
            "tasks_failed": process.get("tasks_failed", 0),
            "tasks_replanned": process.get("tasks_replanned", 0),
            "waves": process.get("waves", 0),
            "blockers": process.get("blockers", 0),
            "rollbacks": process.get("rollbacks", 0),
            "avg_tokens_per_task": process.get("avg_tokens_per_task", 0),
            "improvement_proposals": process.get("improvement_proposals", 0),
        },
    }

    if json:
        output(data, json_mode=True)
        return

    q = data["quality"]
    p = data["process"]
    info(f"Metrics (Phase {phase}):")
    info("  Quality:")
    info(f"    Tests added: {q['tests_added']}, passing: {q['tests_passing']}, linter warnings: {q['linter_warnings']}")
    info(f"    Coverage delta: {q['coverage_delta']}")
    info(f"    Review findings: {q['review_findings_high']} high, {q['review_findings_medium']} medium, {q['review_findings_low']} low")
    info(f"    Acceptance: {q['acceptance_passed']}/{q['acceptance_total']} criteria passed")
    info("  Process:")
    info(f"    Tasks: {p['tasks_completed']} completed, {p['tasks_failed']} failed, {p['tasks_replanned']} replanned")
    info(f"    Waves: {p['waves']}, blockers: {p['blockers']}, rollbacks: {p['rollbacks']}")
    info(f"    Avg tokens/task: {p['avg_tokens_per_task']}")
    info(f"    Improvement proposals: {p['improvement_proposals']}")


@app.command()
def trends(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show metric trends across phases."""
    history_path = dominion_path("metrics-history.toml")
    history = read_toml(history_path)
    phases = history.get("phases", [])

    if not phases:
        info("No metrics history available.")
        return

    columns = ["Phase", "Tests", "Blocker Rate", "Tokens/Task", "High Findings", "Pass Rate", "Proposals"]
    rows = []
    prev = None

    for p in phases:
        phase_num = p.get("phase", "")
        tests = p.get("tests", 0)
        blocker_rate = p.get("blocker_rate", "")
        tokens = p.get("avg_tokens_per_task", 0)
        high = p.get("high_findings", 0)
        pass_rate = p.get("pass_rate", "")
        proposals = p.get("proposals", 0)

        # Compute deltas if previous phase exists
        def _delta(curr: int | float, prev_val: int | float | None) -> str:
            if prev_val is None:
                return str(curr)
            if prev_val == 0:
                return str(curr)
            change = ((curr - prev_val) / prev_val) * 100
            return f"{curr} ({change:+.0f}%)"

        if prev:
            tests_str = _delta(tests, prev.get("tests"))
            tokens_str = _delta(tokens, prev.get("avg_tokens_per_task"))
            high_str = _delta(high, prev.get("high_findings"))
        else:
            tests_str = str(tests)
            tokens_str = str(tokens)
            high_str = str(high)

        rows.append([phase_num, tests_str, blocker_rate, tokens_str, high_str, pass_rate, proposals])
        prev = p

    table("Metric Trends", columns, rows, json)


@app.command()
def baseline(
    phase: Annotated[int, typer.Option("--phase", help="Phase number")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Record recurring indicator measurements."""
    dom = read_toml(dominion_path("dominion.toml"))
    pp = phase_path(phase)
    pp.mkdir(parents=True, exist_ok=True)

    metrics_path = pp / "metrics.toml"
    metrics = read_toml_optional(metrics_path) or {}

    # Read previous phase metrics for comparison
    prev_path = phase_path(phase - 1) / "metrics.toml" if phase > 1 else None
    prev_metrics = read_toml_optional(prev_path) if prev_path else None
    prev_indicators = prev_metrics.get("indicators", {}) if prev_metrics else {}

    # Initialize indicators section
    indicators: dict = {
        "build_time_s": 0,
        "test_duration_s": 0,
        "test_count": 0,
        "dependency_count": 0,
    }

    # Compute deltas
    deltas: dict = {}
    for key in indicators:
        prev_val = prev_indicators.get(key, 0)
        if prev_val and prev_val != 0:
            delta = ((indicators[key] - prev_val) / prev_val) * 100
            deltas[key] = f"{delta:+.1f}%"
        else:
            deltas[key] = "—"

    metrics["indicators"] = indicators
    write_toml(metrics_path, metrics)

    data = {
        "phase": phase,
        "indicators": indicators,
        "deltas": deltas,
    }

    if json:
        output(data, json_mode=True)
        return

    info(f"Baseline (Phase {phase}):")
    info(f"  Build time:    {indicators['build_time_s']}s ({deltas.get('build_time_s', '—')} vs prev)")
    info(f"  Test duration: {indicators['test_duration_s']}s ({deltas.get('test_duration_s', '—')})")
    info(f"  Tests:         {indicators['test_count']} ({deltas.get('test_count', '—')})")
    info(f"  Dependencies:  {indicators['dependency_count']} ({deltas.get('dependency_count', '—')})")
    info("Note: Actual measurement requires running build/test commands from dominion.toml.")
