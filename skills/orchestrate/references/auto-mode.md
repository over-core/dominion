# Auto Mode Protocol

Instructions for running the pipeline unattended via `/dominion:orchestrate --auto`.

## Pre-Flight

1. Run `dominion-tools auto readiness`
2. If result is "NO": present gaps and ask user to resolve before proceeding
3. If result is "YES" (with or without warnings): present summary and confirm start
   ```
   Auto mode ready.
     Circuit breakers: {max_tokens}/task, {max_retries} retries, {session_limit}h session limit
     MCPs: {available}/{total} available
     {warnings if any}

   Starting Phase {N}. Will halt only on governance hard stops.
   Proceed? [Y/n]
   ```
4. On confirmation: set `autonomy.mode = "auto"` in dominion.toml (runtime, revert on exit)

## Step Dispatch — Auto Mode

Follow the same dispatch map as [step-dispatch.md](step-dispatch.md) with these overrides:

### discuss step
Skip interactive discussion. Read `roadmap.toml` for the current phase's goals and title. Use these as the intent — no Advisor conversation. If `intent.md` already exists from a previous interactive run, use it as-is.

### explore, plan, execute, test, review steps
Run without control points. Do NOT ask "Continue? [Y / pause / redo]" between steps. Proceed directly to the next step after each completes.

### improve step
Run in collect-only mode:
- Generate the retrospective data (read metrics, summaries, findings) but do NOT present it interactively
- Collect all proposals from review.toml and write to improvements.toml with `status = "pending"`
- Do NOT apply any proposals
- Do NOT ask for user input
- Log a summary: "Improve step complete (collect-only). {N} proposals queued for review."

## Governance Hard Stops

These halt auto mode and wait for human input regardless:
- Architecture changes (new module boundaries, API contract changes)
- Security decisions (auth changes, encryption choices, permission model changes)
- Data format changes (schema migrations, wire protocol changes)
- Critical halts (any agent raises a critical-level blocker)

When a hard stop fires:
1. Log the halt in state.toml: set `position.status = "blocked"`, populate `[blocker]`
2. Checkpoint state via `dominion-tools state checkpoint`
3. Output: "Auto mode halted: {reason}. Waiting for human input."
4. The next session resume will present the blocker per [resume-logic.md](resume-logic.md)

## Circuit Breaker Enforcement

Read `dominion.toml [autonomy.circuit_breakers]` before each task dispatch:

- **max_tokens_per_task**: if task exceeds budget, halt it, log autonomous decision (type="skip", reason="token budget exceeded")
- **max_retry_attempts**: if task has failed N times, halt it, log autonomous decision (type="skip", reason="max retries exceeded")
- **max_cascade_replans**: if Architect has replanned the same task N times, halt it, log autonomous decision (type="skip", reason="cascade replan limit")
- **max_failed_tasks_per_wave**: if N tasks in current wave have failed, halt the wave, raise blocker
- **session_time_limit_hours**: if elapsed time exceeds limit, checkpoint and exit gracefully

## Autonomous Decision Logging

When any decision is made without human input, append to state.toml `[[autonomous_decisions]]`:

```toml
[[autonomous_decisions]]
id = {next sequential id}
timestamp = "{ISO 8601}"
phase = {current phase}
task = "{task id}"
type = "{replan | skip | retry | split | reorder}"
description = "{what was decided}"
reason = "{why — error context, breaker trigger}"
session_id = "{current session id from lock}"
reviewed = false
outcome = ""
```

Decision types:
- **replan**: Architect changed the plan for a failed task
- **skip**: task skipped after max retries or token budget exceeded
- **retry**: task retried with a different approach (only log if approach changed)
- **split**: task split into subtasks by Architect
- **reorder**: wave tasks reordered due to dependency changes

## Replan Constraints

When the Architect replans a failed task in auto mode, enforce `dominion.toml [autonomy.replan_constraints]`:

- `can_split_tasks = true`: Architect may split a task into smaller subtasks
- `can_reorder_within_wave = true`: Architect may reorder tasks within the current wave
- `can_add_dependencies = true`: Architect may add new dependencies between tasks
- `cannot_change_wave_count = true`: Architect must NOT add or remove waves
- `cannot_modify_completed_tasks = true`: Architect must NOT modify already-completed tasks
- `cannot_alter_governance_rules = true`: Architect must NOT change governance hard stops

If the Architect needs to violate a constraint, this becomes a governance hard stop — halt and wait for human.

## Session End

When auto mode completes (all steps done) or is halted:
1. Run `dominion-tools state checkpoint`
2. Reset `autonomy.mode` to "interactive" in dominion.toml
3. Output summary:
   ```
   Auto session complete.
     Steps completed: {list}
     Autonomous decisions: {count}
     Proposals queued: {count}
     Status: {complete | halted: reason}

   Next: run /dominion:orchestrate to review decisions and proposals.
   ```
