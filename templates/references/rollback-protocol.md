# Rollback Protocol

How to safely revert work at wave, task, or phase boundaries.

## Wave Rollback

Roll back to the merge commit of a previous wave, discarding all subsequent work.

1. Read progress.toml — find the target wave's `completed_at` commit hash
2. Count commits being discarded: `git rev-list --count {target_hash}..HEAD`
3. Present to user: "Wave {N} completed at {hash}. Discard {count} commits from waves {N+1}+? [Y/n]"
4. If confirmed:
   - `git reset --hard {target_hash}`
   - Run `dominion-tools rollback --to-wave {N}` to update progress.toml and state.toml
5. Print: "Rolled back to wave {N}. Ready to re-execute from wave {N+1}."

## Task Rollback

Revert commits from a single completed or failed task.

1. Read progress.toml — find the task's `commits` array
2. Verify task status is "complete" or "failed" — refuse if "in-progress"
3. Present to user: "Task {id} has {count} commits. Revert? [Y/n]"
4. If confirmed:
   - For each commit in reverse order: `git revert --no-commit {hash}`
   - `git commit -m "revert: rollback task {id}"`
   - Run `dominion-tools rollback --task {id}` to update progress.toml and state.toml
5. Print: "Task {id} reverted. {count} commits reversed in one revert commit."

Note: Task rollback uses `git revert` (creates new commits) rather than `git reset` (rewrites history). This is safer for tasks whose changes may have been built upon.

## Phase Rollback

Nuclear option — discard all work in the current phase.

1. Read progress.toml — find `phase.started_at` commit hash
2. Count total commits: `git rev-list --count {started_at}..HEAD`
3. Double confirmation:
   - "This will discard ALL Phase {N} work ({count} commits). Are you sure? [yes/no]" (require full "yes")
   - "Type the phase number to confirm: " (require exact match)
4. If confirmed:
   - `git reset --hard {started_at}`
   - Delete `.dominion/phases/{N}/` directory
   - Run `dominion-tools rollback --to-phase {N}` to update state.toml and clean up phase artifacts
5. Print: "Phase {N} rolled back. All artifacts removed. Ready to restart."

## Rules

- Rollback never deletes signal files or summaries from `.dominion/signals/` — those are diagnostic history
- Always show the user exactly what will be lost before proceeding
- Phase rollback requires double confirmation
- Task rollback uses revert (safe), wave/phase rollback uses reset (destructive)
- If the rollback target commit is not found, halt and present error — do not guess

## Integration with Orchestrate

When wave-execution.md presents failure options (retry, skip, abort), rollback is a fourth option:
- "Rollback wave {N}?" — triggers wave rollback, then re-execute from that wave
