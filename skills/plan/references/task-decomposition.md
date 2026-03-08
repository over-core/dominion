# Task Decomposition

Architect-driven breakdown of phase goals into atomic tasks.

## Input

Read and internalize:
1. `.dominion/phases/{N}/research.toml` — findings, opportunities, assumptions
2. `.dominion/phases/{N}/intent.md` — phase goals, scope boundary, constraints, priorities
3. `.dominion/dominion.toml` — project structure, governance rules

## Decomposition Rules

Break the phase goal into tasks following these rules:

1. **One task = one Developer = one commit boundary.** A task should be completable by a single Developer agent in a single session. If a task requires coordinating multiple files across module boundaries, it is too large — split it.

2. **Single responsibility.** Each task does one thing. "Add endpoint and write tests" is two tasks. "Add endpoint" and "Write endpoint tests" are correct.

3. **Clear scope.** Every task must specify which files/directories it may modify (file_ownership). No ambiguity about what a Developer should touch.

4. **Atomic commits.** The work for a task should be committable as a single logical commit. If a task would require multiple unrelated commits, split it.

5. **Token budget.** Read `dominion.toml [autonomy.circuit_breakers].max_tokens_per_task`. Estimate the token cost for each task based on:
   - Files to read (count and size of files in scope)
   - Changes to produce (number of new/modified files, estimated lines)
   - Test cycles expected (compile/test iterations)
   - Rough guide: reading a file ≈ 1-2k tokens, producing a file ≈ 2-4k tokens, a test/fix cycle ≈ 5-10k tokens
   - If the estimate exceeds 80% of the budget, the task is too large — split it along file ownership or responsibility boundaries
   - Record the estimate in `token_estimate`. If `[autonomy]` section doesn't exist, set `token_estimate = 0` (not estimated)

## Task ID Format

Use `{phase}-{seq}` zero-padded: `01-01`, `01-02`, ..., `02-01`, etc.

## Dependency Identification

For each task, determine:
- Which other tasks must complete before this one can start?
- What data or artifacts does this task consume from upstream tasks?
- Record in `depends_on` as a list of task ids

Dependencies should be minimal — prefer independent tasks that can run in parallel.

## Agent Assignment

Default agent is "Developer". Override only when the task clearly requires a different role:
- Research-heavy tasks → "Researcher"
- Configuration/generation tasks → "Attendant"

## Output

For each task, produce:
- `id`: task id
- `title`: concise description (imperative mood: "Add X", "Refactor Y")
- `depends_on`: list of task ids
- `agent`: role name
- `file_ownership`: list of directories/files this task may modify
- `token_estimate`: estimated token cost (0 if not estimated)
