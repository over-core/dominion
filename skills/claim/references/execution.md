# Claim Execution

Apply the approved claim plan. Generate Dominion artifacts alongside existing setup.

## Execution Order

### 1. Create Directory Structure

```bash
mkdir -p .dominion/agents
mkdir -p .dominion/specs
mkdir -p .dominion/knowledge
mkdir -p .dominion/signals
mkdir -p .dominion/phases
```

### 2. Generate dominion.toml

From `@templates/schemas/dominion.toml`, filled with:
- Project data from discovery results
- Direction from wizard answers
- Claim provenance section recording what was preserved vs added

```toml
[claim]
claimed_at = "{current ISO 8601 timestamp}"
source_setup = "{detected: claude-code-native | gsd | conductor | custom}"

[[claim.preserved]]
artifact = "CLAUDE.md"
sections = ["Project", "Git Conventions", ...]  # user-written section names
policy = "never-overwrite"
```

Add one `[[claim.preserved]]` entry for each preserved artifact.
Add one `[[claim.added]]` entry for each Dominion-generated artifact.

### 3. Generate Agent TOMLs

For each Dominion core agent (8 agents):
- Read template from `@templates/agents/{role}.toml`
- Customize with project-specific data from discovery
- Write to `.dominion/agents/{role}.toml`

For existing agents that map to Dominion roles:
- Merge existing instructions into the TOML's freeform sections
- Preserve any custom tools, MCPs, or governance rules

For existing agents that don't map to Dominion roles:
- Create a TOML config that preserves their existing instructions
- Mark as `source = "claimed"` in the TOML

### 4. Generate Agent .md Files

Follow `@skills/init/references/agent-generation.md`:
- Render agent .md files from TOML configs
- For claimed agents: merge existing .md content into freeform sections

### 5. Merge CLAUDE.md

Read existing CLAUDE.md. Identify Dominion sections to add.
For each Dominion section:
- If no existing section covers this topic → append
- If an existing section partially covers it → merge (keep user content, add Dominion additions)
- Never remove or rewrite user-written content

Present the merged CLAUDE.md as a diff for final approval before writing.

### 6. Update settings.json

Follow `@skills/init/references/settings-generation.md`:
- Read existing settings.json
- Add Dominion MCP permissions (extend, never remove existing)
- Add Dominion CLI tool permission: `Bash(dominion-tools *)`

### 7. Add Lifecycle Hooks

Follow `@skills/init/references/hooks-generation.md`:
- Add Dominion hooks alongside existing hooks
- Do not modify or remove existing hookify rules

### 8. Generate Remaining Artifacts

- `.dominion/style.toml` — from wizard answers + detected conventions
- `.dominion/roadmap.toml` — from wizard answers
- `.dominion/state.toml` — initial state (same as init Step 10)
- `.dominion/knowledge/index.toml` — minimal initial index
- `.dominion/specs/cli-spec.toml` — copy from plugin templates
- `AGENTS.md` — follow `@skills/init/references/agents-md-generation.md`

### 9. CLI Proving Ground

Follow `@skills/init/references/cli-spec-delivery.md`:
- If existing CLI tool detected: register it and extend with Dominion commands
- If no existing CLI: spawn Developer + Tester as in normal init

### 10. Idempotency

If `.dominion/` already exists (re-running claim):
- Read existing `dominion.toml [claim]` section
- Compare against current inventory
- Only apply changes for new/modified artifacts
- Preserve all existing provenance records
- Add new provenance records for newly claimed artifacts
