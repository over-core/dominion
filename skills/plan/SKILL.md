---
name: plan
description: Architect-driven planning step. Translates research into a wave-grouped executable plan with acceptance criteria. Produces plan.toml.
---

# /dominion:plan

Translate research findings into an executable, wave-grouped plan.

<IMPORTANT>
This skill requires research.toml for the current phase.
Check `.dominion/phases/{N}/research.toml` exists. If not, tell the user: "Run /dominion:explore first."
</IMPORTANT>

## Pre-check

1. Read `.dominion/state.toml` — get current phase number
2. Verify `.dominion/phases/{N}/research.toml` exists
3. If `.dominion/phases/{N}/plan.toml` already exists, warn: "Plan already exists for phase {N}. Re-running will overwrite. Continue? [Y/n]"

## Step 1: Task Decomposition

Follow `@references/task-decomposition.md`

## Step 2: Wave Grouping

Follow `@references/wave-grouping.md`

## Step 3: Acceptance Criteria

Follow `@references/acceptance-criteria.md`

## Step 4: Write Plan

Write `.dominion/phases/{N}/plan.toml` using `@templates/schemas/plan.toml` as the schema. Populate with tasks, waves, criteria, and assumption references from Steps 1-3.

## Step 5: Present Plan Summary

Display to the user:
```
Plan Complete (Phase {N}):
  Tasks: {total}
  Waves: {count}

  Wave 1: {task count} tasks
    - {id}: {title}
  Wave 2: {task count} tasks
    - {id}: {title}
  ...

File ownership conflicts: {none | list}
```

Ask: "Approve this plan? [Y / adjust / redo]"

## Step 6: Update State

Update `.dominion/state.toml`:
- `position.step` = "plan"
- `position.status` = "complete"
- `position.last_session` = {today's date}
