---
name: orchestrate
description: Drive the full phase pipeline — discuss, explore, plan, execute, test, review, improve — with auto-resume, status dashboard, and user control points between steps.
---

# /dominion:orchestrate

Drive the full development phase pipeline.

<IMPORTANT>
This skill manages the entire pipeline lifecycle. The pipeline is:
  discuss → explore → plan → execute → test → review → improve

Before starting:
1. Check `.dominion/dominion.toml` exists. If not: "Run /dominion:init first."
2. Check lock in `.dominion/state.toml`. If locked by another session and not expired, warn the user and suggest `/dominion:quick` for lightweight tasks.
3. Parse flags:
   - `--auto`: follow auto-mode protocol
   - `--dry-run`: run discuss → explore → plan only, then halt
4. Set lock with current session info.
</IMPORTANT>

## Pre-check

1. Verify `.dominion/` exists
2. Read `.dominion/state.toml` — determine current position
3. Detect mode:
   - If `--auto` flag passed: follow `@references/auto-mode.md` (readiness check, then unattended execution)
   - If `--dry-run` flag passed: set dry_run = true (compatible with interactive mode only, not --auto)
   - Otherwise: follow interactive mode below
4. Follow `@references/resume-logic.md` to determine next action

## Step 1: Status Dashboard

Present the pipeline status:
```
Phase {N}: {title}
  [status] discuss
  [status] explore
  [status] plan
  [status] execute
  [status] test
  [status] review
  [status] improve
```

Where status is: `✓` complete, `◐` in progress, `○` not started.

If blocked, show blocker details.

## Step 2: Pipeline Execution

Follow `@references/step-dispatch.md` for the dispatch protocol.

For each step in the pipeline:
1. Dispatch to the appropriate skill
2. Wait for completion
3. Present result summary
4. Ask: "Continue? [Y / pause / redo]"
   - **Y**: advance to next step
   - **pause**: save state, release lock, exit
   - **redo**: re-run the current step

## Step 3: Execute Step — Special Handling

The execute step has additional orchestration:
- Follow `@references/wave-execution.md` for worktree lifecycle management
- Between waves, follow `@references/inter-wave.md` for knowledge transfer

## Step 4: Phase Completion

When all steps are complete:
```
Phase {N} Complete:
  Tasks: {count} executed
  Tests: {passed}/{total} criteria passed
  Findings: {high} high, {medium} medium, {low} low

Next: /dominion:orchestrate to start the next phase.
```

Update state.toml: step = "improve", status = "complete".
Clear lock.
