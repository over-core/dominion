"""Tests for signal management commands."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from typer.testing import CliRunner

from dominion_cli.app import app

runner = CliRunner()


class TestBlockerSignal:
    """Tests for `signal blocker`."""

    def test_blocker_create(self, tmp_dominion: Path) -> None:
        result = runner.invoke(
            app,
            ["signal", "blocker", "--level", "task", "--task", "1-01", "--reason", "Tests failing"],
        )
        assert result.exit_code == 0
        assert "Blocker raised" in result.stdout

        # Verify signal file created
        signal_file = tmp_dominion / ".dominion" / "signals" / "blocker-1-01.toml"
        assert signal_file.exists()
        with open(signal_file, "rb") as f:
            data = tomllib.load(f)
        assert data["type"] == "blocker"
        assert data["level"] == "task"
        assert data["task"] == "1-01"
        assert data["reason"] == "Tests failing"

    def test_blocker_updates_state(self, tmp_dominion: Path) -> None:
        """Wave-level blocker should set position status to blocked."""
        runner.invoke(
            app,
            ["signal", "blocker", "--level", "wave", "--task", "1-02", "--reason", "Dependency down"],
        )
        state_path = tmp_dominion / ".dominion" / "state.toml"
        with open(state_path, "rb") as f:
            state = tomllib.load(f)
        assert state["position"]["status"] == "blocked"
        assert state["blocker"]["task"] == "1-02"

    def test_blocker_task_level_no_block_status(self, tmp_dominion: Path) -> None:
        """Task-level blocker should NOT set position status to blocked."""
        # First set status to active explicitly
        runner.invoke(app, ["state", "update", "--status", "active"])
        runner.invoke(
            app,
            ["signal", "blocker", "--level", "task", "--task", "1-01", "--reason", "Minor issue"],
        )
        state_path = tmp_dominion / ".dominion" / "state.toml"
        with open(state_path, "rb") as f:
            state = tomllib.load(f)
        # Task-level blocker doesn't change position status to blocked
        assert state["position"]["status"] == "active"

    def test_blocker_invalid_level(self, tmp_dominion: Path) -> None:
        result = runner.invoke(
            app,
            ["signal", "blocker", "--level", "invalid", "--task", "1-01", "--reason", "Bad level"],
        )
        assert result.exit_code == 1


class TestWarningSignal:
    """Tests for `signal warning`."""

    def test_warning_create(self, tmp_dominion: Path) -> None:
        result = runner.invoke(
            app,
            ["signal", "warning", "--task", "1-01", "--message", "Performance degrading"],
        )
        assert result.exit_code == 0
        assert "Warning raised" in result.stdout

        # Verify signal file created with sequence number
        signal_file = tmp_dominion / ".dominion" / "signals" / "warning-1-01-1.toml"
        assert signal_file.exists()
        with open(signal_file, "rb") as f:
            data = tomllib.load(f)
        assert data["type"] == "warning"
        assert data["task"] == "1-01"
        assert data["message"] == "Performance degrading"

    def test_warning_increments_sequence(self, tmp_dominion: Path) -> None:
        runner.invoke(
            app,
            ["signal", "warning", "--task", "1-01", "--message", "First warning"],
        )
        runner.invoke(
            app,
            ["signal", "warning", "--task", "1-01", "--message", "Second warning"],
        )

        assert (tmp_dominion / ".dominion" / "signals" / "warning-1-01-1.toml").exists()
        assert (tmp_dominion / ".dominion" / "signals" / "warning-1-01-2.toml").exists()


class TestListSignals:
    """Tests for `signal list`."""

    def test_list_json(self, tmp_dominion: Path) -> None:
        # Create a blocker and a warning
        runner.invoke(
            app,
            ["signal", "blocker", "--level", "task", "--task", "1-01", "--reason", "Stuck"],
        )
        runner.invoke(
            app,
            ["signal", "warning", "--task", "1-02", "--message", "Slow build"],
        )

        result = runner.invoke(app, ["signal", "list", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) == 2

        types = {row["type"] for row in data}
        assert "blocker" in types
        assert "warning" in types

    def test_list_empty(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["signal", "list"])
        assert result.exit_code == 0
        assert "No active signals" in result.stdout

    def test_list_filter_affecting(self, tmp_dominion: Path) -> None:
        runner.invoke(
            app,
            ["signal", "blocker", "--level", "task", "--task", "1-01", "--reason", "Issue A"],
        )
        runner.invoke(
            app,
            ["signal", "warning", "--task", "1-02", "--message", "Issue B"],
        )

        result = runner.invoke(app, ["signal", "list", "--affecting", "1-01", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["task"] == "1-01"


class TestResolveSignal:
    """Tests for `signal resolve`."""

    def test_resolve(self, tmp_dominion: Path) -> None:
        # Create a blocker
        runner.invoke(
            app,
            ["signal", "blocker", "--level", "task", "--task", "1-01", "--reason", "Stuck"],
        )
        signal_file = tmp_dominion / ".dominion" / "signals" / "blocker-1-01.toml"
        assert signal_file.exists()

        # Resolve it
        result = runner.invoke(app, ["signal", "resolve", "1-01"])
        assert result.exit_code == 0
        assert "Removed" in result.stdout
        assert not signal_file.exists()

    def test_resolve_blocker_clears_state(self, tmp_dominion: Path) -> None:
        """Resolving a blocker should clear blocker from state and set status to active."""
        runner.invoke(
            app,
            ["signal", "blocker", "--level", "wave", "--task", "1-01", "--reason", "Stuck"],
        )
        runner.invoke(app, ["signal", "resolve", "1-01"])

        state_path = tmp_dominion / ".dominion" / "state.toml"
        with open(state_path, "rb") as f:
            state = tomllib.load(f)
        assert "blocker" not in state
        assert state["position"]["status"] == "active"

    def test_resolve_not_found(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["signal", "resolve", "nonexistent"])
        assert result.exit_code == 1

    def test_resolve_by_filename(self, tmp_dominion: Path) -> None:
        runner.invoke(
            app,
            ["signal", "blocker", "--level", "task", "--task", "1-01", "--reason", "Issue"],
        )
        result = runner.invoke(app, ["signal", "resolve", "blocker-1-01.toml"])
        assert result.exit_code == 0
        assert not (tmp_dominion / ".dominion" / "signals" / "blocker-1-01.toml").exists()
