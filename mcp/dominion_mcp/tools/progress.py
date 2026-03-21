"""Progress tools — get_progress, quality_gate, assess_complexity, advance_step, save_decision.

Pipeline state management tools called by the orchestrator.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..server import mcp
from ..core.config import find_dominion_root, read_toml_optional
from ..core.complexity import (
    assess_complexity as _assess,
    get_pipeline,
)
from ..core.filesystem import (
    read_status,
    scan_step_statuses,
    scan_task_statuses,
    write_status,
)
from ..core.state import (
    get_circuit_breaker,
    get_completed_tasks,
    get_decisions as _get_decisions,
    get_phases,
    get_position,
    save_decision as _save_decision,
    update_circuit_breaker,
    update_phase_status,
    update_position,
)


@mcp.tool()
async def get_progress(phase: str | None = None) -> dict:
    """Read pipeline progress from filesystem status + state.toml.

    state.toml is authoritative for pipeline position.
    Status files are authoritative for individual step/task completion.

    Args:
        phase: Phase ID. Without: returns current phase.
    """
    try:
        dom_root = find_dominion_root()
    except ValueError:
        return {"phase": "00", "step": "idle", "complexity": None, "completed_steps": [], "pipeline": []}

    state = read_toml_optional(dom_root / "state.toml")
    if not state:
        return {"phase": "00", "step": "idle", "complexity": None, "completed_steps": [], "pipeline": []}

    pos = get_position(dom_root)
    target_phase = phase or pos.get("phase", "00")

    if target_phase == "00":
        return {"phase": "00", "step": "idle", "complexity": None, "completed_steps": [], "pipeline": []}

    complexity = pos.get("complexity_level", "moderate")
    pipeline = get_pipeline(complexity)
    cb = get_circuit_breaker(dom_root)

    # Scan step statuses
    step_statuses = scan_step_statuses(dom_root, target_phase, pipeline)
    completed_steps = [s for s, st in step_statuses.items() if st == "complete"]

    # Scan task statuses
    task_statuses = scan_task_statuses(dom_root, target_phase)
    completed_tasks = [t for t, st in task_statuses.items() if st == "complete"]
    pending_tasks = [t for t, st in task_statuses.items() if st in ("pending", "active")]

    result = {
        "phase": target_phase,
        "step": pos.get("step", "idle"),
        "wave": pos.get("wave", 0),
        "complexity": complexity,
        "status": pos.get("status", "ready"),
        "completed_steps": completed_steps,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "retry_count": cb.get("retry_count", 0),
        "circuit_breaker": cb.get("state", "closed"),
        "pipeline": pipeline,
    }

    # Check for completion
    if pos.get("step") == "idle" and pos.get("status") == "complete":
        result["status"] = "complete"

    return result


@mcp.tool()
async def quality_gate(phase: str) -> dict:
    """Compute verdict from review output. Manages circuit breaker.

    Reads verdict.toml, deduplicates findings, classifies blocking vs warning,
    computes same-finding hash, updates circuit breaker state.

    Args:
        phase: Phase ID.
    """
    try:
        dom_root = find_dominion_root()
    except ValueError:
        return {"error": ".dominion/ directory not found."}

    verdict_path = dom_root / "phases" / phase / "review" / "output" / "verdict.toml"
    verdict_data = read_toml_optional(verdict_path)
    if not verdict_data:
        return {"error": f"No review artifact for phase {phase}."}

    findings = verdict_data.get("findings", {})
    if not findings:
        return {"verdict": "go", "blocking_findings": [], "warning_findings": [], "action": "proceed", "retry_count": 0, "same_finding": False}

    # Collect all items across role namespaces, deduplicate
    all_items: list[dict] = []
    seen: set[str] = set()
    verdict = "go"

    for role_key, role_data in findings.items():
        if not isinstance(role_data, dict):
            continue
        if role_data.get("verdict"):
            verdict = role_data["verdict"]
        for item in role_data.get("items", []):
            dedup_key = f"{item.get('category', '')}|{item.get('file', '')}|{item.get('description', '')}"
            if dedup_key not in seen:
                seen.add(dedup_key)
                all_items.append(item)

    # Classify — filter out findings marked as verified-fixed by main reviewer
    blocking = [
        i for i in all_items
        if i.get("severity") in ("critical", "high")
        and i.get("action") not in ("warn", "verified-fixed")
    ]
    warnings = [i for i in all_items if i not in blocking]

    # Read config for halt_on_severity
    config = read_toml_optional(dom_root / "config.toml") or {}
    max_retries = config.get("auto", {}).get("max_retries", 3)
    halt_severity = config.get("auto", {}).get("halt_on_severity", "critical")

    cb = get_circuit_breaker(dom_root)
    retry_count = cb.get("retry_count", 0)

    # Determine action
    if not blocking:
        action = "proceed"
    elif any(i.get("severity") == halt_severity for i in blocking):
        action = "halt"
    elif retry_count >= max_retries:
        action = "halt"
    else:
        action = "retry"

    # Same-finding detection
    sorted_findings = sorted(blocking, key=lambda f: (f.get("category", ""), f.get("file", ""), f.get("description", "")))
    hash_input = json.dumps([(f.get("category"), f.get("file"), f.get("description")) for f in sorted_findings], sort_keys=True)
    findings_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    same_finding = False
    same_count = cb.get("same_finding_count", 0)
    if findings_hash == cb.get("last_findings_hash", ""):
        same_count += 1
        same_finding = True
        if same_count >= 2:
            action = "halt"
    else:
        same_count = 0

    # Update circuit breaker
    new_retry = retry_count + (1 if action == "retry" else 0)
    cb_state = "open" if action == "halt" else "closed"
    await update_circuit_breaker(
        dom_root,
        state_val=cb_state,
        retry_count=new_retry,
        iteration_count=cb.get("iteration_count", 0) + 1,
        last_findings_hash=findings_hash,
        same_finding_count=same_count,
    )

    return {
        "verdict": verdict,
        "blocking_findings": blocking,
        "warning_findings": warnings,
        "action": action,
        "retry_count": new_retry,
        "same_finding": same_finding,
    }


@mcp.tool()
async def assess_complexity_tool(intent: str, has_design_doc: bool = False) -> dict:
    """Keyword-based complexity classification.

    When has_design_doc is True, returns "specified" for tasks with comprehensive
    design documents — skipping discuss and research steps.

    Args:
        intent: User's intent description.
        has_design_doc: Whether a design document/spec is available for this task.
    """
    return _assess(intent, has_design_doc=has_design_doc)


@mcp.tool()
async def advance_step(phase: str, step: str) -> dict:
    """Mark a step as complete and advance pipeline position.

    Called by orchestrator after verifying all agents for a step have submitted.
    For execute step, verifies all task statuses show "complete" first.

    Args:
        phase: Phase ID.
        step: Step that just completed.
    """
    try:
        dom_root = find_dominion_root()
    except ValueError:
        return {"error": ".dominion/ directory not found."}

    phase_dir = dom_root / "phases" / phase
    if not phase_dir.exists():
        return {"error": f"Phase {phase} not found."}

    step_dir = phase_dir / step
    if not step_dir.exists():
        return {"error": f"Step '{step}' not found in phase {phase}."}

    # For execute step, check task completions (tasks write to tasks/{id}/output/, not step/output/)
    if step == "execute":
        task_statuses = scan_task_statuses(dom_root, phase)
        if not task_statuses:
            return {"error": f"No tasks found for execute step in phase {phase}."}
        incomplete = [t for t, s in task_statuses.items() if s != "complete"]
        if incomplete:
            return {"error": f"Tasks not complete: {', '.join(incomplete)}. Cannot advance execute step."}
    else:
        # Other steps write to step/output/
        output_dir = step_dir / "output"
        if not output_dir.exists() or not any(output_dir.iterdir()):
            return {"error": f"No submissions for step '{step}'. Output directory is empty."}

    # Mark step as complete
    write_status(step_dir / "status", "complete")

    # Advance to next step
    state = read_toml_optional(dom_root / "state.toml") or {}
    complexity = state.get("position", {}).get("complexity_level", "moderate")
    pipeline = get_pipeline(complexity)

    try:
        current_idx = pipeline.index(step)
    except ValueError:
        return {"error": f"Step '{step}' not in pipeline {pipeline}."}

    if current_idx + 1 < len(pipeline):
        next_step = pipeline[current_idx + 1]
        await update_position(dom_root, step=next_step, wave=0)
        return {"status": "advanced", "from_step": step, "to_step": next_step}
    else:
        # Last step — pipeline complete
        await update_position(dom_root, step="idle", status="complete")
        await update_phase_status(dom_root, phase, "complete")
        return {"status": "advanced", "from_step": step, "to_step": "idle"}


@mcp.tool()
async def generate_phase_report(phase: str) -> dict:
    """Generate pipeline metrics from phase filesystem data.

    Computes task/wave counts, review findings by severity, circuit breaker
    retry count, and agent roles spawned. Writes report.toml to phase directory.

    Args:
        phase: Phase ID.
    """
    try:
        dom_root = find_dominion_root()
    except ValueError:
        return {"error": ".dominion/ directory not found."}

    phase_dir = dom_root / "phases" / phase
    if not phase_dir.exists():
        return {"error": f"Phase {phase} not found."}

    # Task and wave metrics
    tasks_path = phase_dir / "plan" / "output" / "tasks.toml"
    tasks_data = read_toml_optional(tasks_path)
    task_list: list[dict] = []
    if tasks_data:
        for role_data in tasks_data.get("findings", {}).values():
            if isinstance(role_data, dict):
                for t in role_data.get("tasks", []):
                    task_list.append(t)

    waves = {t.get("wave", 1) for t in task_list}
    agent_roles = [t.get("agent_role", "developer") for t in task_list]

    # Task completion status
    task_statuses = scan_task_statuses(dom_root, phase)
    completed_tasks = sum(1 for s in task_statuses.values() if s == "complete")
    failed_tasks = sum(1 for s in task_statuses.values() if s not in ("complete", "pending"))

    # Review findings
    verdict_path = phase_dir / "review" / "output" / "verdict.toml"
    verdict_data = read_toml_optional(verdict_path)
    findings_by_severity: dict[str, int] = {}
    if verdict_data:
        for role_data in verdict_data.get("findings", {}).values():
            if isinstance(role_data, dict):
                for item in role_data.get("items", []):
                    sev = item.get("severity", "unknown")
                    findings_by_severity[sev] = findings_by_severity.get(sev, 0) + 1

    # Circuit breaker state
    cb = get_circuit_breaker(dom_root)

    # Phase intent
    pos = get_position(dom_root)
    state = read_toml_optional(dom_root / "state.toml") or {}
    phase_entries = state.get("phases", [])
    intent = ""
    for p in phase_entries:
        if p.get("id") == phase:
            intent = p.get("intent", "")
            break

    report = {
        "phase": phase,
        "intent": intent,
        "complexity": pos.get("complexity_level", "moderate"),
        "tasks_total": len(task_list) or len(task_statuses),
        "tasks_completed": completed_tasks,
        "tasks_failed": failed_tasks,
        "waves": len(waves) if waves else 0,
        "agent_roles": list(set(agent_roles)),
        "findings_by_severity": findings_by_severity,
        "retry_count": cb.get("retry_count", 0),
    }

    # Write report.toml
    from ..core.config import write_toml
    report_path = phase_dir / "report.toml"
    write_toml(report_path, {"report": report})

    return report


@mcp.tool()
async def save_decision_tool(
    phase: str, title: str, decision: str, rationale: str, tags: str | None = None
) -> dict:
    """Persist architectural decision to state.toml + decisions.md.

    Args:
        phase: Phase ID where decision was made.
        title: Short identifier (e.g., "auth-approach").
        decision: What was decided.
        rationale: Why.
        tags: Comma-separated domain tags (e.g., "security,architecture").
    """
    if not all([phase, title, decision, rationale]):
        return {"error": "All fields required: phase, title, decision, rationale."}

    try:
        dom_root = find_dominion_root()
    except ValueError:
        return {"error": ".dominion/ directory not found."}

    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    entry = await _save_decision(dom_root, phase, title, decision, rationale, tag_list)
    return {"id": entry["id"], "title": title, "phase": phase}
