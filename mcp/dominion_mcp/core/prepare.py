"""CLAUDE.md generation — the heart of the v0.3.0 context engine.

Assembles markdown briefs for phases, steps, and tasks by reading config,
agent TOML, heuristics, prior summaries, knowledge index, and decisions.
"""

from __future__ import annotations

from pathlib import Path

from .config import read_toml, read_toml_optional


# ---------------------------------------------------------------------------
# Tool directive templates (only included when MCP is detected in config)
# ---------------------------------------------------------------------------

_TOOL_DIRECTIVES: dict[str, str] = {
    "serena": "MANDATORY: Use Serena for ALL code navigation (find_symbol, get_symbols_overview, search_for_pattern). Use Read ONLY for non-code files (markdown, config, JSON, YAML). NEVER use Read for .py/.ts/.js/.rs/.go/.java/.cpp files.",
    "context7": "Documentation: Context7 (resolve-library-id → query-docs) for library docs.",
    "exa": "Search: Exa (web_search_exa) for broader search, recent content, examples.",
    "echovault": "Memory: EchoVault for cross-session decisions. Check before re-deciding.",
    "sequential-thinking": "Reasoning: sequential-thinking for 3+ step reasoning chains.",
}

_DOC_CHAIN = """\
Documentation chain: Context7 -> Exa -> WebSearch -> NEVER guess API signatures."""


# ---------------------------------------------------------------------------
# Phase-level CLAUDE.md
# ---------------------------------------------------------------------------


def generate_phase_claude_md(
    phase: str,
    intent: str,
    complexity: str,
    pipeline: list[str],
    config: dict,
    phases: list[dict],
    decisions: list[dict],
) -> str:
    """Generate phase-level CLAUDE.md content.

    Contains intent, complexity, pipeline, project context, prior phases, decisions.
    """
    sections = [
        f"# Phase {phase}: {intent}",
        "",
        "## Intent",
        intent,
        "",
        "## Complexity",
        complexity,
        "",
        "## Pipeline",
        " -> ".join(pipeline),
        "",
    ]

    # Project context
    project = config.get("project", {})
    if project:
        sections.extend([
            "## Project Context",
            f"- Languages: {', '.join(project.get('languages', []))}",
            f"- Frameworks: {', '.join(project.get('frameworks', []))}",
        ])
        if project.get("direction"):
            sections.append(f"- Direction: {project['direction']}")
        if project.get("git_platform"):
            sections.append(f"- Git platform: {project['git_platform']}")
        sections.append("")

    # Prior phases
    completed_phases = [p for p in phases if p.get("status") == "complete"]
    if completed_phases:
        sections.append("## Prior Phases")
        for p in completed_phases:
            sections.append(f"- Phase {p.get('id', '?')} (complete): {p.get('intent', '?')}")
        sections.append("")

    # Active decisions
    if decisions:
        sections.append("## Active Decisions")
        for d in decisions:
            tags = ", ".join(d.get("tags", []))
            sections.append(
                f"{d.get('id', '?')}. {d.get('title', '?')}: "
                f"{d.get('decision', '?')} ({d.get('rationale', '?')}) [{tags}]"
            )
        sections.append("")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Step-level CLAUDE.md
# ---------------------------------------------------------------------------

# Role display names
_ROLE_NAMES: dict[str, str] = {
    "researcher": "Researcher",
    "architect": "Architect",
    "developer": "Developer",
    "reviewer": "Reviewer",
    "security-auditor": "Security Auditor",
    "analyst": "Analyst",
    "innovation-engineer": "Innovation Engineer",
}


def generate_step_claude_md(
    phase: str,
    step: str,
    role: str,
    intent: str,
    config: dict,
    agent_toml: dict,
    heuristics: str | None,
    prior_summaries: dict[str, str],
    knowledge_entries: list[dict],
    decisions: list[dict],
) -> str:
    """Generate step-level CLAUDE.md content.

    The complete agent brief — everything the agent needs in one file.
    """
    role_name = _ROLE_NAMES.get(role, role.replace("-", " ").title())
    sections = [
        f"# {step.title()} Brief — Phase {phase}",
        "",
        "## Your Role",
        f"You are the {role_name}. {agent_toml.get('agent', {}).get('purpose', '')}",
        "",
        "## Intent",
        intent,
        "",
    ]

    # Heuristics (verbatim from .dominion/heuristics/{step}.md)
    if heuristics:
        sections.extend(["## Heuristics", heuristics, ""])

    # Prior step summaries
    if prior_summaries:
        sections.append("## Prior Step Summaries")
        sections.append("")
        for s_name, s_text in prior_summaries.items():
            sections.extend([f"### {s_name.title()}", s_text, ""])

    # Project conventions
    style = config.get("style", {})
    if style:
        sections.append("## Project Conventions")
        if style.get("testing"):
            sections.append(f"- Testing: {style['testing']}")
        for conv in style.get("conventions", []):
            sections.append(f"- {conv}")
        sections.append("")

    # Existing knowledge
    if knowledge_entries:
        sections.append("## Existing Knowledge")
        for entry in knowledge_entries:
            sections.append(f"- {entry.get('topic', '?')}: {entry.get('summary', '?')}")
        sections.append("")

    # Tool usage
    available_tools = config.get("tools", {}).get("available", [])
    if available_tools:
        sections.append("## Tool Usage (MANDATORY)")
        has_doc_tools = any(t in available_tools for t in ("context7", "exa"))
        if has_doc_tools:
            sections.append(_DOC_CHAIN)
        for tool_name in available_tools:
            if tool_name in _TOOL_DIRECTIVES:
                sections.append(_TOOL_DIRECTIVES[tool_name])
        sections.append("")

    # Hard stops from agent TOML
    hard_stops = agent_toml.get("governance", {}).get("hard_stops", [])
    if hard_stops:
        sections.append("## Hard Stops")
        for stop in hard_stops:
            sections.append(f"- {stop}")
        sections.append("")

    # Decisions
    if decisions:
        sections.append("## Active Decisions")
        for d in decisions:
            sections.append(f"- {d.get('title', '?')}: {d.get('decision', '?')}")
        sections.append("")

    # Submission instructions
    sections.extend([
        "## Submission",
        f'When complete, call mcp__dominion__submit_work with:',
        f'- phase: "{phase}"',
        f'- step: "{step}"',
        f'- role: "{role}"',
        "- content: your findings/results (JSON, will be converted to TOML)",
        "- summary: condensed summary (REQUIRED)",
        "",
    ])

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Task-level CLAUDE.md
# ---------------------------------------------------------------------------


def generate_task_claude_md(
    phase: str,
    task_id: str,
    task_info: dict,
    config: dict,
    agent_toml: dict,
    heuristics: str | None,
    research_summary: str | None,
    plan_summary: str | None,
    knowledge_entries: list[dict],
    upstream_task_summaries: dict[str, str],
) -> str:
    """Generate task-level CLAUDE.md content.

    The full developer brief for a specific task.
    """
    title = task_info.get("title", f"Task {task_id}")
    role = task_info.get("agent_role", "developer")
    role_name = _ROLE_NAMES.get(role, role.replace("-", " ").title())

    sections = [
        f"# Task {task_id}: {title} — Phase {phase}",
        "",
        "## Your Role",
        f"You are the {role_name}. Implement this task, run tests, commit in your worktree.",
        "",
        "## Assignment",
        task_info.get("description", ""),
        "",
    ]

    # Files
    files = task_info.get("files", [])
    if files:
        sections.append("## Files")
        for f in files:
            sections.append(f"- {f}")
        sections.append("")

    # Dependencies
    deps = task_info.get("dependencies", [])
    sections.append("## Dependencies")
    sections.append(f"{'None (wave 1)' if not deps else ', '.join(deps)}")
    sections.append("")

    # Research context
    if research_summary:
        sections.extend(["## Research Context", research_summary, ""])

    # Plan context
    if plan_summary:
        sections.extend(["## Plan Context", plan_summary, ""])

    # Upstream task summaries (from earlier waves)
    if upstream_task_summaries:
        sections.append("## Upstream Tasks")
        for tid, summary in upstream_task_summaries.items():
            sections.extend([f"### Task {tid}", summary, ""])

    # Knowledge
    if knowledge_entries:
        sections.append("## Existing Knowledge")
        for entry in knowledge_entries:
            sections.append(f"- {entry.get('topic', '?')}: {entry.get('summary', '?')}")
        sections.append("")

    # Heuristics
    if heuristics:
        sections.extend(["## Heuristics", heuristics, ""])

    # Project conventions
    style = config.get("style", {})
    if style:
        sections.append("## Project Conventions")
        if style.get("testing"):
            sections.append(f"- Testing: {style['testing']}")
        for conv in style.get("conventions", []):
            sections.append(f"- {conv}")
        sections.append("")

    # Hard stops
    hard_stops = agent_toml.get("governance", {}).get("hard_stops", [])
    if hard_stops:
        sections.append("## Hard Stops")
        for stop in hard_stops:
            sections.append(f"- {stop}")
        sections.append("")

    # Tool usage
    available_tools = config.get("tools", {}).get("available", [])
    if available_tools:
        sections.append("## Tool Usage (MANDATORY)")
        has_doc_tools = any(t in available_tools for t in ("context7", "exa"))
        if has_doc_tools:
            sections.append(_DOC_CHAIN)
        for tool_name in available_tools:
            if tool_name in _TOOL_DIRECTIVES:
                sections.append(_TOOL_DIRECTIVES[tool_name])
        sections.append("")

    # Submission
    sections.extend([
        "## Submission",
        f'When complete, call mcp__dominion__submit_work with:',
        f'- phase: "{phase}"',
        f'- step: "execute"',
        f'- role: "{role}"',
        f'- task_id: "{task_id}"',
        "- content: {commit, files_changed, tests_run, tests_passed}",
        "- summary: what you did, approach taken, issues encountered (REQUIRED)",
        "",
    ])

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Helper: filter knowledge index
# ---------------------------------------------------------------------------


def filter_knowledge_by_step(
    index_entries: list[dict], step: str
) -> list[dict]:
    """Filter knowledge index entries by step tag overlap."""
    return [e for e in index_entries if step in e.get("tags", [])]


def filter_knowledge_by_files(
    index_entries: list[dict], task_files: list[str]
) -> list[dict]:
    """Filter knowledge entries by referenced_files intersection with task files."""
    if not task_files:
        return index_entries
    task_set = set(task_files)
    result = []
    for entry in index_entries:
        ref_files = entry.get("referenced_files", [])
        if not ref_files or task_set & set(ref_files):
            result.append(entry)
    return result


# ---------------------------------------------------------------------------
# Helper: read common inputs for generation
# ---------------------------------------------------------------------------


def read_heuristics(dom_root: Path, step: str, role: str | None = None) -> str | None:
    """Read heuristics for a step, optionally appending role-specific heuristics."""
    parts: list[str] = []
    step_path = dom_root / "heuristics" / f"{step}.md"
    if step_path.exists():
        parts.append(step_path.read_text())
    if role:
        role_path = dom_root / "heuristics" / f"{role}.md"
        if role_path.exists():
            parts.append(role_path.read_text())
    return "\n\n".join(parts) if parts else None


def read_agent_toml(dom_root: Path, role: str) -> dict:
    """Read agent TOML config. Returns empty dict if not found."""
    path = dom_root / "agents" / f"{role}.toml"
    return read_toml_optional(path) or {}


def read_knowledge_index(dom_root: Path) -> list[dict]:
    """Read knowledge index.toml entries. Returns empty list if not found."""
    index = read_toml_optional(dom_root / "knowledge" / "index.toml")
    if not index:
        return []
    return index.get("entries", [])


def read_prior_summaries(
    dom_root: Path, phase: str, pipeline: list[str], current_step: str
) -> dict[str, str]:
    """Read summaries from all completed steps before current_step.

    Also reads summary for the current step if it exists (for two-phase review).
    Returns {step_name: summary_text}.
    """
    from .filesystem import read_summary, read_status

    summaries = {}
    for step in pipeline:
        status_path = dom_root / "phases" / phase / step / "status"
        status = read_status(status_path)

        if status == "complete" or step == current_step:
            summary = read_summary(dom_root, phase, step)
            if summary:
                summaries[step] = summary

        if step == current_step:
            break

    return summaries
