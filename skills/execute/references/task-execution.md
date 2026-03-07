# Task Execution

Wave execution protocol for parallel Developer agents.

## Worktree Setup

For each task in the wave:
```bash
git worktree add .worktrees/dominion-{task-id} -b dominion/{task-id}
```

Verify worktree creation succeeded. If it fails (branch already exists), offer to clean up stale worktrees.

## Agent Spawning

For each task, spawn a Developer agent with:
```bash
claude --agent developer --working-directory .worktrees/dominion-{task-id}
```

Provide the agent with a prompt containing:
1. Task details: id, title, description
2. File ownership: which files/directories the task may modify
3. Acceptance criteria: the verifiable done conditions
4. Verify command: the shell command to run for validation
5. Upstream handoff notes: from completed upstream tasks (if any)
6. Signal protocol: how to raise blockers/warnings

**All wave agents are spawned concurrently.** Do not wait for one to finish before starting the next.

## Monitoring

While agents are running:
1. Poll `.dominion/signals/` for new blocker or warning files
2. If a task-level blocker: note it, let other agents continue
3. If a wave-level blocker: halt all agents in the wave, present to user
4. If a phase-level blocker: halt everything, present to user

## Wave Completion

When all agents in the wave have finished:

1. **Verify summaries**: check `.dominion/phases/{N}/summaries/task-{id}.md` exists for each task
2. **Run verify_command**: for each task with a verify_command, run it in the worktree
3. **Update progress.toml**: mark each task as complete, failed, or blocked

## Merge Protocol

For each completed task (in dependency order):
```bash
git merge --no-ff dominion/{task-id} -m "merge: task {task-id} — {title}"
```

- If merge conflict: **HALT**. Present the conflict to the user. Do NOT auto-resolve.
- After successful merge: record merge commit hash in progress.toml

## Worktree Cleanup

After all merges for the wave:
```bash
git worktree remove .worktrees/dominion-{task-id}
git branch -d dominion/{task-id}
```

## Inter-Wave Checkpoint

After wave cleanup, before starting the next wave:
1. Read all SUMMARY.md files from the completed wave
2. Extract gotchas from "Friction Encountered" and "Decisions Made" sections
3. Apply handoff notes to downstream tasks via `dominion-tools plan handoff`
4. Clean resolved signals from `.dominion/signals/`

## Failure Handling

If a task fails:
1. Mark as "failed" in progress.toml
2. Check downstream dependencies — mark dependent tasks as "blocked"
3. Present failure details to user with options:
   - **Retry**: re-spawn the agent for the failed task
   - **Skip**: mark as skipped, unblock dependents if safe
   - **Abort**: stop execution, preserve state for resume
