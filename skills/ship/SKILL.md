---
name: ship
description: Fully automated ship workflow — sync, test, commit, push, create PR with pipeline-aware body
---

# /dominion:ship

User says `/dominion:ship`, next thing they see is the PR URL.

Fully automated by default. Only stop for merge conflicts, test failures, or items needing human judgment.

## Mode Detection

Read `.dominion/state.toml` for completed phases → check `phases/*/review/output/verdict.toml` for go/go-with-warnings verdict.

- **Pipeline mode**: completed phase with passing review → rich PR body from artifacts
- **Manual mode**: no pipeline artifacts → basic PR body from git diff + commit log

## Steps

### 0. Detect base branch
`gh pr view --json baseRefName 2>/dev/null` → `gh repo view --json defaultBranchRef` → fallback `main`

### 1. Pre-flight
- Verify not on base branch
- `git status` — check for uncommitted changes
- `git diff --stat {base}...HEAD` — diff stats
- Pipeline mode detection

### 2. Sync base
```bash
git fetch origin && git merge origin/{base}
```
Auto-resolve simple conflicts. STOP on complex conflicts.

### 3. Run tests
Detect test command from config.toml `[project].test_command` or CLAUDE.md.
Run full suite. **STOP on failure.** Paste output.

### 4. Pre-ship review
Auto-fix:
- `console.log` / `print()` / `debugger` in production code → remove
- Trailing whitespace → trim
- Commented-out code blocks (>3 lines) → remove

Flag (ASK user):
- TODO/FIXME/HACK in NEW code
- Potential secrets (API keys, tokens)
- Files >500 lines without tests

### 5. Commit strategy
Bisectable commits from any uncommitted changes. Logical grouping.

### 6. Verification gate
**IRON LAW: NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION.**
If ANY code changed after step 3: re-run tests. Paste output.

### 7. Push
```bash
git push -u origin {branch}
```

### 8. Create PR
Platform-aware from config.toml `[project].git_platform`:
- github: `gh pr create`
- gitlab: `glab mr create`
- other: output manual instructions

### 9. PR Body

**Pipeline mode** (rich body from artifacts):
```markdown
## Intent
{from phases/NN/CLAUDE.md}

## What Was Done
{from plan + task summaries}

### Tasks
- [x] Task 01: {title} — {one-line summary}

## Key Decisions
{from state.toml [[decisions]] for this phase}

## Review: {verdict}
{from review/output/summary.md}

## Metrics
Files changed: N | Lines: +X / -Y | Tests added: Z

## Test Results
All tests pass: {N} tests, 0 failures
```

**Manual mode** (basic body):
```markdown
## Summary
{from git log --oneline {base}..HEAD}

## Test Results
{test output}
```

### 10. Output
Print PR URL + status: DONE / DONE_WITH_CONCERNS / BLOCKED
