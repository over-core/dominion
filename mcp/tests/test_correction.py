"""Tests for course correction module."""

from pathlib import Path

import pytest

from dominion_mcp.core.correction import (
    assess_verdict,
    get_correction_action,
    should_halt,
)


# -- assess_verdict -----------------------------------------------------------


def test_verdict_go_no_findings(dom_root_with_plan: Path):
    """No review.toml → go."""
    result = assess_verdict(dom_root_with_plan)
    assert result["verdict"] == "go"
    assert result["critical_findings"] == 0


def test_verdict_go_no_phase(dom_root: Path):
    """No active phase → go."""
    result = assess_verdict(dom_root)
    assert result["verdict"] == "go"


def test_verdict_warnings(dom_root_with_plan: Path):
    """Medium findings → go-with-warnings."""
    from dominion_mcp.core.config import phase_path, write_toml

    p_path = phase_path(dom_root_with_plan, 1)
    review = {
        "findings": [
            {"severity": "medium", "category": "code-quality", "title": "Naming"},
            {"severity": "low", "category": "style", "title": "Format"},
        ]
    }
    write_toml(p_path / "review.toml", review)

    result = assess_verdict(dom_root_with_plan)
    assert result["verdict"] == "go-with-warnings"
    assert result["warning_findings"] == 2


def test_verdict_no_go_high_severity(dom_root_with_plan: Path):
    """High-severity findings → no-go."""
    from dominion_mcp.core.config import phase_path, write_toml

    p_path = phase_path(dom_root_with_plan, 1)
    review = {
        "findings": [
            {"severity": "high", "category": "architecture", "title": "Breaking API"},
            {"severity": "low", "category": "style", "title": "Format"},
        ]
    }
    write_toml(p_path / "review.toml", review)

    result = assess_verdict(dom_root_with_plan)
    assert result["verdict"] == "no-go"
    assert result["critical_findings"] >= 1
    assert len(result["blocking_findings"]) >= 1


def test_verdict_medium_security_blocks(dom_root_with_plan: Path):
    """Medium security findings are blocking."""
    from dominion_mcp.core.config import phase_path, write_toml

    p_path = phase_path(dom_root_with_plan, 1)
    review = {
        "findings": [
            {"severity": "medium", "category": "security", "title": "Auth bypass"},
        ]
    }
    write_toml(p_path / "review.toml", review)

    result = assess_verdict(dom_root_with_plan)
    assert result["verdict"] == "no-go"


# -- should_halt --------------------------------------------------------------


def test_halt_critical_threshold(dom_root_with_plan: Path):
    """halt_on_severity=critical, no-go verdict → halt."""
    verdict = {"verdict": "no-go"}
    assert should_halt(dom_root_with_plan, verdict) is True


def test_halt_critical_warnings_pass(dom_root_with_plan: Path):
    """halt_on_severity=critical, go-with-warnings → no halt."""
    verdict = {"verdict": "go-with-warnings"}
    assert should_halt(dom_root_with_plan, verdict) is False


def test_halt_warning_threshold(dom_root_with_plan: Path):
    """halt_on_severity=warning, go-with-warnings → halt."""
    from dominion_mcp.core.config import write_toml

    # Override dominion.toml with warning threshold.
    dominion_path = dom_root_with_plan / "dominion.toml"
    from dominion_mcp.core.config import read_toml
    dominion = read_toml(dominion_path)
    dominion.setdefault("auto", {})["halt_on_severity"] = "warning"
    write_toml(dominion_path, dominion)

    verdict = {"verdict": "go-with-warnings"}
    assert should_halt(dom_root_with_plan, verdict) is True


def test_halt_none_threshold(dom_root_with_plan: Path):
    """halt_on_severity=none → never halt."""
    from dominion_mcp.core.config import read_toml, write_toml

    dominion_path = dom_root_with_plan / "dominion.toml"
    dominion = read_toml(dominion_path)
    dominion.setdefault("auto", {})["halt_on_severity"] = "none"
    write_toml(dominion_path, dominion)

    verdict = {"verdict": "no-go"}
    assert should_halt(dom_root_with_plan, verdict) is False


# -- get_correction_action ----------------------------------------------------


def test_action_proceed_go(dom_root_with_plan: Path):
    verdict = {"verdict": "go"}
    result = get_correction_action(dom_root_with_plan, verdict)
    assert result["action"] == "proceed"


def test_action_halt_interactive(dom_root_with_plan: Path):
    """Interactive mode + no-go → halt."""
    verdict = {"verdict": "no-go", "summary": "Issues found", "blocking_findings": [{"title": "Bug"}]}
    result = get_correction_action(dom_root_with_plan, verdict)
    assert result["action"] == "halt"
    assert len(result["blocking_findings"]) >= 1


def test_action_auto_fix(dom_root_with_plan: Path):
    """Auto mode + no-go + attempts remaining → auto_fix."""
    from dominion_mcp.core.config import read_toml, write_toml

    dominion_path = dom_root_with_plan / "dominion.toml"
    dominion = read_toml(dominion_path)
    dominion["autonomy"] = {"mode": "auto"}
    dominion.setdefault("auto", {})["halt_on_severity"] = "critical"
    dominion["auto"]["max_fix_attempts"] = 2
    write_toml(dominion_path, dominion)

    verdict = {"verdict": "no-go", "summary": "Issues", "blocking_findings": [{"title": "Bug"}]}
    result = get_correction_action(dom_root_with_plan, verdict)
    assert result["action"] == "auto_fix"
    assert result["fix_attempts_remaining"] == 1
