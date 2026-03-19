---
name: plan
description: Run the plan step — task decomposition with wave grouping
---

# /dominion:plan

Run the plan step standalone. Auto-creates a phase if none is active.

## Steps

1. Call `mcp__dominion__get_progress()`
2. If no active phase: auto-create (assess_complexity + start_phase)
3. Call `mcp__dominion__prepare_step(phase, "plan")` → B-Thread (single Architect)
4. Read CLAUDE.md from returned path
5. Spawn Architect agent with CLAUDE.md content
6. After agent returns: call `mcp__dominion__advance_step(phase, "plan")`
7. Report: "Plan complete. {N} tasks across {W} waves. Run /dominion:execute to continue."
