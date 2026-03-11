"""Direction zone check command (circuit breaker)."""

from __future__ import annotations

from typing import Annotated

import typer

from ..core.config import dominion_path
from ..core.formatters import info, output
from ..core.readers import read_toml

app = typer.Typer(help="Direction zone management")


@app.command()
def check(
    path: Annotated[str, typer.Argument(help="File or directory path to check")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Check direction zone for a file path."""
    dom = read_toml(dominion_path("dominion.toml"))
    direction = dom.get("direction", {})
    mode = direction.get("mode", "")

    if not direction or mode != "restructure":
        data = {
            "zone": "none",
            "mode": mode or "not configured",
            "message": f"No direction constraints. Mode: {mode or 'not configured'}",
        }
        if json:
            output(data, json_mode=True)
        else:
            info(data["message"])
        return

    restructure = direction.get("restructure", {})
    legacy_zones = restructure.get("legacy_zones", [])
    target_state = restructure.get("target_state", "")
    migration_strategy = restructure.get("migration_strategy", "")

    if not legacy_zones:
        data = {
            "zone": "active",
            "mode": "restructure",
            "target_state": target_state,
            "message": f"Full restructure. Follow target state: {target_state}",
        }
        if json:
            output(data, json_mode=True)
        else:
            info(data["message"])
        return

    # Check if path falls under any legacy zone
    for zone in legacy_zones:
        zone_path = zone.get("path", "")
        if path.startswith(zone_path) or path == zone_path:
            policy = zone.get("policy", "minimal-changes")
            data = {
                "zone": "legacy",
                "mode": "restructure",
                "zone_path": zone_path,
                "policy": policy,
                "message": f"Legacy zone: {zone_path}. Policy: {policy}. Minimal changes only.",
            }
            if json:
                output(data, json_mode=True)
            else:
                info(data["message"])
            return

    # Active zone
    data = {
        "zone": "active",
        "mode": "restructure",
        "target_state": target_state,
        "migration_strategy": migration_strategy,
        "message": f"Active zone. Follow target state: {target_state}. Strategy: {migration_strategy}",
    }
    if json:
        output(data, json_mode=True)
    else:
        info(data["message"])
