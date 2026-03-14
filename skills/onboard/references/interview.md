# Interview

Adaptive preference gathering based on project state.

## Mode Selection

Determine interview mode from detection results:

1. **Greenfield** (no `.dominion/`, no `.claude/`, no `CLAUDE.md`): full interview — ask all preference questions
2. **Brownfield** (existing Claude Code setup but no `.dominion/`): show detected values from existing config, ask for confirmation, fill gaps
3. **Re-onboard** (`.dominion/` exists but no MCP wiring): read existing dominion.toml, confirm values, generate MCP artifacts only

## Greenfield Interview

### Question 1: Project Identity

Ask:
1. "What's this project? One sentence." → dominion.toml [project.vision]
2. "Who uses it?" → dominion.toml [project.target_users]
3. "Team size?" → options: solo + AI / small team (2-5) / larger team

### Question 2: Direction

Ask:
1. "What's the project's current state?"
   - **Maintain** — codebase is good, preserve existing patterns
   - **Improve** — mostly good, improve incrementally
   - **Restructure** — significant restructuring planned

If restructure:
2. "Describe the target state" → dominion.toml [direction.restructure.target_state]
3. "Migration strategy?" → strangler-fig / big-bang / incremental

### Question 3: Git Workflow

Present detected values as defaults. Ask to confirm or change:
1. "Commit format?" → conventional commits / ticket-prefixed / free-form (default: detected)
2. "Branching strategy?" → trunk-based / github-flow / gitflow (default: detected)
3. "Merge strategy?" → squash / rebase / merge commits (default: detected)
4. "Include AI co-author trailers? [Y/n]" → dominion.toml [workflow.ai_co_author]

### Question 4: Testing Style

Ask:
1. "Testing approach?" → TDD / test-after / minimal / none-yet
2. "Code review?" → all changes / major only / agents review (default for solo: agents review)

### Question 5: ADRs

Ask:
1. "Record Architecture Decision Records? [Y/n]" (default: Y)
2. If Y: "Location? [docs/adr]" → allow custom path

### Question 6: Autonomy

Ask:
1. "Enable auto mode for unattended pipeline runs? [Y/n]" (default: Y)
2. If Y: "Max tokens per task? [150000]" → override default

### Question 7: Roadmap

Ask:
1. "What's the first milestone?" → roadmap.toml
2. "Rough phases to get there?" → roadmap.toml phases
3. "Success criteria?" → dominion.toml [project.success_criteria]

### Taste (optional)

Ask:
1. "Things you want agents to ALWAYS do?" → style.toml [taste.dos]
2. "Things you want agents to NEVER do?" → style.toml [taste.donts]

## Brownfield Interview

For projects with existing Claude Code setup:

1. Read `CLAUDE.md` — extract project description, conventions, constraints
2. Read `.claude/settings.local.json` — extract existing permissions and hooks
3. Read `.claude/agents/*.md` — list existing agents
4. Read `.mcp.json` — list existing MCP servers

Present extracted values:
```
Detected from existing setup:
  Project:     {from CLAUDE.md}
  Agents:      {count} existing ({names})
  MCPs:        {list from .mcp.json}
  Permissions: {count} rules in settings.local.json
  Hooks:       {count} configured

Dominion will:
  - Create .dominion/ alongside your existing setup
  - Extend (never replace) settings.local.json
  - Add MCP server entry to .mcp.json
  - Generate thin agent dispatchers in AGENTS.md
  - Preserve all existing agents, hooks, and permissions

Confirm? [Y / customize]
```

If **customize**: run greenfield questions for sections where user wants changes.
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
- `git_workflow`: commit_format, branching, merge_strategy, ai_co_author
- `testing`: style, review_process
- `adrs`: enabled, path
- `autonomy`: enabled, max_tokens_per_task
- `roadmap`: milestone, phases, success_criteria
- `taste`: dos, donts
- `brownfield_artifacts`: list of existing files to preserve
