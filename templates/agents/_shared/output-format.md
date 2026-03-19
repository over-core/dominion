# Output Format

## Artifact Submission

Submit all work via `mcp__dominion__agent_submit(role, artifact_type, content)`.

Content must be valid JSON. For structured TOML artifacts (plan.toml, research.toml, review.toml, test-report.toml), submit as a JSON dict — the MCP server writes it as TOML.

## Summary

After completing your work, include in your submission:
- **What was done** — list of changes made
- **Decisions made** — any choices and their rationale
- **Friction encountered** — what was harder than expected
- **Discoveries** — patterns, gotchas, or insights for future agents

Record significant decisions via `mcp__dominion__save_decision(title, decision, rationale)`.

## Memory

Save discoveries for future sessions via `mcp__dominion__save_memory(role, type, content)`:
- `type: "discovery"` — patterns found, gotchas encountered
- `type: "correction"` — things you initially got wrong
- `type: "preference"` — project-specific preferences learned
