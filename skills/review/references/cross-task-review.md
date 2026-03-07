# Cross-Task Review

Reviewer-driven cross-task pattern detection.

## Input

Read and internalize:
1. All summaries from `.dominion/phases/{N}/summaries/task-*.md`
2. Full phase diff (git diff from phase start to HEAD)
3. `.dominion/phases/{N}/test-report.toml` — test results

## Consistency Check

- **Pattern consistency**: do different tasks handle the same patterns differently? (error handling, logging, validation, API response format)
- **Naming consistency**: are new identifiers across tasks using consistent naming for similar concepts?
- **Interface consistency**: do components introduced by different tasks have compatible interfaces?

## Integration Check

- **Composition**: do changes from different tasks compose correctly when merged? Look for:
  - Conflicting global state modifications
  - Incompatible type definitions
  - Duplicate functionality
- **Hidden dependencies**: are there runtime dependencies between tasks that weren't captured in plan.toml depends_on?
- **Runtime risks**: could the combined changes cause issues that individual task testing wouldn't catch? (race conditions, resource contention, configuration conflicts)

## Repeated Friction

- Read "Friction Encountered" from all task summaries
- Did multiple agents hit similar friction? This indicates a systemic issue worth flagging
- Did any agent make a decision that conflicts with another agent's decision?

## Output

For each finding:
- `id`: R{N}, ... (sequential, continuing from architecture-check step)
- `category`: "cross-task"
- `severity`: high (integration bugs) | medium (inconsistency) | low (style differences) | info (observations)
- `title`: one-line summary
- `description`: detailed explanation with references to specific tasks
- `file`: file path (if applicable)
- `suggestion`: actionable fix
