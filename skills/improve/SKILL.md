---
name: improve
description: Phase retrospective, improvement proposal review, and accepted proposal application. The learning step that closes the pipeline loop.
---

# /dominion:improve

Review phase outcomes, present improvement proposals, and apply accepted changes.

<IMPORTANT>
This skill requires review.toml and metrics.toml for the current phase.
Check `.dominion/phases/{N}/review.toml` and `.dominion/phases/{N}/metrics.toml` exist.
If not, tell the user: "Run /dominion:review first."
</IMPORTANT>

## Pre-check

1. Read `.dominion/state.toml` — get current phase number
2. Verify `.dominion/phases/{N}/review.toml` exists
3. Verify `.dominion/phases/{N}/metrics.toml` exists
4. If `.dominion/improvements.toml` does not exist, create from `@templates/schemas/improvements.toml`

## Step 1: Phase Retrospective

Follow `@references/retrospective.md`

## Step 2: Proposal Review

Follow `@references/proposal-review.md`

## Step 3: Apply Accepted Proposals

Follow `@references/proposal-apply.md`

## Step 4: Knowledge Management

Follow `@references/knowledge-management.md`

## Step 5: Update State and Announce

Update `.dominion/state.toml`:
- `position.step` = "improve"
- `position.status` = "complete"
- `position.last_session` = {today's date}

Run `dominion-tools knowledge sync` to rebuild MEMORY.md with any new knowledge entries.

Announce:
```
Phase {N} fully complete.
  Proposals: {accepted} accepted, {rejected} rejected
  Knowledge: {new_entries} new entries, {demoted} demoted
  Metrics trend: {brief trend summary}

Next: /dominion:orchestrate to start the next phase.
```
