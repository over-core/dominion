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
4. For each wave (ascending):
   a. For each task: call `mcp__dominion__prepare_task(phase, task_id)`
   b. Read each task CLAUDE.md from returned path
   c. Spawn `Agent(isolation='worktree', prompt=content, subagent_type=task.agent_role)` for each
   d. After ALL agents return: **Worktree Merge Protocol**
      - Merge each branch: `git merge --no-ff {branch} -m "feat: {task_title}"`
      - On conflict → halt: "Merge conflict. Resolve manually, re-run."
      - On success → `git branch -d {branch}`
      - After all merges → next wave from updated HEAD
5. After all waves: call `mcp__dominion__advance_step(phase, "execute")`
6. Report: "Execute complete. {N} tasks implemented. Run /dominion:review to continue."
