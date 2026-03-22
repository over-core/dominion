# Interview

Adaptive preference gathering based on project state. Uses a 4-phase flow: silent detection (already done) → present & confirm → ask preferences → generate.

Every question asked must produce data that agents consume. Delivery mechanisms:
- **CLAUDE.md** — read by Claude Code at session start, every agent sees it natively
- **config.toml** — read by MCP prepare tools, injected into agent briefs
- **Knowledge** — injected into agent briefs via prepare_step/prepare_task

## Mode Selection

Determine interview mode from detection results:

1. **Greenfield** (no `.dominion/`, no `.claude/`, no `CLAUDE.md`): full 4-phase flow
2. **Brownfield** (existing Claude Code setup but no `.dominion/`): present detected + existing values, ask for confirmation, fill gaps
3. **Re-onboard** (`.dominion/` exists but no MCP wiring): read existing dominion.toml, confirm values, generate MCP artifacts only

## Greenfield Interview

### Phase 2: Present & Confirm

Detection (Phase 1) has already run. Present all detected values in a single confirmation screen:

```
DEVELOPMENT ENVIRONMENT
  Language:        {detected primary language} ({version if detected})
  Package Manager: {dev_profile.name} ({dev_profile.install}, {dev_profile.add}, {dev_profile.run})
  Build System:    {detected build system}
  Frameworks:      {detected frameworks, comma-separated}
  Quality:         {detected formatters}, {detected linters}, {detected test runners}

SAFETY RULES (auto-generated from {language}/{dev_profile.name} profile)
  Use `{dev_profile.install}` for installs, `{dev_profile.add}` for new deps
  NEVER: {dev_profile.prohibited, comma-separated}
  {if dev_profile.venv_required: "Virtual environment required at {dev_profile.venv_path}"}

GIT WORKFLOW (detected from git history)
  Commit format:   {git_workflow.commit_format}
  Branch strategy: {git_workflow.branching}
  Merge strategy:  {git_workflow.merge_strategy}

Is this correct? [Y / edit]
```

If **Y**: accept all detected values, use dev profile safety rules as-is. Continue to Phase 3.
If **edit**: ask targeted questions ONLY for sections the user wants to change. Do NOT re-ask everything.

For polyglot projects, show one block per language with its dev profile.

### Phase 3: Preferences

Ask ONLY questions whose answers cannot be detected from the codebase. Present as a focused sequence — one question at a time. Every answer has a defined delivery path to agents.

#### Question 1: Project Identity

Ask: "Describe this project and who uses it, in 1-2 sentences."

→ Delivery: CLAUDE.md `## Project` section (vision + users)

#### Question 2: Direction

Ask: "What's the project's current direction?"
- **Maintain** — codebase is good, preserve existing patterns
- **Improve** — mostly good, improve incrementally
- **Restructure** — significant restructuring planned

If improve or restructure:
- "What specifically needs work? Describe the pain points, weak areas, or things you'd change." → knowledge entry `project-direction.md`

If restructure (additional):
- "Describe the target state" → config.toml `[direction].target_state`
- "Migration strategy?" → strangler-fig / big-bang / incremental → config.toml `[direction].migration_strategy`

→ Delivery: CLAUDE.md `## Direction` one-liner + config.toml `[direction]` + knowledge entry with full detail (improve and restructure)

#### Question 3: Testing

Ask: "TDD? [Y/n]" (default Y if test files detected, otherwise ask)

→ Delivery: config.toml `[style].testing` → prepare.py → agent briefs (already works)

#### Question 4: Experience Level

Ask: "Your experience level with this codebase?" → beginner / intermediate / advanced
- **beginner**: agents explain decisions, show examples
- **intermediate**: balanced detail (default)
- **advanced**: agents are terse, skip obvious explanations

→ Delivery: CLAUDE.md `## Experience Level` section

#### Taste (optional)

Ask:
1. "Things you want agents to ALWAYS do?"
2. "Things you want agents to NEVER do?"

→ Delivery: CLAUDE.md `## Conventions` section (merged with auto-detected conventions)

## Brownfield Interview

For projects with existing Claude Code setup:

1. Read `CLAUDE.md` — extract project description, conventions, constraints
2. Read `.claude/settings.local.json` — extract existing permissions and hooks
3. Read `.claude/agents/*.md` — list existing agents
4. Read `.mcp.json` — list existing MCP servers

Present extracted values alongside detected dev profile:
```
Detected from existing setup:
  Project:     {from CLAUDE.md}
  Agents:      {count} existing ({names})
  MCPs:        {list from .mcp.json}
  Permissions: {count} rules in settings.local.json
  Hooks:       {count} configured

Dev profile:   {dev_profile.name} — safety rules auto-derived

Dominion will:
  - Create .dominion/ alongside your existing setup
  - Extend (never replace) settings.local.json
  - Add MCP server entry to .mcp.json
  - Generate thin agent dispatchers in AGENTS.md
  - Preserve all existing agents, hooks, and permissions
  - Add auto-derived safety rules from dev profile

Confirm? [Y / customize]
```

If **customize**: run Phase 3 questions for sections where user wants changes.
If **Y**: use detected values, fill gaps with defaults.

## Re-onboard Interview

For projects with `.dominion/` but no MCP wiring:

1. Read `dominion.toml` — show current config
2. Ask: "Upgrading to MCP architecture. Your existing .dominion/ config will be preserved. Proceed? [Y/n]"
3. If Y: skip to generation phase — only generate .mcp.json, update AGENTS.md format, update settings.local.json

## Output

Store all answers as structured data in conversation context for the generation phase:
- `project_identity`: vision + users (one combined answer)
- `direction`: mode + restructure details if applicable
- `dev_profiles`: matched package manager profiles (from detection)
- `git_workflow`: commit_format, branching, merge_strategy (confirmed in Phase 2)
- `testing`: tdd | test-after
- `experience_level`: beginner / intermediate / advanced
- `taste`: dos, donts
- `brownfield_artifacts`: list of existing files to preserve
