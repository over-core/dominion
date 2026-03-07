# Architecture Check

Reviewer-driven architecture compliance assessment.

## Input

Read and internalize:
1. `.dominion/phases/{N}/plan.toml` — planned task scopes and file ownership
2. `.dominion/dominion.toml` — project architecture, governance rules
3. `.dominion/style.toml` — architectural conventions
4. Git diff: all changes in this phase

## Plan Conformance

- **File ownership**: did tasks modify only their assigned files? List any unplanned file modifications.
- **Task completeness**: are all planned tasks marked complete in progress.toml? List any incomplete.
- **Unplanned files**: were any files created or modified that are not in any task's file_ownership?

## Convention Compliance

- **Architecture patterns**: do changes follow the project's established patterns (from dominion.toml and style.toml)?
- **Dependency usage**: are new dependencies justified? Do they comply with governance rules?
- **Module boundaries**: do changes respect module boundaries, or do they introduce new cross-module coupling?
- **API consistency**: do new APIs follow established patterns in the codebase?

## Governance

- **Governance-sensitive files**: were any files from `governance.file_ownership` modified? If so, was the correct agent/role involved?
- **Hard rules**: do changes comply with all `governance.hard_rules`?
- **Security review triggers**: do changes touch authentication, authorization, data handling, or external APIs?

## ADR Evaluation

Read Architect's ADRs from plan.toml:
1. For each ADR in the plan, verify the implementation matches the decision
2. Check: was the chosen approach actually implemented, or did the developer diverge?
3. If implementation diverges: create a finding — either the code should match the ADR, or the ADR needs updating
4. Link each ADR to the files it affects

## License Compatibility

For new dependencies added in this phase:
1. Check each dependency's license
2. Verify compatibility with project license (from dominion.toml or LICENSE file)
3. Flag: GPL/AGPL dependencies in permissive-licensed projects, unknown licenses, no-license packages
4. Severity: Critical for incompatible licenses in public-facing projects

## Backward Compatibility

For changes to public APIs:
1. Identify changed public interfaces (exported functions, API endpoints, public types)
2. Determine: is the change additive (new fields/endpoints) or breaking (removed/renamed)?
3. For breaking changes: are there consumers? Is migration documented? Does semver reflect it?
4. Severity: Major for breaking changes without migration path

## Coupling Analysis

Use Researcher's Martin's Package Coupling metrics if available:
1. Read coupling data from research.toml
2. Check if phase changes increased afferent/efferent coupling beyond acceptable thresholds
3. Flag new cross-module dependencies that weren't in the plan

## Output

For each finding:
- `id`: R{N}, ... (sequential, continuing from code-quality step)
- `category`: "architecture"
- `severity`: high (violations) | medium (concerns) | low (suggestions) | info (observations)
- `title`: one-line summary
- `description`: detailed explanation
- `file`: file path (if applicable)
- `suggestion`: actionable fix
