# Claim Analysis

Parse and understand each found artifact. Identify structure, conventions, and ownership.

## CLAUDE.md Analysis

If CLAUDE.md exists:
1. Parse section headings into a tree structure
2. For each section, classify as:
   - **User-written**: unique project rules, constraints, preferences
   - **Generated**: sections that match known plugin patterns (GSD, Conductor, Dominion)
   - **Mixed**: sections with both generated scaffold and user additions
3. Extract key conventions:
   - Commit format rules
   - File/directory restrictions
   - Tool usage instructions
   - Decision framework (if any)
4. Record which conventions overlap with Dominion's intended CLAUDE.md sections

## Agent Analysis

For each existing `.claude/agents/*.md`:
1. Parse the agent's role and capabilities
2. Map to Dominion agent roles where possible:
   - "code reviewer" → Reviewer
   - "architect" / "planner" → Architect
   - "tester" / "qa" → Tester
   - Unmapped roles → preserve as custom agents
3. Record model preferences mentioned in agent files
4. Note any governance rules embedded in agent instructions

## Settings Analysis

If `.claude/settings.json` exists:
1. Parse MCP permissions — which MCPs have which operations allowed
2. Parse tool allow-lists — what's auto-approved
3. Identify permissions Dominion would add vs what already exists

## Hook Analysis

For each existing hook:
1. Parse the trigger event and conditions
2. Identify purpose (governance, formatting, validation)
3. Check for conflicts with Dominion lifecycle hooks:
   - Session start/end hooks
   - Pre-commit hooks
   - Source-diving prevention hooks

## Plugin Analysis

For detected plugins:
1. **GSD**: Check `.planning/` or `.gsd/` for project state. Identify if GSD orchestration conflicts with Dominion's pipeline.
2. **Conductor**: Check `.conductor/` for tracks and phases. Identify workflow overlap.
3. **Other**: Record purpose, check for orchestration conflicts.

## Output

For each artifact, produce:
- `structure`: parsed tree/sections
- `classification`: user-written / generated / mixed
- `conventions_extracted`: key rules and patterns
- `dominion_overlap`: which Dominion features this overlaps with
- `conflicts`: specific conflicts identified
