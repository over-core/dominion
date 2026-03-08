---
name: discuss
description: Capture user intent for the next phase — goals, scope, constraints, priorities. Advisor-driven conversation that shapes everything downstream.
---

# /dominion:discuss

Capture intent for the next development phase.

<IMPORTANT>
This skill requires Dominion to be initialized. Check that `.dominion/dominion.toml` exists.
If it does not, tell the user: "Run /dominion:init first."
</IMPORTANT>

## Pre-check

1. Read `.dominion/state.toml` — check position.phase and position.step
2. Read `.dominion/roadmap.toml` — find the next pending phase (lowest phase number with status != "complete")
3. If no pending phases remain, tell the user: "All roadmap phases are complete. Add new phases to roadmap.toml or start a new milestone."

## Step 1: Present Phase Context

Display to the user:
```
Phase {N}: {title from roadmap.toml}
Milestone: {milestone from roadmap.toml}
```

If this is not phase 1, read the previous phase's review.toml (if it exists) and summarize:
- High-severity findings from last review
- Any deferred items

## Step 2: Intent Capture

Follow `@references/intent-capture.md`

## Step 3: Update State

Update `.dominion/state.toml`:
- `position.phase` = {N}
- `position.step` = "discuss"
- `position.status` = "complete"
- `position.last_session` = {today's date}

Run: `dominion-tools phase init {N} --title "{title}"`
