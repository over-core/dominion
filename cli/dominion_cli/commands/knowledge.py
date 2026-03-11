"""Knowledge sync and search commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ..core.config import dominion_path
from ..core.formatters import error, info, output, table
from ..core.readers import read_toml, read_toml_optional

app = typer.Typer(help="Knowledge layer management")


@app.command()
def sync() -> None:
    """Sync project MEMORY.md from .dominion/knowledge/index.toml."""
    index_path = dominion_path("knowledge", "index.toml")
    index = read_toml(index_path)

    state = read_toml_optional(dominion_path("state.toml")) or {}
    dom = read_toml_optional(dominion_path("dominion.toml")) or {}

    entries = index.get("entries", [])
    hot_entries = [e for e in entries if e.get("hot", False)]
    hot_entries.sort(key=lambda e: e.get("priority", 999))

    lines: list[str] = []
    lines.append("# Project Knowledge (auto-generated)")
    lines.append("")

    # Current state
    pos = state.get("position", {})
    if pos:
        lines.append("## Current State")
        lines.append(f"- Phase: {pos.get('phase', 0)}")
        lines.append(f"- Step: {pos.get('step', 'idle')}")
        lines.append(f"- Status: {pos.get('status', 'ready')}")
        lines.append("")

    # Documentation chain
    doc = dom.get("documentation", {})
    if doc:
        lines.append("## Documentation Chain")
        for fb in doc.get("fallback", []):
            if isinstance(fb, dict):
                lines.append(f"- {fb.get('source', 'unknown')}: {fb.get('action', '')}")
        lines.append("")

    # Active (hot) knowledge
    if hot_entries:
        lines.append("## Active Knowledge")
        for e in hot_entries:
            lines.append(f"### {e.get('file', 'unknown')}")
            lines.append(f"{e.get('summary', 'No summary.')}")
            lines.append(f"Tags: {', '.join(e.get('tags', []))}")
            lines.append("")

    # Pointers to non-hot entries
    cold_entries = [e for e in entries if not e.get("hot", False)]
    if cold_entries:
        lines.append("## Detailed Knowledge")
        for e in cold_entries:
            lines.append(f"- {e.get('file', 'unknown')}: {e.get('summary', '')}")
        lines.append("")

    # Trim to 200 lines budget
    if len(lines) > 200:
        lines = lines[:197]
        lines.append("")
        lines.append("_(truncated — over 200-line budget)_")

    content = "\n".join(lines) + "\n"

    # Write to MEMORY.md — note: this writes to the knowledge directory
    # The actual Claude memory path is handled by the agent reading this
    memory_path = dominion_path("knowledge", "MEMORY.md")
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(content)

    info(f"Knowledge synced: {len(hot_entries)} hot, {len(cold_entries)} cold entries. {len(lines)} lines.")


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search term")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Search knowledge index by topic or tag."""
    index_path = dominion_path("knowledge", "index.toml")
    index = read_toml(index_path)
    entries = index.get("entries", [])

    query_lower = query.lower()
    matches: list[dict] = []

    for e in entries:
        # Match against tags (exact)
        if query_lower in [t.lower() for t in e.get("tags", [])]:
            matches.append(e)
            continue
        # Match against file name (substring)
        if query_lower in e.get("file", "").lower():
            matches.append(e)
            continue
        # Match against summary (substring)
        if query_lower in e.get("summary", "").lower():
            matches.append(e)
            continue

    if not matches:
        info(f"No knowledge entries match '{query}'.")
        return

    columns = ["File", "Tags", "Summary", "Hot"]
    rows = []
    for m in matches:
        rows.append([
            m.get("file", ""),
            ", ".join(m.get("tags", [])),
            m.get("summary", ""),
            "yes" if m.get("hot") else "no",
        ])
    table("Knowledge Search Results", columns, rows, json)


@app.command(name="summary")
def project_summary(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """One-paragraph project overview."""
    dom = read_toml(dominion_path("dominion.toml"))
    project = dom.get("project", {})

    data = {
        "name": project.get("name", "Unknown"),
        "vision": project.get("vision", ""),
        "stack": ", ".join(project.get("languages", [])),
        "direction": dom.get("direction", {}).get("mode", "maintain"),
        "team_size": project.get("team_size", "unknown"),
    }
    if json:
        output(data, json_mode=True)
        return

    info(f"{data['name']}: {data['vision']}")
    info(f"  Stack: {data['stack']}")
    info(f"  Direction: {data['direction']}")
    info(f"  Team: {data['team_size']}")
