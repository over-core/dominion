---
name: test
description: Tester-driven acceptance validation and coverage gap analysis. Produces test-report.toml with criteria results and identified gaps.
---

# /dominion:test

Validate acceptance criteria and identify test coverage gaps.

<IMPORTANT>
This skill requires execution to be complete. Check `.dominion/state.toml` — position.step should be "execute" with status "complete".
Check `.dominion/phases/{N}/progress.toml` exists. If not, tell the user: "Run /dominion:execute first."
</IMPORTANT>

## Pre-check

1. Read `.dominion/state.toml` — get current phase number
2. Verify `.dominion/phases/{N}/progress.toml` and `.dominion/phases/{N}/plan.toml` exist
3. If `.dominion/phases/{N}/test-report.toml` already exists, warn: "Test report already exists for phase {N}. Re-running will overwrite. Continue? [Y/n]"

## Step 1: Acceptance Validation

Follow `@references/acceptance-validation.md`

## Step 2: Gap Analysis

Follow `@references/gap-analysis.md`

## Step 3: Write Test Report

Write `.dominion/phases/{N}/test-report.toml` using `@templates/schemas/test-report.toml` as the schema. Populate with criteria results and gaps from Steps 1-2.

## Step 4: Present Report

Display to the user:
```
Test Report (Phase {N}):
  Acceptance Criteria: {passed}/{total} passed
  Test Suite: {passed}/{run} tests passed
  Coverage Delta: {delta}

Failed criteria:
  - Task {id}: {criterion} — {evidence}

Gaps ({count}):
  - {G1}: {description} [{severity}]
```

## Step 5: Update State

Update `.dominion/state.toml`:
- `position.step` = "test"
- `position.status` = "complete"
- `position.last_session` = {today's date}
