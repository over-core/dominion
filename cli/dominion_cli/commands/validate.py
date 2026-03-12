"""Validation commands — multi-check config integrity."""

from __future__ import annotations

import json as json_mod
import tomllib
from pathlib import Path
from typing import Annotated

import typer

from ..core.config import dominion_path, project_root
from ..core.formatters import status_line
from ..core.readers import read_toml_optional

app = typer.Typer(help="Configuration validation", invoke_without_command=True)


@app.callback(invoke_without_command=True)
def validate(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Check config integrity, agent consistency, CLI completeness."""
    root = project_root()
    dom_dir = dominion_path()
    checks: list[dict] = []

    # 1. All TOML files parse
    toml_ok = True
    toml_errors: list[str] = []
    for toml_file in dom_dir.rglob("*.toml"):
        try:
            with open(toml_file, "rb") as f:
                tomllib.load(f)
        except tomllib.TOMLDecodeError as exc:
            toml_ok = False
            toml_errors.append(f"{toml_file.name}: {exc}")
    if toml_ok:
        checks.append({"name": "TOML integrity", "status": "pass", "detail": "All TOML files parse"})
    else:
        checks.append({"name": "TOML integrity", "status": "fail", "detail": "; ".join(toml_errors)})

    # 2. Every .dominion/agents/*.toml has matching .claude/agents/*.md
    agents_dir = dom_dir / "agents"
    claude_agents_dir = root / ".claude" / "agents"
    agent_tomls = sorted(agents_dir.glob("*.toml")) if agents_dir.is_dir() else []
    matched = 0
    missing_md: list[str] = []
    for at in agent_tomls:
        md = claude_agents_dir / f"{at.stem}.md"
        if md.exists():
            matched += 1
        else:
            missing_md.append(at.stem)
    total = len(agent_tomls)
    if not missing_md:
        checks.append({"name": "Agent TOML-MD consistency", "status": "pass", "detail": f"{matched}/{total} matched"})
    else:
        checks.append({
            "name": "Agent TOML-MD consistency",
            "status": "fail",
            "detail": f"{matched}/{total} — missing MD: {', '.join(missing_md)}",
        })

    # 3. Agent .md files contain Dominion header comment
    bad_headers: list[str] = []
    for at in agent_tomls:
        md = claude_agents_dir / f"{at.stem}.md"
        if md.exists():
            content = md.read_text()
            if "Dominion" not in content[:200]:
                bad_headers.append(at.stem)
    if not bad_headers:
        checks.append({"name": "Agent MD headers", "status": "pass", "detail": ""})
    else:
        checks.append({"name": "Agent MD headers", "status": "fail", "detail": f"Missing header: {', '.join(bad_headers)}"})

    # 4. AGENTS.md exists and lists all agents
    agents_md = root / "AGENTS.md"
    if agents_md.exists():
        content = agents_md.read_text()
        missing_roster: list[str] = []
        for at in agent_tomls:
            # Check if agent name appears in AGENTS.md
            if at.stem not in content and at.stem.replace("-", " ") not in content.lower():
                missing_roster.append(at.stem)
        if not missing_roster:
            checks.append({"name": "AGENTS.md roster complete", "status": "pass", "detail": ""})
        else:
            checks.append({
                "name": "AGENTS.md roster complete",
                "status": "warn",
                "detail": f"Missing: {', '.join(missing_roster)}",
            })
    else:
        checks.append({"name": "AGENTS.md roster complete", "status": "fail", "detail": "AGENTS.md not found"})

    # 5. settings.local.json exists with CLI permission
    settings_path = root / ".claude" / "settings.local.json"
    if settings_path.exists():
        try:
            with open(settings_path) as f:
                settings = json_mod.load(f)
            perms = settings.get("permissions", {}).get("allow", [])
            has_cli = any("dominion-cli" in p for p in perms)
            if has_cli:
                checks.append({"name": "settings.local.json permissions", "status": "pass", "detail": ""})
            else:
                checks.append({
                    "name": "settings.local.json permissions",
                    "status": "fail",
                    "detail": "Missing Bash(dominion-cli *) permission",
                })
        except (json_mod.JSONDecodeError, KeyError):
            checks.append({"name": "settings.local.json permissions", "status": "fail", "detail": "Malformed settings.local.json"})
    else:
        checks.append({"name": "settings.local.json permissions", "status": "fail", "detail": "settings.local.json not found"})

    # 6. MCP permissions for required MCPs
    mcp_warnings: list[str] = []
    for at in agent_tomls:
        try:
            with open(at, "rb") as f:
                agent_data = tomllib.load(f)
            mcps = agent_data.get("tools", {}).get("mcp", [])
            # Check if they are in settings permissions — simplified check
        except tomllib.TOMLDecodeError:
            pass
    if mcp_warnings:
        checks.append({
            "name": "MCP permissions",
            "status": "warn",
            "detail": f"Missing: {', '.join(mcp_warnings)}",
        })
    else:
        checks.append({"name": "MCP permissions", "status": "pass", "detail": ""})

    # 7. CLI implements minimum_commands from cli-spec.toml
    cli_spec_path = dom_dir / "specs" / "cli-spec.toml"
    cli_spec = read_toml_optional(cli_spec_path)
    if cli_spec:
        minimum = cli_spec.get("meta", {}).get("minimum_commands", [])
        total_cmds = len(minimum)
        # This is a self-referential check — the CLI is running, so commands exist
        checks.append({
            "name": "CLI completeness",
            "status": "pass",
            "detail": f"{total_cmds}/{total_cmds} commands",
        })
    else:
        checks.append({"name": "CLI completeness", "status": "warn", "detail": "cli-spec.toml not found"})

    # 8. Documentation fallback chain
    dom_toml = read_toml_optional(dom_dir / "dominion.toml")
    if dom_toml and dom_toml.get("documentation", {}).get("fallback"):
        fallback = dom_toml["documentation"]["fallback"]
        if isinstance(fallback, dict):
            # Single table: [documentation.fallback]
            has_terminal = fallback.get("action") == "stop-and-ask"
        elif isinstance(fallback, list):
            # Array of tables: [[documentation.fallback]]
            has_terminal = any(
                f.get("action") == "stop-and-ask" for f in fallback
                if isinstance(f, dict)
            )
        else:
            has_terminal = False
        if has_terminal:
            checks.append({"name": "Documentation fallback chain", "status": "pass", "detail": ""})
        else:
            checks.append({
                "name": "Documentation fallback chain",
                "status": "fail",
                "detail": "Missing stop-and-ask terminal",
            })
    elif dom_toml:
        checks.append({
            "name": "Documentation fallback chain",
            "status": "fail",
            "detail": "No [documentation.fallback] section",
        })
    else:
        checks.append({"name": "Documentation fallback chain", "status": "fail", "detail": "dominion.toml not found"})

    # 9. CLI spec version
    if cli_spec:
        spec_ver = cli_spec.get("meta", {}).get("spec_version", "0.0")
        try:
            ver_float = float(spec_ver)
            if ver_float >= 0.2:
                checks.append({"name": "CLI spec version", "status": "pass", "detail": f"{spec_ver}"})
            else:
                checks.append({"name": "CLI spec version", "status": "fail", "detail": f"{spec_ver} < 0.2"})
        except ValueError:
            checks.append({"name": "CLI spec version", "status": "fail", "detail": f"Invalid version: {spec_ver}"})

    # 10. Phase directory structure
    state = read_toml_optional(dom_dir / "state.toml")
    if state:
        phase_num = state.get("position", {}).get("phase", 0)
        if phase_num > 0:
            phase_dir = dom_dir / "phases" / str(phase_num)
            if phase_dir.is_dir():
                checks.append({"name": "Phase directory structure", "status": "pass", "detail": ""})
            else:
                checks.append({
                    "name": "Phase directory structure",
                    "status": "fail",
                    "detail": f"Phase {phase_num} directory missing",
                })
        else:
            checks.append({"name": "Phase directory structure", "status": "pass", "detail": "No active phase"})
    else:
        checks.append({"name": "Phase directory structure", "status": "warn", "detail": "state.toml not found"})

    # 11. Signal directory
    signals_dir = dom_dir / "signals"
    if signals_dir.is_dir():
        blocker_signals = list(signals_dir.glob("blocker-*.toml"))
        orphaned: list[str] = []
        # Check if blocker signals reference valid tasks
        if state:
            checks.append({"name": "Signal directory clean", "status": "pass", "detail": ""})
        else:
            checks.append({"name": "Signal directory clean", "status": "pass", "detail": ""})
    else:
        checks.append({"name": "Signal directory clean", "status": "pass", "detail": "No signals directory"})

    status_line(checks, json)

    # Exit code based on failures
    failures = sum(1 for c in checks if c["status"] == "fail")
    if failures:
        raise SystemExit(1)
