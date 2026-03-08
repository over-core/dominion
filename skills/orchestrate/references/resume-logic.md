# Resume Logic

Determine the next action from state.toml.

## State Reading

Read these fields from `.dominion/state.toml`:
- `position.phase` — current phase number
- `position.step` — current step in pipeline
- `position.status` — ready | active | blocked | complete
- `position.wave` — current wave (execute step only)
- `position.current_task` — task being executed (execute step only)
- `[lock]` — session lock info
- `[blocker]` — active blocker info

## Decision Matrix

### No phase started (phase = 0, step = "idle")
- Read `.dominion/roadmap.toml`
- Find the next pending phase (lowest number not marked complete)
- If found: "Starting Phase {N}: {title}. Beginning with discuss."
- If none: "All roadmap phases complete. Add new phases or start a new milestone."

### Step complete (status = "complete")
- Advance to the next step in the pipeline:
  - idle → discuss
  - discuss → explore
  - explore → plan
  - plan → execute
  - execute → test
  - test → review
  - review → phase complete (reset to idle, increment phase tracking)
- Display: "Step '{current}' complete. Next: '{next}'."

### Step active (status = "active")
- The step was interrupted mid-execution
- For execute step: check wave progress in progress.toml, resume from current wave
- For other steps: re-run the step (they are idempotent or will detect existing artifacts)
- Display: "Resuming '{step}' from where it left off."

### Blocked (status = "blocked")
- Read `[blocker]` for details
- Present to user:
  ```
  Blocked: {reason}
  Task: {task} | Level: {level}

  Options:
    1. Resolve — provide resolution, clear blocker
    2. Skip — mark task as skipped, continue
    3. Replan — go back to plan step
  ```
- Wait for user choice before proceeding

### Lock conflict
- If lock exists and is not expired:
  ```
  Pipeline locked by session {session_id} since {locked_at}.
  Options:
    1. Use /dominion:quick for lightweight tasks
    2. Force-unlock (if session is stale)
  ```
- If lock is expired (older than expires_after_hours): auto-clear and proceed
