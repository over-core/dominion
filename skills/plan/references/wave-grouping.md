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

## Output

Run `dominion-tools plan index` to assign wave fields. Report the wave structure:
```
Wave 1: {task ids}
Wave 2: {task ids}
...
Total waves: {count}
```

Flag any tasks that ended up in a later wave due to file ownership conflicts (not dependency ordering).
