---
name: execute
description: Run the execute step — parallel worktree implementation with wave grouping
---

# /dominion:execute

Run the execute step standalone. Auto-creates a phase if none is active.

## Steps

1. Call `mcp__dominion__get_progress()`
2. If no active phase: auto-create (assess_complexity + start_phase)
3. Read `plan/output/tasks.toml` → group tasks by wave
4. **Wave 0 (stubs, if present):**
   - Spawn architect agent WITHOUT `isolation='worktree'` (direct commit to branch)
   - After stub task completes, verify stubs committed
5. **Pre-wave cleanup** (before spawning worktree agents for each wave):
   a. Verify current branch: `git branch --show-current` → store as `{current_branch}`
   b. Stash dirty state: `git stash --include-untracked -m "dominion-pre-wave-{N}"` (ignore "nothing to stash")
   c. Remove stale worktrees: `for wt in $(git worktree list --porcelain | grep -oP '(?<=worktree ).+\.claude/worktrees/.+'); do git worktree remove --force "$wt"; done`
   d. Include in each agent's prompt: "Your worktree MUST branch from `{current_branch}` at HEAD.
      Do NOT commit directly to `{current_branch}`. All work must be in your worktree."
6. **Wave 1+ (implementation):**
   a. For each task: call `mcp__dominion__prepare_task(phase, task_id)`
   b. Read each task CLAUDE.md from returned path
   c. Spawn in **batches of 4-5**: `Agent(isolation='worktree', prompt=content, subagent_type=task.agent_role)`
      - IMPORTANT: Use Dominion agents (subagent_type resolves to `.claude/agents/{role}.md`). Do NOT use plugin agents.
   d. **Post-batch verification** (after each batch returns):
      - For each agent: check for worktreePath in output. If missing → log warning
      - For each worktree branch: `git merge-base --is-ancestor {current_branch} {branch}` — if not ancestor → flag wrong base
      - Unsubmitted work: if task status not "complete" but agent returned, commit on behalf and submit with zero test verification
   e. **Worktree Merge Protocol:**
      - Pre-merge: `git status --porcelain` — if dirty, `git stash --include-untracked -m "dominion-pre-merge"`
      - Clean each worktree: `git -C {worktree_path} clean -fd`
      - Pre-merge file check: `git diff --name-only {branch} {current_branch}` — verify changed files subset of assignment
      - Squash-merge: `git merge --squash {branch} && git commit -m "feat({scope}): {task_title}"`
      - On conflict → halt: "Merge conflict. Resolve manually, re-run."
      - On success → `git worktree remove .claude/worktrees/{worktree_name}` THEN `git branch -d {branch}`
      - After all merges → pop stash (`git stash pop`, ignore errors) → next wave from updated HEAD
7. **Post-execute cleanup** (after all waves complete):
   - Remove ALL remaining worktrees: `for wt in $(git worktree list --porcelain | grep -oP '(?<=worktree ).+\.claude/worktrees/.+'); do git worktree remove --force "$wt"; done`
   - Pop any remaining stash: `git stash pop` (ignore errors)
   - **Integration validation**: run full test suite. If tests fail: spawn single developer agent (no worktree) to fix integration issues. Re-run tests — if still failing after 1 attempt, halt.
8. After integration passes:
   - Call `mcp__dominion__submit_work(phase, "execute", "orchestrator", {tasks_completed, waves, files_changed}, summary)`
   - Call `mcp__dominion__advance_step(phase, "execute")`
9. Report: "Execute complete. {N} tasks implemented across {M} waves. Run /dominion:review to continue."
