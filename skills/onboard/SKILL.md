---
name: onboard
description: Analyze project and generate AI development methodology with MCP server configuration
---

# /dominion:onboard

Analyze the project and generate a complete AI development methodology with MCP server wiring.

<IMPORTANT>
This skill creates files in the project directory. Before starting:
1. Confirm you are in the correct project root directory
2. Check if `.dominion/` already exists:
   - If yes AND `.mcp.json` has a `dominion` entry: redirect to `/dominion:improve`. Say: "Dominion is already onboarded. Use /dominion:improve for changes."
   - If yes but no `.mcp.json` dominion entry: warn: "Found .dominion/ but no MCP wiring. Re-running will regenerate configs. Continue? [Y/n]"
   - If no: proceed (greenfield or brownfield)
3. MCP is NOT available during onboard — this skill creates `.mcp.json`. All data access is direct file reads.
</IMPORTANT>

## Phase 1: Detection

Followdetection.md

Output: structured detection results in conversation context.

## Phase 2: Assessment

Present findings to the user:
```
Project Analysis:
  Languages:      {list with primary marked}
  Frameworks:     {list by category}
  Package manager: {name} ({install_command})
  Infrastructure: {list}
  Project shape:  {monorepo/workspace/single}

Existing setup:
  .dominion/      {exists/missing}
  CLAUDE.md       {exists/missing}
  .claude/        {exists/missing — list agents/, settings, hooks}
  .mcp.json       {exists/missing}
  AGENTS.md       {exists/missing}

Quality tools:
  Formatters:     {per language}
  Linters:        {per language}
  Test runners:   {per language}
  Pre-commit:     {framework or "none"}
```

## Phase 3: Interview

Followinterview.md

Output: user-approved configuration choices.

## Phase 4: Generation

Followgeneration.md

## Phase 5: Confirmation

Present to the user:
```
Dominion onboarded successfully.

Generated:
  .dominion/              Project config, agent definitions, methodology sections
  .claude/agents/         {N} agent instruction files (thin MCP dispatchers)
  .claude/settings.local.json  MCP permissions + governance hooks (extended)
  .claude/hooks/          Governance hook scripts
  .mcp.json               MCP server configuration (dominion-mcp)
  CLAUDE.md               Project instructions (you own this now)
  AGENTS.md               Agent roster (thin 3-line dispatch entries)

IMPORTANT: Restart your Claude Code session now.
  .mcp.json was created — Claude Code must restart to load the MCP server.
  After restart, all /dominion:* commands will use MCP tools for data access.
```
