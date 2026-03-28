"""Submit tools — submit_work, signal_blocker.

Called by spawned agents to deliver results and signal blockers.
"""

from __future__ import annotations

import json
from pathlib import Path

import tomli_w

from ..server import mcp
from ..core.config import find_dominion_root, read_toml_optional, write_toml
from ..core.filesystem import (
    append_summary,
    append_task_summary,
    count_summary_roles,
    read_status,
    write_output_toml,
    write_task_output_toml,
    write_status,
    write_output,
    write_task_output,
)
from ..core.events import emit_event
from ..core.state import mark_task_complete, remove_active_agent, update_position

# Step → output filename mapping
_OUTPUT_FILES: dict[str, str] = {
    "research": "findings.toml",
    "plan": "tasks.toml",
    "review": "verdict.toml",
    "execute": "result.toml",
    "discuss": "findings.toml",
}


def _validate_research(content: dict) -> str | None:
    items = content.get("items")
    if not isinstance(items, list):
        return "Missing 'items' array in research content."
    for item in items:
        if not item.get("severity"):
            return "Each research item must have a 'severity' field."
    return None


def _validate_plan(content: dict) -> str | None:
    tasks = content.get("tasks")
    if not isinstance(tasks, list):
        return "Missing 'tasks' array in plan content."
    for task in tasks:
        for field in ("task_id", "wave", "dependencies"):
            if field not in task:
                return f"Plan task missing required field '{field}'."
    # Wave dependency validation
    wave_map = {t["task_id"]: t["wave"] for t in tasks}
    for task in tasks:
        for dep in task.get("dependencies", []):
            dep_wave = wave_map.get(dep)
            if dep_wave is not None and dep_wave >= task["wave"]:
                return (
                    f"Task '{task['task_id']}' in wave {task['wave']} depends on "
                    f"task '{dep}' in wave {dep_wave} (same or later wave)."
                )
    return None


def _validate_execute(content: dict) -> str | None:
    if "commit" not in content:
        return "Missing 'commit' field in execute content."
    if "tests_run" not in content:
        return "Missing 'tests_run' field in execute content."
    if "tests_passed" not in content:
        return "Missing 'tests_passed' field in execute content."
    return None


def _validate_review(content: dict) -> str | None:
    verdict = content.get("verdict")
    if verdict not in ("go", "go-with-warnings", "no-go"):
        return f"Missing or invalid 'verdict' field. Required: go | go-with-warnings | no-go. Got: {verdict}"
    items = content.get("items")
    if not isinstance(items, list):
        return "Missing 'items' array in review content."
    for item in items:
        if not item.get("severity"):
            return "Each review item must have a 'severity' field."
    return None


_VALIDATORS: dict[str, callable] = {
    "research": _validate_research,
    "plan": _validate_plan,
    "execute": _validate_execute,
    "review": _validate_review,
}


@mcp.tool()
async def submit_work(
    phase: str,
    step: str,
    role: str,
    content: str,
    summary: str,
    task_id: str | None = None,
) -> dict:
    """Validate, write output, update status.

    Args:
        phase: Phase ID.
        step: Step name (research | plan | execute | review | discuss).
        role: Agent role submitting. NOT validated against roster (pseudo-roles valid).
        content: JSON string of structured findings/results.
        summary: Condensed summary (REQUIRED, rejects if empty).
        task_id: Task ID for execute step.
    """
    if not summary or not summary.strip():
        return {"error": "Summary is required. Provide condensed summary."}

    try:
        dom_root = find_dominion_root()
    except ValueError:
        return {"error": ".dominion/ directory not found."}

    # Parse content
    try:
        content_data = json.loads(content) if isinstance(content, str) else content
    except json.JSONDecodeError:
        return {"error": "Content must be valid JSON."}

    phase_dir = dom_root / "phases" / phase
    if not phase_dir.exists():
        return {"error": f"Phase {phase} not found."}

    # Schema validation per step
    validator = _VALIDATORS.get(step)
    if validator:
        error = validator(content_data)
        if error:
            return {"error": error}

    # Effort level warnings (v0.5.0 — non-blocking, agent can self-correct)
    effort_warnings: list[str] = []
    if step in ("research", "review", "discuss"):
        from ..core.metrics import validate_effort_level

        for item in content_data.get("items", []):
            warning = validate_effort_level(item.get("effort"))
            if warning:
                effort_warnings.append(warning)

    # Namespace content under [findings.{role}]
    if task_id:
        namespace = f"{role}-{task_id}"
    else:
        namespace = role
    namespaced = {"findings": {namespace: content_data}}

    # Determine output directory and write
    filename = _OUTPUT_FILES.get(step, "output.toml")

    if task_id:
        # Task output
        output_path = write_task_output_toml(dom_root, phase, task_id, filename, namespaced)
        summary_path = await append_task_summary(dom_root, phase, task_id, namespace, summary)
        status_path = dom_root / "phases" / phase / "tasks" / task_id / "status"
        write_status(status_path, "complete")
        await mark_task_complete(dom_root, task_id, phase, step)
    else:
        # Step output — merge into existing TOML (parallel agent concurrent writes)
        output_file = dom_root / "phases" / phase / step / "output" / filename
        if output_file.exists():
            existing = read_toml_optional(output_file) or {}
            existing.setdefault("findings", {}).update(namespaced["findings"])
            write_toml(output_file, existing)
            output_path = output_file
        else:
            output_path = write_output_toml(dom_root, phase, step, filename, namespaced)

        summary_path = await append_summary(dom_root, phase, step, role, summary)
        # Step status → complete only after all agents submit
        # Does NOT advance step (C1) — orchestrator calls advance_step

    result: dict = {
        "status": "accepted",
        "output_path": str(output_path.relative_to(dom_root.parent)),
        "summary_path": str(summary_path.relative_to(dom_root.parent)),
    }
    if effort_warnings:
        result["effort_warnings"] = effort_warnings

    # Clear agent from stall detection tracking
    agent_key = f"{role}-{task_id}" if task_id else f"{role}-{step}"
    await remove_active_agent(dom_root, agent_key)

    await emit_event(dom_root, phase=phase, event="work_submitted",
                     step=step, role=role, task_id=task_id,
                     data={"output_path": str(output_path.relative_to(dom_root.parent))})

    return result


@mcp.tool()
async def signal_blocker(phase: str, task_id: str, reason: str) -> dict:
    """Mark a task as blocked, update state.

    Args:
        phase: Phase ID.
        task_id: Task ID that's blocked.
        reason: Description of what's blocking progress.
    """
    if not reason or not reason.strip():
        return {"error": "Reason required when signaling blocker."}

    try:
        dom_root = find_dominion_root()
    except ValueError:
        return {"error": ".dominion/ directory not found."}

    task_dir = dom_root / "phases" / phase / "tasks" / task_id
    if not task_dir.exists():
        return {"error": f"Task directory not found: phases/{phase}/tasks/{task_id}"}

    write_status(task_dir / "status", "blocked")
    blocker_path = task_dir / "output" / "blocker.md"
    blocker_path.parent.mkdir(parents=True, exist_ok=True)
    blocker_path.write_text(f"# Blocker: Task {task_id}\n\n{reason}\n")

    await update_position(dom_root, status="blocked")

    await emit_event(dom_root, phase=phase, event="blocker_signaled",
                     task_id=task_id, data={"reason": reason})

    return {
        "status": "blocked",
        "task_id": task_id,
        "reason": reason,
    }
