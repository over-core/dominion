"""Foundational config, path resolution, and TOML I/O for dominion-mcp."""

from __future__ import annotations

import asyncio
import tomllib
from pathlib import Path
from typing import Callable

import tomli_w


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------


def find_dominion_root(start_path: Path | None = None) -> Path:
    """Walk up from start_path (or cwd) to find the .dominion/ directory.

    Returns the .dominion/ directory itself.
    Raises ValueError if not found.
    """
    current = start_path or Path.cwd()
    for parent in [current, *current.parents]:
        candidate = parent / ".dominion"
        if candidate.is_dir():
            return candidate
    raise ValueError(".dominion/ directory not found")


def dominion_path(root: Path, *parts: str) -> Path:
    """Return a resolved path relative to a .dominion/ root."""
    return root.joinpath(*parts)


def project_root(dom_root: Path) -> Path:
    """Return the project root (parent of .dominion/)."""
    return dom_root.parent


def current_phase(dom_root: Path) -> int:
    """Read current phase number from state.toml. Returns 0 if not set."""
    state = read_toml_optional(dom_root / "state.toml")
    if state is None:
        return 0
    return state.get("position", {}).get("phase", 0)


def phase_path(dom_root: Path, phase: int | None = None) -> Path:
    """Return path to the current (or specified) phase directory."""
    if phase is None:
        phase = current_phase(dom_root)
    return dominion_path(dom_root, "phases", str(phase))


# ---------------------------------------------------------------------------
# TOML I/O
# ---------------------------------------------------------------------------


def read_toml(path: Path) -> dict:
    """Read a TOML file and return its contents as a dict.

    Raises ValueError if the file is missing or contains malformed TOML.
    """
    if not path.exists():
        raise ValueError(f"File not found: {path}")
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Malformed TOML in {path}: {exc}") from exc


def read_toml_optional(path: Path) -> dict | None:
    """Read a TOML file if it exists, return None otherwise.

    Raises ValueError if the file exists but contains malformed TOML.
    """
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Malformed TOML in {path}: {exc}") from exc


def write_toml(path: Path, data: dict) -> None:
    """Write a dict to a TOML file.

    Creates parent directories if needed. Strips top-level keys starting
    with '_' before writing.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = {k: v for k, v in data.items() if not k.startswith("_")}
    with open(path, "wb") as f:
        tomli_w.dump(clean, f)


def read_toml_glob(directory: Path, pattern: str = "*.toml") -> list[dict]:
    """Glob for TOML files in a directory and read them all.

    Returns a list of dicts, each augmented with a '_file' key holding the
    file stem (filename without extension).
    """
    if not directory.is_dir():
        return []
    results: list[dict] = []
    for toml_file in sorted(directory.glob(pattern)):
        data = read_toml(toml_file)
        data["_file"] = toml_file.stem
        results.append(data)
    return results


# ---------------------------------------------------------------------------
# Key traversal utilities
# ---------------------------------------------------------------------------


def validate_file_path(file: str) -> str:
    """Reject path traversal (..) and absolute paths.

    Returns the path unchanged if valid. Raises ValueError otherwise.
    """
    if file.startswith("/") or ".." in file.split("/"):
        raise ValueError(
            f"Invalid path: {file}. Must be relative with no '..' segments."
        )
    return file


def traverse_key(data: dict, key: str) -> object:
    """Traverse a dotted key path into nested dicts and lists.

    Supports dict keys and integer list indices (e.g., 'findings.0.title').
    Raises KeyError on missing dict keys. Raises IndexError on out-of-range
    or non-integer list indices.
    """
    current: object = data
    for part in key.split("."):
        if isinstance(current, dict):
            if part not in current:
                raise KeyError(f"Key not found: {part!r} in path {key!r}")
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
            except ValueError:
                raise IndexError(
                    f"Expected integer index for list, got {part!r} in path {key!r}"
                )
            if idx < 0 or idx >= len(current):
                raise IndexError(
                    f"Index {idx} out of range (list has {len(current)} items) "
                    f"in path {key!r}"
                )
            current = current[idx]
        else:
            raise KeyError(
                f"Cannot traverse into {type(current).__name__} at {part!r} "
                f"in path {key!r}"
            )
    return current


def set_nested(data: dict, key: str, value: object) -> None:
    """Set a value at a dotted key path, creating intermediate dicts as needed.

    Raises KeyError if a non-dict/list node is encountered mid-path.
    Raises IndexError on out-of-range or non-integer list indices.
    """
    parts = key.split(".")
    current: object = data
    for part in parts[:-1]:
        if isinstance(current, dict):
            if part not in current:
                current[part] = {}
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
            except ValueError:
                raise IndexError(
                    f"Expected integer index for list, got {part!r} in path {key!r}"
                )
            if idx < 0 or idx >= len(current):
                raise IndexError(f"Index {idx} out of range in path {key!r}")
            current = current[idx]
        else:
            raise KeyError(
                f"Cannot traverse into {type(current).__name__} at {part!r} "
                f"in path {key!r}"
            )

    last = parts[-1]
    if isinstance(current, dict):
        current[last] = value
    elif isinstance(current, list):
        try:
            idx = int(last)
        except ValueError:
            raise IndexError(
                f"Expected integer index for list, got {last!r} in path {key!r}"
            )
        if idx < 0 or idx >= len(current):
            raise IndexError(f"Index {idx} out of range in path {key!r}")
        current[idx] = value
    else:
        raise KeyError(
            f"Cannot set value on {type(current).__name__} at {last!r} "
            f"in path {key!r}"
        )


# ---------------------------------------------------------------------------
# Async locking for concurrent TOML writes
# ---------------------------------------------------------------------------

_locks: dict[str, asyncio.Lock] = {}


async def write_toml_locked(
    path: Path, updater: Callable[[dict], dict]
) -> dict:
    """Read-modify-write a TOML file with per-file async locking.

    Acquires an asyncio.Lock keyed by the resolved file path string, reads
    the current data (or starts with an empty dict if the file does not
    exist), calls updater(data) to produce the modified data, writes it
    back, and returns the modified dict.
    """
    key = str(path.resolve())
    if key not in _locks:
        _locks[key] = asyncio.Lock()

    async with _locks[key]:
        current = read_toml_optional(path) or {}
        updated = updater(current)
        write_toml(path, updated)
        return updated
