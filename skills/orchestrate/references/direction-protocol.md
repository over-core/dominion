# Direction Protocol

How agents read and apply project direction at runtime.

## Reading Direction

At the start of any task that modifies code, read `.dominion/dominion.toml` `[direction]`:
- `mode` — maintain | improve | restructure

If `[direction]` section does not exist, default to `maintain` behavior.

## Mode: Maintain

- Match existing style and patterns in the files you edit
- Do not proactively improve code outside the task scope
- Do not suggest refactoring unless explicitly asked
- Preserve conventions even if you'd prefer different ones

## Mode: Improve

- Boy scout rule — leave files better than you found them
- When editing a file: fix obvious issues (naming, dead code, missing types) in the code you touch
- Do NOT seek out files to improve — only improve files the task requires editing
- Do NOT refactor across module boundaries
- Log improvements made in SUMMARY.md under a "Boy Scout Improvements" section

## Mode: Restructure

Read `[direction.restructure]` for target state and migration strategy.

### Zone Checking

Before editing any file, determine which zone it belongs to:

1. Read `[[direction.restructure.legacy_zones]]` paths
2. Check if the file path falls under any legacy zone
3. Apply the appropriate policy:

**Legacy zone (minimal-change):**
- Only change what the task explicitly requires
- Do NOT learn patterns from this code — it represents the old architecture
- Do NOT refactor or improve legacy code
- Do NOT add new functionality to legacy zones — create new code in non-legacy locations
- If the task requires changes here, make the smallest possible change

**Non-legacy zone (active):**
- Follow target state conventions strictly
- New code must align with `target_state` description
- Do not copy patterns from legacy zones into new code
- Apply migration strategy patterns where applicable

**No legacy zones defined (full restructure):**
- The entire codebase needs restructuring toward target state
- Follow target state conventions everywhere
- Improve code toward target state as you touch it
- No files are protected — all are fair game for restructuring

### Migration Strategies

Read `migration_strategy` to inform approach:
- **strangler-fig**: Build new alongside old, gradually redirect. Never modify old code to match new patterns — replace it.
- **big-bang**: Coordinated rewrite. Follow target state in all new code. Flag legacy code that blocks progress.
- **incremental**: Module-by-module migration. Each touched module should be fully migrated before moving on.

## Reporting

In SUMMARY.md, note:
- Which direction mode was active
- If restructure: which zone(s) were touched and what policy applied
- Any conflicts between task requirements and direction policy (flag as governance decision)
