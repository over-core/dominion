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
  Complexity:     {complexity}
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
