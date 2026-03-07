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
  - Install the dominion-cli tool

  Estimated token usage: ~100K tokens
  Proceed? [Y/n]
```

## Step 1: Discovery

Follow [discovery.md](../../templates/references/discovery.md) to analyze the project.

Output: structured discovery results in conversation context.

## Step 2: Wizard

Based on discovery results, run the wizard:
- Default: [wizard-quick.md](references/wizard-quick.md)
- If user chooses "full setup": [wizard-full.md](references/wizard-full.md)
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
- `.dominion/dominion.toml` — from [dominion.toml](../../templates/schemas/dominion.toml), filled with project data
- `.dominion/style.toml` — from [style.toml](../../templates/schemas/style.toml), filled with convention choices
- `.dominion/roadmap.toml` — from [roadmap.toml](../../templates/schemas/roadmap.toml), filled with user's roadmap
- `.dominion/knowledge/index.toml` — minimal initial index (empty hot cache)

## Step 4: Generate Agents

Follow [agent-generation.md](../../templates/references/agent-generation.md):
1. Customize agent TOMLs from templates → write to `.dominion/agents/`
2. Render agent .md files → write to `.claude/agents/`

## Step 5: Generate AGENTS.md

Follow [agents-md-generation.md](../../templates/references/agents-md-generation.md):
- Read all `.dominion/agents/*.toml`
- Generate `AGENTS.md` at project root

## Step 6: Generate settings.json

Follow [settings-generation.md](../../templates/references/settings-generation.md):
- Extend `.claude/settings.json` with Dominion permissions
- Configure serena project activation with detected LSPs

## Step 7: Generate Hooks

Follow [hooks-generation.md](../../templates/references/hooks-generation.md):
- Create hookify governance rules for source-diving prevention

## Step 8: Generate CLAUDE.md

Follow [claude-md-generation.md](references/claude-md-generation.md):
- Phase 1: Draft synthesis (ultrathink)
- Phase 2: Section-by-section walkthrough with user

## Verification Gates

After each generation step, verify expected files exist. Fail loudly if missing.

### After Step 3 (Project Config):
- Glob: `.dominion/dominion.toml`, `.dominion/style.toml`, `.dominion/roadmap.toml`, `.dominion/knowledge/index.toml`
- Read each file, verify TOML parses: `python3 -c "import tomllib; tomllib.load(open('{file}','rb'))"`
- FAIL if any missing or unparseable. Do not proceed to Step 4.

### After Step 4 (Agents):
- Glob: `.dominion/agents/*.toml` — expect at least 8 files (core agents)
- Glob: `.claude/agents/*.md` — expect matching count
- Verify each TOML parses.
- FAIL if count mismatch or any unparseable.

### After Step 6 (settings.json):
- Read `.claude/settings.json`, verify JSON parses.
- Check it contains `dominion-cli` in allowed tools.
- FAIL if missing or malformed.

### After Step 7 (Hooks):
- Glob: `.claude/hookify.*.local.md` — expect 4 files
- Read each, verify YAML frontmatter has `event:` field
- FAIL if fewer than 4 or any malformed.

### After Step 9 (CLI):
- Run `dominion-cli --version` — verify exit code 0 and version matches
- FAIL if command not found or version mismatch.

## Step 9: Install CLI

Follow [cli-installation.md](../../templates/references/cli-installation.md):
1. Determine the plugin root directory (derive from this skill's base directory — strip `/skills/init` from the path shown in the system message when this skill loaded)
2. Check uv is available
3. Install dominion-cli from plugin distribution
4. Verify version and smoke test
5. Copy cli-spec.toml to .dominion/specs/

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
cli_installed = true
cli_version = "0.9.1"
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

Generate `DOMINION.md` at project root from [dominion-md.md](../../templates/dominion-md.md):
1. Read `dominion.toml` — extract project info, direction, workflow config
2. Read `roadmap.toml` — extract milestone and phase summary
3. Read all `.dominion/agents/*.toml` — build agent roster table
4. Fill template placeholders
5. Write to `DOMINION.md` at project root

The Secretary maintains this file. It is regenerated when:
- Agent roster changes (`dominion-cli agents generate`)
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
  dominion-cli        Installed via uv tool ({version}, {N} commands)

Validation: {PASS/FAIL with details}

Next steps:
  - Review CLAUDE.md and edit to taste
  - Commit all generated files to git
  - Start your first phase with /dominion:orchestrate (v0.2)
  - For quick tasks: /dominion:quick (v0.2)
  - To check your setup: /dominion:validate
```
