# Status Dashboard

Assemble and present a project status dashboard.

## Data Collection

Read these files (skip any that don't exist):

1. `.dominion/dominion.toml` — `[project]` section for project name and vision
2. `.dominion/state.toml` — `[position]` for phase, step, wave, status, last_session; `[lock]` for active locks; `[blocker]` for active blocker
3. `.dominion/roadmap.toml` — current phase title and milestone context
4. `.dominion/phases/{N}/progress.toml` — wave/task counts and statuses (only if position.phase > 0 and step is execute or later)
5. `.dominion/signals/` — list directory, count `.toml` files by type (blocker vs warning)
6. `.dominion/backlog.toml` — count items by priority (high/medium/low) and status (open only)
7. `.dominion/state.toml` `[[decisions]]` — count decisions for current phase
8. `.dominion/phases/{N}/metrics.toml` — phase metrics summary (only if step is improve or later)
9. `.dominion/improvements.toml` — pending improvement proposals count

## Dashboard Format

Present in this format, adapting sections based on available data:

```
Project: {project.name}
Phase {N}: "{phase_title}" — {step} ({status})

Pipeline:
  {step_name} {icon}  {step_name} {icon}  ...

{wave_section if in execute}
{blocker_section if blockers exist}
{backlog_section if backlog exists}
Decisions this phase: {count}
Last session: {last_session date}
```

### Icons

- Completed step: checkmark character
- In-progress step: half-circle character
- Not started step: open circle character

### Adaptive Sections

**Wave section** (only during execute step):
```
Current wave: {N} — {total} tasks ({complete} complete, {in_progress} in-progress, {failed} failed)
```

**Blocker section** (only if blockers exist):
```
Active blockers: {count}
  - {task_id}: {reason} (level: {level})
```

**Backlog section** (only if open backlog items exist):
```
Backlog: {total} items ({high} high, {medium} medium, {low} low)
```

**Metrics section** (only after review step):
```
Metrics: {tests_added} tests, {findings_high} high findings, {acceptance_pass_rate}% pass rate
```

**Improvements section** (only if improvements.toml has pending proposals):
```
Pending proposals: {count}
```

### Edge Cases

- Phase 0 (no phase started): "Ready for first phase. Run /dominion:orchestrate to start."
- No roadmap.toml: show phase number without title
- No progress.toml during execute: "Execute started but no progress tracked yet."
- No backlog.toml: skip backlog section entirely
- No decisions: show "Decisions this phase: 0"
