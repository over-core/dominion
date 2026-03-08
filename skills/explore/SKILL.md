---
name: explore
description: Researcher-driven codebase analysis for the current phase. Produces research.toml with findings, opportunities, and assumptions.
---

# /dominion:explore

Analyze the codebase in context of the current phase goals.

<IMPORTANT>
This skill requires an active phase. Check `.dominion/state.toml` — position.phase must be > 0.
If phase is 0, tell the user: "No active phase. Run /dominion:discuss first."
</IMPORTANT>

## Pre-check

1. Read `.dominion/state.toml` — get current phase number
2. Verify `.dominion/phases/{N}/` directory exists (create if needed via `dominion-tools phase init`)
3. If `.dominion/phases/{N}/research.toml` already exists, warn: "Research already exists for phase {N}. Re-running will overwrite. Continue? [Y/n]"

## Step 1: Codebase Analysis

Follow `@references/codebase-analysis.md`

## Step 2: Assumption Listing

Follow `@references/assumption-listing.md`

## Step 3: Assumption Verification

Follow `@references/assumption-verification.md`

## Step 3.5: Role Trigger Detection

Check for new specialized role opportunities:
1. Read `@data/detection/roles.toml` for all role triggers
2. Read `.dominion/agents/` to get currently active roles
3. Cross-reference: are there triggers firing for roles not yet activated?
4. For each new trigger found: record as a role proposal in research.toml `[[role_proposals]]`

```toml
[[role_proposals]]
role = ""                           # role name from roles.toml
trigger = ""                        # what triggered the detection
confidence = ""                     # high | medium | low
```

If no new triggers found: skip. This step is silent unless new roles are detected.

## Step 4: Write Research

Write `.dominion/phases/{N}/research.toml` using `@templates/schemas/research.toml` as the schema. Populate with findings, opportunities, and assumptions from Steps 1-3.

## Step 5: Present Summary

Display to the user:
```
Research Complete (Phase {N}):
  Findings: {high} high, {medium} medium, {low} low
  Opportunities: {count}
  Assumptions: {verified} verified, {unverified} unverified

High-severity findings:
  - {F1}: {title}
  - {F2}: {title}

Unverified assumptions:
  - {A1}: {text}
```

## Step 6: Update State

Update `.dominion/state.toml`:
- `position.step` = "explore"
- `position.status` = "complete"
- `position.last_session` = {today's date}
