"""Tests for v0.3.0 complexity detection module."""

from pathlib import Path

import pytest

from dominion_mcp.core.complexity import (
    COMPLEXITY_LEVELS,
    DISPATCH_TABLE,
    PIPELINE_PROFILES,
    assess_complexity,
    get_dispatch,
    get_pipeline,
    refine_complexity,
)


# -- assess_complexity -------------------------------------------------------


def test_assess_trivial_typo():
    result = assess_complexity("fix typo in readme")
    assert result["complexity"] == "trivial"


def test_assess_trivial_rename():
    result = assess_complexity("rename the variable")
    assert result["complexity"] == "trivial"


def test_assess_trivial_bump():
    result = assess_complexity("bump version to 2.0")
    assert result["complexity"] == "trivial"


def test_assess_moderate_default():
    result = assess_complexity("add user authentication endpoint")
    assert result["complexity"] == "moderate"


def test_assess_moderate_ambiguous():
    result = assess_complexity("do some work on the project")
    assert result["complexity"] == "moderate"


def test_assess_complex_redesign():
    result = assess_complexity("redesign the data pipeline")
    assert result["complexity"] == "complex"


def test_assess_complex_migrate():
    result = assess_complexity("migrate from REST to GraphQL")
    assert result["complexity"] == "complex"


def test_assess_major_rewrite():
    result = assess_complexity("rewrite the entire backend architecture")
    assert result["complexity"] == "major"


def test_assess_major_platform_wide():
    result = assess_complexity("platform-wide breaking change")
    assert result["complexity"] == "major"


def test_assess_has_reasoning():
    result = assess_complexity("add rate limiting")
    assert "reasoning" in result
    assert "keywords_matched" in result


# -- get_pipeline ------------------------------------------------------------


def test_pipeline_trivial():
    assert get_pipeline("trivial") == ["execute"]


def test_pipeline_moderate():
    assert get_pipeline("moderate") == ["research", "plan", "execute", "review"]


def test_pipeline_complex():
    assert get_pipeline("complex") == ["discuss", "research", "plan", "execute", "review"]


def test_pipeline_major():
    assert get_pipeline("major") == ["discuss", "research", "plan", "execute", "review"]


def test_pipeline_unknown_defaults_complex():
    assert get_pipeline("unknown") == get_pipeline("complex")


# -- get_dispatch ------------------------------------------------------------


def test_dispatch_research_moderate():
    thread, agents = get_dispatch("research", "moderate", ["researcher", "architect"])
    assert thread == "B-Thread"
    assert len(agents) == 1
    assert agents[0]["role"] == "researcher"


def test_dispatch_research_complex():
    thread, agents = get_dispatch(
        "research", "complex",
        ["researcher", "innovation-engineer", "security-auditor"]
    )
    assert thread == "P-Thread"
    assert len(agents) == 3


def test_dispatch_review_complex():
    thread, agents = get_dispatch(
        "review", "complex",
        ["reviewer", "security-auditor", "analyst"]
    )
    assert thread == "P-Thread"
    assert len(agents) == 3


def test_dispatch_discuss_complex():
    thread, agents = get_dispatch(
        "discuss", "complex",
        ["architect", "security-auditor", "innovation-engineer"]
    )
    assert thread == "F-Thread"


def test_dispatch_degrades_to_bthread():
    """P-Thread with 1 active agent degrades to B-Thread."""
    thread, agents = get_dispatch("research", "complex", ["researcher"])
    assert thread == "B-Thread"
    assert len(agents) == 1


def test_dispatch_primary_role_required():
    """Missing primary role raises ValueError."""
    with pytest.raises(ValueError, match="Primary role 'researcher'"):
        get_dispatch("research", "moderate", ["architect"])


def test_dispatch_invalid_step_complexity():
    with pytest.raises(ValueError, match="No dispatch entry"):
        get_dispatch("research", "trivial", ["researcher"])


# -- DISPATCH_TABLE ----------------------------------------------------------


def test_dispatch_table_has_15_entries():
    assert len(DISPATCH_TABLE) == 15


def test_all_roles_in_dispatch_are_valid():
    valid_roles = {"researcher", "architect", "developer", "reviewer",
                   "security-auditor", "analyst", "innovation-engineer"}
    for (step, complexity), (thread, agents) in DISPATCH_TABLE.items():
        for role, model in agents:
            assert role in valid_roles, f"Unknown role '{role}' in ({step}, {complexity})"


# -- refine_complexity -------------------------------------------------------


def test_refine_no_findings(dom_root: Path):
    """No findings → no change."""
    result = refine_complexity(dom_root, "01")
    assert result["upgraded"] is False


def test_refine_upgrades(dom_root_with_plan: Path):
    """High severity findings → upgrade."""
    from dominion_mcp.core.config import write_toml

    findings_dir = dom_root_with_plan / "phases" / "01" / "research" / "output"
    findings_dir.mkdir(parents=True, exist_ok=True)
    write_toml(findings_dir / "findings.toml", {
        "findings": {
            "researcher": {
                "items": [
                    {"severity": "high", "category": "security", "description": "vuln1"},
                    {"severity": "high", "category": "architecture", "description": "vuln2"},
                    {"severity": "high", "category": "testing", "description": "vuln3"},
                ]
            }
        }
    })

    result = refine_complexity(dom_root_with_plan, "01")
    assert result["refined"] in ("complex", "major")


def test_refine_no_downgrade(dom_root_with_plan: Path):
    """Current complex + weak findings → stays complex."""
    from dominion_mcp.core.config import write_toml, read_toml

    state_path = dom_root_with_plan / "state.toml"
    state = read_toml(state_path)
    state.setdefault("position", {})["complexity_level"] = "complex"
    write_toml(state_path, state)

    findings_dir = dom_root_with_plan / "phases" / "01" / "research" / "output"
    findings_dir.mkdir(parents=True, exist_ok=True)
    write_toml(findings_dir / "findings.toml", {
        "findings": {
            "researcher": {
                "items": [
                    {"severity": "low", "category": "code-quality", "description": "minor"},
                ]
            }
        }
    })

    result = refine_complexity(dom_root_with_plan, "01")
    assert result["refined"] == "complex"
    assert result["upgraded"] is False
