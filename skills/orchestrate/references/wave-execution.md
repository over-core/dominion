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
- Write pre-spawn checkpoint to `.dominion/execution.toml` per [completion-signals.md](../../../templates/references/completion-signals.md) §1
- Run `dominion-cli wave create {wave number}` to initialize wave tracking in progress.toml

### 2. Spawn Agents
- For each task, spawn the assigned agent via Agent tool with `isolation: "worktree"` and `run_in_background: true`:
  ```
  Agent(
    isolation: "worktree",
    run_in_background: true,
    prompt: "<full content of .claude/agents/{role}.md>\n\n<task details>",
    description: "execute task {task-id} — {role}"
  )
  ```
- The SDK creates isolated worktrees in `.claude/worktrees/` (SDK-managed, already gitignored)
- Include in each agent's prompt:
  "On completion, write completion marker: `.dominion/signals/complete-{task-id}.toml`
   with task_id, completed_at, exit_status, commit_hash.
   Write this BEFORE writing SUMMARY.md."
- Provide each agent with: task details, file ownership, criteria, upstream handoffs, signal protocol, behavioral instructions from `.claude/agents/{role}.md`
- All agents spawn concurrently in one message (parallel Agent tool calls)

### 2a. Fallback Protocol
If an agent spawn fails (permission denied, timeout, or error):
- Increment failure counter
- If failures >= 2: SWITCH to serial mode
  - Log: "Parallel execution unavailable. Switching to serial."
  - Execute remaining tasks directly in main context, one at a time
  - Read the assigned agent's `.claude/agents/{role}.md` and follow the methodology inline
- If context consumed > 50% on failures: HALT
  - Run: `dominion-cli state checkpoint`
  - Report to user: "Context budget exhausted by agent failures."

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
- For each completed task, merge the branch returned by the Agent tool:
  ```bash
  git merge --no-ff {branch-name} -m "merge: task {task-id} — {title}"
  ```
- On merge conflict: **HALT**, present to user, do NOT auto-resolve
- Record merge commit hashes in progress.toml

### 6. Cleanup
- SDK auto-cleans worktrees that made no changes
- After successful merge: `git worktree remove {worktree-path}` and `git branch -d {branch-name}`
- Worktree path and branch name are returned by the Agent tool on completion
- Run `dominion-cli wave merge` to update progress.toml wave status

### 7. Post-Wave Checklist (MANDATORY — run before starting next wave)

1. For each completed task in the wave:
   - Run: `dominion-cli state update --task {id} --status complete`
   - Verify: `.dominion/phases/{N}/summaries/task-{id}.md` exists
2. Update progress.toml: `dominion-cli progress update --wave {wave number}`
3. Git commit summaries: `git add .dominion/phases/{N}/summaries/ && git commit -m "docs: wave {wave number} task summaries"`
4. Run: `dominion-cli state checkpoint`
5. Context check: if session feels sluggish or compaction has occurred, STOP and run `dominion-cli state checkpoint` before continuing

Do NOT skip this checklist. Stale progress.toml and uncommitted summaries cause cascading failures in downstream steps (test, review, improve).

## Failure Handling

If a task fails or is blocked:
1. Mark task as "failed" or "blocked" in progress.toml
2. Identify downstream dependent tasks — mark as "blocked"
3. Present to user with options:
   - **Retry**: re-create worktree, re-spawn agent
   - **Skip**: mark as skipped, attempt to unblock dependents
   - **Abort**: stop execution, preserve all state for resume
