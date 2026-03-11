"""Tests for plan management commands."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from dominion_cli.app import app

runner = CliRunner()


class TestPlanTask:
    """Tests for `plan task`."""

    def test_task_json(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "task", "1-01", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "1-01"
        assert data["title"] == "Set up project structure"
        assert data["wave"] == 1
        assert data["agent"] == "developer"
        assert isinstance(data["file_ownership"], list)
        assert isinstance(data["acceptance_criteria"], list)

    def test_task_human(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "task", "1-01"])
        assert result.exit_code == 0
        assert "Set up project structure" in result.stdout
        assert "developer" in result.stdout

    def test_task_not_found(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "task", "99-99"])
        assert result.exit_code == 1

    def test_task_files_only(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "task", "1-01", "--files", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "file_ownership" in data
        assert "src/main.py" in data["file_ownership"]

    def test_task_criteria_only(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "task", "1-01", "--criteria", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "acceptance_criteria" in data
        assert len(data["acceptance_criteria"]) >= 2


class TestPlanWave:
    """Tests for `plan wave`."""

    def test_wave_json(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "wave", "1", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        # Wave 1 has tasks 1-01 and 1-02
        assert len(data) == 2
        ids = {row["id"] for row in data}
        assert "1-01" in ids
        assert "1-02" in ids

    def test_wave_empty(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "wave", "99"])
        assert result.exit_code == 0
        assert "No tasks" in result.stdout

    def test_wave_two(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "wave", "2", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["id"] == "1-03"


class TestPlanDeps:
    """Tests for `plan deps`."""

    def test_deps_no_dependencies(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "deps", "1-01"])
        assert result.exit_code == 0
        assert "1-01" in result.stdout

    def test_deps_with_dependencies(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "deps", "1-03"])
        assert result.exit_code == 0
        assert "1-03" in result.stdout
        assert "1-01" in result.stdout
        assert "1-02" in result.stdout

    def test_deps_not_found(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "deps", "99-99"])
        assert result.exit_code == 1


class TestPlanValidate:
    """Tests for `plan validate`."""

    def test_validate_valid_plan(self, tmp_dominion_with_phase: Path) -> None:
        plan_path = str(
            tmp_dominion_with_phase / ".dominion" / "phases" / "1" / "plan.toml"
        )
        result = runner.invoke(app, ["plan", "validate", plan_path, "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "checks" in data
        assert "summary" in data
        # The fixture plan should pass all checks
        assert data["summary"]["failed"] == 0

    def test_validate_check_names(self, tmp_dominion_with_phase: Path) -> None:
        plan_path = str(
            tmp_dominion_with_phase / ".dominion" / "phases" / "1" / "plan.toml"
        )
        result = runner.invoke(app, ["plan", "validate", plan_path, "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        check_names = {c["name"] for c in data["checks"]}
        assert "Task ID format" in check_names
        assert "Dependency references" in check_names
        assert "No circular deps" in check_names
        assert "Acceptance criteria" in check_names
        assert "File ownership" in check_names
        assert "Wave numbering" in check_names


class TestPlanIndex:
    """Tests for `plan index` (wave auto-assignment)."""

    def test_index(self, tmp_dominion_with_phase: Path) -> None:
        result = runner.invoke(app, ["plan", "index"])
        assert result.exit_code == 0
        assert "Wave 1" in result.stdout
        assert "Wave 2" in result.stdout
        assert "Indexed" in result.stdout
