---
name: onboard
description: Analyze project and generate AI development context engine with MCP server configuration
---

# /dominion:onboard

Analyze the project and generate a complete AI development context engine with MCP wiring.

<IMPORTANT>
Before starting:
1. Confirm you are in the correct project root directory
2. Check if `.dominion/` already exists:
   - If yes AND `.mcp.json` has a `dominion` entry: "Dominion is already onboarded. Use /dominion:improve for changes, or delete .dominion/ to re-onboard."
   - If yes but no `.mcp.json` dominion entry: warn: "Found .dominion/ but no MCP wiring. Re-running will regenerate configs. Continue? [Y/n]"
   - If no: proceed
3. MCP is NOT available during onboard — this skill creates `.mcp.json`. All data access is direct file reads.
4. v0.3.0 requires re-onboard. Existing .dominion/ from v0.2.x is not compatible.
</IMPORTANT>

## Phase 1: Detection

Follow detection.md

Output: languages, frameworks, MCPs, git platform, test command, dev profiles.

## Phase 2: Assessment

Present findings:
```
Project Analysis:
  Languages:      {list with primary marked}
  Frameworks:     {list by category}
  Package manager: {name} ({install_command})
  Test command:    {detected or "not detected"}
  Git platform:   {github/gitlab/bitbucket/other}

Existing setup:
  .dominion/      {exists/missing}
  CLAUDE.md       {exists/missing}
  .mcp.json       {detected MCPs or "missing"}

Available MCPs:
  {list detected MCPs: serena, context7, exa, echovault, etc.}

CLI tools:
  rtk             {installed (v0.x.x) / not installed — recommend}
```

## Phase 3: Interview

Follow interview.md (4 questions + optional taste: project identity, direction, testing, experience level)

## Phase 4: Generation

Follow generation.md — creates all artifacts:
1. `.dominion/config.toml` — merged config
2. `.dominion/agents/*.toml` — 7 flat agent configs
3. `.dominion/heuristics/*.md` — 5 step heuristics
4. `.dominion/knowledge/index.toml` — empty index
5. `.claude/agents/*.md` — thin agent briefs
6. `.claude/hooks/` — block-dominion-writes, session-start, prefer-serena
7. `.claude/settings.local.json` — permissions + hooks
8. `.mcp.json` — MCP server registration
9. `CLAUDE.md` — project instructions (60-100 lines)

## Phase 5: Confirmation

```
Dominion v0.3.0 onboarded successfully.

Generated:
  .dominion/config.toml        Project config (languages, frameworks, agents)
  .dominion/agents/             7 agent configs (~20 lines each)
  .dominion/heuristics/         5 step heuristics (customizable)
  .dominion/knowledge/          Knowledge index (grows during pipeline runs)
  .claude/agents/               7 agent briefs + AGENTS.md
  .claude/settings.local.json   MCP permissions + hooks
  .claude/hooks/                Governance hooks
  .mcp.json                     MCP server config
  CLAUDE.md                     Project instructions (you own this now)

IMPORTANT: Restart your Claude Code session now.
  .mcp.json was created — Claude Code must restart to load the MCP server.

NEXT STEP after restart:
  /dominion:orchestrate "Analyze codebase: document framework patterns,
  flag anti-patterns, audit security, assess test coverage, and produce
  an improvement roadmap"

  This runs in analysis mode (research → review only, no code changes).
  The orchestrator compiles findings into knowledge entries and reports.
  Without this, agents have zero project-specific knowledge.
  After this run, every agent brief includes framework-specific
  coding guidance, anti-pattern warnings, and security findings.

{if rtk not installed:}
Recommended: Install rtk for 60-90% token savings on Bash output.
  brew install rtk && rtk init --global
  Reduces token cost across all agents, especially worktree agents without Serena.
```
