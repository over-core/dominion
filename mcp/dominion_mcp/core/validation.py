"""Configuration integrity validation checks."""

from __future__ import annotations

import json as json_mod
import tomllib
from pathlib import Path

from .config import read_toml_optional


def validate_project(dom_root: Path) -> list[dict]:
    """Run all integrity checks on a Dominion project.

    Returns list of check result dicts:
    [{"check": "name", "status": "pass"|"warn"|"fail", "detail": "..."}]
    """
    project_root = dom_root.parent
    checks: list[dict] = []

    checks.append(_check_toml_integrity(dom_root))
    checks.append(_check_agent_toml_md_consistency(dom_root, project_root))
    checks.append(_check_agent_md_headers(dom_root, project_root))
    checks.append(_check_agents_md(dom_root, project_root))
    checks.append(_check_mcp_json(project_root))
    checks.append(_check_settings_permissions(project_root))
    checks.append(_check_dominion_config(dom_root))
    checks.append(_check_phase_structure(dom_root))
    checks.append(_check_signal_directory(dom_root))
    checks.append(_check_memory_directory(dom_root))
    checks.append(_check_methodology_sections(dom_root))

    return checks


def _check_toml_integrity(dom_root: Path) -> dict:
    """Check all TOML files parse cleanly."""
    errors: list[str] = []
    for toml_file in dom_root.rglob("*.toml"):
        try:
            with open(toml_file, "rb") as f:
                tomllib.load(f)
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"{toml_file.name}: {exc}")

    if errors:
        return {"check": "TOML integrity", "status": "fail", "detail": "; ".join(errors)}
    return {"check": "TOML integrity", "status": "pass", "detail": "All TOML files parse"}


def _check_agent_toml_md_consistency(dom_root: Path, project_root: Path) -> dict:
    """Every .dominion/agents/*.toml has matching .claude/agents/*.md."""
    agents_dir = dom_root / "agents"
    claude_agents_dir = project_root / ".claude" / "agents"
    agent_tomls = sorted(agents_dir.glob("*.toml")) if agents_dir.is_dir() else []

    missing_md: list[str] = []
    for at in agent_tomls:
        md = claude_agents_dir / f"{at.stem}.md"
        if not md.exists():
            missing_md.append(at.stem)

    total = len(agent_tomls)
    matched = total - len(missing_md)

    if not missing_md:
        return {"check": "Agent TOML-MD consistency", "status": "pass", "detail": f"{matched}/{total} matched"}
    return {
        "check": "Agent TOML-MD consistency",
        "status": "fail",
        "detail": f"{matched}/{total} — missing MD: {', '.join(missing_md)}",
    }


def _check_agent_md_headers(dom_root: Path, project_root: Path) -> dict:
    """Agent .md files contain Dominion marker."""
    agents_dir = dom_root / "agents"
    claude_agents_dir = project_root / ".claude" / "agents"
    agent_tomls = sorted(agents_dir.glob("*.toml")) if agents_dir.is_dir() else []

    bad_headers: list[str] = []
    for at in agent_tomls:
        md = claude_agents_dir / f"{at.stem}.md"
        if md.exists():
            content = md.read_text()
            if "Dominion" not in content[:200] and "dominion" not in content[:200]:
                bad_headers.append(at.stem)

    if not bad_headers:
        return {"check": "Agent MD headers", "status": "pass", "detail": ""}
    return {"check": "Agent MD headers", "status": "fail", "detail": f"Missing header: {', '.join(bad_headers)}"}


def _check_agents_md(dom_root: Path, project_root: Path) -> dict:
    """AGENTS.md exists and lists all agents."""
    agents_md = project_root / "AGENTS.md"
    if not agents_md.exists():
        return {"check": "AGENTS.md roster", "status": "fail", "detail": "AGENTS.md not found"}

    agents_dir = dom_root / "agents"
    agent_tomls = sorted(agents_dir.glob("*.toml")) if agents_dir.is_dir() else []
    content = agents_md.read_text().lower()

    missing: list[str] = []
    for at in agent_tomls:
        name = at.stem
        if name not in content and name.replace("-", " ") not in content:
            missing.append(name)

    if not missing:
        return {"check": "AGENTS.md roster", "status": "pass", "detail": ""}
    return {"check": "AGENTS.md roster", "status": "warn", "detail": f"Missing: {', '.join(missing)}"}


def _check_mcp_json(project_root: Path) -> dict:
    """Check .mcp.json exists with dominion server config."""
    mcp_json = project_root / ".mcp.json"
    if not mcp_json.exists():
        return {"check": ".mcp.json", "status": "fail", "detail": ".mcp.json not found"}

    try:
        with open(mcp_json) as f:
            data = json_mod.load(f)
        if "dominion" in data:
            return {"check": ".mcp.json", "status": "pass", "detail": "dominion server configured"}
        return {"check": ".mcp.json", "status": "fail", "detail": "No 'dominion' entry in .mcp.json"}
    except json_mod.JSONDecodeError:
        return {"check": ".mcp.json", "status": "fail", "detail": "Malformed .mcp.json"}


def _check_settings_permissions(project_root: Path) -> dict:
    """Check settings.local.json has MCP permissions."""
    settings_path = project_root / ".claude" / "settings.local.json"
    if not settings_path.exists():
        return {"check": "Settings permissions", "status": "fail", "detail": "settings.local.json not found"}

    try:
        with open(settings_path) as f:
            settings = json_mod.load(f)
        perms = settings.get("permissions", {}).get("allow", [])
        has_mcp = any("mcp__dominion__" in p for p in perms)
        if has_mcp:
            return {"check": "Settings permissions", "status": "pass", "detail": "MCP permissions present"}
        return {"check": "Settings permissions", "status": "warn", "detail": "No mcp__dominion__ permissions found"}
    except json_mod.JSONDecodeError:
        return {"check": "Settings permissions", "status": "fail", "detail": "Malformed settings.local.json"}


def _check_dominion_config(dom_root: Path) -> dict:
    """Check dominion.toml exists with required sections."""
    dominion = read_toml_optional(dom_root / "dominion.toml")
    if not dominion:
        return {"check": "dominion.toml", "status": "fail", "detail": "dominion.toml not found"}

    if "project" not in dominion:
        return {"check": "dominion.toml", "status": "fail", "detail": "Missing [project] section"}

    return {"check": "dominion.toml", "status": "pass", "detail": "Core config present"}


def _check_phase_structure(dom_root: Path) -> dict:
    """Check active phase directory exists."""
    state = read_toml_optional(dom_root / "state.toml")
    if not state:
        return {"check": "Phase structure", "status": "warn", "detail": "state.toml not found"}

    phase_num = state.get("position", {}).get("phase", 0)
    if phase_num == 0:
        return {"check": "Phase structure", "status": "pass", "detail": "No active phase"}

    phase_dir = dom_root / "phases" / str(phase_num)
    if phase_dir.is_dir():
        return {"check": "Phase structure", "status": "pass", "detail": ""}
    return {"check": "Phase structure", "status": "fail", "detail": f"Phase {phase_num} directory missing"}


def _check_signal_directory(dom_root: Path) -> dict:
    """Check signal directory for orphaned signals."""
    signals_dir = dom_root / "signals"
    if not signals_dir.is_dir():
        return {"check": "Signal directory", "status": "pass", "detail": "No signals directory"}

    blockers = list(signals_dir.glob("blocker-*.toml"))
    if not blockers:
        return {"check": "Signal directory", "status": "pass", "detail": "No active blockers"}
    return {"check": "Signal directory", "status": "warn", "detail": f"{len(blockers)} active blocker(s)"}


def _check_memory_directory(dom_root: Path) -> dict:
    """Check agent memory directory exists."""
    memory_dir = dom_root / "memory"
    if memory_dir.is_dir():
        return {"check": "Agent memory", "status": "pass", "detail": "Memory directory present"}
    return {"check": "Agent memory", "status": "warn", "detail": "Memory directory missing (run onboard)"}


def _check_methodology_sections(dom_root: Path) -> dict:
    """Check agent methodology section directories exist."""
    agents_dir = dom_root / "agents"
    if not agents_dir.is_dir():
        return {"check": "Methodology sections", "status": "warn", "detail": "No agents directory"}

    agent_tomls = sorted(agents_dir.glob("*.toml"))
    missing_sections: list[str] = []
    for at in agent_tomls:
        sections_dir = agents_dir / at.stem / "sections"
        if not sections_dir.is_dir():
            missing_sections.append(at.stem)

    if not missing_sections:
        return {"check": "Methodology sections", "status": "pass", "detail": "All agents have sections"}
    if len(missing_sections) == len(agent_tomls):
        return {"check": "Methodology sections", "status": "warn", "detail": "No agents have methodology sections yet"}
    return {
        "check": "Methodology sections",
        "status": "warn",
        "detail": f"Missing sections for: {', '.join(missing_sections)}",
    }
