"""Shared fixtures for dominion-cli tests.

Creates a temporary .dominion/ directory structure with sample TOML files
that mirror a real Dominion project.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dominion_cli.core.config import reset_cache


# ---------------------------------------------------------------------------
# Minimal TOML content for each fixture file
# ---------------------------------------------------------------------------

DOMINION_TOML = """\
[project]
name = "test-project"
language = "python"
framework = "fastapi"
tier = "full"

[workflow]
pipeline = ["discuss", "explore", "plan", "execute", "test", "review", "improve"]
ai_co_author = false

[documentation]
fallback = [
    { source = "context7", action = "search" },
    { source = "web", action = "search" },
    { source = "human", action = "stop-and-ask" },
]
"""

STATE_TOML = """\
[meta]
created = "2025-01-01T00:00:00Z"
version = "0.9.1"

[position]
phase = 1
step = "execute"
wave = 2
status = "active"
last_session = "2025-06-01T12:00:00Z"

[init]
completed = true
"""

STYLE_TOML = """\
[commit]
format = "conventional"
scope_required = true

[code]
line_length = 100
indent = 4
"""

ROADMAP_TOML = """\
[[milestones]]
name = "v1.0"
status = "in-progress"

[[milestones.phases]]
number = 1
title = "Foundation"
status = "active"
"""

RESEARCHER_TOML = """\
[role]
name = "Researcher"
purpose = "Evidence-graded research and analysis"

[model]
name = "claude-sonnet-4-20250514"

[tools]
mcp = ["context7", "echovault"]
cli = ["dominion-cli research *"]

[governance]
file_ownership = [".dominion/knowledge/"]
hard_stops = ["No ungraded findings"]

[workflow]
produces = ["research-report.md"]
commit_style = "docs(research): description"
"""

DEVELOPER_TOML = """\
[role]
name = "Developer"
purpose = "Implement planned tasks with quality"

[model]
name = "claude-sonnet-4-20250514"

[tools]
mcp = ["serena", "echovault"]
cli = ["dominion-cli plan *", "dominion-cli state *"]

[governance]
file_ownership = ["src/"]
hard_stops = ["Never modify files outside task scope"]

[workflow]
produces = ["source code", "tests"]
commit_style = "feat(scope): description"
"""

CLI_SPEC_TOML = """\
[meta]
spec_version = "0.5"
minimum_commands = ["state resume", "state update", "agents list", "agents show", "signal blocker", "validate"]
"""

KNOWLEDGE_INDEX_TOML = """\
[index]
files = []
"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_dominion(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary .dominion/ directory tree and chdir into the project root.

    Returns the project root (parent of .dominion/).
    The fixture resets the cached root in config.py so discovery works.
    """
    project_root = tmp_path / "project"
    project_root.mkdir()
    dom = project_root / ".dominion"
    dom.mkdir()

    # Core config files
    (dom / "dominion.toml").write_text(DOMINION_TOML)
    (dom / "state.toml").write_text(STATE_TOML)
    (dom / "style.toml").write_text(STYLE_TOML)
    (dom / "roadmap.toml").write_text(ROADMAP_TOML)

    # Agents
    agents_dir = dom / "agents"
    agents_dir.mkdir()
    (agents_dir / "researcher.toml").write_text(RESEARCHER_TOML)
    (agents_dir / "developer.toml").write_text(DEVELOPER_TOML)

    # Specs
    specs_dir = dom / "specs"
    specs_dir.mkdir()
    (specs_dir / "cli-spec.toml").write_text(CLI_SPEC_TOML)

    # Knowledge
    knowledge_dir = dom / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "index.toml").write_text(KNOWLEDGE_INDEX_TOML)

    # Signals (empty directory)
    (dom / "signals").mkdir()

    # Phases — create directory matching phase number in state.toml
    (dom / "phases").mkdir()
    (dom / "phases" / "1").mkdir()

    # .claude/agents/ with matching markdown stubs (for validate checks)
    claude_agents_dir = project_root / ".claude" / "agents"
    claude_agents_dir.mkdir(parents=True)
    (claude_agents_dir / "researcher.md").write_text(
        "<!-- Dominion-managed agent: researcher -->\n# Researcher\n"
    )
    (claude_agents_dir / "developer.md").write_text(
        "<!-- Dominion-managed agent: developer -->\n# Developer\n"
    )

    # AGENTS.md
    (project_root / "AGENTS.md").write_text(
        "# Agents\n\n| Agent | Model | Purpose |\n"
        "| researcher | claude-sonnet-4-20250514 | Evidence-graded research |\n"
        "| developer | claude-sonnet-4-20250514 | Implement planned tasks |\n"
    )

    # .claude/settings.json with CLI permission
    (project_root / ".claude" / "settings.json").write_text(
        json.dumps({
            "permissions": {
                "allow": ["Bash(dominion-cli *)"],
            },
        })
    )

    # Reset cached root so find_dominion_root() re-discovers
    reset_cache()
    monkeypatch.chdir(project_root)

    yield project_root

    # Cleanup: reset cache again so other tests start fresh
    reset_cache()


@pytest.fixture()
def tmp_dominion_with_phase(tmp_dominion: Path) -> Path:
    """Extend tmp_dominion with a phase directory containing plan.toml."""
    phase_dir = tmp_dominion / ".dominion" / "phases" / "1"
    phase_dir.mkdir(parents=True, exist_ok=True)

    plan_toml = """\
[[tasks]]
id = "1-01"
title = "Set up project structure"
wave = 1
agent = "developer"
depends_on = []
file_ownership = ["src/main.py", "pyproject.toml"]
token_estimate = 50000
acceptance_criteria = ["Project builds successfully", "All directories created"]
verify_command = "python -m pytest"

[[tasks]]
id = "1-02"
title = "Implement core module"
wave = 1
agent = "developer"
depends_on = []
file_ownership = ["src/core.py"]
token_estimate = 80000
acceptance_criteria = ["Module passes unit tests", "Type hints on all public functions"]
verify_command = "python -m pytest tests/test_core.py"

[[tasks]]
id = "1-03"
title = "Add API endpoints"
wave = 2
agent = "developer"
depends_on = ["1-01", "1-02"]
file_ownership = ["src/api.py"]
token_estimate = 60000
acceptance_criteria = ["All endpoints respond", "OpenAPI docs generated"]
verify_command = "python -m pytest tests/test_api.py"
"""
    (phase_dir / "plan.toml").write_text(plan_toml)

    return tmp_dominion
