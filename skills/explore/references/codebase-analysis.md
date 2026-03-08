# Codebase Analysis

Researcher-driven analysis scoped to the current phase goals.

## Scope Determination

1. Read `.dominion/phases/{N}/intent.md` for phase goals and scope boundary
2. Read `.dominion/roadmap.toml` for phase description
3. Identify relevant source directories, modules, and files based on goals
4. Explicitly note what is OUT of scope per the intent

## Architecture Scan

For each relevant area:
1. Use Glob to find source files in the area
2. Read key files — entry points, interfaces, configuration
3. Identify patterns: design patterns in use, layering, module boundaries
4. Note coupling: which modules depend on each other, shared state, cross-cutting concerns
5. Map public APIs and interfaces that the phase may need to modify or extend

Record findings with category "architecture".

## Dependency Analysis

1. Read package manifests (Cargo.toml, pyproject.toml, package.json, go.mod, etc.)
2. Check dependency versions — are any deprecated, outdated, or known-vulnerable?
3. Cross-reference with `.dominion/dominion.toml` `[governance.hard_rules]` for dependency constraints
4. Note any dependency changes the phase goals may require

Record findings with category "dependency".

## Code Quality Scan

1. Use Grep to find error handling patterns — bare excepts, unwraps, unchecked returns
2. Check test coverage — do areas the phase will modify have tests?
3. Look for documentation gaps in public APIs the phase will extend
4. Check for TODO/FIXME/HACK comments in relevant areas

Record findings with category "testing", "performance", or "security" as appropriate.

## Risk Identification

For each area the phase will modify:
1. What could go wrong? (breaking changes, data loss, security gaps)
2. What is the blast radius? (how many other modules are affected)
3. What existing test coverage exists?
4. Are there governance-sensitive files (from dominion.toml)?

Record high-risk findings with severity "high".

## Output Format

Each finding must have:
- `id`: F1, F2, ... (sequential)
- `severity`: high | medium | low
- `category`: architecture | dependency | performance | security | testing
- `title`: one-line summary
- `description`: detailed explanation
- `evidence`: list of file:line references
- `recommendation`: actionable next step
