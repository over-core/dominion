"""Style convention checking."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from ..core.config import dominion_path
from ..core.formatters import info, output
from ..core.readers import read_toml, read_toml_optional

app = typer.Typer(help="Code style conventions")


@app.command()
def check(
    files: Annotated[Optional[str], typer.Option("--files", help="Specific files to check")] = None,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Check code against style.toml conventions."""
    style_path = dominion_path("style.toml")
    style = read_toml_optional(style_path)

    if not style:
        info("No style.toml found.")
        return

    conventions = style.get("conventions", [])
    if not conventions:
        info("No conventions defined in style.toml.")
        return

    results: list[dict] = []
    for conv in conventions:
        name = conv.get("name", "unnamed")
        # Style check is primarily a report for the agent to act on
        results.append({
            "convention": name,
            "description": conv.get("description", ""),
            "pattern": conv.get("pattern", ""),
            "status": "pending",
        })

    if json:
        output({"conventions": results, "status": "pending"}, json_mode=True)
        return

    info("Style Conventions:")
    for r in results:
        info(f"  {r['convention']}: {r['description']}")
        if r["pattern"]:
            info(f"    Pattern: {r['pattern']}")
    info("")
    info("Note: Full style checking requires Grep/Glob operations performed by the agent.")
