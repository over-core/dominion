"""Tests for v0.3.0 core/prepare module."""

from pathlib import Path

import pytest

from dominion_mcp.core.prepare import (
    filter_knowledge_by_files,
    filter_knowledge_by_step,
    generate_phase_claude_md,
    generate_step_claude_md,
    generate_task_claude_md,
    read_agent_toml,
    read_heuristics,
    read_interface_contracts,
    read_knowledge_index,
)


def test_generate_phase_claude_md():
    content = generate_phase_claude_md(
        phase="01",
        intent="Add rate limiting",
        complexity="moderate",
        pipeline=["research", "plan", "execute", "review"],
        config={"project": {"languages": ["python"], "frameworks": ["fastapi"], "direction": "API-first"}},
        phases=[],
        decisions=[],
    )
    assert "# Phase 01: Add rate limiting" in content
    assert "moderate" in content
    assert "research -> plan -> execute -> review" in content
    assert "python" in content


def test_generate_phase_claude_md_with_prior_phases():
    content = generate_phase_claude_md(
        phase="02", intent="Add auth", complexity="complex",
        pipeline=["discuss", "research", "plan", "execute", "review"],
        config={"project": {"languages": ["python"]}},
        phases=[{"id": "01", "intent": "Rate limiting", "status": "complete"}],
        decisions=[{"id": 1, "title": "approach", "decision": "middleware", "rationale": "clean", "tags": ["arch"]}],
    )
    assert "Prior Phases" in content
    assert "Rate limiting" in content
    assert "Active Decisions" in content
    assert "middleware" in content


def test_generate_step_claude_md(dom_root: Path):
    agent_toml = read_agent_toml(dom_root, "researcher")
    content = generate_step_claude_md(
        phase="01", step="research", role="researcher",
        intent="Add rate limiting",
        config={"tools": {"available": ["serena", "context7"]}, "style": {"testing": "tdd", "conventions": ["type hints"]}},
        agent_toml=agent_toml,
        heuristics="## Focus\n- Coupling\n- Test gaps",
        prior_summaries={},
        knowledge_entries=[{"topic": "auth", "summary": "Auth patterns"}],
        decisions=[],
    )
    assert "Research Brief" in content
    assert "Researcher" in content
    assert "rate limiting" in content
    assert "Serena" in content
    assert "Context7" in content
    assert "auth" in content
    assert "tdd" in content


def test_generate_task_claude_md(dom_root: Path):
    agent_toml = read_agent_toml(dom_root, "developer")
    content = generate_task_claude_md(
        phase="01", task_id="01",
        task_info={"title": "Create middleware", "description": "Rate limit middleware", "files": ["src/middleware.py"], "agent_role": "developer", "dependencies": [], "wave": 1},
        config={"tools": {"available": ["serena"]}, "style": {"testing": "tdd"}},
        agent_toml=agent_toml,
        heuristics="## Execute\n- Run tests",
        research_summary="API has no rate limiting.",
        plan_summary="2 tasks across 2 waves.",
        knowledge_entries=[],
        upstream_task_summaries={},
    )
    assert "Task 01: Create middleware" in content
    assert "Developer" in content
    assert "src/middleware.py" in content
    assert "submit_work" in content


def test_read_heuristics(dom_root: Path):
    h = read_heuristics(dom_root, "research")
    assert h is not None
    assert "Heuristics" in h


def test_read_heuristics_with_role(dom_root: Path):
    """Role-keyed heuristic should be appended after step heuristic."""
    h = read_heuristics(dom_root, "review", role="security-auditor")
    assert h is not None
    assert "Review Heuristics" in h
    assert "Security Auditor" in h
    assert "OWASP" in h


def test_read_heuristics_role_only(dom_root: Path):
    """If step heuristic missing but role exists, return role heuristic."""
    h = read_heuristics(dom_root, "nonexistent", role="security-auditor")
    assert h is not None
    assert "Security Auditor" in h


def test_read_heuristics_missing(dom_root: Path):
    assert read_heuristics(dom_root, "nonexistent") is None


def test_read_heuristics_wave_review(dom_root: Path):
    """wave-review heuristic loads from wave-review.md when present."""
    (dom_root / "heuristics" / "wave-review.md").write_text(
        "## Wave Review\n\nCross-task integration check.\n"
    )
    result = read_heuristics(dom_root, "wave-review")
    assert result is not None
    assert "Wave Review" in result


@pytest.mark.asyncio
async def test_prepare_task_wave_review_uses_wave_heuristic(dom_root_with_plan: Path):
    """prepare_task with wave-review-* prefix uses wave-review heuristic."""
    import json

    # Create wave-review heuristic
    (dom_root_with_plan / "heuristics" / "wave-review.md").write_text(
        "## Wave Review\n\nVerify cross-task consistency.\n"
    )

    import dominion_mcp.tools.setup as setup_mod
    original = setup_mod.find_dominion_root
    setup_mod.find_dominion_root = lambda: dom_root_with_plan

    try:
        task_info = json.dumps({
            "title": "Wave 1 integration review",
            "description": "Verify cross-task consistency",
            "files": ["src/middleware.py"],
            "wave": 1,
            "dependencies": [],
            "agent_role": "developer",
        })
        result = await setup_mod.prepare_task(
            phase="01", task_id="wave-review-1", task_info=task_info,
        )
    finally:
        setup_mod.find_dominion_root = original

    assert "claude_md_path" in result
    # Verify the generated CLAUDE.md contains wave-review heuristic
    claude_path = dom_root_with_plan.parent / result["claude_md_path"]
    content = claude_path.read_text()
    assert "Wave Review" in content


def test_read_knowledge_index(dom_root: Path):
    entries = read_knowledge_index(dom_root)
    assert len(entries) == 1
    assert entries[0]["topic"] == "auth-patterns"


def test_filter_knowledge_by_step():
    entries = [
        {"topic": "a", "tags": ["research", "execute"]},
        {"topic": "b", "tags": ["review"]},
    ]
    assert len(filter_knowledge_by_step(entries, "research")) == 1
    assert len(filter_knowledge_by_step(entries, "review")) == 1
    assert len(filter_knowledge_by_step(entries, "plan")) == 0


def test_filter_knowledge_by_files():
    entries = [
        {"topic": "a", "referenced_files": ["src/auth/provider.py"]},
        {"topic": "b", "referenced_files": ["src/other.py"]},
        {"topic": "c", "referenced_files": []},  # no files → included
    ]
    result = filter_knowledge_by_files(entries, ["src/auth/provider.py"])
    topics = [e["topic"] for e in result]
    assert "a" in topics
    assert "c" in topics  # no referenced_files → included
    assert "b" not in topics


# -- interface contracts (v0.4.3) ------------------------------------------


def test_interface_contracts_injected(dom_root_with_plan):
    """Task brief should include interface contracts from tasks.toml."""
    from dominion_mcp.core.config import write_toml

    dom = dom_root_with_plan
    # Add interfaces to tasks.toml
    tasks_path = dom / "phases" / "01" / "plan" / "output" / "tasks.toml"
    tasks_data = {
        "findings": {"architect": {"tasks": [
            {"task_id": "01", "wave": 1, "title": "Models", "description": "Create models", "files": ["models.py"], "agent_role": "developer", "dependencies": []},
            {"task_id": "02", "wave": 2, "title": "Workflow", "description": "Create workflow", "files": ["workflow.py"], "agent_role": "developer", "dependencies": ["01"]},
        ]}},
        "interfaces": {
            "symbols": [
                {"name": "ValidationReport", "defined_in": "01", "imported_by": ["02"], "module": "models.py", "signature": "class ValidationReport(BaseModel)"},
            ],
            "runtime_contracts": [],
        },
    }
    write_toml(tasks_path, tasks_data)

    result = read_interface_contracts(dom, "01", "01")
    assert result is not None
    assert "ValidationReport" in result
    assert "YOU DEFINE" in result

    result2 = read_interface_contracts(dom, "01", "02")
    assert result2 is not None
    assert "ValidationReport" in result2
    assert "task 01 defines" in result2


def test_interface_contracts_filtered_by_task(dom_root_with_plan):
    """Only contracts relevant to the task should be included."""
    from dominion_mcp.core.config import write_toml

    dom = dom_root_with_plan
    tasks_path = dom / "phases" / "01" / "plan" / "output" / "tasks.toml"
    tasks_data = {
        "findings": {"architect": {"tasks": []}},
        "interfaces": {
            "symbols": [
                {"name": "Foo", "defined_in": "01", "imported_by": ["02"], "module": "foo.py", "signature": "class Foo"},
                {"name": "Bar", "defined_in": "03", "imported_by": ["04"], "module": "bar.py", "signature": "class Bar"},
            ],
            "runtime_contracts": [],
        },
    }
    write_toml(tasks_path, tasks_data)

    result = read_interface_contracts(dom, "01", "01")
    assert "Foo" in result
    assert "Bar" not in result


def test_interface_contracts_missing_graceful(dom_root_with_plan):
    """No interfaces section → returns None."""
    result = read_interface_contracts(dom_root_with_plan, "01", "01")
    assert result is None


def test_task_claude_md_includes_contracts():
    """generate_task_claude_md should include interface contracts section."""
    content = generate_task_claude_md(
        phase="01",
        task_id="02",
        task_info={"title": "Workflow", "description": "Build it", "files": ["workflow.py"], "dependencies": ["01"], "agent_role": "developer"},
        config={"style": {}},
        agent_toml={"agent": {"purpose": "Implementation"}, "governance": {"hard_stops": []}},
        heuristics=None,
        research_summary=None,
        plan_summary=None,
        knowledge_entries=[],
        upstream_task_summaries={},
        interface_contracts="### Shared Symbols\n- `Report` in `models.py` — task 01 defines",
    )
    assert "## Interface Contracts" in content
    assert "Report" in content


@pytest.mark.asyncio
async def test_prepare_task_wave_review_missing_heuristic(dom_root_with_plan: Path):
    """Wave-review task works even if wave-review.md heuristic doesn't exist."""
    import json
    # Do NOT create wave-review.md — test graceful degradation

    import dominion_mcp.tools.setup as setup_mod
    original = setup_mod.find_dominion_root
    setup_mod.find_dominion_root = lambda: dom_root_with_plan
    try:
        task_info = json.dumps({
            "title": "Wave 1 review",
            "description": "Check consistency",
            "files": ["src/middleware.py"],
            "wave": 1, "dependencies": [], "agent_role": "developer",
        })
        result = await setup_mod.prepare_task(phase="01", task_id="wave-review-1", task_info=task_info)
    finally:
        setup_mod.find_dominion_root = original

    # Should still succeed — CLAUDE.md created, just without heuristic section
    assert "claude_md_path" in result
    claude_path = dom_root_with_plan.parent / result["claude_md_path"]
    assert claude_path.exists()


@pytest.mark.asyncio
async def test_prepare_task_wave_review_excludes_execute(dom_root_with_plan: Path):
    """Wave-review task does NOT include execute.md heuristic content."""
    import json
    # Create both heuristics
    (dom_root_with_plan / "heuristics" / "wave-review.md").write_text("## Wave Review\nCheck consistency.\n")
    # execute.md already exists from conftest (has "Execute Heuristics" header)

    import dominion_mcp.tools.setup as setup_mod
    original = setup_mod.find_dominion_root
    setup_mod.find_dominion_root = lambda: dom_root_with_plan
    try:
        task_info = json.dumps({
            "title": "Wave 1 review",
            "description": "Check consistency",
            "files": ["src/middleware.py"],
            "wave": 1, "dependencies": [], "agent_role": "developer",
        })
        result = await setup_mod.prepare_task(phase="01", task_id="wave-review-1", task_info=task_info)
    finally:
        setup_mod.find_dominion_root = original

    claude_path = dom_root_with_plan.parent / result["claude_md_path"]
    content = claude_path.read_text()
    assert "Wave Review" in content
    # Execute heuristic should NOT be present
    assert "Execute Heuristics" not in content


# ---------------------------------------------------------------------------
# CLI tool directives (v0.5.0)
# ---------------------------------------------------------------------------


def test_cli_directives_security_auditor(dom_root: Path):
    """CLI tool directives injected for security-auditor when tools detected."""
    agent_toml = read_agent_toml(dom_root, "security-auditor")
    content = generate_step_claude_md(
        phase="01", step="review", role="security-auditor",
        intent="Review code",
        config={"tools": {"available": ["serena"], "cli": ["semgrep", "pip-audit"]}},
        agent_toml=agent_toml, heuristics=None,
        prior_summaries={}, knowledge_entries=[], decisions=[],
    )
    assert "CLI Analysis Tools" in content
    assert "semgrep" in content
    assert "pip-audit" in content


def test_cli_directives_analyst(dom_root: Path):
    """CLI tool directives injected for analyst when tools detected."""
    agent_toml = read_agent_toml(dom_root, "analyst")
    content = generate_step_claude_md(
        phase="01", step="review", role="analyst",
        intent="Analyze quality",
        config={"tools": {"available": [], "cli": ["radon", "vulture", "jscpd"]}},
        agent_toml=agent_toml, heuristics=None,
        prior_summaries={}, knowledge_entries=[], decisions=[],
    )
    assert "CLI Analysis Tools" in content
    assert "radon" in content
    assert "vulture" in content
    assert "jscpd" in content


def test_cli_directives_wrong_role(dom_root: Path):
    """Developer gets no CLI directives."""
    agent_toml = read_agent_toml(dom_root, "developer")
    content = generate_step_claude_md(
        phase="01", step="execute", role="developer",
        intent="Implement",
        config={"tools": {"available": [], "cli": ["semgrep"]}},
        agent_toml=agent_toml, heuristics=None,
        prior_summaries={}, knowledge_entries=[], decisions=[],
    )
    assert "CLI Analysis Tools" not in content


def test_cli_directives_empty_cli_list(dom_root: Path):
    """No CLI section when config has empty cli list."""
    agent_toml = read_agent_toml(dom_root, "security-auditor")
    content = generate_step_claude_md(
        phase="01", step="review", role="security-auditor",
        intent="Review",
        config={"tools": {"available": ["serena"], "cli": []}},
        agent_toml=agent_toml, heuristics=None,
        prior_summaries={}, knowledge_entries=[], decisions=[],
    )
    assert "CLI Analysis Tools" not in content


def test_cli_directives_missing_cli_config(dom_root: Path):
    """No CLI section when [tools].cli missing (old config)."""
    agent_toml = read_agent_toml(dom_root, "security-auditor")
    content = generate_step_claude_md(
        phase="01", step="review", role="security-auditor",
        intent="Review",
        config={"tools": {"available": ["serena"]}},
        agent_toml=agent_toml, heuristics=None,
        prior_summaries={}, knowledge_entries=[], decisions=[],
    )
    assert "CLI Analysis Tools" not in content


def test_cli_directives_only_matching_tools(dom_root: Path):
    """Analyst only gets analyst tools, not security tools."""
    agent_toml = read_agent_toml(dom_root, "analyst")
    content = generate_step_claude_md(
        phase="01", step="review", role="analyst",
        intent="Analyze",
        config={"tools": {"available": [], "cli": ["semgrep", "radon"]}},
        agent_toml=agent_toml, heuristics=None,
        prior_summaries={}, knowledge_entries=[], decisions=[],
    )
    assert "radon" in content
    assert "semgrep" not in content


def test_cli_directives_in_task_claude_md(dom_root: Path):
    """Task briefs also get CLI directives for matching roles."""
    agent_toml = read_agent_toml(dom_root, "security-auditor")
    content = generate_task_claude_md(
        phase="01", task_id="fix-01",
        task_info={"title": "Fix vuln", "description": "Fix it", "files": ["auth.py"],
                   "agent_role": "security-auditor", "dependencies": []},
        config={"tools": {"available": [], "cli": ["semgrep"]}},
        agent_toml=agent_toml, heuristics=None,
        research_summary=None, plan_summary=None,
        knowledge_entries=[], upstream_task_summaries={},
    )
    assert "CLI Analysis Tools" in content
    assert "semgrep" in content


# ---------------------------------------------------------------------------
# Pre-metrics persistence (v0.5.0 — Gap 1 fix)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_prepare_step_reads_metrics_json(dom_root_with_plan: Path):
    """prepare_step injects pre-analysis metrics from metrics.json."""
    import json

    import dominion_mcp.tools.setup as setup_mod

    dom = dom_root_with_plan

    # Write metrics.json to research step dir
    metrics_path = dom / "phases" / "01" / "research" / "metrics.json"
    metrics_path.write_text(json.dumps({"Python LOC": "5432", "Test files": "87"}))

    # Reset research step to active so prepare_step can regenerate
    (dom / "phases" / "01" / "research" / "status").write_text("active")

    original = setup_mod.find_dominion_root
    setup_mod.find_dominion_root = lambda: dom
    try:
        result = await setup_mod.prepare_step(phase="01", step="research")
    finally:
        setup_mod.find_dominion_root = original

    claude_path = dom.parent / result["claude_md_path"]
    content = claude_path.read_text()
    assert "Pre-Analysis Metrics" in content
    assert "5432" in content
    assert "87" in content
