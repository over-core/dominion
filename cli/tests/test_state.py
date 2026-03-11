"""Tests for state management commands."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from typer.testing import CliRunner

from dominion_cli.app import app

runner = CliRunner()


class TestResume:
    """Tests for `state resume`."""

    def test_resume_json(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "resume", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["phase"] == 1
        assert data["step"] == "execute"
        assert data["status"] == "active"
        assert "last_session" in data
        assert "message" in data

    def test_resume_human(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "resume"])
        assert result.exit_code == 0
        assert "Phase" in result.stdout

    def test_resume_phase_zero(self, tmp_dominion: Path) -> None:
        """When phase is 0, message indicates no active phase."""
        state_path = tmp_dominion / ".dominion" / "state.toml"
        state_path.write_text(
            "[meta]\nversion = \"0.9.1\"\n\n[position]\nphase = 0\nstep = \"idle\"\nstatus = \"ready\"\n"
        )
        result = runner.invoke(app, ["state", "resume", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["phase"] == 0
        assert "No active phase" in data["message"]


class TestPosition:
    """Tests for `state position`."""

    def test_position_json(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "position", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["phase"] == 1
        assert data["step"] == "execute"
        assert data["wave"] == 2
        assert data["status"] == "active"

    def test_position_human(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "position"])
        assert result.exit_code == 0
        assert "Phase 1" in result.stdout
        assert "execute" in result.stdout


class TestUpdate:
    """Tests for `state update`."""

    def test_update_phase_and_step(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "update", "--phase", "2", "--step", "plan"])
        assert result.exit_code == 0
        assert "phase=2" in result.stdout
        assert "step=plan" in result.stdout

        # Verify file was actually updated
        state_path = tmp_dominion / ".dominion" / "state.toml"
        with open(state_path, "rb") as f:
            state = tomllib.load(f)
        assert state["position"]["phase"] == 2
        assert state["position"]["step"] == "plan"

    def test_update_status(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "update", "--status", "blocked"])
        assert result.exit_code == 0
        assert "status=blocked" in result.stdout

    def test_update_wave(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "update", "--wave", "3"])
        assert result.exit_code == 0
        assert "wave=3" in result.stdout

    def test_update_invalid_step(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "update", "--step", "nonexistent"])
        assert result.exit_code == 1

    def test_update_invalid_status(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "update", "--status", "broken"])
        assert result.exit_code == 1

    def test_update_no_fields(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "update"])
        assert result.exit_code == 1


class TestCheckpoint:
    """Tests for `state checkpoint`."""

    def test_checkpoint(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "checkpoint"])
        assert result.exit_code == 0
        assert "checkpointed" in result.stdout

        # Verify last_session got updated
        state_path = tmp_dominion / ".dominion" / "state.toml"
        with open(state_path, "rb") as f:
            state = tomllib.load(f)
        assert "last_session" in state["position"]
        # Session was active, should now be ready
        assert state["position"]["status"] == "ready"

    def test_checkpoint_clears_lock(self, tmp_dominion: Path) -> None:
        """Checkpoint should remove any lock section."""
        state_path = tmp_dominion / ".dominion" / "state.toml"
        # Add a lock to state
        content = state_path.read_text()
        content += '\n[lock]\nagent = "developer"\ntask = "1-01"\n'
        state_path.write_text(content)

        result = runner.invoke(app, ["state", "checkpoint"])
        assert result.exit_code == 0

        with open(state_path, "rb") as f:
            state = tomllib.load(f)
        assert "lock" not in state


class TestDecision:
    """Tests for `state decision`."""

    def test_decision(self, tmp_dominion: Path) -> None:
        result = runner.invoke(
            app,
            ["state", "decision", "--task", "1-01", "--text", "Use FastAPI over Flask"],
        )
        assert result.exit_code == 0
        assert "D1" in result.stdout

        # Verify decision is in state.toml
        state_path = tmp_dominion / ".dominion" / "state.toml"
        with open(state_path, "rb") as f:
            state = tomllib.load(f)
        decisions = state.get("decisions", [])
        assert len(decisions) == 1
        assert decisions[0]["id"] == 1
        assert decisions[0]["task"] == "1-01"
        assert decisions[0]["text"] == "Use FastAPI over Flask"

    def test_decision_with_tags(self, tmp_dominion: Path) -> None:
        result = runner.invoke(
            app,
            [
                "state", "decision",
                "--task", "1-01",
                "--text", "Use PostgreSQL",
                "--tags", "database,infrastructure",
            ],
        )
        assert result.exit_code == 0

        state_path = tmp_dominion / ".dominion" / "state.toml"
        with open(state_path, "rb") as f:
            state = tomllib.load(f)
        decisions = state["decisions"]
        assert "database" in decisions[0]["tags"]
        assert "infrastructure" in decisions[0]["tags"]

    def test_decision_increments_id(self, tmp_dominion: Path) -> None:
        runner.invoke(
            app,
            ["state", "decision", "--task", "1-01", "--text", "First"],
        )
        runner.invoke(
            app,
            ["state", "decision", "--task", "1-02", "--text", "Second"],
        )
        state_path = tmp_dominion / ".dominion" / "state.toml"
        with open(state_path, "rb") as f:
            state = tomllib.load(f)
        decisions = state["decisions"]
        assert len(decisions) == 2
        assert decisions[0]["id"] == 1
        assert decisions[1]["id"] == 2


class TestDefer:
    """Tests for `state defer` and `state deferred`."""

    def test_defer(self, tmp_dominion: Path) -> None:
        result = runner.invoke(
            app,
            ["state", "defer", "--text", "Consider adding caching layer"],
        )
        assert result.exit_code == 0
        assert "Deferred" in result.stdout

        # Verify in state.toml
        state_path = tmp_dominion / ".dominion" / "state.toml"
        with open(state_path, "rb") as f:
            state = tomllib.load(f)
        deferred = state["outstanding"]["deferred"]
        assert "Consider adding caching layer" in deferred

    def test_deferred_json(self, tmp_dominion: Path) -> None:
        # Add a deferred item first
        runner.invoke(
            app,
            ["state", "defer", "--text", "Item one"],
        )
        runner.invoke(
            app,
            ["state", "defer", "--text", "Item two"],
        )

        result = runner.invoke(app, ["state", "deferred", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "deferred" in data
        assert len(data["deferred"]) == 2
        assert "Item one" in data["deferred"]
        assert "Item two" in data["deferred"]

    def test_deferred_empty(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "deferred"])
        assert result.exit_code == 0
        assert "No deferred items" in result.stdout

    def test_deferred_human(self, tmp_dominion: Path) -> None:
        runner.invoke(app, ["state", "defer", "--text", "Think about it"])
        result = runner.invoke(app, ["state", "deferred"])
        assert result.exit_code == 0
        assert "Think about it" in result.stdout


class TestDecisions:
    """Tests for `state decisions` (list/search)."""

    def test_decisions_empty(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "decisions"])
        assert result.exit_code == 0
        assert "No decisions" in result.stdout

    def test_decisions_list(self, tmp_dominion: Path) -> None:
        runner.invoke(
            app,
            ["state", "decision", "--task", "1-01", "--text", "Use FastAPI", "--tags", "arch"],
        )
        result = runner.invoke(app, ["state", "decisions", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) >= 1

    def test_decisions_filter_by_tags(self, tmp_dominion: Path) -> None:
        runner.invoke(
            app,
            ["state", "decision", "--task", "1-01", "--text", "Use FastAPI", "--tags", "arch"],
        )
        runner.invoke(
            app,
            ["state", "decision", "--task", "1-02", "--text", "Use Postgres", "--tags", "db"],
        )
        result = runner.invoke(app, ["state", "decisions", "--tags", "db", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1


class TestBlockers:
    """Tests for `state blockers`."""

    def test_blockers_empty(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["state", "blockers"])
        assert result.exit_code == 0
        assert "No active blockers" in result.stdout

    def test_blockers_from_state(self, tmp_dominion: Path) -> None:
        # Create a blocker via signal command first
        runner.invoke(
            app,
            ["signal", "blocker", "--level", "task", "--task", "1-01", "--reason", "Tests failing"],
        )
        result = runner.invoke(app, ["state", "blockers", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) >= 1
