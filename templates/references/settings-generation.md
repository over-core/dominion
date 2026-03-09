# settings.json Generation

Extend (never replace) `.claude/settings.json` with Dominion permissions.

## Read Existing

If `.claude/settings.json` exists, read it and preserve all existing entries.
If it doesn't exist, create it.

## Core Permissions

Always add:
```json
{
  "permissions": {
    "allow": [
      "Bash(dominion-tools *)"
    ]
  }
}
```

## MCP Permission Detection

Reference: `@registry/registry.toml`

For each MCP detected during discovery (Phase 5):

1. Look up the MCP in registry.toml `[mcps.{name}]`
2. If found and has `safe_read_tools` array: add all tools to `permissions.allow`
3. If found but `safe_read_tools` is empty: skip (tool names vary by installation)
4. If NOT found in registry (unknown/custom MCP): do not add permissions, warn user:
   ```
   Unknown MCP "{name}" detected. No auto-permissions added.
   You can manually add read permissions to .claude/settings.json.
   ```

For MCPs rated "recommended" in registry but not installed:
- During wizard (Section 5), present with install command and ask user
- If user installs: add safe_read_tools permissions
- If user skips: note in dominion.toml [tools.skipped_mcps]

## Rules

- Only add READ operations. Write operations require human approval.
- Merge with existing permissions — never duplicate, never remove.
- If settings.json has an existing `permissions.allow` array, append to it.
- Unknown MCPs: preserve existing permissions, do not remove.

## Configure Serena Project

If serena is installed and project hasn't been activated:
1. Call `mcp__serena__activate_project` with the project root path
2. Note detected LSP backends from `@registry/registry.toml` [mcps.serena.lsp_config]
   for each detected language
