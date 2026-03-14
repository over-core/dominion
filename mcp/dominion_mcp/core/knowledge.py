"""Knowledge file access and search."""

from __future__ import annotations

from pathlib import Path

from .config import read_toml, read_toml_optional


def get_knowledge_file(dom_root: Path, file: str) -> str:
    """Read a specific knowledge file's contents.

    file is relative to .dominion/knowledge/ (e.g., 'auth-decisions.md').
    Raises ValueError if file not found or path traversal attempted.
    """
    if file.startswith("/") or ".." in file.split("/"):
        raise ValueError(f"Invalid path: {file}. Must be relative with no '..' segments.")

    path = dom_root / "knowledge" / file
    if not path.exists():
        raise ValueError(f"Knowledge file not found: {file}")

    return path.read_text()


def search_knowledge(dom_root: Path, query: str) -> list[dict]:
    """Search knowledge index by topic, tag, or file name.

    Matches against tags (exact, case-insensitive), file name (substring),
    and summary (substring). Returns list of matching entry dicts.
    """
    index_path = dom_root / "knowledge" / "index.toml"
    index = read_toml(index_path)
    entries = index.get("entries", [])

    query_lower = query.lower()
    matches: list[dict] = []

    for e in entries:
        if query_lower in [t.lower() for t in e.get("tags", [])]:
            matches.append(e)
            continue
        if query_lower in e.get("file", "").lower():
            matches.append(e)
            continue
        if query_lower in e.get("summary", "").lower():
            matches.append(e)
            continue

    return matches


def sync_memory(dom_root: Path) -> dict:
    """Sync project MEMORY.md from knowledge index.

    Generates MEMORY.md content from .dominion/knowledge/index.toml with:
    - Current state section
    - Documentation chain
    - Hot entries (priority-sorted)
    - Cold entry pointers
    - 200-line budget enforcement

    Returns dict with hot_count, cold_count, line_count.
    """
    index_path = dom_root / "knowledge" / "index.toml"
    index = read_toml(index_path)

    state = read_toml_optional(dom_root / "state.toml") or {}
    dominion = read_toml_optional(dom_root / "dominion.toml") or {}

    entries = index.get("entries", [])
    hot_entries = sorted(
        [e for e in entries if e.get("hot", False)],
        key=lambda e: e.get("priority", 999),
    )
    cold_entries = [e for e in entries if not e.get("hot", False)]

    lines: list[str] = [
        "# Project Knowledge (auto-generated)",
        "",
    ]

    pos = state.get("position", {})
    if pos:
        lines.extend([
            "## Current State",
            f"- Phase: {pos.get('phase', 0)}",
            f"- Step: {pos.get('step', 'idle')}",
            f"- Status: {pos.get('status', 'ready')}",
            "",
        ])

    doc = dominion.get("documentation", {})
    if doc:
        lines.append("## Documentation Chain")
        for fb in doc.get("fallback", []):
            if isinstance(fb, dict):
                lines.append(f"- {fb.get('source', 'unknown')}: {fb.get('action', '')}")
        lines.append("")

    if hot_entries:
        lines.append("## Active Knowledge")
        for e in hot_entries:
            lines.extend([
                f"### {e.get('file', 'unknown')}",
                f"{e.get('summary', 'No summary.')}",
                f"Tags: {', '.join(e.get('tags', []))}",
                "",
            ])

    if cold_entries:
        lines.append("## Detailed Knowledge")
        for e in cold_entries:
            lines.append(f"- {e.get('file', 'unknown')}: {e.get('summary', '')}")
        lines.append("")

    if len(lines) > 200:
        lines = lines[:197]
        lines.extend(["", "_(truncated — over 200-line budget)_"])

    content = "\n".join(lines) + "\n"

    memory_path = dom_root / "knowledge" / "MEMORY.md"
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(content)

    return {
        "hot_count": len(hot_entries),
        "cold_count": len(cold_entries),
        "line_count": len(lines),
    }
