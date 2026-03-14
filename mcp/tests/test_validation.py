"""Tests for dominion_mcp.core.validation module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dominion_mcp.core.validation import validate_project


# ---------------------------------------------------------------------------
# validate_project
# ---------------------------------------------------------------------------


def test_validate_project_returns_checks(dom_root: Path) -> None:
    """validate_project returns a list of check results."""
    checks = validate_project(dom_root)
    assert isinstance(checks, list)
    assert all(isinstance(c, dict) for c in checks)
    assert all("check" in c and "status" in c for c in checks)


def test_validate_project_check_count(dom_root: Path) -> None:
    """validate_project returns exactly 11 checks."""
    checks = validate_project(dom_root)
    assert len(checks) == 11


def test_validate_project_all_pass_or_warn(dom_root: Path) -> None:
    """All checks pass or warn for the well-formed fixture."""
    checks = validate_project(dom_root)
    for check in checks:
        assert check["status"] in ("pass", "warn"), (
            f"Check '{check['check']}' failed: {check.get('detail', '')}"
        )


def test_validate_project_toml_integrity(dom_root: Path) -> None:
    """TOML integrity check passes."""
    checks = validate_project(dom_root)
    toml_check = next(c for c in checks if c["check"] == "TOML integrity")
    assert toml_check["status"] == "pass"


def test_validate_project_agent_consistency(dom_root: Path) -> None:
    """Agent TOML-MD consistency check passes."""
    checks = validate_project(dom_root)
    agent_check = next(c for c in checks if c["check"] == "Agent TOML-MD consistency")
    assert agent_check["status"] == "pass"


def test_validate_project_mcp_json(dom_root: Path) -> None:
    """.mcp.json check passes."""
    checks = validate_project(dom_root)
    mcp_check = next(c for c in checks if c["check"] == ".mcp.json")
    assert mcp_check["status"] == "pass"


def test_validate_project_settings_permissions(dom_root: Path) -> None:
    """Settings permissions check passes."""
    checks = validate_project(dom_root)
    settings_check = next(c for c in checks if c["check"] == "Settings permissions")
    assert settings_check["status"] == "pass"


def test_validate_project_dominion_config(dom_root: Path) -> None:
    """dominion.toml check passes."""
    checks = validate_project(dom_root)
    config_check = next(c for c in checks if c["check"] == "dominion.toml")
    assert config_check["status"] == "pass"


def test_validate_project_phase_structure(dom_root: Path) -> None:
    """Phase structure check passes."""
    checks = validate_project(dom_root)
    phase_check = next(c for c in checks if c["check"] == "Phase structure")
    assert phase_check["status"] == "pass"


def test_validate_project_methodology_sections(dom_root: Path) -> None:
    """Methodology sections check passes."""
    checks = validate_project(dom_root)
    meth_check = next(c for c in checks if c["check"] == "Methodology sections")
    assert meth_check["status"] == "pass"
