# Wave Execution

Orchestrator-level wave management during the execute step.

## Pre-Execution

1. Read `.dominion/phases/{N}/plan.toml` — get task list and wave structure
2. Read or create `.dominion/phases/{N}/progress.toml` from [progress.toml](../../../templates/schemas/progress.toml)
3. Determine starting wave:
   - If progress.toml is new: start at wave 1
   - If resuming: find first wave with status != "complete"

## Per-Wave Protocol

For each wave:

### 1. Setup
- Run `dominion-cli state update --wave {wave number} --status active`
- Create worktrees for each task in the wave:
  ```bash
  git worktree add .worktrees/dominion-{task-id} -b dominion/{task-id}
  ```
- Write pre-spawn checkpoint to `.dominion/execution.toml` per [completion-signals.md](../../../templates/references/completion-signals.md) §1
- Run `dominion-cli wave create {wave number}` to initialize wave tracking in progress.toml

### 2. Spawn Agents
- For each task, spawn Developer agent via Agent tool with `run_in_background: true`
- Include in each agent's prompt:
  "On completion, write completion marker: `.dominion/signals/complete-{task-id}.toml`
   with task_id, completed_at, exit_status, commit_hash.
   Write this BEFORE writing SUMMARY.md."
- Provide each agent with: task details, file ownership, criteria, upstream handoffs, signal protocol
- All agents spawn concurrently in one message (parallel Agent tool calls)

### 3. Monitor
- Agents run as background subprocesses — notifications arrive when each completes
- As each notification arrives: read completion marker, update execution.toml
- React to signals per the signal protocol (task/wave/phase blockers)
- On context compaction: follow recovery protocol ([completion-signals.md](../../../templates/references/completion-signals.md) §4)
  - Read execution.toml for spawned agent list
  - Check completion markers on disk
  - Poll every 30 seconds for remaining agents (they're still running)
  - Timeout after 15 minutes of no new completions → mark stale, prompt user

### 4. Verify
- For each task: check completion marker exists (`.dominion/signals/complete-{task-id}.toml` with exit_status = "success")
- Check SUMMARY.md exists for each task: `.dominion/phases/{N}/summaries/task-{id}.md`
- Run verify_command for each task (if specified)
- If completion marker missing but SUMMARY.md exists: warn but proceed
- If both missing: task did not complete, handle as failure

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
- Run `dominion-cli wave merge` to update progress.toml wave status

## Failure Handling

If a task fails or is blocked:
1. Mark task as "failed" or "blocked" in progress.toml
2. Identify downstream dependent tasks — mark as "blocked"
3. Present to user with options:
   - **Retry**: re-create worktree, re-spawn agent
   - **Skip**: mark as skipped, attempt to unblock dependents
   - **Abort**: stop execution, preserve all state for resume
