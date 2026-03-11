# Status Dashboard

Assemble and present a project status dashboard.

## Data Collection

Collect data using CLI commands. Run each via Bash, skip any that fail:

1. **Project info**: `dominion-cli data get dominion.toml --key project --json`
2. **State position**: `dominion-cli state position --json`
3. **Roadmap**: `dominion-cli roadmap show --json`
4. **Phase progress** (only if position.phase > 0 and step is execute or later): `dominion-cli phase progress {N} --json`
5. **Signals**: `dominion-cli signal list --json`
6. **Backlog** (open items only): `dominion-cli backlog list --status open --json`
7. **Decisions**: `dominion-cli state decisions --json`
8. **Metrics** (only if step is improve or later): `dominion-cli metrics show --phase {N} --json`
9. **Improvements**: `dominion-cli improve list --status pending --json`
10. **Autonomy config** (only if autonomy section exists): `dominion-cli data get dominion.toml --key autonomy --json`
11. **Auto decisions**: `dominion-cli auto decisions --reviewed false --json`
12. **MCP status**: `dominion-cli data get state.toml --key mcp_status --json`

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

**Autonomy section** (only if [autonomy] exists in dominion.toml):
```
Mode: {autonomy.mode} | Circuit breakers: {max_tokens}/task, {max_retries} retries
```

**Autonomous decisions section** (only if unreviewed decisions exist):
```
Unreviewed decisions: {count}
```

**MCP status section** (only if any MCP is unavailable):
```
MCPs degraded: {unavailable_list} — fallback active
```

### Edge Cases

- Phase 0 (no phase started): "Ready for first phase. Run /dominion:orchestrate to start."
- No roadmap.toml: show phase number without title
- No progress.toml during execute: "Execute started but no progress tracked yet."
- No backlog.toml: skip backlog section entirely
- No decisions: show "Decisions this phase: 0"
