"""Generic .dominion/ data access commands."""

from __future__ import annotations

import json
from typing import Annotated, Optional

import typer

from ..core.config import dominion_path
from ..core.formatters import error, info, output
from ..core.readers import read_toml, write_toml

app = typer.Typer(help="Generic .dominion/ data access")


def _validate_file_arg(file: str) -> str:
    """Reject path traversal and absolute paths."""
    if file.startswith("/") or ".." in file.split("/"):
        error(f"Invalid path: {file}. Must be relative to .dominion/ with no '..' segments.")
        raise SystemExit(1)
    return file


def _traverse_key(data: dict, key: str) -> object:
    """Traverse a dotted key path into nested dicts/lists.

    Supports dict keys and integer list indices (e.g., "findings.0.title").
    """
    current: object = data
    for part in key.split("."):
        if isinstance(current, dict):
            if part not in current:
                error(f"Key not found: {part!r} in path {key!r}")
                raise SystemExit(1)
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
            except ValueError:
                error(f"Expected integer index for list, got {part!r} in path {key!r}")
                raise SystemExit(1)
            if idx < 0 or idx >= len(current):
                error(f"Index {idx} out of range (list has {len(current)} items) in path {key!r}")
                raise SystemExit(1)
            current = current[idx]
        else:
            error(f"Cannot traverse into {type(current).__name__} at {part!r} in path {key!r}")
            raise SystemExit(1)
    return current


def _set_nested(data: dict, key: str, value: object) -> None:
    """Set a value at a dotted key path, creating intermediate dicts as needed."""
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
                error(f"Expected integer index for list, got {part!r} in path {key!r}")
                raise SystemExit(1)
            if idx < 0 or idx >= len(current):
                error(f"Index {idx} out of range in path {key!r}")
                raise SystemExit(1)
            current = current[idx]
        else:
            error(f"Cannot traverse into {type(current).__name__} at {part!r} in path {key!r}")
            raise SystemExit(1)

    last = parts[-1]
    if isinstance(current, dict):
        current[last] = value
    elif isinstance(current, list):
        try:
            idx = int(last)
        except ValueError:
            error(f"Expected integer index for list, got {last!r} in path {key!r}")
            raise SystemExit(1)
        if idx < 0 or idx >= len(current):
            error(f"Index {idx} out of range in path {key!r}")
            raise SystemExit(1)
        current[idx] = value
    else:
        error(f"Cannot set value on {type(current).__name__} at {last!r} in path {key!r}")
        raise SystemExit(1)


@app.command()
def get(
    file: Annotated[str, typer.Argument(help="TOML file path relative to .dominion/")],
    key: Annotated[Optional[str], typer.Option("--key", help="Dotted key path (e.g., project.name)")] = None,
    json_out: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Read any .dominion/ TOML file or a specific key within it."""
    _validate_file_arg(file)
    path = dominion_path(*file.split("/"))
    data = read_toml(path)

    if key:
        value = _traverse_key(data, key)
        if json_out:
            output({"key": key, "value": value}, json_mode=True)
        elif isinstance(value, (dict, list)):
            output({"key": key, "value": value}, json_mode=True)
        else:
            info(str(value))
    else:
        output(data, json_mode=json_out)


@app.command()
def set(
    file: Annotated[str, typer.Argument(help="TOML file path relative to .dominion/")],
    key: Annotated[str, typer.Option("--key", help="Dotted key path to write")],
    value: Annotated[str, typer.Option("--value", help="JSON-encoded value to write")],
) -> None:
    """Write a value to any .dominion/ TOML file."""
    _validate_file_arg(file)

    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        error(f"Invalid JSON value: {exc}")
        raise SystemExit(1)

    if parsed is None:
        error("null is not a valid TOML value.")
        raise SystemExit(1)

    path = dominion_path(*file.split("/"))
    data = read_toml(path)
    _set_nested(data, key, parsed)

    try:
        write_toml(path, data)
    except TypeError as exc:
        error(f"Value cannot be serialized to TOML: {exc}")
        raise SystemExit(1)

    info(f"Updated {file}: {key} = {json.dumps(parsed)}")
