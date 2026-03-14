"""Per-agent memory management with cap and priority-based pruning."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .config import read_toml_optional, write_toml_locked

MEMORY_CAP = 20
PRUNE_PRIORITY = ["discovery", "preference", "correction"]  # first pruned -> last pruned


def get_agent_memory(dom_root: Path, role: str) -> list[dict]:
    """Read agent memory entries from .dominion/memory/{role}.toml.

    Returns list of entry dicts. Empty list if file doesn't exist.
    """
    path = dom_root / "memory" / f"{role}.toml"
    data = read_toml_optional(path)
    if data is None:
        return []
    return data.get("entries", [])


async def save_agent_memory(
    dom_root: Path, role: str, memory_type: str, content: str, source: str
) -> None:
    """Save a memory entry for an agent.

    memory_type: "correction", "preference", or "discovery"
    Appends entry, then prunes if over MEMORY_CAP.
    """
    path = dom_root / "memory" / f"{role}.toml"

    entry = {
        "type": memory_type,
        "content": content,
        "source": source,
        "created": datetime.now(timezone.utc).isoformat(),
    }

    def updater(data: dict) -> dict:
        entries = data.get("entries", [])
        entries.append(entry)
        data["entries"] = prune_memory(entries, MEMORY_CAP)
        return data

    await write_toml_locked(path, updater)


def prune_memory(entries: list[dict], cap: int = MEMORY_CAP) -> list[dict]:
    """Prune memory entries to stay within cap.

    Priority order (first to be pruned -> last):
    1. discoveries (oldest first) -- volatile, may be outdated
    2. preferences (oldest first) -- user-provided but may reflect past state
    3. corrections (oldest first) -- most valuable, pruned last

    Returns pruned list.
    """
    if len(entries) <= cap:
        return entries

    # Group by type
    by_type: dict[str, list[dict]] = {}
    for entry in entries:
        t = entry.get("type", "discovery")
        by_type.setdefault(t, []).append(entry)

    result = list(entries)  # copy

    for prune_type in PRUNE_PRIORITY:
        if len(result) <= cap:
            break
        # Remove oldest entries of this type
        type_entries = [e for e in result if e.get("type", "discovery") == prune_type]
        # Sort by created date (oldest first)
        type_entries.sort(key=lambda e: e.get("created", ""))

        while len(result) > cap and type_entries:
            oldest = type_entries.pop(0)
            result.remove(oldest)

    return result
