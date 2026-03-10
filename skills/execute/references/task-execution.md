# Task Execution

Wave execution protocol for parallel Developer agents.

## Developer Methodology

Each Developer agent follows a 7-phase execution cycle per task:

1. **Task Intake** — Read the task from plan.toml (id, title, file_ownership, acceptance criteria, verify_command). Load knowledge_refs and upstream handoff notes. Search EchoVault for gotchas related to task files and domain.

2. **Context Building** — Use serena (`get_symbols_overview`, `find_referencing_symbols`) to map symbols and relationships within the file_ownership scope. Read existing tests for affected code. Check style.toml for conventions. Identify existing patterns and abstractions to extend rather than reinvent.

3. **TDD Red** — Write tests that capture acceptance criteria as executable assertions. Run them and verify they fail for the right reason. Skip for pure refactoring tasks.

4. **Implementation (TDD Green)** — Write minimum code to pass the failing test. Follow clean code and SOLID principles. Use existing codebase patterns. Stay within file_ownership boundaries. Priority order: working > clean > fast.

5. **Refactor** — Apply refactoring patterns (Fowler catalog) if code smells are present. Boy Scout Rule: leave code better than found, but only within task scope. Run tests after each refactoring step.

6. **Verification** — Run verify_command from acceptance criteria. Run the existing test suite to check for regressions. Verify changes stay within file_ownership. If verification fails, iterate from the Implementation phase.

7. **Commit & Handoff** — Atomic commit with conventional commit message. Write SUMMARY.md with friction, decisions, and discoveries. Save discoveries to EchoVault. Report blockers via signal protocol.

### Context Building with Serena

Before writing any code, Developers use serena to understand the code they will change:

- `get_symbols_overview` on each file in file_ownership — understand the public API, classes, functions, and types.
- `find_referencing_symbols` on symbols being modified — identify callers, implementors, and dependents to assess impact.
- `find_symbol` to read specific implementations when understanding behavior before changing it.
- `replace_symbol_body` for targeted edits to existing functions/methods — preferred over raw file editing.

This replaces "read the whole file and grep around." Symbol-level navigation gives precise scope awareness with lower token cost.

### Mode Adaptation

The 7-phase cycle adapts based on execution mode:

- **Orchestrated mode** (`/dominion:execute`): Strict Red-Green-Refactor discipline. One atomic commit per task. file_ownership boundaries enforced from plan.toml. Full summary writing.
- **Quick mode** (`/dominion:quick`): Relaxed — tests-after is acceptable. One commit for the whole change. Developer determines own scope. Abbreviated summaries.
- **Improve mode** (`/dominion:improve`): Matches the task type (fix, refactor, enhancement). Per mini-plan task from Architect's improvement plan. Standard summaries.

### TDD Discipline

TDD is the default execution pattern (Kent Beck's Red-Green-Refactor):

1. **Red**: Write a failing test that encodes the acceptance criterion. Run it. Confirm it fails for the expected reason (not a syntax error or import failure).
2. **Green**: Write the minimum code to make the test pass. No more. Resist the urge to generalize.
3. **Refactor**: With tests green, improve the code structure. Extract methods, rename for clarity, remove duplication. Run tests after each refactoring.

Exceptions:
- Pure refactoring tasks: existing tests serve as the safety net. No new tests needed unless coverage gaps are found.
- Quick mode: tests-after is acceptable when speed matters. Write them, but the order is relaxed.
- Infrastructure/config tasks: where executable tests are impractical, verify_command serves as the test.

## Worktree Setup

For each task in the wave:
```bash
git worktree add .worktrees/dominion-{task-id} -b dominion/{task-id}
```

Verify worktree creation succeeded. If it fails (branch already exists), offer to clean up stale worktrees.

## Agent Spawning

For each task, spawn a Developer agent with:
```bash
claude --agent developer --working-directory .worktrees/dominion-{task-id}
```

Provide the agent with a prompt containing:
1. Task details: id, title, description
2. File ownership: which files/directories the task may modify
3. Acceptance criteria: the verifiable done conditions
4. Verify command: the shell command to run for validation
5. Upstream handoff notes: from completed upstream tasks (if any)
6. Signal protocol: how to raise blockers/warnings
7. Knowledge refs: relevant `.dominion/knowledge/` files from plan.toml `knowledge_refs` (if any)

**All wave agents are spawned concurrently.** Do not wait for one to finish before starting the next.

## Monitoring

While agents are running:
1. Poll `.dominion/signals/` for new blocker or warning files
2. If a task-level blocker: note it, let other agents continue
3. If a wave-level blocker: halt all agents in the wave, present to user
4. If a phase-level blocker: halt everything, present to user

## Decision Recording

When the developer makes a significant decision during task work — architectural trade-offs, deviations from plan, technology choices — record it:

```bash
dominion-tools state decision --task {task-id} --text "{description}" --tags "{comma-separated tags}"
```

Not every decision. Only those that:
- Affect other tasks or downstream waves
- Deviate from the plan
- Involve trade-offs the user should know about

These surface during `/dominion:improve` retrospective for review.

## Deferred Items

When the developer encounters work that is out of scope for the current task — a bug in unrelated code, a refactoring opportunity, a missing feature — park it:

```bash
dominion-tools state defer --text "{description}"
```

These surface during the next `/dominion:discuss` session so the user can decide whether to address them.

## Wave Completion

When all agents in the wave have finished:

1. **Verify summaries**: check `.dominion/phases/{N}/summaries/task-{id}.md` exists for each task
2. **Run verify_command**: for each task with a verify_command, run it in the worktree
3. **Update progress**: run `dominion-tools wave status` to check and update task statuses (complete, failed, or blocked)

## Merge Protocol

For each completed task (in dependency order):
```bash
git merge --no-ff dominion/{task-id} -m "merge: task {task-id} — {title}"
```

- If merge conflict: **HALT**. Present the conflict to the user. Do NOT auto-resolve.
- After successful merge: record merge commit hash in progress.toml

## Worktree Cleanup

After all merges for the wave:
```bash
git worktree remove .worktrees/dominion-{task-id}
git branch -d dominion/{task-id}
```

## Inter-Wave Checkpoint

After wave cleanup, before starting the next wave:
1. Read all SUMMARY.md files from the completed wave
2. Extract gotchas from "Friction Encountered" and "Decisions Made" sections
3. Apply handoff notes to downstream tasks via `dominion-tools plan handoff`
4. Clean resolved signals from `.dominion/signals/`

## Failure Handling

If a task fails:
1. Mark as "failed" in progress.toml
2. Check downstream dependencies — mark dependent tasks as "blocked"
3. Present failure details to user with options:
   - **Retry**: re-spawn the agent for the failed task
   - **Skip**: mark as skipped, unblock dependents if safe
   - **Abort**: stop execution, preserve state for resume
