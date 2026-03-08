---
name: review
description: Reviewer-driven post-phase quality assessment. Produces review.toml with code quality, architecture, and cross-task findings.
---

# /dominion:review

Post-phase quality assessment across all phase changes.

<IMPORTANT>
This skill requires test-report.toml for the current phase.
Check `.dominion/phases/{N}/test-report.toml` exists. If not, tell the user: "Run /dominion:test first."
</IMPORTANT>

## Pre-check

1. Read `.dominion/state.toml` — get current phase number
2. Verify `.dominion/phases/{N}/test-report.toml` exists
3. If `.dominion/phases/{N}/review.toml` already exists, warn: "Review already exists for phase {N}. Re-running will overwrite. Continue? [Y/n]"

## Step 1: Code Quality Review

Follow `@references/code-quality.md`

## Step 2: Architecture Check

Follow `@references/architecture-check.md`

## Step 3: Cross-Task Review

Follow `@references/cross-task-review.md`

## Step 4: Write Review

Write `.dominion/phases/{N}/review.toml` using `@templates/schemas/review.toml` as the schema. Populate with findings from Steps 1-3.

Note: v0.2 produces findings only. The `[[proposals]]` section is deferred to v0.4.

## Step 5: Present Review

Display to the user:
```
Review Complete (Phase {N}):
  Findings: {high} high, {medium} medium, {low} low, {info} info

High-severity findings:
  - {R1}: {title} — {suggestion}
  - {R2}: {title} — {suggestion}

Categories:
  Code quality: {count}
  Architecture: {count}
  Cross-task: {count}
```

## Step 6: Update State and Announce

Update `.dominion/state.toml`:
- `position.step` = "review"
- `position.status` = "complete"
- `position.last_session` = {today's date}

Announce: "Phase {N} is complete. Review the findings above. To start the next phase, run /dominion:orchestrate or /dominion:discuss."
