# settings.local.json Generation

Extend (never replace) `.claude/settings.local.json` with Dominion permissions and hooks.

## Read Existing

If `.claude/settings.local.json` exists, read it and preserve all existing entries.
If it doesn't exist, create it.

## Core Permissions

Always add:
```json
{
  "permissions": {
    "allow": [
      "Bash(dominion-cli *)",
      "Read(~/.claude/plugins/cache/dominion/**)"
    ]
  }
}
```

## MCP Permission Detection

Reference: [registry.toml](../../registry/registry.toml)

For each MCP detected during discovery (Phase 5):

1. Look up the MCP in registry.toml `[mcps.{name}]`
2. If found and has `safe_read_tools` array: add all tools to `permissions.allow`
3. If found but `safe_read_tools` is empty: skip (tool names vary by installation)
4. If NOT found in registry (unknown/custom MCP): do not add permissions, warn user:
   ```
   Unknown MCP "{name}" detected. No auto-permissions added.
   You can manually add read permissions to .claude/settings.local.json.
   ```

For MCPs rated "recommended" in registry but not installed:
- During wizard (Section 5), present with install command and ask user
- If user installs: add safe_read_tools permissions
- If user skips: note in dominion.toml [tools.skipped_mcps]

## Hooks

Native Claude Code hooks for governance rules that require filesystem checks at runtime.
These complement the hookify rules in [hooks-generation.md](hooks-generation.md).

### Hook: Warn on Active Blocker

Add to `settings.local.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{"type": "command", "command": ".claude/hooks/warn-blocker.sh"}]
      }
    ]
  }
}
```

Create `.claude/hooks/warn-blocker.sh`:
```bash
#!/bin/sh
state=".dominion/state.toml"
[ -f "$state" ] || exit 0
grep -q 'status = "blocked"' "$state" 2>/dev/null || exit 0
printf '{"systemMessage":"WARNING: A blocker is active. Run: dominion-cli state blockers"}\n'
```

Make executable: `chmod +x .claude/hooks/warn-blocker.sh`

### Hook: Session Start — Auto-Resume

Add to the same `settings.local.json` hooks config:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [{"type": "command", "command": ".claude/hooks/session-start.sh"}]
      }
    ]
  }
}
```

Create `.claude/hooks/session-start.sh`:
```bash
#!/bin/sh
[ -d ".dominion" ] || exit 0
dominion-cli state resume 2>/dev/null || true
```

Make executable: `chmod +x .claude/hooks/session-start.sh`

## Rules

- Only add READ operations to permissions. Write operations require human approval.
- Merge with existing permissions — never duplicate, never remove.
- If settings.local.json has an existing `permissions.allow` array, append to it.
- If settings.local.json has existing `hooks`, merge hook entries — never overwrite.
- Unknown MCPs: preserve existing permissions, do not remove.

## Configure Serena Project

If serena is installed and project hasn't been activated:
1. Call `mcp__serena__activate_project` with the project root path
2. Note detected LSP backends from [registry.toml](../../registry/registry.toml) [mcps.serena.lsp_config]
   for each detected language
