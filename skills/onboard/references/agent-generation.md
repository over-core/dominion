# Agent Generation

## Step 1: Customize Agent TOMLs

For each agent template in [agents/](../agents/):

1. Read the template
2. Replace placeholder values (`{{...}}`) with discovery results:
   - `{{required_mcps}}` — MCPs marked required for this agent's affinity (from registry)
   - `{{optional_mcps}}` — MCPs marked optional/recommended for this agent's affinity
   - `{{fallback_chain}}` — documentation sources from dominion.toml [documentation.sources], ordered by priority
   - `{{pre_commit_commands}}` — from style.toml per-language pre_commit arrays
   - `{{file_ownership}}` — empty for now (populated by Architect during planning)
   - `{{hard_stops}}` — from dominion.toml [project.constraints.hard_rules] + defaults
   - `{{testing_styles}}` — detected from test frameworks (property-based if proptest/hypothesis found, e2e if playwright/cypress found, etc.)
   - `{{security_scope}}` — language-specific security concerns (from security-auditor.toml template)
3. Write customized TOML to `.dominion/agents/{role}/agent.toml`

## Step 2: Deploy Methodology Sections

For each agent, copy methodology .md files flat into the agent's runtime directory from two sources:

1. **Shared sections** from `templates/agents/_shared/`:
   ```
   templates/agents/_shared/*.md → .dominion/agents/{role}/*.md
   ```
   Conditional: only copy `tools-exa.md` if exa detected, `specialist-security.md` if security-auditor active, `tools-serena.md` if serena detected.

2. **Role-specific sections** from the agent's template directory:
   ```
   templates/agents/{role}/*.md → .dominion/agents/{role}/*.md
   ```
   Conditional: only copy `lang-python.md`, `lang-typescript.md` if that language was detected.

### Verification

For each `.dominion/agents/{role}/agent.toml`, read its `[[methodology.sections]]` entries. For each entry with `always_include = true`, verify the referenced section file exists in `.dominion/agents/{role}/`. Warn (don't fail) for conditional sections whose conditions may not apply.

## Step 3: Render Agent .md Files

For each customized `.dominion/agents/{role}/agent.toml`, generate a thin stub pointing to MCP:

```markdown
<!-- Dominion agent: {role} -->
# {name}

You are a Dominion agent. Call `mcp__dominion__agent_start(role: "{role}")` with the phase_id from your task prompt. Follow the returned methodology exactly. Submit your work via `mcp__dominion__agent_submit()` when complete.
```

Same 3-line pattern for ALL 17 agents. No methodology, no tool routing, no governance in the .md file. The MCP server serves conditional methodology dynamically via `agent_start` based on project context, active tools, and phase type.

Write each rendered .md to `.claude/agents/{role}.md`.

## Post-Generation Verification

After generating all agent files:

### TOML Verification
For each `.dominion/agents/{role}/agent.toml`:
1. TOML parses without error
2. `[governance]` section exists with non-empty `hard_stops` array
3. `[methodology]` section exists with at least one `[[methodology.sections]]` entry
4. `[tools.mcps]` section exists
5. `[tools.mcp]` section exists with `dominion` key
6. `[workflow]` section exists with non-empty `produces` field

### Section Verification
For each `.dominion/agents/{role}/`:
7. Directory exists
8. `core.md` exists (always_include)
9. `output-format.md` exists (always_include)

### Agent .md Verification
For each `.claude/agents/{role}.md`:
10. File contains "Dominion agent" in first 100 characters
11. File contains `mcp__dominion__agent_start`
12. File contains `mcp__dominion__agent_submit`

FAIL if any check fails. List specific agents and missing fields. Do not proceed to AGENTS.md generation until all checks pass.
