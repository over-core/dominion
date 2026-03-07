"""Minimal TOML writer.

Implements the core of tomli_w (MIT License) for writing TOML from Python dicts.
Handles: str, int, float, bool, datetime, date, time, list, dict.
Supports nested tables, inline tables for simple dicts, and arrays of tables.
"""

from __future__ import annotations

import datetime
import re
from typing import IO, Any

_BARE_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def dump(obj: dict[str, Any], fp: IO[bytes]) -> None:
    """Serialize a dict to TOML and write to a binary file object."""
    fp.write(dumps(obj).encode())


def dumps(obj: dict[str, Any]) -> str:
    """Serialize a dict to a TOML string."""
    lines: list[str] = []
    _dump_table(obj, [], lines, is_root=True)
    return "\n".join(lines) + "\n" if lines else ""


def _dump_table(
    table: dict[str, Any],
    key_path: list[str],
    lines: list[str],
    *,
    is_root: bool = False,
) -> None:
    """Dump a table (dict) as TOML.

    Simple key-value pairs come first, then sub-tables, then arrays of tables.
    """
    simple_pairs: list[tuple[str, Any]] = []
    sub_tables: list[tuple[str, dict]] = []
    arrays_of_tables: list[tuple[str, list[dict]]] = []

    for key, value in table.items():
        if isinstance(value, dict):
            sub_tables.append((key, value))
        elif isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
            arrays_of_tables.append((key, value))
        else:
            simple_pairs.append((key, value))

    # Emit table header (skip for root)
    if not is_root and key_path:
        header = ".".join(_format_key(k) for k in key_path)
        if lines and lines[-1] != "":
            lines.append("")
        lines.append(f"[{header}]")

    # Emit simple key-value pairs
    for key, value in simple_pairs:
        lines.append(f"{_format_key(key)} = {_format_value(value)}")

    # Emit sub-tables
    for key, sub in sub_tables:
        _dump_table(sub, key_path + [key], lines)

    # Emit arrays of tables
    for key, arr in arrays_of_tables:
        for item in arr:
            full_path = key_path + [key]
            header = ".".join(_format_key(k) for k in full_path)
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(f"[[{header}]]")
            # Emit items within the array-of-tables entry
            _dump_aot_entry(item, full_path, lines)


def _dump_aot_entry(
    table: dict[str, Any],
    key_path: list[str],
    lines: list[str],
) -> None:
    """Dump an entry within an array of tables."""
    simple_pairs: list[tuple[str, Any]] = []
    sub_tables: list[tuple[str, dict]] = []
    arrays_of_tables: list[tuple[str, list[dict]]] = []

    for key, value in table.items():
        if isinstance(value, dict):
            sub_tables.append((key, value))
        elif isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
            arrays_of_tables.append((key, value))
        else:
            simple_pairs.append((key, value))

    for key, value in simple_pairs:
        lines.append(f"{_format_key(key)} = {_format_value(value)}")

    for key, sub in sub_tables:
        _dump_table(sub, key_path + [key], lines)

    for key, arr in arrays_of_tables:
        for item in arr:
            full_path = key_path + [key]
            header = ".".join(_format_key(k) for k in full_path)
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(f"[[{header}]]")
            _dump_aot_entry(item, full_path, lines)


def _format_key(key: str) -> str:
    """Format a key — bare if possible, quoted otherwise."""
    if _BARE_KEY_RE.match(key):
        return key
    return _quote_string(key)


def _format_value(value: Any) -> str:
    """Format a single value to its TOML representation."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value != value:  # NaN
            return "nan"
        if value == float("inf"):
            return "inf"
        if value == float("-inf"):
            return "-inf"
        return repr(value)
    if isinstance(value, str):
        return _quote_string(value)
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, datetime.time):
        return value.isoformat()
    if isinstance(value, list):
        return _format_array(value)
    if isinstance(value, dict):
        return _format_inline_table(value)
    return _quote_string(str(value))


def _quote_string(s: str) -> str:
    """Quote a string for TOML, using basic strings with escapes."""
    escaped = (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return f'"{escaped}"'


def _format_array(arr: list[Any]) -> str:
    """Format a list as a TOML array."""
    if not arr:
        return "[]"
    # For short arrays of simple types, inline them
    items = [_format_value(v) for v in arr]
    inline = f"[{', '.join(items)}]"
    if len(inline) <= 80:
        return inline
    # Multi-line for longer arrays
    inner = ",\n".join(f"    {item}" for item in items)
    return f"[\n{inner},\n]"


def _format_inline_table(table: dict[str, Any]) -> str:
    """Format a dict as a TOML inline table."""
    if not table:
        return "{}"
    pairs = [f"{_format_key(k)} = {_format_value(v)}" for k, v in table.items()]
    return "{" + ", ".join(pairs) + "}"
