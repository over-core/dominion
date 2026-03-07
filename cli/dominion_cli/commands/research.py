"""Research findings and opportunities commands."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from ..core.config import current_phase, phase_path
from ..core.formatters import info, output, table
from ..core.readers import read_toml

app = typer.Typer(help="Research findings and analysis")


def _research_toml(phase: int | None = None) -> dict:
    """Read research.toml for the current or specified phase."""
    p = phase if phase is not None else current_phase()
    return read_toml(phase_path(p) / "research.toml")


@app.command()
def findings(
    severity: Annotated[Optional[str], typer.Option("--severity", help="Filter: high | medium | low")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Filter research findings by severity."""
    research = _research_toml()
    items = research.get("findings", [])

    if severity:
        items = [f for f in items if f.get("severity") == severity]

    if not items:
        info("No findings found.")
        return

    columns = ["ID", "Severity", "Category", "Title"]
    rows = []
    for f in items:
        rows.append([
            f.get("id", ""),
            f.get("severity", ""),
            f.get("category", ""),
            f.get("title", ""),
        ])
    table("Research Findings", columns, rows, json)


@app.command()
def finding(
    id: Annotated[str, typer.Argument(help="Finding id (e.g., F1)")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show single finding detail."""
    research = _research_toml()
    items = research.get("findings", [])

    match = next((f for f in items if f.get("id") == id), None)
    if match is None:
        info(f"Finding {id} not found.")
        raise SystemExit(1)

    data = {
        "id": match.get("id"),
        "title": match.get("title", ""),
        "severity": match.get("severity", ""),
        "category": match.get("category", ""),
        "description": match.get("description", ""),
        "evidence": match.get("evidence", []),
        "recommendation": match.get("recommendation", ""),
    }

    if json:
        output(data, json_mode=True)
        return

    info(f"{data['id']}: {data['title']}")
    info(f"  Severity: {data['severity']} | Category: {data['category']}")
    if data["description"]:
        info(f"  Description: {data['description']}")
    if data["evidence"]:
        info("  Evidence:")
        for e in data["evidence"]:
            info(f"    - {e}")
    if data["recommendation"]:
        info(f"  Recommendation: {data['recommendation']}")


@app.command()
def opportunities(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List opportunities from research."""
    research = _research_toml()
    items = research.get("opportunities", [])

    if not items:
        info("No opportunities found.")
        return

    columns = ["ID", "Title", "Benefit", "Effort"]
    rows = []
    for o in items:
        rows.append([
            o.get("id", ""),
            o.get("title", ""),
            o.get("benefit", ""),
            o.get("effort", ""),
        ])
    table("Opportunities", columns, rows, json)


@app.command(name="summary")
def research_summary(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Auto-generated research overview."""
    research = _research_toml()
    findings_list = research.get("findings", [])
    opps = research.get("opportunities", [])
    assumptions = research.get("assumptions", [])

    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for f in findings_list:
        sev = f.get("severity", "low")
        if sev in severity_counts:
            severity_counts[sev] += 1

    verified = sum(1 for a in assumptions if a.get("status") == "verified")
    unverified = sum(1 for a in assumptions if a.get("status") == "unverified")
    false_count = sum(1 for a in assumptions if a.get("status") == "false")

    phase = current_phase()
    data = {
        "phase": phase,
        "findings_high": severity_counts["high"],
        "findings_medium": severity_counts["medium"],
        "findings_low": severity_counts["low"],
        "opportunities": len(opps),
        "assumptions_verified": verified,
        "assumptions_unverified": unverified,
        "assumptions_false": false_count,
    }

    if json:
        output(data, json_mode=True)
        return

    info(f"Research Summary (Phase {phase}):")
    info(f"  Findings: {severity_counts['high']} high, {severity_counts['medium']} medium, {severity_counts['low']} low")
    info(f"  Opportunities: {len(opps)}")
    info(f"  Assumptions: {verified} verified, {unverified} unverified, {false_count} false")
