---
name: execute
description: Developer-driven wave-by-wave parallel task execution. Manages worktrees, agent spawning, signals, progress tracking. Produces progress.toml and task summaries.
---

# /dominion:execute

Execute the plan wave by wave with parallel Developer agents.

<IMPORTANT>
This skill requires plan.toml for the current phase. Check `.dominion/phases/{N}/plan.toml` exists.
If not, tell the user: "Run /dominion:plan first."

Before starting, check the lock:
- If `.dominion/state.toml` `[lock].session_id` is set and not expired, warn: "Pipeline is locked by session {id} since {locked_at}. Use /dominion:quick for lightweight tasks, or force-unlock if the session is stale."
</IMPORTANT>

## Pre-check

1. Read `.dominion/state.toml` — get current phase, check lock
2. Verify `.dominion/phases/{N}/plan.toml` exists
3. Set lock: update state.toml `[lock]` with session_id, locked_at

## Step 1: Assumption Verification

Read `.dominion/phases/{N}/research.toml` — find all assumptions with status "unverified".

For each unverified assumption:
- Attempt to verify now (read files, check versions, run commands)
- Update status to "verified" or "false"
- If any assumption is "false": halt execution, present the false assumption to the user, ask whether to continue, replan, or abort

## Step 2: Initialize Progress

If `.dominion/phases/{N}/progress.toml` does not exist:
- Create from `@templates/schemas/progress.toml`
- Populate phase number, wave structure, and task entries from plan.toml

If progress.toml exists, resume from current state (find first incomplete wave).

## Step 3: Wave Execution

For each wave (starting from the first incomplete wave):

Follow `@references/task-execution.md` for the wave execution protocol:
1. Set up worktrees for each task in the wave
2. Spawn Developer agents in parallel
3. Monitor for signals per `@references/signal-protocol.md`
4. Wait for all agents to complete
5. Verify SUMMARY.md exists for each task (per `@references/summary-writing.md`)
6. Merge completed tasks
7. Clean up worktrees
8. Update progress.toml

Between waves: inter-wave checkpoint (handled by /dominion:orchestrate if running under it).

## Step 4: Post-Execution Summary

Display to the user:
```
Execution Complete (Phase {N}):
  Waves: {completed}/{total}
  Tasks: {completed} complete, {failed} failed, {blocked} blocked
  Blockers: {list or "none"}
```

## Step 5: Update State

Update `.dominion/state.toml`:
- `position.step` = "execute"
- `position.status` = "complete" (or "blocked" if blockers remain)
- `position.wave` = 0
- `position.current_task` = ""
- Clear `[lock]`
- `position.last_session` = {today's date}
