"""Tests for v0.3.0 core/prepare module."""

from pathlib import Path

from dominion_mcp.core.prepare import (
    filter_knowledge_by_files,
    filter_knowledge_by_step,
    generate_phase_claude_md,
    generate_step_claude_md,
    generate_task_claude_md,
    read_agent_toml,
    read_heuristics,
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
