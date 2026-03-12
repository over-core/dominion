"""Tests for validation commands."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from dominion_cli.app import app

runner = CliRunner()


class TestValidate:
    """Tests for `validate` (top-level validation)."""

    def test_validate_passes(self, tmp_dominion: Path) -> None:
        """With a correct structure, validate should pass (exit 0)."""
        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 0

    def test_validate_json(self, tmp_dominion: Path) -> None:
        """JSON output should have checks array and summary."""
        result = runner.invoke(app, ["validate", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "checks" in data
        assert "summary" in data
        assert isinstance(data["checks"], list)
        assert "passed" in data["summary"]
        assert "warnings" in data["summary"]
        assert "failed" in data["summary"]

        # With our fixture, there should be no failures
        assert data["summary"]["failed"] == 0

    def test_validate_check_names(self, tmp_dominion: Path) -> None:
        """Verify expected check names appear in output."""
        result = runner.invoke(app, ["validate", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        check_names = {c["name"] for c in data["checks"]}
        assert "TOML integrity" in check_names
        assert "Agent TOML-MD consistency" in check_names
        assert "settings.local.json permissions" in check_names

    def test_validate_missing_dominion_toml(self, tmp_dominion: Path) -> None:
        """Removing dominion.toml should cause a failure."""
        (tmp_dominion / ".dominion" / "dominion.toml").unlink()
        result = runner.invoke(app, ["validate", "--json"])
        # Should still run but report documentation fallback failure
        data = json.loads(result.stdout)
        check_map = {c["name"]: c for c in data["checks"]}
        assert check_map["Documentation fallback chain"]["status"] == "fail"

    def test_validate_missing_agents_md(self, tmp_dominion: Path) -> None:
        """Removing AGENTS.md should cause a failure."""
        (tmp_dominion / "AGENTS.md").unlink()
        result = runner.invoke(app, ["validate", "--json"])
        data = json.loads(result.stdout)
        check_map = {c["name"]: c for c in data["checks"]}
        assert check_map["AGENTS.md roster complete"]["status"] == "fail"
        assert result.exit_code == 1

    def test_validate_missing_settings_json(self, tmp_dominion: Path) -> None:
        """Removing settings.local.json should cause a failure."""
        (tmp_dominion / ".claude" / "settings.local.json").unlink()
        result = runner.invoke(app, ["validate", "--json"])
        data = json.loads(result.stdout)
        check_map = {c["name"]: c for c in data["checks"]}
        assert check_map["settings.local.json permissions"]["status"] == "fail"
        assert result.exit_code == 1

    def test_validate_missing_agent_md(self, tmp_dominion: Path) -> None:
        """Removing a .claude/agents/*.md file should cause consistency failure."""
        (tmp_dominion / ".claude" / "agents" / "researcher.md").unlink()
        result = runner.invoke(app, ["validate", "--json"])
        data = json.loads(result.stdout)
        check_map = {c["name"]: c for c in data["checks"]}
        assert check_map["Agent TOML-MD consistency"]["status"] == "fail"
        assert result.exit_code == 1

    def test_validate_malformed_toml(self, tmp_dominion: Path) -> None:
        """A malformed TOML file should cause TOML integrity failure."""
        bad_file = tmp_dominion / ".dominion" / "bad.toml"
        bad_file.write_text("[broken\nthis is not valid toml = {\n")
        result = runner.invoke(app, ["validate", "--json"])
        data = json.loads(result.stdout)
        check_map = {c["name"]: c for c in data["checks"]}
        assert check_map["TOML integrity"]["status"] == "fail"
        assert result.exit_code == 1

    def test_validate_human_output(self, tmp_dominion: Path) -> None:
        """Human output should show PASS/FAIL markers."""
        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 0
        assert "passed" in result.stdout
