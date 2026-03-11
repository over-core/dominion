"""Tests for generic data access commands."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from dominion_cli.app import app

runner = CliRunner()


class TestDataGet:
    """Tests for `data get`."""

    def test_get_whole_file(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "get", "dominion.toml", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["project"]["name"] == "test-project"

    def test_get_with_key(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "get", "dominion.toml", "--key", "project.name"])
        assert result.exit_code == 0
        assert "test-project" in result.stdout

    def test_get_with_key_json(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "get", "dominion.toml", "--key", "project.name", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["value"] == "test-project"

    def test_get_nested_key(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "get", "dominion.toml", "--key", "workflow.pipeline", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data["value"], list)
        assert "discuss" in data["value"]

    def test_get_nonexistent_file(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "get", "nonexistent.toml"])
        assert result.exit_code == 1

    def test_get_nonexistent_key(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "get", "dominion.toml", "--key", "no.such.key"])
        assert result.exit_code == 1

    def test_get_subdirectory_file(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "get", "agents/researcher.toml", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["role"]["name"] == "Researcher"

    def test_get_path_traversal_blocked(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "get", "../secrets.toml"])
        assert result.exit_code == 1

    def test_get_absolute_path_blocked(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "get", "/etc/passwd"])
        assert result.exit_code == 1


class TestDataSet:
    """Tests for `data set`."""

    def test_set_string_value(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "set", "state.toml", "--key", "position.step", "--value", '"testing"'])
        assert result.exit_code == 0

        verify = runner.invoke(app, ["data", "get", "state.toml", "--key", "position.step"])
        assert "testing" in verify.stdout

    def test_set_integer_value(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "set", "state.toml", "--key", "position.wave", "--value", "5"])
        assert result.exit_code == 0

        verify = runner.invoke(app, ["data", "get", "state.toml", "--key", "position.wave", "--json"])
        data = json.loads(verify.stdout)
        assert data["value"] == 5

    def test_set_boolean_value(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "set", "state.toml", "--key", "init.completed", "--value", "false"])
        assert result.exit_code == 0

        verify = runner.invoke(app, ["data", "get", "state.toml", "--key", "init.completed", "--json"])
        data = json.loads(verify.stdout)
        assert data["value"] is False

    def test_set_creates_intermediate_tables(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "set", "state.toml", "--key", "custom.nested.key", "--value", '"hello"'])
        assert result.exit_code == 0

        verify = runner.invoke(app, ["data", "get", "state.toml", "--key", "custom.nested.key", "--json"])
        data = json.loads(verify.stdout)
        assert data["value"] == "hello"

    def test_set_invalid_json(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "set", "state.toml", "--key", "position.step", "--value", "not json"])
        assert result.exit_code == 1

    def test_set_null_rejected(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "set", "state.toml", "--key", "position.step", "--value", "null"])
        assert result.exit_code == 1

    def test_set_path_traversal_blocked(self, tmp_dominion: Path) -> None:
        result = runner.invoke(app, ["data", "set", "../evil.toml", "--key", "x", "--value", '"y"'])
        assert result.exit_code == 1
