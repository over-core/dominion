"""Tests for dominion_mcp.core.state module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dominion_mcp.core.config import read_toml
from dominion_mcp.core.state import (
    VALID_STEPS,
    checkpoint,
    defer_item,
    get_deferred,
    get_decisions,
    get_position,
    list_signals,
    raise_blocker,
    raise_warning,
    resolve_signal,
    save_decision,
    update_position,
)


# ---------------------------------------------------------------------------
# get_position
# ---------------------------------------------------------------------------


def test_get_position_returns_fields(dom_root: Path) -> None:
    """get_position returns phase, step, wave, status from state.toml."""
    pos = get_position(dom_root)
    assert pos["phase"] == 1
    assert pos["step"] == "execute"
    assert pos["wave"] == 2
    assert pos["status"] == "active"


def test_get_position_includes_message(dom_root: Path) -> None:
    """get_position includes a human-readable message."""
    pos = get_position(dom_root)
    assert "Phase 1" in pos["message"]
    assert "execute" in pos["message"]


def test_get_position_defaults_without_state(tmp_path: Path) -> None:
    """get_position returns defaults when state.toml is absent."""
    dom = tmp_path / ".dominion"
    dom.mkdir()
    pos = get_position(dom)
    assert pos["phase"] == 0
    assert pos["step"] == "idle"
    assert pos["status"] == "ready"


# ---------------------------------------------------------------------------
# update_position
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_position_updates_step(dom_root: Path) -> None:
    """update_position updates the step field."""
    result = await update_position(dom_root, step="plan")
    assert result["step"] == "plan"
    # Verify it persisted
    pos = get_position(dom_root)
    assert pos["step"] == "plan"


@pytest.mark.asyncio
async def test_update_position_rejects_invalid_step(dom_root: Path) -> None:
    """update_position raises ValueError for an invalid step name."""
    with pytest.raises(ValueError, match="Invalid step"):
        await update_position(dom_root, step="invalid_step")


@pytest.mark.asyncio
async def test_update_position_rejects_invalid_status(dom_root: Path) -> None:
    """update_position raises ValueError for an invalid status."""
    with pytest.raises(ValueError, match="Invalid status"):
        await update_position(dom_root, status="broken")


@pytest.mark.asyncio
async def test_update_position_updates_multiple_fields(dom_root: Path) -> None:
    """update_position can set phase, step, wave, and status at once."""
    result = await update_position(dom_root, phase=2, step="research", wave=1, status="ready")
    assert result["phase"] == 2
    assert result["step"] == "research"
    assert result["wave"] == 1
    assert result["status"] == "ready"


# ---------------------------------------------------------------------------
# checkpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_checkpoint_sets_timestamp_and_resets_status(dom_root: Path) -> None:
    """checkpoint sets last_session, clears lock, resets active to ready."""
    await checkpoint(dom_root)
    pos = get_position(dom_root)
    assert pos["status"] == "ready"
    assert pos["last_session"] != "unknown"
    # Verify lock is cleared
    state = read_toml(dom_root / "state.toml")
    assert "lock" not in state


@pytest.mark.asyncio
async def test_checkpoint_preserves_non_active_status(dom_root: Path) -> None:
    """checkpoint only resets 'active' status, leaves others unchanged."""
    await update_position(dom_root, status="blocked")
    await checkpoint(dom_root)
    pos = get_position(dom_root)
    assert pos["status"] == "blocked"


# ---------------------------------------------------------------------------
# save_decision / get_decisions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_decision_appends_entry(dom_root: Path) -> None:
    """save_decision appends a decision entry to state.toml."""
    entry = await save_decision(dom_root, "01-01", "Use FastAPI for routing", ["api"])
    assert entry["id"] == 1
    assert entry["task"] == "01-01"
    assert entry["text"] == "Use FastAPI for routing"
    assert entry["tags"] == ["api"]


@pytest.mark.asyncio
async def test_save_decision_auto_increments_id(dom_root: Path) -> None:
    """save_decision auto-increments the decision ID."""
    await save_decision(dom_root, "01-01", "Decision A")
    entry2 = await save_decision(dom_root, "01-02", "Decision B")
    assert entry2["id"] == 2


def test_get_decisions_returns_empty_initially(dom_root: Path) -> None:
    """get_decisions returns empty list when no decisions exist."""
    assert get_decisions(dom_root) == []


@pytest.mark.asyncio
async def test_get_decisions_filters_by_tags(dom_root: Path) -> None:
    """get_decisions filters by tags when specified."""
    await save_decision(dom_root, "01-01", "API choice", ["api"])
    await save_decision(dom_root, "01-02", "DB choice", ["database"])
    await save_decision(dom_root, "01-03", "Auth method", ["api", "security"])

    api_decisions = get_decisions(dom_root, tags=["api"])
    assert len(api_decisions) == 2

    db_decisions = get_decisions(dom_root, tags=["database"])
    assert len(db_decisions) == 1


@pytest.mark.asyncio
async def test_get_decisions_filters_by_phase(dom_root: Path) -> None:
    """get_decisions filters by phase number."""
    await save_decision(dom_root, "01-01", "Phase 1 decision")
    decisions = get_decisions(dom_root, phase=1)
    assert len(decisions) == 1
    no_match = get_decisions(dom_root, phase=99)
    assert len(no_match) == 0


# ---------------------------------------------------------------------------
# defer_item / get_deferred
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_defer_item_appends_to_deferred(dom_root: Path) -> None:
    """defer_item appends text to outstanding.deferred list."""
    await defer_item(dom_root, "Refactor auth module")
    deferred = get_deferred(dom_root)
    assert "Refactor auth module" in deferred


@pytest.mark.asyncio
async def test_defer_item_multiple(dom_root: Path) -> None:
    """Multiple deferred items accumulate in the list."""
    await defer_item(dom_root, "Item A")
    await defer_item(dom_root, "Item B")
    deferred = get_deferred(dom_root)
    assert len(deferred) == 2
    assert deferred[0] == "Item A"
    assert deferred[1] == "Item B"


def test_get_deferred_returns_empty_initially(dom_root: Path) -> None:
    """get_deferred returns empty list when nothing deferred."""
    assert get_deferred(dom_root) == []


# ---------------------------------------------------------------------------
# raise_blocker
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_raise_blocker_creates_signal_file(dom_root: Path) -> None:
    """raise_blocker creates a signal TOML file."""
    signal = await raise_blocker(dom_root, "wave", "01-02", "Dependency unavailable")
    assert signal["type"] == "blocker"
    assert signal["level"] == "wave"
    assert signal["task"] == "01-02"
    assert signal["reason"] == "Dependency unavailable"
    # Check file was created
    signal_file = dom_root / "signals" / "blocker-01-02.toml"
    assert signal_file.exists()


@pytest.mark.asyncio
async def test_raise_blocker_sets_status_blocked(dom_root: Path) -> None:
    """raise_blocker at wave/phase/critical level sets status to blocked."""
    await raise_blocker(dom_root, "wave", "01-02", "Blocked")
    pos = get_position(dom_root)
    assert pos["status"] == "blocked"


@pytest.mark.asyncio
async def test_raise_blocker_task_level_does_not_block(dom_root: Path) -> None:
    """raise_blocker at task level does not change position status."""
    await raise_blocker(dom_root, "task", "01-01", "Minor issue")
    pos = get_position(dom_root)
    assert pos["status"] == "active"


@pytest.mark.asyncio
async def test_raise_blocker_rejects_invalid_level(dom_root: Path) -> None:
    """raise_blocker raises ValueError for an invalid level."""
    with pytest.raises(ValueError, match="Invalid blocker level"):
        await raise_blocker(dom_root, "invalid", "01-01", "Reason")


# ---------------------------------------------------------------------------
# raise_warning
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_raise_warning_creates_signal_file(dom_root: Path) -> None:
    """raise_warning creates a warning signal TOML file."""
    await raise_warning(dom_root, "01-01", "Check dependency version")
    signals = list((dom_root / "signals").glob("warning-01-01-*.toml"))
    assert len(signals) == 1


@pytest.mark.asyncio
async def test_raise_warning_increments_sequence(dom_root: Path) -> None:
    """Multiple warnings for the same task get sequenced filenames."""
    await raise_warning(dom_root, "01-01", "Warning A")
    await raise_warning(dom_root, "01-01", "Warning B")
    signals = sorted((dom_root / "signals").glob("warning-01-01-*.toml"))
    assert len(signals) == 2


# ---------------------------------------------------------------------------
# list_signals
# ---------------------------------------------------------------------------


def test_list_signals_empty(dom_root: Path) -> None:
    """list_signals returns empty list when no signals exist."""
    assert list_signals(dom_root) == []


@pytest.mark.asyncio
async def test_list_signals_returns_all(dom_root: Path) -> None:
    """list_signals returns all signal files."""
    await raise_blocker(dom_root, "task", "01-01", "Blocker")
    await raise_warning(dom_root, "01-02", "Warning")
    signals = list_signals(dom_root)
    assert len(signals) == 2


@pytest.mark.asyncio
async def test_list_signals_filters_by_affecting(dom_root: Path) -> None:
    """list_signals filters signals by affecting task_id."""
    await raise_blocker(dom_root, "task", "01-01", "Blocker")
    await raise_warning(dom_root, "01-02", "Warning")
    signals = list_signals(dom_root, affecting="01-01")
    assert len(signals) == 1
    assert signals[0]["task"] == "01-01"


# ---------------------------------------------------------------------------
# resolve_signal
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_signal_removes_file(dom_root: Path) -> None:
    """resolve_signal removes the signal file."""
    await raise_warning(dom_root, "01-01", "Check this")
    signals_before = list_signals(dom_root)
    assert len(signals_before) == 1
    await resolve_signal(dom_root, "01-01")
    signals_after = list_signals(dom_root)
    assert len(signals_after) == 0


@pytest.mark.asyncio
async def test_resolve_signal_blocker_resets_status(dom_root: Path) -> None:
    """resolve_signal for a blocker clears blocker state and sets status active."""
    await raise_blocker(dom_root, "wave", "01-02", "Dependency issue")
    pos = get_position(dom_root)
    assert pos["status"] == "blocked"

    await resolve_signal(dom_root, "01-02")
    pos = get_position(dom_root)
    assert pos["status"] == "active"
    state = read_toml(dom_root / "state.toml")
    assert "blocker" not in state


@pytest.mark.asyncio
async def test_resolve_signal_raises_when_not_found(dom_root: Path) -> None:
    """resolve_signal raises ValueError when no matching signal exists."""
    with pytest.raises(ValueError, match="No signal found"):
        await resolve_signal(dom_root, "99-99")
