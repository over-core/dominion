"""Tests for dominion_mcp.core.methodology module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dominion_mcp.core.methodology import (
    MODEL_BUDGETS,
    assemble_methodology,
    curate_sections,
    evaluate_conditions,
    get_budget,
    get_condition_signals,
)


# ---------------------------------------------------------------------------
# get_budget
# ---------------------------------------------------------------------------


def test_get_budget_opus() -> None:
    """get_budget returns 500000 for opus model."""
    agent = {"agent": {"model": "opus"}}
    assert get_budget(agent) == 500_000


def test_get_budget_sonnet() -> None:
    """get_budget returns 150000 for sonnet model."""
    agent = {"agent": {"model": "sonnet"}}
    assert get_budget(agent) == 150_000


def test_get_budget_override() -> None:
    """get_budget uses max_tokens override when present."""
    agent = {"agent": {"model": "opus", "max_tokens": 300_000}}
    assert get_budget(agent) == 300_000


def test_get_budget_unknown_model() -> None:
    """get_budget returns default 150000 for unknown model."""
    agent = {"agent": {"model": "unknown"}}
    assert get_budget(agent) == 150_000


def test_get_budget_missing_agent_section() -> None:
    """get_budget handles missing agent section gracefully."""
    assert get_budget({}) == 150_000


# ---------------------------------------------------------------------------
# get_condition_signals
# ---------------------------------------------------------------------------


def test_get_condition_signals_languages(dom_root: Path) -> None:
    """get_condition_signals returns correct languages from dominion.toml."""
    signals = get_condition_signals(dom_root)
    assert signals["languages"] == ["python"]


def test_get_condition_signals_frameworks(dom_root: Path) -> None:
    """get_condition_signals returns correct frameworks."""
    signals = get_condition_signals(dom_root)
    assert signals["framework"] == ["fastapi"]


def test_get_condition_signals_tools(dom_root: Path) -> None:
    """get_condition_signals returns enabled tools."""
    signals = get_condition_signals(dom_root)
    assert "serena" in signals["tools_available"]
    assert "echovault" in signals["tools_available"]


def test_get_condition_signals_agents(dom_root: Path) -> None:
    """get_condition_signals returns active agents."""
    signals = get_condition_signals(dom_root)
    assert "security-auditor" in signals["agents_active"]


def test_get_condition_signals_direction(dom_root: Path) -> None:
    """get_condition_signals returns direction mode."""
    signals = get_condition_signals(dom_root)
    assert signals["direction_mode"] == "improve"


def test_get_condition_signals_testing_style(dom_root: Path) -> None:
    """get_condition_signals returns testing styles from style.toml."""
    signals = get_condition_signals(dom_root)
    assert signals["testing_style"] == ["tdd"]


# ---------------------------------------------------------------------------
# evaluate_conditions
# ---------------------------------------------------------------------------


def test_evaluate_conditions_matching_list(dom_root: Path) -> None:
    """evaluate_conditions returns True when language condition matches."""
    signals = get_condition_signals(dom_root)
    assert evaluate_conditions({"languages": ["python"]}, signals) is True


def test_evaluate_conditions_non_matching_list(dom_root: Path) -> None:
    """evaluate_conditions returns False when language does not match."""
    signals = get_condition_signals(dom_root)
    assert evaluate_conditions({"languages": ["rust"]}, signals) is False


def test_evaluate_conditions_empty_conditions() -> None:
    """Empty conditions dict always evaluates to True."""
    assert evaluate_conditions({}, {"anything": "value"}) is True


def test_evaluate_conditions_missing_signal() -> None:
    """Returns False when signal key is not present."""
    assert evaluate_conditions({"unknown_key": ["val"]}, {}) is False


def test_evaluate_conditions_multiple_conditions_all_match(dom_root: Path) -> None:
    """Returns True when ALL conditions match (AND logic)."""
    signals = get_condition_signals(dom_root)
    result = evaluate_conditions(
        {"languages": ["python"], "tools_available": ["serena"]}, signals
    )
    assert result is True


def test_evaluate_conditions_multiple_conditions_one_fails(dom_root: Path) -> None:
    """Returns False when one condition fails (AND logic)."""
    signals = get_condition_signals(dom_root)
    result = evaluate_conditions(
        {"languages": ["python"], "tools_available": ["nonexistent"]}, signals
    )
    assert result is False


def test_evaluate_conditions_scalar_required_in_list() -> None:
    """Scalar required value checks membership in list signal."""
    signals = {"languages": ["python", "go"]}
    assert evaluate_conditions({"languages": "python"}, signals) is True
    assert evaluate_conditions({"languages": "rust"}, signals) is False


def test_evaluate_conditions_scalar_to_scalar() -> None:
    """Scalar required value checks equality against scalar signal."""
    signals = {"direction_mode": "improve"}
    assert evaluate_conditions({"direction_mode": "improve"}, signals) is True
    assert evaluate_conditions({"direction_mode": "maintain"}, signals) is False


# ---------------------------------------------------------------------------
# curate_sections
# ---------------------------------------------------------------------------


def test_curate_sections_always_include() -> None:
    """always_include sections are always in the result."""
    sections = [{"id": "core", "always_include": True}]
    result = curate_sections(sections, {}, "sonnet")
    assert len(result) == 1
    assert result[0]["id"] == "core"


def test_curate_sections_opus_permissive(dom_root: Path) -> None:
    """Opus mode includes sections where ANY condition key matches."""
    signals = get_condition_signals(dom_root)
    sections = [
        {
            "id": "multi-cond",
            "conditions": {"languages": ["python"], "phase_type": ["brownfield"]},
        }
    ]
    # Opus: only one key needs to match. languages matches, phase_type doesn't.
    result = curate_sections(sections, signals, "opus")
    assert len(result) == 1


def test_curate_sections_sonnet_strict(dom_root: Path) -> None:
    """Sonnet mode requires ALL conditions to match."""
    signals = get_condition_signals(dom_root)
    sections = [
        {
            "id": "multi-cond",
            "conditions": {"languages": ["python"], "phase_type": ["brownfield"]},
        }
    ]
    # Sonnet: both must match. phase_type is None, so it fails.
    result = curate_sections(sections, signals, "sonnet")
    assert len(result) == 0


def test_curate_sections_sonnet_all_match(dom_root: Path) -> None:
    """Sonnet includes sections when all conditions match."""
    signals = get_condition_signals(dom_root)
    sections = [
        {
            "id": "python-serena",
            "conditions": {"languages": ["python"], "tools_available": ["serena"]},
        }
    ]
    result = curate_sections(sections, signals, "sonnet")
    assert len(result) == 1


def test_curate_sections_no_conditions() -> None:
    """Sections with no conditions are always included."""
    sections = [{"id": "unconditioned"}]
    result = curate_sections(sections, {}, "sonnet")
    assert len(result) == 1


# ---------------------------------------------------------------------------
# assemble_methodology
# ---------------------------------------------------------------------------


def test_assemble_methodology_returns_content(dom_root: Path) -> None:
    """assemble_methodology returns non-empty string with section content."""
    signals = get_condition_signals(dom_root)
    result = assemble_methodology(dom_root, "researcher", signals, "opus")
    assert len(result) > 0
    assert "Researcher" in result


def test_assemble_methodology_includes_core(dom_root: Path) -> None:
    """assemble_methodology always includes the core section."""
    signals = get_condition_signals(dom_root)
    result = assemble_methodology(dom_root, "researcher", signals, "opus")
    assert "You are the Researcher agent" in result


def test_assemble_methodology_includes_conditional_for_opus(dom_root: Path) -> None:
    """Opus includes conditional sections that partially match."""
    signals = get_condition_signals(dom_root)
    result = assemble_methodology(dom_root, "researcher", signals, "opus")
    # Python research section should be included (language matches)
    assert "Python Research" in result
    # Serena section should be included (tool available)
    assert "Serena Workflow" in result


def test_assemble_methodology_developer(dom_root: Path) -> None:
    """assemble_methodology works for developer role."""
    signals = get_condition_signals(dom_root)
    result = assemble_methodology(dom_root, "developer", signals, "sonnet")
    assert "Developer" in result
    # TDD section should match (testing_style=["tdd"] from style.toml)
    assert "TDD Protocol" in result
