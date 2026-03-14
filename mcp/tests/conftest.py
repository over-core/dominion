"""Shared fixtures for dominion-mcp tests.

Creates a temporary .dominion/ directory structure with sample TOML files
that mirror a real Dominion project configured for MCP architecture.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Minimal TOML content for each fixture file
# ---------------------------------------------------------------------------

DOMINION_TOML = """\
[project]
name = "test-project"
languages = ["python"]
frameworks = ["fastapi"]

[direction]
mode = "improve"

[tools]
serena = { enabled = true }
echovault = { enabled = true }

[agents]
active = ["security-auditor"]

[documentation]
fallback = [
    { source = "context7", action = "search" },
    { source = "web", action = "search" },
    { source = "human", action = "stop-and-ask" },
]

[budget]
mode = "performance"
"""

STATE_TOML = """\
[meta]
created = "2025-01-01T00:00:00Z"
version = "0.2.0"

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

[testing]
styles = ["tdd"]
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
[agent]
name = "Researcher"
role = "researcher"
model = "opus"
purpose = "Evidence-graded research and analysis"

[tools.mcp]
dominion = ["agent_start", "agent_submit", "agent_signal", "get_knowledge", "search_knowledge"]

[governance]
file_ownership = [".dominion/knowledge/"]
hard_stops = ["No ungraded findings", "Use mcp__dominion__* tools only"]

[[methodology.sections]]
id = "core"
file = "sections/core.md"
always_include = true

[[methodology.sections]]
id = "protocol-greenfield"
file = "sections/protocol-greenfield.md"
conditions = { phase_type = ["greenfield", "new-feature"] }

[[methodology.sections]]
id = "lang-python"
file = "sections/lang-python.md"
conditions = { languages = ["python"] }

[[methodology.sections]]
id = "tools-serena"
file = "sections/tools-serena.md"
conditions = { tools_available = ["serena"] }

[[methodology.sections]]
id = "specialist-security"
file = "sections/specialist-security.md"
conditions = { agents_active = ["security-auditor"] }
"""

DEVELOPER_TOML = """\
[agent]
name = "Developer"
role = "developer"
model = "sonnet"
purpose = "Implement planned tasks with quality"

[tools.mcp]
dominion = ["agent_start", "agent_submit", "agent_signal", "get_plan", "update_progress"]

[governance]
file_ownership = ["src/"]
hard_stops = ["Never modify files outside task scope", "Use mcp__dominion__* tools only"]

[[methodology.sections]]
id = "core"
file = "sections/core.md"
always_include = true

[[methodology.sections]]
id = "protocol-implement"
file = "sections/protocol-implement.md"
conditions = { task_type = ["new-code", "modify"] }

[[methodology.sections]]
id = "protocol-tdd"
file = "sections/protocol-tdd.md"
conditions = { testing_style = ["tdd"] }
"""

KNOWLEDGE_INDEX_TOML = """\
[[entries]]
file = "auth-patterns.md"
summary = "Authentication patterns used in the project"
tags = ["auth", "security"]
hot = true
priority = 1

[[entries]]
file = "api-conventions.md"
summary = "API naming and versioning conventions"
tags = ["api", "conventions"]
hot = false
"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def dom_root(tmp_path: Path) -> Path:
    """Create a temporary .dominion/ directory tree.

    Returns the .dominion/ directory itself (not the project root).
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

    # Agent methodology sections
    researcher_sections = agents_dir / "researcher" / "sections"
    researcher_sections.mkdir(parents=True)
    (researcher_sections / "core.md").write_text(
        "# Researcher\n\nYou are the Researcher agent.\n"
    )
    (researcher_sections / "lang-python.md").write_text(
        "## Python Research\n\nUse pytest patterns.\n"
    )
    (researcher_sections / "tools-serena.md").write_text(
        "## Serena Workflow\n\nUse serena for symbol analysis.\n"
    )
    (researcher_sections / "specialist-security.md").write_text(
        "## Security Research\n\nInclude threat analysis.\n"
    )

    developer_sections = agents_dir / "developer" / "sections"
    developer_sections.mkdir(parents=True)
    (developer_sections / "core.md").write_text(
        "# Developer\n\nYou are the Developer agent.\n"
    )
    (developer_sections / "protocol-tdd.md").write_text(
        "## TDD Protocol\n\nWrite tests first.\n"
    )

    # Knowledge
    knowledge_dir = dom / "knowledge"
    knowledge_dir.mkdir()
    (knowledge_dir / "index.toml").write_text(KNOWLEDGE_INDEX_TOML)
    (knowledge_dir / "auth-patterns.md").write_text(
        "# Auth Patterns\n\nJWT-based authentication.\n"
    )

    # Memory (empty directory)
    (dom / "memory").mkdir()

    # Signals (empty directory)
    (dom / "signals").mkdir()

    # Phases
    (dom / "phases").mkdir()
    phase1 = dom / "phases" / "1"
    phase1.mkdir()
    (phase1 / "summaries").mkdir()

    # .claude/ artifacts
    claude_agents_dir = project_root / ".claude" / "agents"
    claude_agents_dir.mkdir(parents=True)
    (claude_agents_dir / "researcher.md").write_text(
        "<!-- Dominion agent: researcher -->\n# Researcher\n"
    )
    (claude_agents_dir / "developer.md").write_text(
        "<!-- Dominion agent: developer -->\n# Developer\n"
    )

    # AGENTS.md
    (project_root / "AGENTS.md").write_text(
        "# Agents\n\n## researcher\nDescription: Research\n\n## developer\nDescription: Develop\n"
    )

    # .mcp.json
    (project_root / ".mcp.json").write_text(
        json.dumps({"dominion": {"command": "dominion-mcp"}})
    )

    # .claude/settings.local.json
    (project_root / ".claude" / "settings.local.json").write_text(
        json.dumps({
            "permissions": {
                "allow": ["mcp__dominion__*"],
            },
        })
    )

    return dom


@pytest.fixture()
def dom_root_with_plan(dom_root: Path) -> Path:
    """Extend dom_root with plan.toml and progress.toml in phase 1."""
    phase_dir = dom_root / "phases" / "1"

    plan_toml = """\
[[tasks]]
id = "01-01"
title = "Set up project structure"
wave = 1
assigned_to = "developer"
model = "sonnet"
depends_on = []
file_ownership = ["src/main.py", "pyproject.toml"]
token_estimate = 50000
acceptance_criteria = ["Project builds successfully"]

[[tasks]]
id = "01-02"
title = "Implement core module"
wave = 1
assigned_to = "developer"
model = "sonnet"
depends_on = []
file_ownership = ["src/core.py"]
token_estimate = 80000
acceptance_criteria = ["Module passes unit tests"]

[[tasks]]
id = "01-03"
title = "Add API endpoints"
wave = 2
assigned_to = "developer"
model = "opus"
depends_on = ["01-01", "01-02"]
file_ownership = ["src/api.py"]
token_estimate = 60000
acceptance_criteria = ["All endpoints respond"]
"""
    (phase_dir / "plan.toml").write_text(plan_toml)

    progress_toml = """\
[[waves]]
number = 1
status = "active"

[[waves.tasks]]
id = "01-01"
status = "complete"

[[waves.tasks]]
id = "01-02"
status = "active"

[[waves]]
number = 2
status = "pending"

[[waves.tasks]]
id = "01-03"
status = "pending"
"""
    (phase_dir / "progress.toml").write_text(progress_toml)

    return dom_root
