# Readiness Check

Pre-flight verification before auto mode starts. Also useful as a standalone diagnostic.

## Invocation

Run `dominion-cli auto readiness` (or invoke the check logic directly).

## Check 1: Autonomy Configuration

Read `.dominion/dominion.toml`:
- Verify `[autonomy]` section exists
- Verify `[autonomy.circuit_breakers]` has all required fields
- Verify values are numeric and non-negative
- If missing: FAIL — "No autonomy config. Add [autonomy] section to dominion.toml or re-run /dominion:init."

## Check 2: Permission Audit

Read `.claude/settings.json` and `registry/registry.toml`:
- For each MCP in `dominion.toml [mcps.installed]`:
  - Look up MCP in registry.toml
  - For each tool in `safe_read_tools`: verify it appears in settings.json `permissions.allow`
- Report: "{approved}/{total} read tools pre-approved"
- If gaps found: list missing permissions with the MCP name and tool name

**Hard rule:** This check only verifies read permissions. Write permissions are NEVER auto-approved.

## Check 3: MCP Availability

For each MCP in `dominion.toml [mcps.installed]`:
- Attempt a lightweight probe (tool listing or simple query)
- Record result in state.toml `[[mcp_status]]`:
  - `name = "{mcp_name}"`, `available = true|false`, `checked_at = "{ISO 8601}"`, `fallback_active = false`
- If MCP is unavailable AND `critical = true` in registry: FAIL — auto mode cannot proceed
- If MCP is unavailable AND `critical = false`: WARN — note the missing_consequence from registry

## Result

Aggregate checks into a readiness verdict:
- All checks pass: "Ready for auto mode: YES"
- Warnings only: "Ready for auto mode: YES (with warnings)"
- Any FAIL: "Ready for auto mode: NO" — list failures
