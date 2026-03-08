---
name: init
description: Analyze your project and generate a complete AI development methodology — agents, tools, conventions, CLI toolkit. Run this once to set up Dominion.
---

# /dominion:init

Generate a complete AI development methodology for this project.

<IMPORTANT>
This skill creates files in the project directory. Before starting:
1. Confirm you are in the correct project root directory
2. Check if .dominion/ already exists — if it does, warn the user:
   "Dominion is already initialized in this project. Re-running will overwrite existing config.
    For merging with existing setup, use /dominion:claim (available in v0.7).
    Continue? [Y/n]"
</IMPORTANT>

## Token Cost Estimate

Before starting, inform the user:
```
Dominion init will:
  - Analyze your project structure
  - Generate agent configs and instructions (8 agents)
  - Draft and walk through CLAUDE.md with you
  - Spawn a Developer agent to build dominion-tools CLI
  - Spawn a Tester agent to validate the CLI

  Estimated token usage: ~200K tokens
  Proceed? [Y/n]
```

## Step 1: Discovery

Follow `@references/discovery.md` to analyze the project.

Output: structured discovery results in conversation context.

## Step 2: Wizard

Based on discovery results, run the wizard:
- Default: `@references/wizard-quick.md`
- If user chooses "full setup": `@references/wizard-full.md`
- If user chooses "customize": selected sections from wizard-full.md

Output: user-approved configuration choices.

## Step 3: Generate Project Config

Create the `.dominion/` directory structure:

```bash
mkdir -p .dominion/agents
mkdir -p .dominion/specs
mkdir -p .dominion/knowledge
mkdir -p .dominion/signals
mkdir -p .dominion/phases
```

Generate these files from discovery results + wizard answers:
- `.dominion/dominion.toml` — from `@templates/schemas/dominion.toml`, filled with project data
- `.dominion/style.toml` — from `@templates/schemas/style.toml`, filled with convention choices
- `.dominion/roadmap.toml` — from `@templates/schemas/roadmap.toml`, filled with user's roadmap
- `.dominion/knowledge/index.toml` — minimal initial index (empty hot cache)

## Step 4: Generate Agents

Follow `@references/agent-generation.md`:
1. Customize agent TOMLs from templates → write to `.dominion/agents/`
2. Render agent .md files → write to `.claude/agents/`

## Step 5: Generate AGENTS.md

Follow `@references/agents-md-generation.md`:
- Read all `.dominion/agents/*.toml`
- Generate `AGENTS.md` at project root

## Step 6: Generate settings.json

Follow `@references/settings-generation.md`:
- Extend `.claude/settings.json` with Dominion permissions
- Configure serena project activation with detected LSPs

## Step 7: Generate Hooks

Follow `@references/hooks-generation.md`:
- Create hookify governance rules for source-diving prevention

## Step 8: Generate CLAUDE.md

Follow `@references/claude-md-generation.md`:
- Phase 1: Draft synthesis (ultrathink)
- Phase 2: Section-by-section walkthrough with user

## Step 9: CLI Proving Ground

Follow `@references/cli-spec-delivery.md`:
1. Copy cli-spec.toml to `.dominion/specs/`
2. Spawn Developer agent to implement dominion-tools
3. Spawn Tester agent to validate
4. Handle failures if any

## Step 10: Initialize State

Write `.dominion/state.toml`:
```toml
[meta]
schema_version = 1

[position]
phase = 0
step = "idle"
status = "ready"
last_session = "{today's date}"

[init]
completed_at = "{current ISO 8601 timestamp}"
cli_proven = {true if all CLI tests passed, false otherwise}
validate_passed = false
```

## Step 11: Validate

Run `/dominion:validate` to confirm everything is consistent.

If validate passes, update state.toml: `validate_passed = true`

## Step 12: Append .gitignore

If `.gitignore` exists, append:
```
# Dominion
.dominion/state.toml
.worktrees/
```

If `.gitignore` doesn't exist, create it with the above content.

## Step 13: Generate DOMINION.md

Generate `DOMINION.md` at project root from `@templates/dominion-md.md`:
1. Read `dominion.toml` — extract project info, direction, workflow config
2. Read `roadmap.toml` — extract milestone and phase summary
3. Read all `.dominion/agents/*.toml` — build agent roster table
4. Fill template placeholders
5. Write to `DOMINION.md` at project root

The Attendant maintains this file. It is regenerated when:
- Agent roster changes (`dominion-tools agents generate`)
- Improve step applies structural changes
- Roadmap phases are added or completed

## Step 14: Summary

Present to the user:
```
Dominion initialized successfully.

Generated:
  .dominion/          Project config, agent definitions, CLI spec
  .claude/agents/     8 agent instruction files
  .claude/settings.json  MCP permissions (extended)
  CLAUDE.md           Project instructions (you own this now)
  AGENTS.md           Agent roster (auto-generated)
  DOMINION.md           Project overview and Dominion cheatsheet
  dominion-tools/     CLI tool ({language}, {N} commands)

Validation: {PASS/FAIL with details}

Next steps:
  - Review CLAUDE.md and edit to taste
  - Commit all generated files to git
  - Start your first phase with /dominion:orchestrate (v0.2)
  - For quick tasks: /dominion:quick (v0.2)
  - To check your setup: /dominion:validate
```
