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

## Profile-Aware Dispatch

Before dispatching any step, check if `~/.claude/.dominion/user-profile.toml` exists.

If it exists, read `experience_level` and pass it to the dispatched agent as context:
- **Beginner**: agents explain what they're doing and why at each major decision
- **Intermediate**: agents give brief status updates, explain only non-obvious decisions
- **Advanced**: agents work silently, report results only

This affects presentation, not behavior. All agents perform the same work regardless of level.

Run `dominion-cli profile tick` at the start of each orchestrate session.

## Transition Rules

Each step has prerequisites. Verify before dispatching:

- **discuss**: phase number identified from roadmap.toml
- **explore**: discuss complete (intent.md exists or phase goals are in roadmap)
- **plan**: research.toml exists for current phase
- **execute**: plan.toml exists for current phase, lock acquired, `dominion-cli plan validate` passes
- **test**: progress.toml exists, execute step complete
- **review**: test-report.toml exists for current phase
- **improve**: review.toml and metrics.toml exist for current phase

If a prerequisite is missing, inform the user and suggest the required step.

## Cost Estimation Gate

After plan step completes and before execute step dispatches:

1. Read `.dominion/phases/{N}/plan.toml` — count tasks per wave, identify agent assignments
2. For each task: look up the assigned agent's `.dominion/agents/{role}.toml` for model
3. Apply token estimates:
   - Developer (sonnet): 40K per task
   - Tester (sonnet): 20K per task
   - Reviewer (opus): 30K per task
   - Other sonnet agents: 30K per task
   - Other opus agents: 40K per task
4. Add overhead: test step (20K) + review step (30K)

Present to user:
```
Phase {N} cost estimate:
  Wave 1: {task_count} tasks × {agents} ≈ {tokens}K tokens
  Wave 2: {task_count} tasks × {agents} ≈ {tokens}K tokens
  Test + Review: ≈ {tokens}K tokens
  Total: ≈ {total}K tokens

Proceed? [Y/n]
```

If user approves: write `[estimates]` section to plan.toml and continue to execute.
If user declines: pause pipeline, run `dominion-cli state update --step plan --status complete`.

In auto mode: write estimates to plan.toml, log but do not halt. Circuit breakers handle cost control.

### Estimates Schema (plan.toml addition)

```toml
[estimates]
total_tokens = 0
estimated_at = ""

[[estimates.waves]]
wave = 1
tasks = 0
tokens = 0

[estimates.overhead]
test = 20000
review = 30000
```

## Dry-Run Halt

If `--dry-run` flag is set:

After the cost estimation gate (plan step complete + estimates presented), halt the pipeline:

```
Dry run complete.
  Plan: {task_count} tasks across {wave_count} waves
  Estimated cost: ≈ {total}K tokens
  Artifacts: intent.md, research.toml, plan.toml

Resume with /dominion:orchestrate to execute.
```

Run `dominion-cli state update --step plan --status complete`. Release lock. Exit.

When the user later runs `/dominion:orchestrate` without `--dry-run`, resume-logic picks up from execute step normally.

## State Updates

Before dispatching a step:
- Run `dominion-cli state update --step {step name} --status active`

After step completes:
- Run `dominion-cli state update --status complete`
- Run `dominion-cli state checkpoint`

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

On halt: run `dominion-cli state update --status blocked`, then `dominion-cli state checkpoint`, wait for human.

See [auto-mode.md](auto-mode.md) for full protocol.
