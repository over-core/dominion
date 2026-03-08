# Step Dispatch

Protocol for dispatching pipeline steps to their skills.

## Dispatch Map

| Step     | Skill               | Agent Role  | Produces               |
|----------|----------------------|-------------|------------------------|
| discuss  | /dominion:discuss    | Advisor     | intent.md              |
| explore  | /dominion:explore    | Researcher  | research.toml          |
| plan     | /dominion:plan       | Architect   | plan.toml              |
| execute  | /dominion:execute    | Developer   | progress.toml, summaries |
| test     | /dominion:test       | Tester      | test-report.toml       |
| review   | /dominion:review     | Reviewer    | review.toml            |
| improve  | /dominion:improve    | Advisor     | improvements.toml, knowledge |

## Transition Rules

Each step has prerequisites. Verify before dispatching:

- **discuss**: phase number identified from roadmap.toml
- **explore**: discuss complete (intent.md exists or phase goals are in roadmap)
- **plan**: research.toml exists for current phase
- **execute**: plan.toml exists for current phase, lock acquired, `dominion-tools plan validate` passes
- **test**: progress.toml exists, execute step complete
- **review**: test-report.toml exists for current phase
- **improve**: review.toml and metrics.toml exist for current phase

If a prerequisite is missing, inform the user and suggest the required step.

## State Updates

Before dispatching a step:
- Set `position.step` = {step name}
- Set `position.status` = "active"

After step completes:
- Set `position.status` = "complete"
- Update `position.last_session`

## User Control Points

After each step completes, present the result and ask:
```
{step} complete. {brief summary}
Continue to {next step}? [Y / pause / redo]
```

- **Y**: dispatch next step
- **pause**: save state (status remains "complete" for current step), release lock, exit gracefully
- **redo**: re-run current step (warn about overwriting artifacts)

## Auto Mode Overrides

When running in auto mode (`--auto`), the following overrides apply:

### Dispatch Changes
- **discuss**: skip interactive discussion — use roadmap.toml phase goals as intent
- **improve**: collect-only — generate data, queue proposals, do not present or apply

### No Control Points
Do not present "Continue? [Y / pause / redo]" prompts. Proceed directly to the next step.

### Halt Conditions
Auto mode halts (becomes a control point) only for:
- Governance hard stops (architecture, security, data format changes)
- Critical blocker signals (level = "critical")
- Circuit breaker: `max_failed_tasks_per_wave` exceeded
- Circuit breaker: `session_time_limit_hours` exceeded

On halt: set `position.status = "blocked"`, checkpoint state, wait for human.

See `@references/auto-mode.md` for full protocol.
