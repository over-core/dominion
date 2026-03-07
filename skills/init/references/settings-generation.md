# settings.json Generation

Extend (never replace) `.claude/settings.json` with Dominion permissions.

## Read Existing

If `.claude/settings.json` exists, read it and preserve all existing entries.
If it doesn't exist, create it.

## Permissions to Add

```json
{
  "permissions": {
    "allow": [
      "Bash(dominion-tools *)"
    ]
  }
}
```

Add MCP read-operation permissions for each installed MCP. Reference `@registry/registry.toml` for the tool names:

For serena (if installed):
```json
"mcp__serena__get_symbols_overview",
"mcp__serena__find_symbol",
"mcp__serena__find_referencing_symbols",
"mcp__serena__find_file",
"mcp__serena__list_dir",
"mcp__serena__search_for_pattern",
"mcp__serena__activate_project",
"mcp__serena__read_memory",
"mcp__serena__list_memories",
"mcp__serena__get_current_config",
"mcp__serena__check_onboarding_performed"
```

For context7 (if installed):
```json
"mcp__context7__resolve-library-id",
"mcp__context7__query-docs"
```

For sequential-thinking (if installed):
```json
"mcp__sequential-thinking__sequentialthinking"
```

For echovault (if installed):
```json
"mcp__echovault__memory_search",
"mcp__echovault__memory_context"
```

For github (if installed):
```json
"mcp__plugin_github_github__get_file_contents",
"mcp__plugin_github_github__list_issues",
"mcp__plugin_github_github__list_pull_requests",
"mcp__plugin_github_github__search_code"
```

## Rules

- Only add READ operations. Write operations require human approval.
- Merge with existing permissions — never duplicate, never remove.
- If settings.json has an existing `permissions.allow` array, append to it.

## Configure Serena Project

If serena is installed and project hasn't been activated:
1. Call `mcp__serena__activate_project` with the project root path
2. Note detected LSP backends from `@registry/registry.toml` [mcps.serena.lsp_config]
   for each detected language
