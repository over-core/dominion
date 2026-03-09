# Code Quality Review

Reviewer-driven code quality assessment.

## Input

Read and internalize:
1. Git diff: all changes in this phase (diff from phase start commit to current HEAD)
2. `.dominion/phases/{N}/test-report.toml` — test results and gaps
3. `.dominion/style.toml` — project code conventions
4. Run `dominion-tools style check` to get automated convention violations

## Checklist

### Style Compliance
- **Naming**: do new identifiers follow the project's naming conventions (from style.toml)?
- **Formatting**: consistent indentation, line length, import ordering?
- **Imports**: no unused imports, proper grouping?
- Run project linter if configured (detect from project structure)

### Error Handling
- Are errors handled explicitly, not silently swallowed?
- Do error messages provide context (what failed, why, what to do)?
- Are error types appropriate (not generic catch-all)?

### Complexity
- Flag functions/methods over 50 lines
- Flag nesting deeper than 3 levels
- Flag functions with more than 5 parameters
- Suggest extraction or simplification for flagged items

### Documentation
- Do new public APIs have documentation?
- Are complex algorithms commented?
- Are configuration options documented?

### Style Check Results
- **Style check results**: include any violations from `dominion-tools style check` as findings with category "convention"

## Output

For each finding:
- `id`: R1, R2, ... (sequential, continuing from other review steps)
- `category`: "code-quality"
- `severity`: high (bugs, security) | medium (maintainability) | low (style) | info (suggestions)
- `title`: one-line summary
- `description`: detailed explanation
- `file`: file path where the issue was found
- `suggestion`: actionable fix
