# Claim Inventory

Scan for all existing Claude Code artifacts. Record what exists and what doesn't.

## Artifact Checklist

Check each of these and record: exists (yes/no), size, last modified.

### Core Files

1. `CLAUDE.md` — read and record section headings (lines starting with `#` or `##`)
2. `AGENTS.md` — read and record listed agents
3. `.claude/settings.json` — read and record MCP permissions, tool allow-lists
4. `.claude/settings.local.json` — check existence (user-local overrides)

### Agent Files

5. Glob `.claude/agents/*.md` — list all agent files, read each and record:
   - Agent name (from filename or first heading)
   - Purpose (from description or first paragraph)
   - Model mentioned (if any)
   - Tools/MCPs referenced

### Hooks

6. Glob `.claude/hooks/*.md` or check `.claude/hooks/` directory
   - List all hook files
   - Record trigger events and rule descriptions

### Git Hooks

7. Check `.githooks/` — list all hook scripts
8. Check `.pre-commit-config.yaml`, `.husky/`, `lefthook.yml`
9. Check git config for `core.hooksPath`

### Plugins

10. Check for plugin artifacts:
    - `.gsd/` or `.planning/` → GSD plugin
    - `.conductor/` → Conductor plugin
    - Other `.claude/` directories that suggest plugins

### MCPs

11. Detect currently available MCPs by checking which `mcp__*` tools are loaded
12. Read `.claude/settings.json` for configured MCP permissions
13. Cross-reference against `@registry/registry.toml`

### Project Analysis

14. Run the same project analysis as init discovery ([discovery.md](../../../templates/references/discovery.md) Phases 1-8)
    - Languages, frameworks, infrastructure, git workflow, style sampling
    - This provides the data needed for the reduced wizard

## Output

Organize as structured data:

- `existing_artifacts`: list with path, exists, size, last_modified
- `existing_agents`: list with name, purpose, model, tools
- `existing_hooks`: list with trigger, description
- `existing_plugins`: list with name, detected_by
- `existing_mcps`: list with name, configured_permissions
- `discovery_results`: same structure as init discovery output
