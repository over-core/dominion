"""Tests for panel mode module."""

from pathlib import Path

import pytest

from dominion_mcp.core.panel import (
    PANEL_CONFIGURATIONS,
    get_panel_context,
    get_panel_participants,
    get_step_panel_type,
)


# -- get_panel_participants ---------------------------------------------------


def test_participants_architecture():
    active = ["architect", "security-auditor", "analyst", "developer"]
    result = get_panel_participants("architecture", active)
    assert result == ["architect", "security-auditor", "analyst"]


def test_participants_filters_inactive():
    active = ["architect", "reviewer"]
    result = get_panel_participants("architecture", active)
    assert result == ["architect"]
    assert "security-auditor" not in result
    assert "analyst" not in result


def test_participants_feature_strategy():
    active = ["architect", "innovation-engineer", "reviewer"]
    result = get_panel_participants("feature_strategy", active)
    assert result == ["architect", "innovation-engineer", "reviewer"]


def test_participants_unknown_type():
    with pytest.raises(ValueError, match="Unknown panel decision type"):
        get_panel_participants("nonexistent", ["architect"])


# -- get_panel_context --------------------------------------------------------


def test_panel_context_structure(dom_root: Path):
    """Panel context has required fields."""
    result = get_panel_context(dom_root, "architecture", "Should we use microservices?")
    assert result["decision_type"] == "architecture"
    assert result["topic"] == "Should we use microservices?"
    assert isinstance(result["participants"], list)
    assert len(result["participants"]) >= 2
    assert "facilitation" in result
    assert "output_format" in result


def test_panel_context_topic_in_facilitation(dom_root: Path):
    topic = "Database migration strategy"
    result = get_panel_context(dom_root, "architecture", topic)
    assert topic in result["facilitation"]


def test_panel_context_perspectives(dom_root: Path):
    """Perspectives dict contains methodology for available agents."""
    result = get_panel_context(dom_root, "architecture", "test topic")
    assert isinstance(result["perspectives"], dict)


# -- get_step_panel_type ------------------------------------------------------


def test_step_panel_type_discuss():
    assert get_step_panel_type("discuss") == "architecture"


def test_step_panel_type_improve():
    assert get_step_panel_type("improve") == "retrospective"


def test_step_panel_type_unknown():
    """Unknown step defaults to architecture."""
    assert get_step_panel_type("execute") == "architecture"
