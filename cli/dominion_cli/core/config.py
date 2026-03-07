"""Discovery and path resolution for .dominion/ directory."""

from __future__ import annotations

import sys
from pathlib import Path

_cached_root: Path | None = None


def find_dominion_root() -> Path:
    """Walk up from cwd to find a directory containing .dominion/.

    Returns the .dominion/ directory itself.
    Raises SystemExit if not found.
    """
    global _cached_root
    if _cached_root is not None:
        return _cached_root

    current = Path.cwd()
    for parent in [current, *current.parents]:
        candidate = parent / ".dominion"
        if candidate.is_dir():
            _cached_root = candidate
            return candidate

    print("Error: .dominion/ directory not found. Are you in a Dominion project?", file=sys.stderr)
    raise SystemExit(1)


def dominion_path(*parts: str) -> Path:
    """Return a resolved path relative to .dominion/.

    Usage:
        dominion_path("state.toml")           -> /project/.dominion/state.toml
        dominion_path("agents", "dev.toml")   -> /project/.dominion/agents/dev.toml
        dominion_path("phases", "1", "plan.toml") -> /project/.dominion/phases/1/plan.toml
    """
    root = find_dominion_root()
    return root.joinpath(*parts)


def project_root() -> Path:
    """Return the project root (parent of .dominion/)."""
    return find_dominion_root().parent


def current_phase() -> int:
    """Read current phase number from state.toml. Returns 0 if not set."""
    import tomllib

    state_path = dominion_path("state.toml")
    if not state_path.exists():
        return 0
    with open(state_path, "rb") as f:
        state = tomllib.load(f)
    return state.get("position", {}).get("phase", 0)


def phase_path(phase: int | None = None) -> Path:
    """Return path to the current (or specified) phase directory."""
    if phase is None:
        phase = current_phase()
    return dominion_path("phases", str(phase))


def reset_cache() -> None:
    """Reset cached root (useful for testing)."""
    global _cached_root
    _cached_root = None
