---
name: educate
description: Capture domain knowledge through structured interview or external sources. Produces knowledge files, skills, or agent configs.
---

# /dominion:educate

Teach Dominion domain knowledge from humans, documentation, or external sources.

## Flag Parsing

- `--from <source>`: Pull from external source (notion, confluence, obsidian, url, file path)
- `--agent`: Force output as agent config (skip output routing)
- `--skill`: Force output as skill file (skip output routing)
- No flags: interactive DKCP interview

## Pre-check

1. Read `.dominion/dominion.toml` — verify project is initialized
2. If `--from` provided: verify source is accessible (file exists, URL reachable, API token configured)
3. Create `.dominion/knowledge/` directory if it doesn't exist

## With `--from` Source

Follow `@references/source-integration.md` to extract knowledge from the external source.
Then skip to Phase 5 (Artifact Grounding) of the DKCP protocol.

## Without `--from` (Interactive Interview)

Follow `@references/dkcp-protocol.md` — the full 7-phase Domain Knowledge Capture Protocol.

## Output Routing

If `--agent` or `--skill` flag provided, use that output format directly.
Otherwise, follow `@references/output-routing.md` to determine the best output format.

## Post-capture

1. If output is a knowledge file: write to `.dominion/knowledge/{topic}.md`, update `.dominion/knowledge/index.toml`
2. If output is a skill: write to `.dominion/skills/{name}.md`
3. If output is an agent: write TOML to `.dominion/agents/{role}.toml`, generate `.claude/agents/{role}.md` via Attendant
4. Run `dominion-tools knowledge sync` to update MEMORY.md with new knowledge
5. Commit all new files
