"""Tests for dominion_mcp.core.config module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dominion_mcp.core.config import (
    dominion_path,
    find_dominion_root,
    current_phase,
    phase_path,
    project_root,
    read_toml,
    read_toml_glob,
    read_toml_optional,
    set_nested,
    traverse_key,
    validate_file_path,
    write_toml,
    write_toml_locked,
)


# ---------------------------------------------------------------------------
# find_dominion_root
# ---------------------------------------------------------------------------


def test_find_dominion_root_from_subdirectory(dom_root: Path) -> None:
    """Walking up from a nested subdirectory finds .dominion/."""
    nested = dom_root.parent / "src" / "deep" / "nested"
    nested.mkdir(parents=True)
    found = find_dominion_root(nested)
    assert found == dom_root


def test_find_dominion_root_from_project_root(dom_root: Path) -> None:
    """Starting at the project root itself finds .dominion/."""
    found = find_dominion_root(dom_root.parent)
    assert found == dom_root


def test_find_dominion_root_raises_when_missing(tmp_path: Path) -> None:
    """Raises ValueError when no .dominion/ exists anywhere up the tree."""
    leaf = tmp_path / "a" / "b" / "c"
    leaf.mkdir(parents=True)
    with pytest.raises(ValueError, match=r"\.dominion/ directory not found"):
        find_dominion_root(leaf)


# ---------------------------------------------------------------------------
# dominion_path
# ---------------------------------------------------------------------------


def test_dominion_path_resolves_correctly(dom_root: Path) -> None:
    """dominion_path joins parts relative to .dominion/ root."""
    result = dominion_path(dom_root, "agents", "researcher.toml")
    assert result == dom_root / "agents" / "researcher.toml"


def test_dominion_path_single_part(dom_root: Path) -> None:
    """dominion_path works with a single path part."""
    result = dominion_path(dom_root, "state.toml")
    assert result == dom_root / "state.toml"


# ---------------------------------------------------------------------------
# project_root
# ---------------------------------------------------------------------------


def test_project_root_returns_parent(dom_root: Path) -> None:
    """project_root returns the parent of .dominion/."""
    result = project_root(dom_root)
    assert result == dom_root.parent
    assert result.name == "project"


# ---------------------------------------------------------------------------
# current_phase
# ---------------------------------------------------------------------------


def test_current_phase_reads_from_state(dom_root: Path) -> None:
    """current_phase reads phase number from state.toml position."""
    phase = current_phase(dom_root)
    assert phase == 1


def test_current_phase_returns_zero_without_state(tmp_path: Path) -> None:
    """current_phase returns 0 when state.toml is missing."""
    dom = tmp_path / ".dominion"
    dom.mkdir()
    phase = current_phase(dom)
    assert phase == 0


# ---------------------------------------------------------------------------
# phase_path
# ---------------------------------------------------------------------------


def test_phase_path_with_explicit_phase(dom_root: Path) -> None:
    """phase_path with explicit phase number returns correct path."""
    result = phase_path(dom_root, 2)
    assert result == dom_root / "phases" / "2"


def test_phase_path_reads_current_phase(dom_root: Path) -> None:
    """phase_path without phase argument uses current_phase."""
    result = phase_path(dom_root)
    assert result == dom_root / "phases" / "1"


# ---------------------------------------------------------------------------
# read_toml
# ---------------------------------------------------------------------------


def test_read_toml_valid_file(dom_root: Path) -> None:
    """read_toml returns dict from valid TOML file."""
    data = read_toml(dom_root / "dominion.toml")
    assert data["project"]["name"] == "test-project"
    assert data["project"]["languages"] == ["python"]


def test_read_toml_raises_on_missing(tmp_path: Path) -> None:
    """read_toml raises ValueError for missing file."""
    with pytest.raises(ValueError, match="File not found"):
        read_toml(tmp_path / "nonexistent.toml")


def test_read_toml_raises_on_malformed(tmp_path: Path) -> None:
    """read_toml raises ValueError for malformed TOML."""
    bad = tmp_path / "bad.toml"
    bad.write_text("[broken\nno closing bracket")
    with pytest.raises(ValueError, match="Malformed TOML"):
        read_toml(bad)


# ---------------------------------------------------------------------------
# read_toml_optional
# ---------------------------------------------------------------------------


def test_read_toml_optional_returns_none_for_missing(tmp_path: Path) -> None:
    """read_toml_optional returns None when file does not exist."""
    result = read_toml_optional(tmp_path / "nope.toml")
    assert result is None


def test_read_toml_optional_returns_dict_for_existing(dom_root: Path) -> None:
    """read_toml_optional returns parsed dict when file exists."""
    result = read_toml_optional(dom_root / "state.toml")
    assert result is not None
    assert result["position"]["phase"] == 1


def test_read_toml_optional_raises_on_malformed(tmp_path: Path) -> None:
    """read_toml_optional raises ValueError for malformed existing TOML."""
    bad = tmp_path / "bad.toml"
    bad.write_text("[[broken")
    with pytest.raises(ValueError, match="Malformed TOML"):
        read_toml_optional(bad)


# ---------------------------------------------------------------------------
# write_toml
# ---------------------------------------------------------------------------


def test_write_toml_creates_file(tmp_path: Path) -> None:
    """write_toml writes valid TOML and creates parent directories."""
    path = tmp_path / "sub" / "dir" / "out.toml"
    data = {"section": {"key": "value"}}
    write_toml(path, data)
    assert path.exists()
    result = read_toml(path)
    assert result["section"]["key"] == "value"


def test_write_toml_strips_underscore_keys(tmp_path: Path) -> None:
    """write_toml strips top-level keys starting with underscore."""
    path = tmp_path / "out.toml"
    data = {"_file": "researcher", "_internal": True, "visible": "yes"}
    write_toml(path, data)
    result = read_toml(path)
    assert "_file" not in result
    assert "_internal" not in result
    assert result["visible"] == "yes"


# ---------------------------------------------------------------------------
# read_toml_glob
# ---------------------------------------------------------------------------


def test_read_toml_glob_reads_all_files(dom_root: Path) -> None:
    """read_toml_glob reads all TOML files in a directory."""
    results = read_toml_glob(dom_root / "agents")
    assert len(results) == 2
    stems = {r["_file"] for r in results}
    assert stems == {"developer", "researcher"}


def test_read_toml_glob_returns_empty_for_missing_dir(tmp_path: Path) -> None:
    """read_toml_glob returns empty list for non-existent directory."""
    results = read_toml_glob(tmp_path / "nonexistent")
    assert results == []


# ---------------------------------------------------------------------------
# validate_file_path
# ---------------------------------------------------------------------------


def test_validate_file_path_accepts_relative() -> None:
    """Valid relative paths pass through unchanged."""
    assert validate_file_path("src/main.py") == "src/main.py"


def test_validate_file_path_rejects_dotdot() -> None:
    """Paths containing .. are rejected."""
    with pytest.raises(ValueError, match="Invalid path"):
        validate_file_path("../escape/file.py")


def test_validate_file_path_rejects_absolute() -> None:
    """Absolute paths are rejected."""
    with pytest.raises(ValueError, match="Invalid path"):
        validate_file_path("/etc/passwd")


def test_validate_file_path_rejects_dotdot_in_middle() -> None:
    """Paths with .. segment in the middle are rejected."""
    with pytest.raises(ValueError, match="Invalid path"):
        validate_file_path("src/../../etc/passwd")


# ---------------------------------------------------------------------------
# traverse_key
# ---------------------------------------------------------------------------


def test_traverse_key_simple_dict() -> None:
    """traverse_key navigates simple nested dicts."""
    data = {"a": {"b": {"c": 42}}}
    assert traverse_key(data, "a.b.c") == 42


def test_traverse_key_list_index() -> None:
    """traverse_key navigates into lists by integer index."""
    data = {"items": [{"name": "first"}, {"name": "second"}]}
    assert traverse_key(data, "items.1.name") == "second"


def test_traverse_key_missing_key_raises() -> None:
    """traverse_key raises KeyError for missing dict keys."""
    data = {"a": {"b": 1}}
    with pytest.raises(KeyError, match="Key not found"):
        traverse_key(data, "a.c")


def test_traverse_key_out_of_range_raises() -> None:
    """traverse_key raises IndexError for out-of-range list indices."""
    data = {"items": [1, 2, 3]}
    with pytest.raises(IndexError, match="out of range"):
        traverse_key(data, "items.5")


# ---------------------------------------------------------------------------
# set_nested
# ---------------------------------------------------------------------------


def test_set_nested_creates_intermediate_dicts() -> None:
    """set_nested creates intermediate dicts as needed."""
    data: dict = {}
    set_nested(data, "a.b.c", 99)
    assert data["a"]["b"]["c"] == 99


def test_set_nested_overwrites_existing() -> None:
    """set_nested overwrites an existing value."""
    data = {"a": {"b": "old"}}
    set_nested(data, "a.b", "new")
    assert data["a"]["b"] == "new"


def test_set_nested_into_list() -> None:
    """set_nested can set values inside a list by index."""
    data = {"items": [{"status": "pending"}, {"status": "pending"}]}
    set_nested(data, "items.1.status", "done")
    assert data["items"][1]["status"] == "done"


# ---------------------------------------------------------------------------
# write_toml_locked (async)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_write_toml_locked_read_modify_write(tmp_path: Path) -> None:
    """write_toml_locked does read-modify-write atomically."""
    path = tmp_path / "locked.toml"
    write_toml(path, {"count": 0})

    def increment(data: dict) -> dict:
        data["count"] = data.get("count", 0) + 1
        return data

    result = await write_toml_locked(path, increment)
    assert result["count"] == 1

    result = await write_toml_locked(path, increment)
    assert result["count"] == 2


@pytest.mark.asyncio
async def test_write_toml_locked_creates_file_if_missing(tmp_path: Path) -> None:
    """write_toml_locked creates the file if it doesn't exist."""
    path = tmp_path / "new.toml"

    def init(data: dict) -> dict:
        data["created"] = True
        return data

    result = await write_toml_locked(path, init)
    assert result["created"] is True
    assert path.exists()
