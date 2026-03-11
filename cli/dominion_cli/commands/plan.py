"""Plan management commands."""

from __future__ import annotations

import re
from typing import Annotated, Optional

import typer

from ..core.config import current_phase, dominion_path, phase_path
from ..core.formatters import error, info, output, status_line, table
from ..core.readers import read_toml, read_toml_optional, write_toml

app = typer.Typer(help="Plan task and wave management")


def _plan_toml(phase: int | None = None) -> dict:
    """Read plan.toml for the current or specified phase."""
    p = phase if phase is not None else current_phase()
    return read_toml(phase_path(p) / "plan.toml")


def _find_task(plan: dict, task_id: str) -> dict | None:
    """Find a task by ID in plan.toml."""
    for t in plan.get("tasks", []):
        if t.get("id") == task_id:
            return t
    return None


@app.command()
def task(
    id: Annotated[str, typer.Argument(help="Task id (e.g., 02-01)")],
    files: Annotated[bool, typer.Option("--files", help="Show file ownership only")] = False,
    criteria: Annotated[bool, typer.Option("--criteria", help="Show acceptance criteria only")] = False,
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show task details and handoffs."""
    plan = _plan_toml()
    t = _find_task(plan, id)
    if t is None:
        error(f"Task {id} not found in plan.toml.")
        raise SystemExit(1)

    if files:
        data = {"id": id, "file_ownership": t.get("file_ownership", [])}
        output(data, json)
        return

    if criteria:
        data = {"id": id, "acceptance_criteria": t.get("acceptance_criteria", [])}
        output(data, json)
        return

    data = {
        "id": t.get("id"),
        "title": t.get("title", ""),
        "wave": t.get("wave", 0),
        "agent": t.get("agent", ""),
        "depends_on": t.get("depends_on", []),
        "file_ownership": t.get("file_ownership", []),
        "token_estimate": t.get("token_estimate", 0),
        "acceptance_criteria": t.get("acceptance_criteria", []),
        "verify_command": t.get("verify_command", ""),
        "handoffs": t.get("handoffs", []),
    }
    if json:
        output(data, json)
        return

    info(f"Task {data['id']}: {data['title']}")
    info(f"  Wave: {data['wave']} | Agent: {data['agent']}")
    info(f"  Depends on: {', '.join(data['depends_on']) if data['depends_on'] else 'none'}")
    info(f"  Files: {', '.join(data['file_ownership']) if data['file_ownership'] else 'none'}")
    if data["acceptance_criteria"]:
        info("  Criteria:")
        for c in data["acceptance_criteria"]:
            info(f"    - {c}")
    if data["verify_command"]:
        info(f"  Verify: {data['verify_command']}")
    if data["handoffs"]:
        info("  Handoffs:")
        for h in data["handoffs"]:
            info(f"    {h.get('from', '?')} -> {h.get('note', '')}")


@app.command()
def wave(
    number: Annotated[int, typer.Argument(help="Wave number")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show all tasks in a wave."""
    plan = _plan_toml()
    tasks = [t for t in plan.get("tasks", []) if t.get("wave") == number]

    if not tasks:
        info(f"No tasks in wave {number}.")
        return

    columns = ["ID", "Title", "Agent", "Deps"]
    rows = []
    for t in tasks:
        deps = ", ".join(t.get("depends_on", [])) or "—"
        rows.append([t.get("id", ""), t.get("title", ""), t.get("agent", ""), deps])

    table(f"Wave {number} Tasks", columns, rows, json)


@app.command()
def deps(
    id: Annotated[str, typer.Argument(help="Task id")],
) -> None:
    """Show dependency chain for a task."""
    plan = _plan_toml()
    task_map = {t["id"]: t for t in plan.get("tasks", []) if "id" in t}

    if id not in task_map:
        error(f"Task {id} not found.")
        raise SystemExit(1)

    def _print_tree(task_id: str, prefix: str = "", is_last: bool = True) -> None:
        connector = "└── " if is_last else "├── "
        info(f"{prefix}{connector}{task_id}" if prefix else task_id)
        new_prefix = prefix + ("    " if is_last else "│   ")
        dep_ids = task_map.get(task_id, {}).get("depends_on", [])
        for i, dep in enumerate(dep_ids):
            _print_tree(dep, new_prefix, i == len(dep_ids) - 1)

    _print_tree(id)


@app.command()
def handoff(
    from_task: Annotated[str, typer.Argument(metavar="FROM", help="Source task id")],
    to: Annotated[str, typer.Option("--to", help="Target task id")],
    message: Annotated[str, typer.Argument(help="Handoff note content")],
) -> None:
    """Write a targeted handoff note between tasks."""
    p = current_phase()
    path = phase_path(p) / "plan.toml"
    plan = read_toml(path)

    from_t = _find_task(plan, from_task)
    to_t = _find_task(plan, to)

    if from_t is None:
        error(f"Source task {from_task} not found.")
        raise SystemExit(1)
    if to_t is None:
        error(f"Target task {to} not found.")
        raise SystemExit(1)

    if "handoffs" not in to_t:
        to_t["handoffs"] = []
    to_t["handoffs"].append({"from": from_task, "note": message})

    write_toml(path, plan)
    info(f"Handoff from {from_task} to {to} recorded.")


@app.command()
def index() -> None:
    """Group tasks into waves by dependency analysis."""
    p = current_phase()
    path = phase_path(p) / "plan.toml"
    plan = read_toml(path)
    tasks = plan.get("tasks", [])
    task_map = {t["id"]: t for t in tasks if "id" in t}

    # Topological sort for wave assignment
    waves: dict[str, int] = {}

    def _assign_wave(task_id: str, visited: set[str]) -> int:
        if task_id in waves:
            return waves[task_id]
        if task_id in visited:
            error(f"Circular dependency detected involving {task_id}.")
            raise SystemExit(1)
        visited.add(task_id)
        dep_ids = task_map.get(task_id, {}).get("depends_on", [])
        if not dep_ids:
            waves[task_id] = 1
            return 1
        max_dep_wave = max(_assign_wave(d, visited) for d in dep_ids)
        waves[task_id] = max_dep_wave + 1
        return waves[task_id]

    for tid in task_map:
        _assign_wave(tid, set())

    # Update tasks with computed waves
    for t in tasks:
        tid = t.get("id")
        if tid and tid in waves:
            t["wave"] = waves[tid]

    write_toml(path, plan)

    # Report
    max_wave = max(waves.values()) if waves else 0
    for w in range(1, max_wave + 1):
        wave_tasks = [tid for tid, wn in waves.items() if wn == w]
        info(f"  Wave {w}: {', '.join(wave_tasks)}")

    info(f"Indexed {len(waves)} tasks into {max_wave} waves.")


@app.command(name="validate")
def validate_plan(
    file: Annotated[str, typer.Argument(help="Path to plan.toml")],
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Validate plan structure."""
    from pathlib import Path

    plan = read_toml(Path(file))
    tasks = plan.get("tasks", [])
    checks: list[dict] = []

    # 1. Unique IDs in {phase}-{seq} format
    ids = [t.get("id", "") for t in tasks]
    id_pattern = re.compile(r"^\d+-\d+$")
    bad_ids = [i for i in ids if not id_pattern.match(i)]
    dup_ids = [i for i in ids if ids.count(i) > 1]
    if bad_ids or dup_ids:
        detail = ""
        if bad_ids:
            detail += f"bad format: {', '.join(bad_ids)} "
        if dup_ids:
            detail += f"duplicates: {', '.join(set(dup_ids))}"
        checks.append({"name": "Task ID format", "status": "fail", "detail": detail})
    else:
        checks.append({"name": "Task ID format", "status": "pass", "detail": f"{len(ids)} valid"})

    # 2. Dependencies reference existing tasks
    id_set = set(ids)
    bad_deps = []
    for t in tasks:
        for dep in t.get("depends_on", []):
            if dep not in id_set:
                bad_deps.append(f"{t.get('id')} -> {dep}")
    if bad_deps:
        checks.append({"name": "Dependency references", "status": "fail", "detail": ", ".join(bad_deps)})
    else:
        checks.append({"name": "Dependency references", "status": "pass", "detail": "All valid"})

    # 3. No circular dependencies
    def _has_cycle(start: str, visited: set[str], path_set: set[str]) -> bool:
        visited.add(start)
        path_set.add(start)
        task_obj = next((t for t in tasks if t.get("id") == start), None)
        if task_obj:
            for dep in task_obj.get("depends_on", []):
                if dep in path_set:
                    return True
                if dep not in visited and _has_cycle(dep, visited, path_set):
                    return True
        path_set.discard(start)
        return False

    visited: set[str] = set()
    has_cycle = False
    for tid in ids:
        if tid not in visited and _has_cycle(tid, visited, set()):
            has_cycle = True
            break
    if has_cycle:
        checks.append({"name": "No circular deps", "status": "fail", "detail": "Cycle detected"})
    else:
        checks.append({"name": "No circular deps", "status": "pass", "detail": ""})

    # 4. At least 2 acceptance criteria per task
    low_criteria = [t.get("id", "?") for t in tasks if len(t.get("acceptance_criteria", [])) < 2]
    if low_criteria:
        checks.append({"name": "Acceptance criteria", "status": "fail", "detail": f"<2: {', '.join(low_criteria)}"})
    else:
        checks.append({"name": "Acceptance criteria", "status": "pass", "detail": "All >= 2"})

    # 5. No file ownership conflicts within same wave
    wave_files: dict[int, dict[str, list[str]]] = {}
    for t in tasks:
        w = t.get("wave", 0)
        if w not in wave_files:
            wave_files[w] = {}
        for f in t.get("file_ownership", []):
            if f not in wave_files[w]:
                wave_files[w][f] = []
            wave_files[w][f].append(t.get("id", "?"))
    conflicts = []
    for w, files_map in wave_files.items():
        for f, task_ids in files_map.items():
            if len(task_ids) > 1:
                conflicts.append(f"wave {w}: {f} ({', '.join(task_ids)})")
    if conflicts:
        checks.append({"name": "File ownership", "status": "fail", "detail": "; ".join(conflicts)})
    else:
        checks.append({"name": "File ownership", "status": "pass", "detail": "No conflicts"})

    # 6. Sequential wave numbering
    wave_nums = sorted(set(t.get("wave", 0) for t in tasks if t.get("wave")))
    expected = list(range(1, len(wave_nums) + 1))
    if wave_nums != expected and wave_nums:
        checks.append({"name": "Wave numbering", "status": "fail", "detail": f"Got {wave_nums}, expected {expected}"})
    else:
        checks.append({"name": "Wave numbering", "status": "pass", "detail": ""})

    # 7. Token budget check
    dom_path = dominion_path("dominion.toml")
    dom = read_toml_optional(dom_path) if dom_path.exists() else None
    max_tokens = 0
    if dom:
        max_tokens = dom.get("autonomy", {}).get("circuit_breakers", {}).get("max_tokens_per_task", 0)
    if max_tokens > 0:
        over_budget = []
        warn_budget = []
        for t in tasks:
            est = t.get("token_estimate", 0)
            if est > max_tokens:
                over_budget.append(f"{t.get('id')} ({est})")
            elif est > max_tokens * 0.8:
                warn_budget.append(f"{t.get('id')} ({est})")
        if over_budget:
            checks.append({"name": "Token budget", "status": "fail", "detail": f">100%: {', '.join(over_budget)}"})
        elif warn_budget:
            checks.append({"name": "Token budget", "status": "warn", "detail": f">80%: {', '.join(warn_budget)}"})
        else:
            checks.append({"name": "Token budget", "status": "pass", "detail": f"All within {max_tokens}"})

    status_line(checks, json)
