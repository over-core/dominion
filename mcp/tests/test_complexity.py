"""Tests for complexity detection module."""

from pathlib import Path

import pytest

from dominion_mcp.core.complexity import (
    COMPLEXITY_LEVELS,
    PIPELINE_PROFILES,
    assess_complexity,
    get_dispatch_override,
    get_effective_steps,
    refine_complexity,
)


# -- assess_complexity -------------------------------------------------------


def test_assess_trivial_typo():
    assert assess_complexity("fix typo in readme") == "trivial"


def test_assess_trivial_rename():
    assert assess_complexity("rename the variable") == "trivial"


def test_assess_trivial_bump():
    assert assess_complexity("bump version to 2.0") == "trivial"


def test_assess_trivial_single_file_scope():
    assert assess_complexity("update the header", scope="config.py") == "trivial"


def test_assess_moderate_default():
    assert assess_complexity("add user authentication endpoint") == "moderate"


def test_assess_moderate_ambiguous():
    assert assess_complexity("do some work on the project") == "moderate"


def test_assess_complex_redesign():
    assert assess_complexity("redesign the data pipeline") == "complex"


def test_assess_complex_migrate():
    assert assess_complexity("migrate from REST to GraphQL") == "complex"


def test_assess_major_rewrite():
    assert assess_complexity("rewrite the entire backend architecture") == "major"


def test_assess_major_platform_wide():
    assert assess_complexity("platform-wide breaking change") == "major"


def test_assess_major_multi_service():
    assert assess_complexity("deploy across multi-service infrastructure") == "major"


# -- refine_complexity -------------------------------------------------------


def test_refine_no_research(dom_root: Path):
    """No research.toml → returns current level unchanged."""
    result = refine_complexity(dom_root)
    assert result in COMPLEXITY_LEVELS


def test_refine_upgrades_to_complex(dom_root_with_plan: Path):
    """Many high-severity findings → upgrade to complex."""
    from dominion_mcp.core.config import phase_path, write_toml

    p_path = phase_path(dom_root_with_plan, 1)
    research = {
        "findings": [
            {"severity": "high", "category": "architecture", "title": f"F{i}"}
            for i in range(3)
        ]
        + [
            {"severity": "medium", "category": "code-quality", "title": "F4"},
            {"severity": "low", "category": "testing", "title": "F5"},
            {"severity": "high", "category": "security", "title": "F6"},
        ]
    }
    write_toml(p_path / "research.toml", research)

    result = refine_complexity(dom_root_with_plan)
    assert result in ("complex", "major")


def test_refine_no_downgrade(dom_root_with_plan: Path):
    """Current level is complex, weak research → stays complex."""
    from dominion_mcp.core.config import write_toml, phase_path, read_toml

    # Set complexity_level directly in state.toml.
    state_path = dom_root_with_plan / "state.toml"
    state = read_toml(state_path)
    state.setdefault("position", {})["complexity_level"] = "complex"
    write_toml(state_path, state)

    p_path = phase_path(dom_root_with_plan, 1)
    research = {
        "findings": [
            {"severity": "low", "category": "code-quality", "title": "Minor"},
        ]
    }
    write_toml(p_path / "research.toml", research)

    result = refine_complexity(dom_root_with_plan)
    assert result == "complex"


def test_refine_specialist_referral_upgrades(dom_root_with_plan: Path):
    """Specialist referral triggers upgrade."""
    from dominion_mcp.core.config import phase_path, write_toml

    p_path = phase_path(dom_root_with_plan, 1)
    research = {
        "findings": [
            {
                "severity": "medium",
                "category": "performance",
                "title": "Perf issue",
                "specialist_referral": "analyst",
            },
        ]
    }
    write_toml(p_path / "research.toml", research)

    result = refine_complexity(dom_root_with_plan)
    assert result in ("complex", "major")


# -- get_effective_steps ------------------------------------------------------


def test_effective_steps_trivial():
    assert get_effective_steps("trivial") == ["execute"]


def test_effective_steps_moderate():
    steps = get_effective_steps("moderate")
    assert steps == ["research", "plan", "execute", "audit"]


def test_effective_steps_complex():
    steps = get_effective_steps("complex")
    assert len(steps) == 7


def test_effective_steps_major():
    steps = get_effective_steps("major")
    assert len(steps) == 7


def test_effective_steps_none():
    """No complexity → full pipeline."""
    steps = get_effective_steps(None)
    assert len(steps) == 7


def test_effective_steps_unknown():
    """Unknown level → full pipeline."""
    steps = get_effective_steps("unknown")
    assert len(steps) == 7


# -- get_dispatch_override ----------------------------------------------------


def test_dispatch_override_major_discuss():
    assert get_dispatch_override("major", "discuss") == "panel"


def test_dispatch_override_major_improve():
    assert get_dispatch_override("major", "improve") == "panel"


def test_dispatch_override_complex_discuss():
    """Complex doesn't override discuss."""
    assert get_dispatch_override("complex", "discuss") is None


def test_dispatch_override_none_level():
    assert get_dispatch_override(None, "discuss") is None


def test_dispatch_override_major_execute():
    """Execute has no override even at major."""
    assert get_dispatch_override("major", "execute") is None
