---
name: quick
description: Lightweight task execution — skip the full pipeline ceremony for small, well-scoped changes. Still follows conventions and governance.
---

# /dominion:quick

Execute a small task without full pipeline overhead.

<IMPORTANT>
Quick tasks do not advance phase state, do not require a lock, and do not produce pipeline artifacts.
They still follow project conventions from CLAUDE.md, style.toml, and governance rules.
If the task sounds large (multiple files across modules, needs planning, has dependencies), suggest: "This sounds like it needs the full pipeline. Consider /dominion:orchestrate instead."
</IMPORTANT>

## Pre-check

1. Verify `.dominion/` directory exists. If not, tell the user: "Run /dominion:init first."
2. Read `.dominion/dominion.toml` — load project context
3. Read `.dominion/style.toml` — load conventions

## Step 1: Task Input

Ask the user: "What needs to be done?"

Evaluate the response:
- If the task involves >3 files across module boundaries → suggest full pipeline
- If the task has unclear scope → ask clarifying questions
- If the task is well-scoped → proceed

## Step 2: Quick Execution

Follow `@references/quick-workflow.md`

## Step 3: Summary

Display to the user:
```
Done:
  {what was done — one line}
  Files: {list of changed files}
  Tests: {passed/failed/skipped}
  Commit: {hash}
```
