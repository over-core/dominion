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

    def test_generate_cli_commands_expanded(self, tmp_dominion: Path) -> None:
        """Group prefix 'dominion-cli signal' should expand into leaf commands."""
        # Developer has cli = ["dominion-cli plan *", "dominion-cli state *"]
        # "plan *" should expand to plan task, plan wave, plan deps, etc.
        result = runner.invoke(app, ["agents", "generate"])
        assert result.exit_code == 0

        content = (tmp_dominion / ".claude" / "agents" / "developer.md").read_text()
        # "plan *" should expand to individual plan commands
        assert "dominion-cli plan task" in content
        assert "dominion-cli plan wave" in content
        assert "dominion-cli plan deps" in content
        # "state *" should expand to individual state commands
        assert "dominion-cli state resume" in content
        assert "dominion-cli state position" in content
        assert "dominion-cli state update" in content

    def test_generate_cli_commands_with_descriptions(self, tmp_dominion: Path) -> None:
        """Descriptions from cli-spec.toml should appear in generated .md files."""
        result = runner.invoke(app, ["agents", "generate"])
        assert result.exit_code == 0

        content = (tmp_dominion / ".claude" / "agents" / "developer.md").read_text()
        # Commands should have descriptions from cli-spec.toml
        assert "Show task details and handoffs" in content
        assert "Show current pipeline position" in content

    def test_generate_universal_commands(self, tmp_dominion: Path) -> None:
        """data get, data set, state position, state resume appear for every agent."""
        result = runner.invoke(app, ["agents", "generate"])
        assert result.exit_code == 0

        for agent_file in ["researcher.md", "developer.md"]:
            content = (tmp_dominion / ".claude" / "agents" / agent_file).read_text()
            assert "dominion-cli data get" in content, f"data get missing from {agent_file}"
            assert "dominion-cli data set" in content, f"data set missing from {agent_file}"
            assert "dominion-cli state position" in content, f"state position missing from {agent_file}"
            assert "dominion-cli state resume" in content, f"state resume missing from {agent_file}"

    def test_generate_governance_rule(self, tmp_dominion: Path) -> None:
        """'NEVER edit .dominion/ TOML files directly' should appear in every agent .md."""
        result = runner.invoke(app, ["agents", "generate"])
        assert result.exit_code == 0

        for agent_file in ["researcher.md", "developer.md"]:
            content = (tmp_dominion / ".claude" / "agents" / agent_file).read_text()
            assert "NEVER edit `.dominion/` TOML files directly" in content, (
                f"governance rule missing from {agent_file}"
            )

    def test_generate_handles_nested_tools_format(self, tmp_dominion: Path) -> None:
        """tools.cli as a dict with 'commands' key should work."""
        # Overwrite developer.toml with nested format
        agent_toml = tmp_dominion / ".dominion" / "agents" / "developer.toml"
        agent_toml.write_text("""\
[role]
name = "Developer"
purpose = "Implement planned tasks with quality"

[model]
name = "claude-sonnet-4-20250514"

[tools]
mcp = ["serena", "echovault"]

[tools.cli]
commands = ["dominion-cli signal blocker", "dominion-cli signal warning"]

[governance]
file_ownership = ["src/"]
hard_stops = ["Never modify files outside task scope"]

[workflow]
produces = ["source code", "tests"]
commit_style = "feat(scope): description"
""")
        result = runner.invoke(app, ["agents", "generate"])
        assert result.exit_code == 0

        content = (tmp_dominion / ".claude" / "agents" / "developer.md").read_text()
        assert "dominion-cli signal blocker" in content
        assert "dominion-cli signal warning" in content
        # Universal commands still injected
        assert "dominion-cli data get" in content
