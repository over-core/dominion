"""Tests for agent management commands."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from dominion_cli.app import app

runner = CliRunner()


class TestListAgents:
    """Tests for `agents list`."""

    def test_list_json(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["agents", "list", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) == 2

        roles = {row["agent"] for row in data}
        assert "Researcher" in roles
        assert "Developer" in roles

        # Each row should have expected keys
        for row in data:
            assert "agent" in row
            assert "model" in row
            assert "purpose" in row

    def test_list_human(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["agents", "list"])
        assert result.exit_code == 0
        assert "Researcher" in result.stdout
        assert "Developer" in result.stdout

    def test_list_available(self, tmp_dominion: Path) -> None:
        """--available should include inactive specialist roles."""
        result = runner.invoke(app, ["agents", "list", "--available", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        # Should include active agents + inactive specialist roles
        assert len(data) > 2
        roles = {row["agent"] for row in data}
        assert "frontend-engineer" in roles


class TestShowAgent:
    """Tests for `agents show`."""

    def test_show_json(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["agents", "show", "researcher", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "role" in data
        assert data["role"]["name"] == "Researcher"
        assert "model" in data
        assert "tools" in data
        assert "governance" in data

    def test_show_human(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["agents", "show", "developer"])
        assert result.exit_code == 0
        assert "Developer" in result.stdout

    def test_show_not_found(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["agents", "show", "nonexistent"])
        assert result.exit_code == 1

    def test_show_developer(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["agents", "show", "developer", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["role"]["name"] == "Developer"
        assert "serena" in data["tools"]["mcp"]


class TestGenerate:
    """Tests for `agents generate`."""

    def test_generate_creates_agents_md(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["agents", "generate"])
        assert result.exit_code == 0

        agents_md = tmp_dominion / "AGENTS.md"
        assert agents_md.exists()
        content = agents_md.read_text()
        assert "Researcher" in content
        assert "Developer" in content

    def test_generate_creates_claude_agent_files(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["agents", "generate"])
        assert result.exit_code == 0

        claude_agents = tmp_dominion / ".claude" / "agents"
        assert (claude_agents / "researcher.md").exists()
        assert (claude_agents / "developer.md").exists()

        content = (claude_agents / "researcher.md").read_text()
        assert "Dominion" in content
        assert "Researcher" in content
