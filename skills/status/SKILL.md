---
name: status
description: Display pipeline status — current phase, step progress, circuit breaker, decisions
---

# /dominion:status

Display the current Dominion pipeline status.

## Display

1. Call `mcp__dominion__get_progress()`
2. Display status table:

```
Pipeline Status:
  Phase:          {phase} — {intent from phase CLAUDE.md}
  Pipeline:       {pipeline}
  Current step:   {step} ({status})
  Circuit breaker: {circuit_breaker state}
  Retry count:    {retry_count}

Step Progress:
  {for each step in pipeline}
  {step_name}: {status} {✓ if complete, → if active, · if pending}

Tasks:
  Completed: {completed_tasks count}
  Pending:   {pending_tasks count}

Recent Decisions:
  {last 3 from state.toml [[decisions]]}

Knowledge Files:
  {count from knowledge/index.toml entries}
```

3. If circuit_breaker == "open": highlight "HALTED — circuit breaker open. Fix issues and re-run orchestrate."
4. If status == "blocked": show blocker reason from task output

## Quality Metrics (v0.5.0)

After the status table, if the phase has a completed review step, call `mcp__dominion__quality_gate(phase)` and display:

```
Quality:
  Score:        {score.score}/10 ({score.deductions} deductions)
  Verdict:      {verdict}
  Effort:       avg {effort.mean}/10 (max {effort.max}) · {effort.distribution.localized} localized · {effort.distribution.cross_cutting} cross-cutting · {effort.distribution.structural} structural
  Delta:        {delta.summary}
```

If quality_gate returns error (no review yet), skip this section.

## Active Objectives (v0.5.0)

5. Call `mcp__dominion__get_objective()` → list active objectives
6. If objectives exist, display:

```
Active Objectives:
  {id} ({status}, {len(phases)} phases)
    Phase {pid}: "{intent}" — {phase_status}
```

## Event Feed (v0.5.0)

7. If `recent_events` in get_progress response is non-empty, display last 10 events:

```
Recent Events:
  {ts}  {event}  {step/role context}  {data summary}
```

Format: `HH:MM:SS  event_type  context — data`
Example: `15:30:45  phase_started  [research, plan, execute, review] — "Add auth system"`
