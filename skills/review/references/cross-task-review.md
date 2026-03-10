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

## Specialist Consultation Protocol

When specialist agents are active (check `.dominion/agents/` for specialist roles):

1. For each active specialist, read `specialist_referral` tags from research.toml
2. Filter the phase diff to only include files relevant to that specialist's domain
3. Formulate a scoped query:
   - "Review the phase {N} changes from a {domain} perspective."
   - "Changed files in your domain: {filtered file list}"
   - "Assess: domain-specific correctness, domain-specific risks, domain-specific improvements"
   - "Return: findings with severity and specific file:line references"
4. Collect specialist assessment
5. Assign finding IDs, record `source = "{specialist role}"` for provenance
6. Integrate into unified review — Reviewer owns all findings, specialists contribute expertise
7. Skip if no specialists are active

## Output

For each finding:
- `id`: R{N}, ... (sequential, continuing from architecture-check step)
- `category`: "cross-task"
- `severity`: high (integration bugs) | medium (inconsistency) | low (style differences) | info (observations)
- `title`: one-line summary
- `description`: detailed explanation with references to specific tasks
- `file`: file path (if applicable)
- `suggestion`: actionable fix
