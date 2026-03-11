# Wave Grouping

Assign tasks to waves for parallel execution.

## Algorithm

1. **Build DAG** from task dependencies (`depends_on` fields)
2. **Detect cycles** — if any circular dependencies exist, report and halt
3. **Topological sort** to assign waves:
   - Wave 1: tasks with no dependencies
   - Wave 2: tasks whose dependencies are all in wave 1
   - Wave 3: tasks whose dependencies are all in waves 1-2
   - Continue until all tasks are assigned

## Coupling-Aware Grouping

Before assigning waves by pure topological sort, consider module coupling:

1. **Read Martin's coupling metrics** from research.toml. Afferent coupling (Ca) = inbound dependencies. Efferent coupling (Ce) = outbound dependencies. Instability = Ce / (Ca + Ce).
2. **Co-locate coupled modules.** Tasks modifying tightly coupled modules (high Ca + Ce between them) should be in the same wave when possible. This reduces cross-wave integration risk — changes to coupled modules in different waves create handoff fragility.
3. **Separate stable from unstable.** High-stability modules (low instability score) are safe to modify early. High-instability modules benefit from later waves where upstream changes have settled.
4. **Coupling overrides balance, not correctness.** Co-locating coupled tasks may create uneven wave sizes. This is acceptable — coupling-aware grouping prevents integration failures that balanced-but-decoupled waves would cause.

## Critical Path Marking

After topological sort, identify the critical path:

1. **Longest dependency chain** through the DAG is the critical path. These tasks determine minimum phase duration.
2. **Mark critical-path tasks** with `critical_path = true` in plan.toml. These tasks cannot slip without delaying the entire phase.
3. **Non-critical tasks have slack.** Tasks not on the critical path can be delayed or reordered within their wave without affecting phase duration.
4. **Prioritize critical-path tasks** within each wave — if resource constraints force sequential execution within a wave, run critical-path tasks first.

## File Ownership Conflict Check

Within each wave, verify no two tasks have overlapping `file_ownership`:
- Exact file matches are conflicts
- Directory overlaps are conflicts (task A owns `src/auth/`, task B owns `src/auth/login.rs`)
- If conflicts exist, move the later task to the next wave

## Wave Balancing

Wave balancing is secondary to correctness:
- Never break a dependency to balance wave sizes
- Never introduce file ownership conflicts for balance
- If a wave has only one task and the task has no conflicts with the next wave, it is fine — do not merge waves

## Knowledge Refs

For each task, check `.dominion/knowledge/index.toml` for entries whose tags or topics relate to the task's file ownership or domain. Populate `knowledge_refs` with relevant file names. This gives Developer agents targeted knowledge without reading the full knowledge base.

## Output

Run `dominion-cli plan index` to assign wave fields. Report the wave structure:
```
Wave 1: {task ids}
Wave 2: {task ids}
...
Total waves: {count}
```

Flag any tasks that ended up in a later wave due to file ownership conflicts (not dependency ordering).
