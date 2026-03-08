# Degraded Mode

Behavior when MCPs are unavailable. Agents read `[[mcp_status]]` from state.toml before attempting MCP calls.

## Pre-Call Check

Before calling any MCP tool, the agent checks state.toml `[[mcp_status]]`:
- If `available = false` for the target MCP: skip the call, use the fallback chain
- If `available = true`: proceed normally
- If no `[[mcp_status]]` entry exists for the MCP: attempt the call (assume available)

## Fallback Behavior

### Non-Critical MCPs (critical = false in registry)

Continue without the MCP. Use the documentation fallback chain from `dominion.toml [documentation]`:
1. Try next source in priority order
2. If all sources exhausted: follow `[documentation.fallback]` action (stop-and-ask)

Note the gap in SUMMARY.md:
```
## Tool Availability
- {mcp_name}: unavailable — used {fallback_source} instead
```

### Critical MCPs (critical = true in registry)

Halt the current task. Raise a blocker signal:
```bash
dominion-tools signal blocker --task {task_id} --level task --reason "{mcp_name} unavailable — required for {purpose}"
```

The orchestrator handles the blocker per standard blocker protocol.

## MCP Recovery

If a previously-unavailable MCP becomes available mid-session:
- Agents should NOT automatically retry failed tasks
- The readiness check can be re-run to update `[[mcp_status]]`
- User decides whether to retry failed tasks with the recovered MCP

## Per-MCP Fallback Details

| MCP | Critical | Fallback |
|-----|----------|----------|
| context7 | No | WebFetch for docs, higher token cost |
| serena | Yes | Halt task — Grep/Glob insufficient for large codebases |
| sequential-thinking | No | Standard reasoning without structured thinking |
| github | No | gh CLI for all GitHub operations |
| gitlab | No | glab CLI for all GitLab operations |
| echovault | No | MEMORY.md + .dominion/knowledge/ files only |
