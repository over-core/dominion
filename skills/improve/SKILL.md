---
name: improve
description: Unified improvement skill. Post-pipeline mode reviews phase outcomes and applies proposals. Ad-hoc mode captures knowledge, creates agents, skills, CLI commands, hooks, and config extensions.
---

# /dominion:improve

Improve the project's Dominion setup — from post-phase proposals to ad-hoc agent/skill creation.

<IMPORTANT>
This skill operates in two modes based on context:
- **Post-pipeline mode**: after a completed review step (phase context exists)
- **Ad-hoc mode**: standalone invocation for creating or modifying Dominion entities
</IMPORTANT>

## Flag Parsing

- `--agent`: create a new agent (ad-hoc mode, skip output routing)
- `--skill`: create a new skill (ad-hoc mode, skip output routing)
- `--from <source>`: import from external source (notion, confluence, obsidian, url, file path)
- No flags: context-detected (post-pipeline if phase context, ad-hoc otherwise)

## Context Detection

1. Read `.dominion/state.toml` — get current phase number and step
2. Check if post-pipeline context exists:
   - `position.step = "review"` AND
   - `.dominion/phases/{N}/review.toml` exists AND
   - `.dominion/phases/{N}/metrics.toml` exists
3. If all three: **post-pipeline mode**
4. Otherwise: **ad-hoc mode**

Exception: if `--agent`, `--skill`, or `--from` flags are present, always use **ad-hoc mode** regardless of context.

## Post-Pipeline Mode

### Pre-check

1. If `.dominion/improvements.toml` does not exist, create from `@templates/schemas/improvements.toml`

### Step 1: Phase Retrospective

Follow `@references/retrospective.md`

### Step 2: Proposal Review

Follow `@references/proposal-review.md`

### Step 3: Apply Accepted Proposals

Follow `@references/proposal-apply.md`

For structural proposals (new agents, new CLI commands, new skills):
- Read `@templates/references/structural-awareness.md` for creation steps
- Run Reviewer criticism before applying (same as ad-hoc Step 4)

### Step 4: Knowledge Management

Follow `@references/knowledge-management.md`

### Step 5: Update State and Announce

Update `.dominion/state.toml`:
- `position.step` = "improve"
- `position.status` = "complete"
- `position.last_session` = {today's date}

Run `dominion-tools knowledge sync` to rebuild MEMORY.md with any new knowledge entries.

If any structural changes were applied, run `dominion-tools doc generate` to regenerate DOMINION.md.

Announce:
```
Phase {N} fully complete.
  Proposals: {accepted} accepted, {rejected} rejected
  Knowledge: {new_entries} new entries, {demoted} demoted
  Metrics trend: {brief trend summary}

Next: /dominion:orchestrate to start the next phase.
```

## Ad-Hoc Mode

Follow `@references/ad-hoc-pipeline.md` — the 6-step pipeline:
1. Advisor captures intent
2. Researcher investigates overlap
3. Advisor designs proposal
4. Reviewer criticizes
5. Advisor presents final proposal
6. Attendant creates artifacts
