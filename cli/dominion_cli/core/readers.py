"""TOML/JSON reading and writing utilities."""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

from .._vendor import tomli_w


def read_toml(path: Path) -> dict:
    """Read a TOML file and return its contents as a dict.

    Exits with a clear error message if the file is missing or malformed.
    """
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        raise SystemExit(1)
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        print(f"Error: malformed TOML in {path}: {exc}", file=sys.stderr)
        raise SystemExit(1)


def read_toml_optional(path: Path) -> dict | None:
    """Read a TOML file if it exists, return None otherwise."""
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        print(f"Error: malformed TOML in {path}: {exc}", file=sys.stderr)
        raise SystemExit(1)


def read_toml_glob(directory: Path, pattern: str = "*.toml") -> list[dict]:
    """Glob for TOML files in a directory and read them all.

    Returns list of dicts, each augmented with a '_file' key containing the filename.
    """
    if not directory.is_dir():
        return []
    results = []
    for toml_file in sorted(directory.glob(pattern)):
        data = read_toml(toml_file)
        data["_file"] = toml_file.stem
        results.append(data)
    return results


def write_toml(path: Path, data: dict) -> None:
    """Write a dict to a TOML file using vendored tomli_w.

    Creates parent directories if needed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # Remove internal keys before writing
    clean = {k: v for k, v in data.items() if not k.startswith("_")}
    with open(path, "wb") as f:
        tomli_w.dump(clean, f)


def read_json(path: Path) -> dict:
    """Read a JSON file and return its contents as a dict."""
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        raise SystemExit(1)
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Error: malformed JSON in {path}: {exc}", file=sys.stderr)
        raise SystemExit(1)


def read_json_optional(path: Path) -> dict | None:
    """Read a JSON file if it exists, return None otherwise."""
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Error: malformed JSON in {path}: {exc}", file=sys.stderr)
        raise SystemExit(1)
