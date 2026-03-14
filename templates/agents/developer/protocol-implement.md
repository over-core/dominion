# Implementation Protocol

For new-code and modify task types:

1. **Task intake** — read task from plan.toml (id, title, file_ownership, acceptance criteria, verify_command)
2. **Read knowledge_refs** — targeted context from Architect's selection
3. **Read upstream handoff notes** — wave transition docs from previous wave
4. **Search EchoVault** for gotchas related to task files/domain

## Context Building

1. Use serena `get_symbols_overview` on files in `file_ownership` scope
2. Read existing tests for affected code
3. Check `style.toml` for conventions (formatter, linter, naming)
4. Identify existing patterns and abstractions to build on — do NOT reinvent

## Implementation

1. Follow existing codebase patterns. New code should look like it was written by the same team.
2. Stay within `file_ownership` boundaries. Report if boundaries are wrong via `agent_signal`.
3. Prioritize: **working > clean > fast**
4. Apply Clean Code principles: intention-revealing names, small functions, SRP
5. Apply SOLID principles where language-appropriate

## Verification

1. Run `verify_command` from acceptance criteria
2. Run existing test suite for regressions
3. Verify changes stay within `file_ownership`
4. If verify fails, iterate from implementation — do NOT submit failing code

## Commit & Handoff

1. Atomic commit with conventional commit message
2. Write SUMMARY.md with friction, decisions, discoveries
3. Save discoveries to EchoVault via `memory_save`
4. Report blockers via `agent_signal(signal_type: "blocker")`
