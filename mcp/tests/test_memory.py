"""Tests for dominion_mcp.core.memory module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dominion_mcp.core.memory import (
    MEMORY_CAP,
    get_agent_memory,
    prune_memory,
    save_agent_memory,
)


# ---------------------------------------------------------------------------
# get_agent_memory
# ---------------------------------------------------------------------------


def test_get_agent_memory_empty(dom_root: Path) -> None:
    """get_agent_memory returns empty list for a new agent."""
    entries = get_agent_memory(dom_root, "researcher")
    assert entries == []


# ---------------------------------------------------------------------------
# save_agent_memory / get_agent_memory round-trip
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_agent_memory_creates_entry(dom_root: Path) -> None:
    """save_agent_memory creates a memory entry that can be retrieved."""
    await save_agent_memory(dom_root, "researcher", "correction", "Don't re-research", "user")
    entries = get_agent_memory(dom_root, "researcher")
    assert len(entries) == 1
    assert entries[0]["type"] == "correction"
    assert entries[0]["content"] == "Don't re-research"
    assert entries[0]["source"] == "user"


@pytest.mark.asyncio
async def test_save_agent_memory_multiple_entries(dom_root: Path) -> None:
    """Multiple save calls accumulate entries."""
    await save_agent_memory(dom_root, "researcher", "correction", "Entry 1", "user")
    await save_agent_memory(dom_root, "researcher", "discovery", "Entry 2", "agent")
    await save_agent_memory(dom_root, "researcher", "preference", "Entry 3", "user")
    entries = get_agent_memory(dom_root, "researcher")
    assert len(entries) == 3


@pytest.mark.asyncio
async def test_save_agent_memory_has_timestamp(dom_root: Path) -> None:
    """Saved entries include a created timestamp."""
    await save_agent_memory(dom_root, "researcher", "correction", "Test", "user")
    entries = get_agent_memory(dom_root, "researcher")
    assert "created" in entries[0]
    assert len(entries[0]["created"]) > 0


# ---------------------------------------------------------------------------
# prune_memory
# ---------------------------------------------------------------------------


def test_prune_memory_under_cap_unchanged() -> None:
    """prune_memory returns entries unchanged when under cap."""
    entries = [
        {"type": "correction", "content": f"C{i}", "created": f"2025-01-0{i+1}T00:00:00Z"}
        for i in range(5)
    ]
    result = prune_memory(entries, cap=10)
    assert len(result) == 5


def test_prune_memory_at_cap_unchanged() -> None:
    """prune_memory returns entries unchanged when exactly at cap."""
    entries = [
        {"type": "correction", "content": f"C{i}", "created": f"2025-01-{i+1:02d}T00:00:00Z"}
        for i in range(3)
    ]
    result = prune_memory(entries, cap=3)
    assert len(result) == 3


def test_prune_memory_discoveries_first() -> None:
    """prune_memory prunes discoveries before preferences and corrections."""
    entries = [
        {"type": "discovery", "content": "D1", "created": "2025-01-01T00:00:00Z"},
        {"type": "preference", "content": "P1", "created": "2025-01-02T00:00:00Z"},
        {"type": "correction", "content": "C1", "created": "2025-01-03T00:00:00Z"},
        {"type": "discovery", "content": "D2", "created": "2025-01-04T00:00:00Z"},
    ]
    result = prune_memory(entries, cap=3)
    assert len(result) == 3
    types = [e["type"] for e in result]
    assert "discovery" in types  # D2 remains (newer)
    assert "preference" in types
    assert "correction" in types


def test_prune_memory_25_to_20() -> None:
    """Pruning 25 entries reduces to default cap of 20."""
    entries = []
    for i in range(10):
        entries.append({"type": "discovery", "content": f"D{i}", "created": f"2025-01-{i+1:02d}T00:00:00Z"})
    for i in range(10):
        entries.append({"type": "preference", "content": f"P{i}", "created": f"2025-02-{i+1:02d}T00:00:00Z"})
    for i in range(5):
        entries.append({"type": "correction", "content": f"C{i}", "created": f"2025-03-{i+1:02d}T00:00:00Z"})

    assert len(entries) == 25
    result = prune_memory(entries)
    assert len(result) == MEMORY_CAP


def test_prune_memory_corrections_last() -> None:
    """Corrections are the last type to be pruned."""
    entries = []
    # 5 discoveries, 5 preferences, 15 corrections = 25 total
    for i in range(5):
        entries.append({"type": "discovery", "content": f"D{i}", "created": f"2025-01-{i+1:02d}T00:00:00Z"})
    for i in range(5):
        entries.append({"type": "preference", "content": f"P{i}", "created": f"2025-02-{i+1:02d}T00:00:00Z"})
    for i in range(15):
        entries.append({"type": "correction", "content": f"C{i}", "created": f"2025-03-{i+1:02d}T00:00:00Z"})

    result = prune_memory(entries, cap=20)
    assert len(result) == 20
    # All corrections should remain (only 5 discoveries pruned to get to 20)
    corrections = [e for e in result if e["type"] == "correction"]
    assert len(corrections) == 15
