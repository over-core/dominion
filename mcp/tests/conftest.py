"""Shared fixtures for dominion-mcp v0.3.0 tests.

Creates a temporary .dominion/ directory structure with v0.3.0 layout:
config.toml, state.toml, agents/*.toml, heuristics/*.md, knowledge/,
phases/ with CLAUDE.md, status files, and output directories.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dominion_mcp.core.config import write_toml


# ---------------------------------------------------------------------------
# v0.3.0 config.toml
# ---------------------------------------------------------------------------

CONFIG = {
    "project": {
        "name": "test-project",
        "languages": ["python"],
        "frameworks": ["fastapi"],
        "direction": "API-first microservices",
        "git_platform": "github",
        "test_command": "pytest",
    },
    "tools": {
        "available": ["serena", "context7"],
    },
    "agents": {
        "active": [
            "researcher", "architect", "developer", "reviewer",
            "security-auditor", "analyst", "innovation-engineer",
        ],
    },
    "style": {
        "testing": "tdd",
        "conventions": ["type hints required", "async by default"],
    },
    "user": {
        "skill_level": "advanced",
    },
    "auto": {
        "halt_on_severity": "critical",
        "max_retries": 3,
        "max_iterations": 10,
    },
}

# ---------------------------------------------------------------------------
# v0.3.0 state.toml (with active phase)
# ---------------------------------------------------------------------------

STATE = {
    "position": {
        "phase": "01",
        "step": "research",
        "wave": 0,
        "status": "active",
        "complexity_level": "moderate",
        "last_session": "2026-03-18T09:00:00Z",
    },
    "circuit_breaker": {
        "state": "closed",
        "retry_count": 0,
        "iteration_count": 0,
        "last_findings_hash": "",
        "same_finding_count": 0,
    },
    "completed_tasks": {},
    "phases": [
        {
            "id": "01",
            "intent": "Add rate limiting",
            "status": "active",
            "complexity": "moderate",
            "started": "2026-03-18T09:00:00Z",
        },
    ],
    "decisions": [],
}

# ---------------------------------------------------------------------------
# v0.3.0 agent TOML (flat files, ~20 lines each)
# ---------------------------------------------------------------------------

AGENT_TOMLS = {
    "researcher": {
        "agent": {"name": "Researcher", "role": "researcher", "model": "opus", "purpose": "Codebase analysis"},
        "tools": {"mcps": {"preferred": ["serena"], "optional": ["context7"]}},
        "governance": {"hard_stops": ["Always cite file:line", "Grade by severity"]},
        "workflow": {"produces": "findings.toml"},
    },
    "architect": {
        "agent": {"name": "Architect", "role": "architect", "model": "opus", "purpose": "Planning and task decomposition"},
        "tools": {"mcps": {"preferred": ["serena"], "optional": []}},
        "governance": {"hard_stops": ["No two tasks in same wave touch same files"]},
        "workflow": {"produces": "tasks.toml"},
    },
    "developer": {
        "agent": {"name": "Developer", "role": "developer", "model": "sonnet", "purpose": "Implementation + self-verification"},
        "tools": {"mcps": {"preferred": ["serena"], "optional": []}},
        "governance": {"hard_stops": ["Run ALL tests before submitting"]},
        "workflow": {"produces": "summary.md"},
    },
    "reviewer": {
        "agent": {"name": "Reviewer", "role": "reviewer", "model": "opus", "purpose": "Cross-cutting code review"},
        "tools": {"mcps": {"preferred": ["serena"], "optional": []}},
        "governance": {"hard_stops": ["Verdict MUST be go, go-with-warnings, or no-go"]},
        "workflow": {"produces": "verdict.toml"},
    },
    "security-auditor": {
        "agent": {"name": "Security Auditor", "role": "security-auditor", "model": "opus", "purpose": "Security analysis"},
        "tools": {"mcps": {"preferred": ["serena"], "optional": []}},
        "governance": {"hard_stops": ["Cite CWE/CVE when applicable"]},
        "workflow": {"produces": "findings.toml"},
    },
    "analyst": {
        "agent": {"name": "Analyst", "role": "analyst", "model": "opus", "purpose": "Performance analysis"},
        "tools": {"mcps": {"preferred": ["serena"], "optional": []}},
        "governance": {"hard_stops": ["Quantify claims with measurements"]},
        "workflow": {"produces": "findings.toml"},
    },
    "innovation-engineer": {
        "agent": {"name": "Innovation Engineer", "role": "innovation-engineer", "model": "opus", "purpose": "Creative contradiction analysis"},
        "tools": {"mcps": {"preferred": ["serena"], "optional": []}},
        "governance": {"hard_stops": ["Identify contradictions"]},
        "workflow": {"produces": "findings.toml"},
    },
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def dom_root(tmp_path: Path) -> Path:
    """Create a minimal .dominion/ v0.3.0 directory structure.

    Returns the .dominion/ directory.
    """
    project_root = tmp_path / "project"
    project_root.mkdir()
    dom = project_root / ".dominion"
    dom.mkdir()

    # Config
    write_toml(dom / "config.toml", CONFIG)
    write_toml(dom / "state.toml", STATE)

    # Agents (flat .toml files)
    agents_dir = dom / "agents"
    agents_dir.mkdir()
    for role, data in AGENT_TOMLS.items():
        write_toml(agents_dir / f"{role}.toml", data)

    # Heuristics
    heuristics_dir = dom / "heuristics"
    heuristics_dir.mkdir()
    for step in ("research", "plan", "execute", "review", "discuss"):
        (heuristics_dir / f"{step}.md").write_text(
            f"## {step.title()} Heuristics\n\nFocus on quality and correctness.\n"
        )

    # Knowledge
    knowledge_dir = dom / "knowledge"
    knowledge_dir.mkdir()
    write_toml(knowledge_dir / "index.toml", {
        "entries": [
            {
                "topic": "auth-patterns",
                "summary": "Authentication patterns used in this project",
                "tags": ["research", "execute"],
                "path": "auth-patterns.md",
                "referenced_files": ["src/auth/provider.py"],
            },
        ],
    })
    (knowledge_dir / "auth-patterns.md").write_text("# Auth Patterns\n\nJWT-based.\n")

    # Phases directory (empty, populated by start_phase)
    (dom / "phases").mkdir()

    return dom


@pytest.fixture()
def dom_root_with_plan(dom_root: Path) -> Path:
    """Extend dom_root with a phase 01 directory structure including plan output."""
    phase_dir = dom_root / "phases" / "01"
    phase_dir.mkdir(parents=True, exist_ok=True)
    (phase_dir / "status").write_text("active")
    (phase_dir / "CLAUDE.md").write_text("# Phase 01: Add rate limiting\n\n## Intent\nAdd rate limiting\n")

    # Research step (complete)
    research_dir = phase_dir / "research"
    research_dir.mkdir()
    (research_dir / "status").write_text("complete")
    (research_dir / "output").mkdir()
    (research_dir / "output" / "summary.md").write_text(
        "## researcher\nAPI has no rate limiting. 2 high-severity findings.\n"
    )

    # Plan step (complete)
    plan_dir = phase_dir / "plan"
    plan_dir.mkdir()
    (plan_dir / "status").write_text("complete")
    (plan_dir / "output").mkdir()
    write_toml(plan_dir / "output" / "tasks.toml", {
        "findings": {
            "architect": {
                "total_waves": 2,
                "total_tasks": 2,
                "tasks": [
                    {"task_id": "01", "wave": 1, "title": "Create middleware", "description": "Rate limit middleware", "files": ["src/middleware.py"], "agent_role": "developer", "dependencies": []},
                    {"task_id": "02", "wave": 2, "title": "Apply to endpoints", "description": "Add decorators", "files": ["src/api.py"], "agent_role": "developer", "dependencies": ["01"]},
                ],
            },
        },
    })
    (plan_dir / "output" / "summary.md").write_text(
        "## architect\n2 tasks across 2 waves.\n"
    )

    # Execute and review dirs (pending)
    for step in ("execute", "review"):
        d = phase_dir / step
        d.mkdir()
        (d / "status").write_text("pending")
        (d / "output").mkdir()

    # Tasks dir
    (phase_dir / "tasks").mkdir()

    return dom_root
