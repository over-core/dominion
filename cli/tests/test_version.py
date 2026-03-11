"""Tests for version and top-level CLI flags."""

from __future__ import annotations

from typer.testing import CliRunner

from dominion_cli.app import app

runner = CliRunner()


class TestVersion:
    """Tests for --version flag."""

    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "dominion-cli 0.9.1" in result.stdout

    def test_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "dominion-cli" in result.stdout.lower() or "Dominion" in result.stdout

    def test_no_args_shows_help(self) -> None:
        result = runner.invoke(app, [])
        # Typer no_args_is_help=True exits with code 0 or 2 depending on version
        assert result.exit_code in (0, 2)
        assert "Usage" in result.stdout or "Commands" in result.stdout or "Options" in result.stdout
