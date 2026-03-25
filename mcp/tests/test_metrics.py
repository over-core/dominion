"""Tests for core/metrics.py — effort parsing, scoring, metric commands, delta."""

from __future__ import annotations

from dominion_mcp.core.metrics import (
    _WEIGHT_BUCKETS,
    _infer_category,
    aggregate_effort,
    compute_delta,
    compute_quality_score,
    format_metrics_section,
    get_metric_commands,
    parse_effort_level,
    validate_effort_level,
)


# ---------------------------------------------------------------------------
# parse_effort_level
# ---------------------------------------------------------------------------


def test_parse_effort_level_valid():
    assert parse_effort_level(1) == 1
    assert parse_effort_level(5) == 5
    assert parse_effort_level(10) == 10


def test_parse_effort_level_string():
    assert parse_effort_level("3") == 3
    assert parse_effort_level("10") == 10


def test_parse_effort_level_none():
    assert parse_effort_level(None) is None


def test_parse_effort_level_out_of_range():
    assert parse_effort_level(0) is None
    assert parse_effort_level(11) is None
    assert parse_effort_level(-1) is None


def test_parse_effort_level_garbage():
    assert parse_effort_level("high") is None
    assert parse_effort_level("") is None
    assert parse_effort_level("2h") is None


# ---------------------------------------------------------------------------
# validate_effort_level
# ---------------------------------------------------------------------------


def test_validate_effort_level_valid():
    for level in range(1, 11):
        assert validate_effort_level(level) is None


def test_validate_effort_level_absent():
    assert validate_effort_level(None) is None


def test_validate_effort_level_invalid():
    warning = validate_effort_level(15)
    assert warning is not None
    assert "1-10" in warning

    warning = validate_effort_level("bogus")
    assert warning is not None
    assert "1-10" in warning


# ---------------------------------------------------------------------------
# aggregate_effort
# ---------------------------------------------------------------------------


def test_aggregate_effort_mixed():
    items = [
        {"severity": "high", "effort": 2},
        {"severity": "medium", "effort": 5},
        {"severity": "low", "effort": 8},
    ]
    result = aggregate_effort(items)
    assert result["mean"] == 5.0
    assert result["max"] == 8
    assert result["distribution"] == {"localized": 1, "cross_cutting": 1, "structural": 1}
    assert result["with_effort"] == 3
    assert result["without_effort"] == 0


def test_aggregate_effort_with_missing():
    items = [
        {"severity": "high", "effort": 3},
        {"severity": "low"},
    ]
    result = aggregate_effort(items)
    assert result["mean"] == 3.0
    assert result["max"] == 3
    assert result["with_effort"] == 1
    assert result["without_effort"] == 1


def test_aggregate_effort_empty():
    result = aggregate_effort([])
    assert result["mean"] == 0.0
    assert result["max"] == 0
    assert result["with_effort"] == 0
    assert result["without_effort"] == 0


def test_aggregate_effort_all_without():
    items = [{"severity": "high"}, {"severity": "low"}]
    result = aggregate_effort(items)
    assert result["mean"] == 0.0
    assert result["without_effort"] == 2


def test_aggregate_effort_distribution_localized():
    items = [{"effort": 1}, {"effort": 2}, {"effort": 3}]
    result = aggregate_effort(items)
    assert result["distribution"]["localized"] == 3
    assert result["distribution"]["cross_cutting"] == 0
    assert result["distribution"]["structural"] == 0


def test_aggregate_effort_string_values():
    """Effort values as strings (from JSON) should parse correctly."""
    items = [{"effort": "4"}, {"effort": "7"}]
    result = aggregate_effort(items)
    assert result["mean"] == 5.5
    assert result["max"] == 7


# ---------------------------------------------------------------------------
# get_metric_commands
# ---------------------------------------------------------------------------


def test_get_metric_commands_python():
    cmds = get_metric_commands(["python"])
    names = [c["name"] for c in cmds]
    assert "loc" in names
    assert "test_count" in names
    assert "todo_count" in names


def test_get_metric_commands_with_cli_tools():
    cmds = get_metric_commands(["python"], cli_tools=["radon"])
    names = [c["name"] for c in cmds]
    assert "complexity_avg" in names
    assert "maintainability" in names


def test_get_metric_commands_dedup():
    cmds = get_metric_commands(["python", "typescript"])
    loc_cmds = [c for c in cmds if c["name"] == "loc"]
    assert len(loc_cmds) == 1


def test_get_metric_commands_unknown_language():
    assert get_metric_commands(["cobol"]) == []


def test_get_metric_commands_empty():
    assert get_metric_commands([]) == []


# ---------------------------------------------------------------------------
# format_metrics_section
# ---------------------------------------------------------------------------


def test_format_metrics_section():
    section = format_metrics_section({"Python LOC": "12345", "Test files": "42"})
    assert "## Pre-Analysis Metrics" in section
    assert "12345" in section
    assert "42" in section


def test_format_metrics_section_empty():
    assert format_metrics_section({}) == ""


# ---------------------------------------------------------------------------
# compute_quality_score
# ---------------------------------------------------------------------------


def test_score_no_findings():
    result = compute_quality_score([])
    assert result["score"] == 10.0
    assert result["deductions"] == 0


def test_score_critical_security():
    items = [{"severity": "critical", "category": "security"}]
    result = compute_quality_score(items)
    # security bucket: 10 - 2.0 = 8.0, weight 0.15 → 1.2
    # other buckets untouched: 10 * (0.25+0.20+0.20+0.10+0.10) = 8.5
    # total = 8.5 + 1.2 = 9.7
    assert result["score"] == 9.7
    assert result["deductions"] == 1


def test_score_verified_fixed_excluded():
    items = [
        {"severity": "critical", "category": "security", "action": "verified-fixed"},
        {"severity": "medium", "category": "style"},
    ]
    result = compute_quality_score(items)
    # Only style deduction: code_quality bucket 10 - 0.3 = 9.7, weight 0.20
    # all others at 10
    assert result["deductions"] == 1
    assert result["score"] > 9.0


def test_score_warn_excluded():
    items = [{"severity": "high", "category": "security", "action": "warn"}]
    result = compute_quality_score(items)
    assert result["score"] == 10.0


def test_score_floor_at_zero():
    items = [{"severity": "critical", "category": "security"} for _ in range(20)]
    result = compute_quality_score(items)
    assert result["score"] >= 0.0
    assert result["breakdown"]["security"]["raw"] == 0.0


def test_score_mixed_buckets():
    items = [
        {"severity": "high", "category": "security"},       # sec: 10-1.0=9.0
        {"severity": "medium", "category": "performance"},   # perf: 10-0.3=9.7
        {"severity": "low", "category": "documentation"},    # doc: 10-0.1=9.9
    ]
    result = compute_quality_score(items)
    assert result["deductions"] == 3
    # Untouched buckets: arch 10*0.25=2.5, cq 10*0.20=2.0, test 10*0.20=2.0
    # Changed: sec 9.0*0.15=1.35, perf 9.7*0.10=0.97, doc 9.9*0.10=0.99
    expected = 2.5 + 2.0 + 2.0 + 1.35 + 0.97 + 0.99
    assert result["score"] == round(expected, 1)


def test_score_unknown_category_defaults_to_code_quality():
    items = [{"severity": "medium", "category": "unicorns"}]
    result = compute_quality_score(items)
    assert result["breakdown"]["code_quality"]["raw"] == 9.7


def test_score_weights_sum_to_one():
    total = sum(w for w, _ in _WEIGHT_BUCKETS.values())
    assert abs(total - 1.0) < 0.001


# ---------------------------------------------------------------------------
# compute_delta
# ---------------------------------------------------------------------------


def test_delta_no_baseline():
    current = [{"category": "security", "file": "a.py"}]
    result = compute_delta(current, knowledge_entries=[])
    assert result["new"] == 1
    assert result["resolved"] == 0
    assert result["trend"] == "baseline"


def test_delta_all_resolved():
    current: list[dict] = []
    knowledge = [
        {"tags": ["review"], "topic": "security-issues", "referenced_files": ["a.py"]},
    ]
    result = compute_delta(current, knowledge)
    assert result["resolved"] == 1
    assert result["new"] == 0
    assert result["trend"] == "improving"


def test_delta_persistent():
    current = [{"category": "security", "file": "a.py"}]
    knowledge = [
        {"tags": ["review"], "topic": "security-issues", "referenced_files": ["a.py"]},
    ]
    result = compute_delta(current, knowledge)
    assert result["persistent"] == 1
    assert result["new"] == 0
    assert result["resolved"] == 0
    assert result["trend"] == "stable"


def test_delta_mixed():
    current = [
        {"category": "security", "file": "a.py"},   # persistent
        {"category": "performance", "file": "c.py"}, # new
    ]
    knowledge = [
        {"tags": ["review"], "topic": "security-check", "referenced_files": ["a.py"]},
        {"tags": ["review"], "topic": "quality-review", "referenced_files": ["b.py"]},
    ]
    result = compute_delta(current, knowledge)
    assert result["new"] == 1
    assert result["resolved"] == 1
    assert result["persistent"] == 1
    assert result["trend"] == "stable"


def test_delta_uses_finding_id():
    current = [{"finding_id": "sa-01", "category": "security", "file": "a.py"}]
    knowledge = []  # no baseline — all new
    result = compute_delta(current, knowledge)
    assert result["new"] == 1
    assert result["trend"] == "baseline"


def test_delta_ignores_non_review_knowledge():
    current = [{"category": "security", "file": "a.py"}]
    knowledge = [
        {"tags": ["research"], "topic": "security-stuff", "referenced_files": ["a.py"]},
    ]
    result = compute_delta(current, knowledge)
    assert result["new"] == 1
    assert result["trend"] == "baseline"


def test_delta_summary_format():
    result = compute_delta(
        [{"category": "performance", "file": "x.py"}],
        [{"tags": ["review"], "topic": "quality-old", "referenced_files": ["y.py"]}],
    )
    assert "1 new" in result["summary"]
    assert "1 resolved" in result["summary"]


# ---------------------------------------------------------------------------
# _infer_category
# ---------------------------------------------------------------------------


def test_infer_category_direct():
    assert _infer_category("security-issues") == "security"
    assert _infer_category("performance-check") == "performance"
    assert _infer_category("architecture-review") == "architecture"
    assert _infer_category("testing-gaps") == "testing"
    assert _infer_category("random-stuff") == "quality"


def test_infer_category_domain_synonyms():
    """Domain terms in knowledge topics map to correct categories."""
    assert _infer_category("auth-jwt-patterns") == "security"
    assert _infer_category("n+1-query-fix") == "performance"
    assert _infer_category("dead-code-cleanup") == "quality"
    assert _infer_category("cve-2024-review") == "security"
    assert _infer_category("coupling-analysis") == "architecture"
    assert _infer_category("test-coverage-report") == "testing"
    assert _infer_category("cache-strategy") == "performance"
    assert _infer_category("docstring-conventions") == "documentation"
    assert _infer_category("credential-rotation") == "security"
    assert _infer_category("latency-bottleneck") == "performance"
    assert _infer_category("refactoring-plan") == "quality"
