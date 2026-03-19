# Interview

Adaptive preference gathering based on project state. Uses a 4-phase flow: silent detection (already done) → present & confirm → ask preferences → generate.

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

Ask ONLY questions whose answers cannot be detected from the codebase. Present as a focused sequence — one question at a time.

#### Question 1: Project Identity

Ask:
1. "What's this project? One sentence." → dominion.toml [project.vision]
2. "Who uses it?" → dominion.toml [project.target_users]
3. "Team size?" → options: solo + AI / small team (2-5) / larger team

#### Question 2: Direction

Ask:
1. "What's the project's current state?"
   - **Maintain** — codebase is good, preserve existing patterns
   - **Improve** — mostly good, improve incrementally
   - **Restructure** — significant restructuring planned

If restructure:
2. "Describe the target state" → dominion.toml [direction.restructure.target_state]
3. "Migration strategy?" → strangler-fig / big-bang / incremental

#### Question 3: Testing Style

Ask:
1. "Testing approach?" → TDD / test-after / both
2. "Code review?" → all changes / major only / agents review (default for solo: agents review)

#### Question 4: ADRs

Ask:
1. "Record Architecture Decision Records? [Y/n]" (default: Y)
2. If Y: "Location? [docs/adr]" → allow custom path

#### Question 5: Autonomy

Ask:
1. "Enable auto mode for unattended pipeline runs? [Y/n]" (default: Y)
2. If Y: "Max tokens per task? [150000]" → override default

#### Question 6: Roadmap

Ask:
1. "What's the first milestone?" → roadmap.toml
2. "Rough phases to get there?" → roadmap.toml phases
3. "Success criteria?" → dominion.toml [project.success_criteria]

#### Question 7: Experience Level

Ask:
1. "Your experience level with this codebase?" → options: beginner / intermediate / advanced
   - **beginner**: new to the language or codebase — agents explain more, show examples
   - **intermediate**: comfortable but not expert — balanced detail (default)
   - **advanced**: deep expertise — agents are terse, skip obvious explanations

Store in: user-profile.toml `[user].experience_level`

#### Taste (optional)

Ask:
1. "Things you want agents to ALWAYS do?" → style.toml [taste.dos]
2. "Things you want agents to NEVER do?" → style.toml [taste.donts]

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
- `project_identity`: vision, target_users, team_size
- `direction`: mode, restructure details if applicable
- `dev_profiles`: matched package manager profiles (from detection)
- `git_workflow`: commit_format, branching, merge_strategy (confirmed in Phase 2)
- `testing`: style, review_process
- `adrs`: enabled, path
- `autonomy`: enabled, max_tokens_per_task
- `roadmap`: milestone, phases, success_criteria
- `experience_level`: beginner / intermediate / advanced
- `taste`: dos, donts
- `brownfield_artifacts`: list of existing files to preserve
