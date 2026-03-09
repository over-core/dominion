# Wave Execution

Orchestrator-level wave management during the execute step.

## Pre-Execution

1. Read `.dominion/phases/{N}/plan.toml` — get task list and wave structure
2. Read or create `.dominion/phases/{N}/progress.toml` from `@templates/schemas/progress.toml`
3. Determine starting wave:
   - If progress.toml is new: start at wave 1
   - If resuming: find first wave with status != "complete"

## Per-Wave Protocol

For each wave:

### 1. Setup
- Run `dominion-tools state update --wave {wave number} --status active`
- Create worktrees for each task in the wave:
  ```bash
  git worktree add .worktrees/dominion-{task-id} -b dominion/{task-id}
  ```
- Run `dominion-tools wave create {wave number}` to initialize wave tracking in progress.toml

### 2. Spawn Agents
- For each task in the wave, spawn a Developer agent:
  ```bash
  claude --agent developer --working-directory .worktrees/dominion-{task-id}
  ```
- Provide each agent with: task details, file ownership, criteria, upstream handoffs, signal protocol
- All agents spawn concurrently

### 3. Monitor
- Poll `.dominion/signals/` for new signal files
- React to signals per the signal protocol (task/wave/phase blockers)
- Wait for all agents to complete or signal

### 4. Verify
- Check SUMMARY.md exists for each task: `.dominion/phases/{N}/summaries/task-{id}.md`
- Run verify_command for each task (if specified)

### 5. Merge
- For each completed task:
  ```bash
  git merge --no-ff dominion/{task-id} -m "merge: task {task-id} — {title}"
  ```
- On merge conflict: **HALT**, present to user, do NOT auto-resolve
- Record merge commit hashes in progress.toml

### 6. Cleanup
- Remove worktrees: `git worktree remove .worktrees/dominion-{task-id}`
- Delete branches: `git branch -d dominion/{task-id}`
- Run `dominion-tools wave merge` to update progress.toml wave status

## Failure Handling

If a task fails or is blocked:
1. Mark task as "failed" or "blocked" in progress.toml
2. Identify downstream dependent tasks — mark as "blocked"
3. Present to user with options:
   - **Retry**: re-create worktree, re-spawn agent
   - **Skip**: mark as skipped, attempt to unblock dependents
   - **Abort**: stop execution, preserve all state for resume
