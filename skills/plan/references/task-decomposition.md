# Task Decomposition

Architect-driven breakdown of phase goals into atomic tasks.

## Research Consumption

Before decomposition, systematically intake the Researcher's output:

1. **Read research.toml findings** via `dominion-cli research findings`. Process severity-sorted: critical findings first, then high, medium, low. Each finding has an impact scope — note which files/modules are affected.
2. **Read assumptions** — unverified assumptions first. These are risks that may invalidate task scoping. Flag any assumption that, if wrong, would change the decomposition.
3. **Read opportunities** — potential improvements the Researcher surfaced. Decide which opportunities align with the phase goal and should become tasks.
4. **Read specialist_referrals** — the Researcher flags work that needs specialist agents (Frontend, API, Database, DevOps, etc.). These directly feed into agent assignment.
5. **Internalize Bohner-Arnold impact maps** — understand which modules are affected by proposed changes and their transitive impact radius.
6. **Internalize Martin's coupling metrics** — afferent/efferent coupling scores indicate which modules are tightly coupled and must be co-located in the same wave or sequenced carefully.
7. **Search EchoVault** for prior planning decisions — `memory_search` with the phase topic to retrieve past decomposition patterns, wave grouping pitfalls, and task splitting lessons from previous phases.

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

## Specialist Routing

Assign the right agent to each task using specialist referrals from research:

1. **Read specialist_referral from findings.** The Researcher flags specific findings with a recommended specialist role (e.g., "frontend", "api-designer", "database").
2. **Check `.dominion/agents/` for active specialists.** If the referred specialist agent exists and is active in this project, assign the task to that specialist.
3. **Specialist not active → Developer with context.** If the specialist role is not active, assign to Developer but include the specialist referral in `knowledge_refs` so the Developer has domain-specific guidance.
4. **Default assignment:** Developer for implementation tasks. Secretary for configuration/generation tasks.

## Agent Assignment

Default agent is "Developer". Override only when the task clearly requires a different role:
- Research-heavy tasks → "Researcher"
- Configuration/generation tasks → "Secretary"
- Specialist-referred tasks → the referred specialist (if active) or Developer with specialist knowledge_refs

## Output

For each task, produce:
- `id`: task id
- `title`: concise description (imperative mood: "Add X", "Refactor Y")
- `depends_on`: list of task ids
- `agent`: role name
- `file_ownership`: list of directories/files this task may modify
- `token_estimate`: estimated token cost (0 if not estimated)

## ADR Recording

Record Architecture Decision Records for non-obvious planning choices:

1. **Decomposition trade-offs.** When splitting a task is debatable (e.g., keeping a large task whole for coherence vs. splitting for parallelism), record the decision and rationale as an ADR.
2. **Agent routing rationale.** When assigning a task to a specialist instead of Developer (or vice versa), record why — especially when overriding a specialist_referral.
3. **Wave-grouping decisions.** When co-locating or separating tasks deviates from the default topological sort (e.g., coupling-aware grouping, critical path priority), record the reasoning.
4. **Write ADRs** via `dominion-cli plan task` metadata or as notes in plan.toml. ADRs are consumed by the Reviewer agent during the review step to validate planning rationale.
