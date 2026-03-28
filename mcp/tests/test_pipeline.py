"""Tests for v0.5.1 pipeline module."""

from dominion_mcp.core.pipeline import (
    CANONICAL_ORDER,
    PRIMARY_ROLES,
    suggest_pipeline,
    valid_steps,
    validate_pipeline,
)

import pytest


# -- suggest_pipeline -------------------------------------------------------


def test_suggest_trivial_typo():
    result = suggest_pipeline("fix typo in readme")
    assert result["pipeline"] == ["execute"]


def test_suggest_trivial_rename():
    result = suggest_pipeline("rename the variable")
    assert result["pipeline"] == ["execute"]


def test_suggest_trivial_bump():
    result = suggest_pipeline("bump version to 2.0")
    assert result["pipeline"] == ["execute"]


def test_suggest_default_moderate():
    result = suggest_pipeline("add user authentication endpoint")
    assert result["pipeline"] == ["research", "plan", "execute", "review"]


def test_suggest_ambiguous():
    result = suggest_pipeline("do some work on the project")
    assert result["pipeline"] == ["research", "plan", "execute", "review"]


def test_suggest_complex_redesign():
    result = suggest_pipeline("redesign the data pipeline")
    assert result["pipeline"] == ["discuss", "research", "plan", "execute", "review"]


def test_suggest_complex_migrate():
    result = suggest_pipeline("migrate from REST to GraphQL")
    assert result["pipeline"] == ["discuss", "research", "plan", "execute", "review"]


def test_suggest_major_rewrite():
    result = suggest_pipeline("rewrite the entire backend architecture")
    assert result["pipeline"] == ["discuss", "research", "plan", "execute", "review"]


def test_suggest_major_platform_wide():
    result = suggest_pipeline("platform-wide breaking change")
    assert result["pipeline"] == ["discuss", "research", "plan", "execute", "review"]


def test_suggest_has_reasoning():
    result = suggest_pipeline("add rate limiting")
    assert "reasoning" in result
    assert "keywords_matched" in result


def test_suggest_specified_with_design_doc():
    result = suggest_pipeline("implement per design doc", has_design_doc=True)
    assert result["pipeline"] == ["plan", "execute", "review"]


def test_suggest_design_doc_no_override_for_major():
    result = suggest_pipeline("rewrite the entire backend", has_design_doc=True)
    assert result["pipeline"] == ["discuss", "research", "plan", "execute", "review"]


def test_suggest_design_doc_no_override_for_complex():
    result = suggest_pipeline("redesign the data pipeline", has_design_doc=True)
    assert result["pipeline"] == ["discuss", "research", "plan", "execute", "review"]


def test_suggest_design_doc_false_gives_standard():
    result = suggest_pipeline("add endpoint", has_design_doc=False)
    assert result["pipeline"] == ["research", "plan", "execute", "review"]


def test_suggest_analysis_analyze():
    result = suggest_pipeline("Analyze codebase: document patterns and flag anti-patterns")
    assert result["pipeline"] == ["research", "review"]


def test_suggest_analysis_audit():
    result = suggest_pipeline("audit security and assess test coverage")
    assert result["pipeline"] == ["research", "review"]


# -- validate_pipeline ------------------------------------------------------


def test_validate_preserves_order():
    result = validate_pipeline(["research", "plan", "execute", "review"])
    assert result == ["research", "plan", "execute", "review"]


def test_validate_subset():
    result = validate_pipeline(["research", "review"])
    assert result == ["research", "review"]


def test_validate_rejects_wrong_order():
    with pytest.raises(ValueError, match="canonical order"):
        validate_pipeline(["review", "research"])


def test_validate_rejects_execute_before_plan():
    with pytest.raises(ValueError, match="canonical order"):
        validate_pipeline(["execute", "plan"])


def test_validate_single_step():
    result = validate_pipeline(["execute"])
    assert result == ["execute"]


def test_validate_config_insertion():
    config = {
        "agents": {"active": ["security-auditor"]},
        "pipeline": {"insertions": [
            {"name": "security-review", "after": "execute", "when": "security-auditor"}
        ]},
    }
    result = validate_pipeline(["research", "plan", "execute", "review"], config)
    assert result == ["research", "plan", "execute", "security-review", "review"]


def test_validate_config_insertion_inactive_agent():
    config = {
        "agents": {"active": ["researcher"]},
        "pipeline": {"insertions": [
            {"name": "security-review", "after": "execute", "when": "security-auditor"}
        ]},
    }
    result = validate_pipeline(["research", "plan", "execute", "review"], config)
    assert result == ["research", "plan", "execute", "review"]


def test_validate_config_insertion_missing_after():
    config = {
        "agents": {"active": ["security-auditor"]},
        "pipeline": {"insertions": [
            {"name": "security-review", "after": "nonexistent", "when": "security-auditor"}
        ]},
    }
    result = validate_pipeline(["research", "plan", "execute", "review"], config)
    assert result == ["research", "plan", "execute", "review"]


# -- valid_steps ------------------------------------------------------------


def test_valid_steps_base():
    steps = valid_steps()
    assert "idle" in steps
    assert "research" in steps
    assert "execute" in steps


def test_valid_steps_with_config():
    config = {"pipeline": {"insertions": [
        {"name": "security-review"},
        {"name": "compliance-check"},
    ]}}
    steps = valid_steps(config)
    assert "security-review" in steps
    assert "compliance-check" in steps
    assert "research" in steps


# -- PRIMARY_ROLES ----------------------------------------------------------


def test_primary_roles_covers_all_steps():
    for step in CANONICAL_ORDER:
        assert step in PRIMARY_ROLES


def test_canonical_order():
    assert CANONICAL_ORDER == ["discuss", "research", "plan", "execute", "review"]
