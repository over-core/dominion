# settings.local.json Generation (v0.3.1)

Extend (never replace) `.claude/settings.local.json` with Dominion permissions, hooks, and environment.

## Read Existing

If `.claude/settings.local.json` exists, read it and preserve all existing entries.
If it doesn't exist, create it.

## Core Permissions

Always add:
```json
{
  "permissions": {
    "allow": [
      "mcp__dominion__*"
    ]
  }
}
```

## MCP Permission Detection

For each MCP detected during discovery:
1. Look up in registry.toml `[mcps.{name}]`
2. If found and has `safe_read_tools`: add to `permissions.allow`
3. Unknown MCPs: warn, don't add permissions

## Dev Profile Safety Rules

For each `prohibited` command in detected dev profile:
- Add `"Bash({command}*)"` to `permissions.deny`

Example for Python with uv:
```json
{
  "permissions": {
    "deny": [
      "Bash(uv pip install*)",
      "Bash(pip install*)"
    ]
  }
}
```

## Hooks

### Hook: Block .dominion/ Writes

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Edit", "hooks": [{"type": "command", "command": ".claude/hooks/block-dominion-writes.sh"}]},
      {"matcher": "Write", "hooks": [{"type": "command", "command": ".claude/hooks/block-dominion-writes.sh"}]}
    ]
  }
}
```

See [hooks-generation.md](hooks-generation.md) for script content.

### Hook: Session Start — Auto-Resume

```json
{
  "hooks": {
    "SessionStart": [
      {"hooks": [{"type": "command", "command": ".claude/hooks/session-start.sh"}]}
    ]
  }
}
```

See [hooks-generation.md](hooks-generation.md) for script content.

### Hook: Prefer Serena (if installed)

Only added if serena is in config.toml [tools].available.

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Read", "hooks": [
        {"type": "command", "command": ".claude/hooks/prefer-serena.sh"}
      ]}
    ]
  }
}
```

When sensitive-file-alert is also registered (it always is), both go in the same Read matcher:

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Read", "hooks": [
        {"type": "command", "command": ".claude/hooks/sensitive-file-alert.sh"},
        {"type": "command", "command": ".claude/hooks/prefer-serena.sh"}
      ]}
    ]
  }
}
```

### Hook: Secret Detection (always added)

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {"hooks": [{"type": "command", "command": ".claude/hooks/detect-secrets.sh"}]}
    ]
  }
}
```

See [hooks-generation.md](hooks-generation.md) for script content.

### Hook: Sensitive File Alert (always added)

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Read", "hooks": [
        {"type": "command", "command": ".claude/hooks/sensitive-file-alert.sh"}
      ]}
    ]
  }
}
```

When Serena is also detected, merge into the same Read matcher array (see Prefer Serena section above).

See [hooks-generation.md](hooks-generation.md) for script content.

### Hook: PreCompact State Preservation (always added)

```json
{
  "hooks": {
    "PreCompact": [
      {"hooks": [{"type": "command", "command": ".claude/hooks/pre-compact.sh"}]}
    ]
  }
}
```

See [hooks-generation.md](hooks-generation.md) for script content.

## Environment Variables

Always add:
```json
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50"
  }
}
```

Triggers compaction at 50% context capacity (default 95%). Produces higher-quality summaries for long-running pipeline sessions.

Merge with existing `env` — if user already has `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` set, preserve their value.

## Rules

- Only add READ operations to permissions. Write operations require human approval.
- Merge with existing permissions — never duplicate, never remove.
- If existing `permissions.allow` array: append to it.
- If existing `hooks`: merge hook entries — never overwrite.
- If existing `env`: merge env entries — never overwrite user values.

## Configure Serena Project

If serena is installed:
1. Call `mcp__serena__activate_project` with the project root path
2. Note detected LSP backends for each detected language
