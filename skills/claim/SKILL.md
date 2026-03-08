---
name: claim
description: Merge Dominion into a project with an existing Claude Code setup. Detects, preserves, and extends what's already configured.
---

# /dominion:claim

Merge Dominion into a project with an existing Claude Code setup.

<IMPORTANT>
This skill preserves existing work. It never deletes user-written rules, hooks, or agent configs.
If `.dominion/` already exists, warn:
  "Dominion is already initialized. Re-running claim will re-analyze and merge.
   Continue? [Y/n]"
</IMPORTANT>

## Token Cost Estimate

Before starting, inform the user:
```
Dominion claim will:
  - Inventory your existing Claude Code setup
  - Analyze each artifact for structure and conventions
  - Detect conflicts with Dominion's methodology
  - Present a merge plan for your approval
  - Generate .dominion/ structure alongside existing config

  Estimated token usage: ~250K tokens
  Proceed? [Y/n]
```

## Phase 1: Inventory

Follow `@references/inventory.md` to scan all existing Claude Code artifacts.

Output: structured inventory of what exists and what's missing.

## Phase 2: Analysis

Follow `@references/analysis.md` to parse and understand each found artifact.

Output: per-artifact structure analysis in conversation context.

## Phase 3: Conflict Detection

Follow `@references/conflict-detection.md` to identify overlaps, conflicts, and gaps.

Output: categorized list — compatible (merge), conflicting (user decides), missing (Dominion adds).

## Phase 4: Claim Plan

Follow `@references/claim-plan.md` to present the merge plan.

Output: user-approved plan with per-artifact decisions.

## Phase 5: Execution

Follow `@references/execution.md` to apply the approved plan.

This phase:
1. Creates `.dominion/` directory structure
2. Generates TOML configs from existing artifacts
3. Merges CLAUDE.md (Dominion sections alongside existing)
4. Updates settings.json (extend, never replace)
5. Adds lifecycle hooks alongside existing hooks
6. Records provenance in `dominion.toml [claim]`
7. Runs the reduced wizard for sections that need user input

## Post-Claim: Validate

Run `/dominion:validate` to confirm everything is consistent.

## Post-Claim: Gitignore

Same as init Step 12 — append `.dominion/state.toml` and `.worktrees/` to `.gitignore`.

## Summary

Present to the user:
```
Dominion claim complete.

Preserved:
  {list of preserved artifacts with section counts}

Added:
  .dominion/          Project config, agent definitions
  .claude/agents/     {N} agent instruction files (merged with {M} existing)
  AGENTS.md           Agent roster

Conflicts resolved:
  {list of user decisions}

Validation: {PASS/FAIL with details}

Next steps:
  - Review merged CLAUDE.md
  - Commit all changes to git
  - Start your first phase with /dominion:orchestrate
```
