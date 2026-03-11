# Inter-Wave Knowledge Transfer

Lightweight information propagation between waves.

## Timing

Execute after wave merge completes, before the next wave starts. This should take ~30 seconds — it is NOT a review, just information transfer.

## Protocol

### 1. Read Summaries
Read all SUMMARY.md files from the completed wave:
`.dominion/phases/{N}/summaries/task-{id}.md`

### 2. Extract Gotchas
From each summary, extract key information from:
- **Friction Encountered**: unexpected difficulties, workarounds used
- **Decisions Made**: design choices, trade-offs, deviations from plan

Compile into a brief list of gotchas relevant to downstream tasks.

### 3. Update MEMORY.md
Append wave gotchas to the project's MEMORY.md:
```
## Wave {N} Gotchas (Phase {P})
- {gotcha 1}
- {gotcha 2}
```

Keep it concise — one line per gotcha. Remove gotchas from previous waves that are no longer relevant.

### 4. Apply Handoff Notes
For each completed task that has downstream dependents:
- Read the "Handoff Notes" section from the task's SUMMARY.md
- Write the handoff to downstream tasks via:
  ```bash
  dominion-cli plan handoff {from-id} --to {to-id} "{note}"
  ```

### 5. Clean Signals
Remove resolved signal files from `.dominion/signals/`:
- Warnings from completed tasks can be cleaned
- Resolved blockers can be cleaned
- Active blockers for ongoing tasks remain

## What This Is NOT

This is not a review. Do not:
- Evaluate code quality
- Suggest refactoring
- Question design decisions
- Add new findings

Just transfer information so the next wave's agents start informed.
