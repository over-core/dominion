# Proposal Apply

Apply accepted improvement proposals using the hybrid model.

## Hybrid Apply Model

Categorize each accepted proposal:

### Config-Only Changes (Direct Apply)

These are applied directly by the Attendant — no plan/execute cycle:

- **TOML updates**: style.toml additions, agent TOML instruction changes, dominion.toml updates
- **Agent instruction refinement**: update agent TOML `[tools.skills]` or behavioral sections, then run `dominion-tools agents generate` to regenerate .md files
- **Style drift correction**: update style.toml conventions, regenerate affected CLAUDE.md sections
- **New hookify rules**: create hookify rule in `.claude/hooks/`
- **Documentation chain updates**: update dominion.toml `[documentation]` section

For each direct-apply proposal:
1. Make the change
2. Validate (TOML parses, hookify rule is well-formed)
3. Commit: `git commit -m "improve: {proposal title}"`
4. Update improvements.toml: set `applied_at` = commit hash, `applied_by` = "direct"

### Code-Touching Changes (Mini Pipeline)

These require a plan/execute cycle:

- **New CLI commands**: need implementation in dominion-tools/
- **New hook scripts**: need shell script generation
- **Structural changes**: new file templates, new directory structures

For each pipeline-apply proposal:
1. Architect writes a mini-plan (1-3 tasks, inline — not a full plan.toml)
2. Developer implements each task
3. Commit per task: `git commit -m "improve: {proposal title} — {task description}"`
4. Update improvements.toml: set `applied_at` = final commit hash, `applied_by` = "pipeline"

## Guard Rails

- Never auto-apply. Each change is visible to the user in this session.
- Never remove a governance hard stop — skip the proposal and flag it.
- If a proposal fails to apply (TOML doesn't parse, test fails), mark as `status = "rolled-back"` and inform the user.
- Run `dominion-tools agents generate` after any agent TOML changes.

## Completion

After all proposals applied:
```
Applied {count} proposals:
  Direct: {direct_count} (config changes)
  Pipeline: {pipeline_count} (code changes)
  Failed: {failed_count}
```
