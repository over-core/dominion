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

## Output

For each finding:
- `id`: R{N}, ... (sequential, continuing from code-quality step)
- `category`: "architecture"
- `severity`: high (violations) | medium (concerns) | low (suggestions) | info (observations)
- `title`: one-line summary
- `description`: detailed explanation
- `file`: file path (if applicable)
- `suggestion`: actionable fix
