"""Setup tools — start_phase, prepare_step, prepare_task.

Called by the orchestrator to initialize phases and prepare agent context.
"""

from __future__ import annotations

from pathlib import Path

from ..server import mcp
from ..core.config import find_dominion_root, read_toml, read_toml_optional
from ..core.complexity import get_dispatch, get_pipeline
from ..core.filesystem import (
    create_phase_dirs,
    create_task_dirs,
    read_status,
    write_status,
    write_claude_md,
    write_agent_claude_md,
    write_phase_claude_md,
    write_task_claude_md,
    read_summary,
)
from ..core.prepare import (
    generate_phase_claude_md,
    generate_step_claude_md,
    generate_task_claude_md,
    read_agent_toml,
    read_heuristics,
    read_interface_contracts,
    read_knowledge_index,
    read_prior_summaries,
    filter_knowledge_by_step,
    filter_knowledge_by_files,
)
from ..core.state import (
    add_phase,
    get_decisions,
    get_phases,
    next_phase_id,
    update_position,
)


@mcp.tool()
async def start_phase(intent: str, complexity: str) -> dict:
    """Initialize a new pipeline phase.

    Creates phase directory tree, generates phase CLAUDE.md, updates state.toml.

    Args:
        intent: What the user wants to accomplish.
        complexity: trivial | analysis | specified | moderate | complex | major.
    """
    valid = ("trivial", "analysis", "specified", "moderate", "complex", "major")
    if complexity not in valid:
        return {"error": f"Invalid complexity '{complexity}'. Must be one of: {', '.join(valid)}"}

    try:
        dom_root = find_dominion_root()
    except ValueError:
        return {"error": ".dominion/ directory not found. Run /dominion:onboard first."}

    config = read_toml_optional(dom_root / "config.toml") or {}
    pipeline = get_pipeline(complexity)
    phase_id = next_phase_id(dom_root)

    # Create directory tree
    phase_dir = create_phase_dirs(dom_root, phase_id, pipeline)

    # Generate phase CLAUDE.md
    phases = get_phases(dom_root)
    decisions = get_decisions(dom_root)
    content = generate_phase_claude_md(
        phase=phase_id,
        intent=intent,
        complexity=complexity,
        pipeline=pipeline,
        config=config,
        phases=phases,
        decisions=decisions,
    )
    write_phase_claude_md(dom_root, phase_id, content)

    # Update state.toml
    await add_phase(dom_root, phase_id, intent, complexity)
    await update_position(
        dom_root,
        phase=phase_id,
        step=pipeline[0],
        wave=0,
        status="active",
        complexity_level=complexity,
    )

    return {
        "phase": phase_id,
        "complexity": complexity,
        "pipeline": pipeline,
        "phase_dir": str(phase_dir.relative_to(dom_root.parent)),
    }


@mcp.tool()
async def prepare_step(phase: str, step: str, role: str | None = None) -> dict:
    """Generate step-level CLAUDE.md from config + prior outputs + heuristics + knowledge.

    Idempotent — can be called multiple times. Re-call regenerates CLAUDE.md.
    Returns path + dispatch info (NO claude_md_content for context pressure mitigation).

    Args:
        phase: Phase ID (e.g., "01").
        step: Step name (research | plan | review | discuss).
        role: Override role for the brief. When provided, generates a role-specific brief.
    """
    try:
        dom_root = find_dominion_root()
    except ValueError:
        return {"error": ".dominion/ directory not found."}

    phase_dir = dom_root / "phases" / phase
    if not phase_dir.exists():
        return {"error": f"Phase {phase} not found. Call start_phase first."}

    step_dir = phase_dir / step
    if not step_dir.exists():
        return {"error": f"Step '{step}' not in pipeline for phase {phase}."}

    config = read_toml_optional(dom_root / "config.toml") or {}
    active_agents = config.get("agents", {}).get("active", [])
    complexity = (read_toml_optional(dom_root / "state.toml") or {}).get(
        "position", {}
    ).get("complexity_level", "moderate")

    # Determine target role
    if role:
        target_role = role
    else:
        # Use primary role from dispatch table
        try:
            _, agents = get_dispatch(step, complexity, active_agents)
            target_role = agents[0]["role"] if agents else step
        except ValueError:
            target_role = step

    if role and role not in active_agents:
        return {"error": f"Role '{role}' not in config.toml [agents].active."}

    # Read inputs
    agent_toml = read_agent_toml(dom_root, target_role)
    heuristics = read_heuristics(dom_root, step, role=target_role)
    knowledge_index = read_knowledge_index(dom_root)
    knowledge_entries = filter_knowledge_by_step(knowledge_index, step)

    # Load full knowledge content (v0.4.3 — inject content, not just summaries)
    for entry in knowledge_entries:
        kpath = dom_root / "knowledge" / entry.get("path", f"{entry.get('topic', 'unknown')}.md")
        if kpath.exists():
            entry["_content"] = kpath.read_text()
    decisions = get_decisions(dom_root)
    pipeline = get_pipeline(complexity)

    # Read prior summaries (including current step for two-phase review)
    prior_summaries = read_prior_summaries(dom_root, phase, pipeline, step)

    # Read phase intent
    phase_claude = phase_dir / "CLAUDE.md"
    intent = ""
    if phase_claude.exists():
        for line in phase_claude.read_text().splitlines():
            if line.startswith("# Phase"):
                intent = line.split(": ", 1)[1] if ": " in line else ""
                break

    # Generate CLAUDE.md
    content = generate_step_claude_md(
        phase=phase,
        step=step,
        role=target_role,
        intent=intent,
        config=config,
        agent_toml=agent_toml,
        heuristics=heuristics,
        prior_summaries=prior_summaries,
        knowledge_entries=knowledge_entries,
        decisions=decisions,
    )

    # Write CLAUDE.md
    if role:
        path = write_agent_claude_md(dom_root, phase, step, role, content)
    else:
        path = write_claude_md(dom_root, phase, step, content)

    # Status management: pending→active, active→unchanged, complete→active (retry)
    status_path = step_dir / "status"
    current_status = read_status(status_path)
    if current_status == "pending":
        write_status(status_path, "active")
    elif current_status == "complete":
        write_status(status_path, "active")  # Retry support (C4)

    # Get dispatch info
    try:
        thread_type, agents = get_dispatch(step, complexity, active_agents)
    except ValueError:
        thread_type = "B-Thread"
        agents = [{"role": target_role, "model": "opus"}]

    # Override model from agent TOML if specified + add agent_path
    for agent in agents:
        agent_conf = read_agent_toml(dom_root, agent["role"])
        if agent_conf.get("agent", {}).get("model"):
            agent["model"] = agent_conf["agent"]["model"]
        agent["agent_path"] = f".claude/agents/{agent['role']}.md"

    return {
        "claude_md_path": str(path.relative_to(dom_root.parent)),
        "thread_type": thread_type,
        "agents": agents,
    }


@mcp.tool()
async def prepare_task(
    phase: str, task_id: str, task_info: str | None = None
) -> dict:
    """Generate task-level CLAUDE.md from plan + research + knowledge.

    Args:
        phase: Phase ID.
        task_id: Task ID (e.g., "01", "fix-01").
        task_info: JSON string with inline task definition. Required for fix/trivial tasks.
                   Format: {"title", "description", "files", "wave", "dependencies", "agent_role"}.
    """
    import json

    try:
        dom_root = find_dominion_root()
    except ValueError:
        return {"error": ".dominion/ directory not found."}

    phase_dir = dom_root / "phases" / phase
    if not phase_dir.exists():
        return {"error": f"Phase {phase} not found."}

    config = read_toml_optional(dom_root / "config.toml") or {}

    # Get task definition
    if task_info:
        try:
            task = json.loads(task_info) if isinstance(task_info, str) else task_info
        except json.JSONDecodeError:
            return {"error": "task_info must be valid JSON."}
        if not task.get("title") or not task.get("description"):
            return {"error": "task_info requires 'title' and 'description' fields."}
    else:
        # Read from tasks.toml — find under any [findings.*.tasks] namespace (H3)
        tasks_path = phase_dir / "plan" / "output" / "tasks.toml"
        tasks_data = read_toml_optional(tasks_path)
        if not tasks_data:
            return {
                "error": f"Task {task_id} not found in plan. Provide task_info for fix/trivial tasks."
            }

        task = None
        findings = tasks_data.get("findings", {})
        for role_key, role_data in findings.items():
            if isinstance(role_data, dict):
                for t in role_data.get("tasks", []):
                    if t.get("task_id") == task_id:
                        task = t
                        break
            if task:
                break

        if not task:
            return {"error": f"Task {task_id} not found in tasks.toml under any role namespace."}

    # Read inputs
    agent_role = task.get("agent_role", "developer")
    agent_toml = read_agent_toml(dom_root, agent_role)
    heuristics = read_heuristics(dom_root, "execute", role=agent_role)

    research_summary = read_summary(dom_root, phase, "research")
    plan_summary = read_summary(dom_root, phase, "plan")

    # Knowledge filtering: by "execute" tag + referenced_files intersection
    knowledge_index = read_knowledge_index(dom_root)
    knowledge_entries = filter_knowledge_by_step(knowledge_index, "execute")
    task_files = task.get("files", [])
    if task_files:
        knowledge_entries = filter_knowledge_by_files(knowledge_entries, task_files)

    # Load full knowledge content (v0.4.3 — inject content, not just summaries)
    for entry in knowledge_entries:
        kpath = dom_root / "knowledge" / entry.get("path", f"{entry.get('topic', 'unknown')}.md")
        if kpath.exists():
            entry["_content"] = kpath.read_text()

    # Upstream task summaries (from earlier waves)
    from ..core.filesystem import read_task_summary
    upstream: dict[str, str] = {}
    for dep_id in task.get("dependencies", []):
        dep_summary = read_task_summary(dom_root, phase, dep_id)
        if dep_summary:
            upstream[dep_id] = dep_summary

    # Interface contracts (v0.4.3 — cross-task visibility)
    contracts = read_interface_contracts(dom_root, phase, task_id)

    # Decisions (v0.4.3 — visible to task agents, not just step agents)
    decisions = get_decisions(dom_root)

    # Generate CLAUDE.md
    content = generate_task_claude_md(
        phase=phase,
        task_id=task_id,
        task_info=task,
        config=config,
        agent_toml=agent_toml,
        heuristics=heuristics,
        research_summary=research_summary,
        plan_summary=plan_summary,
        knowledge_entries=knowledge_entries,
        upstream_task_summaries=upstream,
        interface_contracts=contracts,
        decisions=decisions,
    )

    # Create task directory and write CLAUDE.md
    task_dir = create_task_dirs(dom_root, phase, task_id)
    path = write_task_claude_md(dom_root, phase, task_id, content)

    return {
        "claude_md_path": str(path.relative_to(dom_root.parent)),
        "task": {
            "task_id": task_id,
            "title": task.get("title", ""),
            "wave": task.get("wave", 1),
            "agent_role": agent_role,
            "files": task_files,
        },
    }
