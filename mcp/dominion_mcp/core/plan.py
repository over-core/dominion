"""Plan management — task lookup, wave computation, and validation."""

from __future__ import annotations

import re
from pathlib import Path

from .config import current_phase, phase_path, read_toml, write_toml


# ---------------------------------------------------------------------------
# Plan and task access
# ---------------------------------------------------------------------------


def get_plan(dom_root: Path, phase: int | None = None) -> dict:
    """Read plan.toml for the given phase (or current phase if None).

    Returns the full plan dict.
    Raises ValueError if plan.toml is missing or malformed.
    """
    p = phase if phase is not None else current_phase(dom_root)
    return read_toml(phase_path(dom_root, p) / "plan.toml")


def get_task(dom_root: Path, task_id: str, phase: int | None = None) -> dict | None:
    """Find a specific task by ID in the plan.

    Returns the task dict or None if not found.
    """
    plan = get_plan(dom_root, phase)
    return _find_task(plan, task_id)


def get_wave_tasks(dom_root: Path, wave: int, phase: int | None = None) -> list[dict]:
    """Get all tasks assigned to a specific wave number."""
    plan = get_plan(dom_root, phase)
    return [t for t in plan.get("tasks", []) if t.get("wave") == wave]


# ---------------------------------------------------------------------------
# Wave computation (topological sort)
# ---------------------------------------------------------------------------


def compute_waves(tasks: list[dict]) -> dict[str, int]:
    """Compute wave assignments using topological sort on dependency graph.

    Returns a mapping of {task_id: wave_number} where wave 1 contains tasks
    with no dependencies, wave 2 contains tasks whose dependencies are all
    in wave 1, and so on.

    Raises ValueError on circular dependencies.
    """
    tasks_by_id: dict[str, dict] = {
        t["id"]: t for t in tasks if "id" in t
    }
    waves: dict[str, int] = {}
    in_stack: set[str] = set()

    def _assign(task_id: str) -> int:
        if task_id in waves:
            return waves[task_id]
        if task_id in in_stack:
            raise ValueError(f"Circular dependency detected involving {task_id}")
        if task_id not in tasks_by_id:
            # External dependency not in this plan — treat as resolved (wave 0).
            return 0

        in_stack.add(task_id)
        deps = tasks_by_id[task_id].get("depends_on", [])
        max_dep_wave = 0
        for dep in deps:
            dep_wave = _assign(dep)
            max_dep_wave = max(max_dep_wave, dep_wave)

        in_stack.discard(task_id)
        waves[task_id] = max_dep_wave + 1
        return waves[task_id]

    for tid in tasks_by_id:
        _assign(tid)

    return waves


# ---------------------------------------------------------------------------
# Plan validation
# ---------------------------------------------------------------------------

_ID_PATTERN = re.compile(r"^\d{2}-\d{2}$")


def validate_plan(plan: dict, max_tokens: int | None = None) -> list[dict]:
    """Run validation checks on plan data.

    Returns a list of check result dicts:
        [{"check": "name", "status": "pass"|"warn"|"fail", "message": "..."}]

    Checks performed:
        1. Task ID format (XX-YY pattern)
        2. No circular dependencies in dependency graph
        3. No file ownership conflicts within same wave
        4. Token budget check (if max_tokens provided)
        5. All dependency references exist
        6. Every task has title and assigned_to
        7. Wave assignments are consistent with dependencies
    """
    tasks = plan.get("tasks", [])
    checks: list[dict] = []

    ids = [t.get("id", "") for t in tasks]
    id_set = set(ids)

    # 1. Task ID format
    bad_ids = [i for i in ids if not _ID_PATTERN.match(i)]
    dup_ids = sorted({i for i in ids if ids.count(i) > 1})
    if bad_ids or dup_ids:
        parts: list[str] = []
        if bad_ids:
            parts.append(f"bad format: {', '.join(bad_ids)}")
        if dup_ids:
            parts.append(f"duplicates: {', '.join(dup_ids)}")
        checks.append({"check": "task_id_format", "status": "fail", "message": "; ".join(parts)})
    else:
        checks.append({"check": "task_id_format", "status": "pass", "message": f"{len(ids)} valid"})

    # 2. No circular dependencies
    try:
        waves = compute_waves(tasks)
        checks.append({"check": "no_circular_deps", "status": "pass", "message": ""})
    except ValueError as exc:
        waves = {}
        checks.append({"check": "no_circular_deps", "status": "fail", "message": str(exc)})

    # 3. No file ownership conflicts within same wave
    wave_files: dict[int, dict[str, list[str]]] = {}
    for t in tasks:
        w = t.get("wave", 0)
        if w not in wave_files:
            wave_files[w] = {}
        for f in t.get("file_ownership", []):
            wave_files[w].setdefault(f, []).append(t.get("id", "?"))
    conflicts = []
    for w in sorted(wave_files):
        for f, owners in wave_files[w].items():
            if len(owners) > 1:
                conflicts.append(f"wave {w}: {f} ({', '.join(owners)})")
    if conflicts:
        checks.append({"check": "file_ownership", "status": "fail", "message": "; ".join(conflicts)})
    else:
        checks.append({"check": "file_ownership", "status": "pass", "message": "no conflicts"})

    # 4. Token budget check
    if max_tokens is not None and max_tokens > 0:
        over_budget = []
        warn_budget = []
        for t in tasks:
            est = t.get("token_estimate", 0)
            if est > max_tokens:
                over_budget.append(f"{t.get('id', '?')} ({est})")
            elif est > max_tokens * 0.8:
                warn_budget.append(f"{t.get('id', '?')} ({est})")
        if over_budget:
            checks.append({
                "check": "token_budget",
                "status": "fail",
                "message": f"exceeds limit: {', '.join(over_budget)}",
            })
        elif warn_budget:
            checks.append({
                "check": "token_budget",
                "status": "warn",
                "message": f">80% of limit: {', '.join(warn_budget)}",
            })
        else:
            checks.append({
                "check": "token_budget",
                "status": "pass",
                "message": f"all within {max_tokens}",
            })

    # 5. All dependency references exist
    bad_deps = []
    for t in tasks:
        for dep in t.get("depends_on", []):
            if dep not in id_set:
                bad_deps.append(f"{t.get('id', '?')} -> {dep}")
    if bad_deps:
        checks.append({"check": "dependency_refs", "status": "fail", "message": ", ".join(bad_deps)})
    else:
        checks.append({"check": "dependency_refs", "status": "pass", "message": "all valid"})

    # 6. Every task has title and assigned_to
    missing = []
    for t in tasks:
        tid = t.get("id", "?")
        lacks = []
        if not t.get("title"):
            lacks.append("title")
        if not t.get("assigned_to"):
            lacks.append("assigned_to")
        if lacks:
            missing.append(f"{tid} missing {', '.join(lacks)}")
    if missing:
        checks.append({"check": "required_fields", "status": "fail", "message": "; ".join(missing)})
    else:
        checks.append({"check": "required_fields", "status": "pass", "message": "all tasks have title and assigned_to"})

    # 7. Wave assignments consistent with dependencies
    if waves:
        inconsistent = []
        for t in tasks:
            tid = t.get("id", "")
            assigned_wave = t.get("wave")
            if assigned_wave is None or tid not in waves:
                continue
            for dep in t.get("depends_on", []):
                dep_wave = waves.get(dep)
                if dep_wave is not None and assigned_wave <= dep_wave:
                    inconsistent.append(
                        f"{tid} (wave {assigned_wave}) depends on {dep} (wave {dep_wave})"
                    )
        if inconsistent:
            checks.append({
                "check": "wave_consistency",
                "status": "fail",
                "message": "; ".join(inconsistent),
            })
        else:
            checks.append({"check": "wave_consistency", "status": "pass", "message": ""})

    return checks


# ---------------------------------------------------------------------------
# Handoff management
# ---------------------------------------------------------------------------


async def write_handoff(
    dom_root: Path, from_task: str, to_task: str, message: str
) -> None:
    """Write a handoff note between tasks.

    Creates a markdown file at
    .dominion/phases/{phase}/handoffs/{from_task}_to_{to_task}.md
    with the handoff message. Overwrites any existing handoff for the same
    task pair.
    """
    p = current_phase(dom_root)
    handoff_dir = phase_path(dom_root, p) / "handoffs"
    handoff_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{from_task}_to_{to_task}.md"
    path = handoff_dir / filename

    content = (
        f"# Handoff: {from_task} -> {to_task}\n"
        f"\n"
        f"{message}\n"
    )
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _find_task(plan: dict, task_id: str) -> dict | None:
    """Find a task by ID in plan data."""
    for t in plan.get("tasks", []):
        if t.get("id") == task_id:
            return t
    return None
