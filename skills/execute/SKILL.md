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
5. **Before spawning worktree agents:** verify current branch with `git branch --show-current`.
   Include in each agent's prompt: "Your worktree MUST branch from `{current_branch}` at HEAD.
   Verify with `git log --oneline -1` that your branch includes the Wave 0 stubs."
6. **Wave 1+ (implementation):**
   a. For each task: call `mcp__dominion__prepare_task(phase, task_id)`
   b. Read each task CLAUDE.md from returned path
   c. Spawn in **batches of 4-5**: `Agent(isolation='worktree', prompt=content, subagent_type=task.agent_role)`
      - IMPORTANT: Use Dominion agents (subagent_type resolves to `.claude/agents/{role}.md`). Do NOT use plugin agents.
   d. After each batch returns: verify worktree creation, retry failures once
   e. **Worktree Merge Protocol:**
      - Pre-merge check: `git diff --name-only {branch} $(git branch --show-current)` — verify changed files are a subset of the agent's assignment. If unexpected files appear, halt and report.
      - Clean worktree before merge: `git -C {worktree_path} clean -fd` to remove untracked files.
      - Squash-merge each branch: `git merge --squash {branch} && git commit -m "feat({scope}): {task_title}"`
      - On conflict → halt: "Merge conflict. Resolve manually, re-run."
      - On success → `git branch -d {branch}`
      - After all merges → next wave from updated HEAD
7. After all waves complete:
   - Call `mcp__dominion__submit_work(phase, "execute", "orchestrator", {tasks_completed, waves, files_changed}, summary)`
   - Call `mcp__dominion__advance_step(phase, "execute")`
8. Report: "Execute complete. {N} tasks implemented across {M} waves. Run /dominion:review to continue."
