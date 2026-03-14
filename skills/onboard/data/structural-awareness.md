# Structural Awareness

Reference for agents that need to understand Dominion's building blocks. Read this before creating, modifying, or recommending structural changes.

## Building Blocks

### Agent

An autonomous role with defined capabilities, tool access, and governance rules.

**Composed of:**
- `.dominion/agents/{role}/agent.toml` — configuration (model, tools, governance, methodology)
- `.dominion/agents/{role}/*.md` — methodology section files (flat, next to agent.toml)
- `.claude/agents/{role}.md` — generated dispatch stub (from TOML by Secretary)
- Entry in `AGENTS.md` — auto-generated roster
- Permissions in `.claude/settings.local.json` — MCP and tool access

**To create:**
1. Write `.dominion/agents/{role}/agent.toml` (use existing agent TOMLs as reference)
2. Write methodology section .md files in the same directory
3. Have Secretary generate `.claude/agents/{role}.md` and update AGENTS.md
4. Update `.claude/settings.local.json` with required MCP permissions

**When to create vs extend:**
- Create a new agent when: ongoing specialized behavior, distinct file ownership, separate governance rules
- Extend an existing agent when: adding a methodology section or capability to an existing role

### Skill

A repeatable procedure or workflow invoked as a `/dominion:*` command.

**Composed of:**
- `skills/{name}/SKILL.md` — skill file with YAML frontmatter and directive prose
- Optional: `skills/{name}/references/*.md` — sub-step instructions (auto-loaded by Claude Code)

**To create:**
1. Define architecture: name, purpose, reference files needed
2. Write `skills/{name}/SKILL.md` with YAML frontmatter (`name`, `description`)
3. Write reference files in `skills/{name}/references/` for detailed sub-steps

**When to create vs use knowledge:**
- Create a skill when: repeatable procedure, decision tree, process that fires as a command
- Use knowledge when: domain facts, constraints, reference information

### Knowledge File

Domain knowledge that agents reference during their work.

**Composed of:**
- `.dominion/knowledge/{topic}.md` — markdown content
- Entry in `.dominion/knowledge/index.toml` — hot/warm/cold designation, summary

**To create:**
1. Write `.dominion/knowledge/{topic}.md`
2. Add entry to `.dominion/knowledge/index.toml` with temperature and summary

**Budget:** Hot entries load into MEMORY.md. Total hot summary lines must stay under `memory_budget_lines`.

### MCP Tool

A tool exposed by the dominion-mcp server for agents to access project state and methodology.

**Composed of:**
- Tool function in `mcp/dominion_mcp/tools/*.py` — registered via `@mcp.tool()` decorator
- Entry in `templates/mcp-spec.toml` — tool specification

**21 tools** across 4 modules: agent_lifecycle (4), pipeline_tools (5), data_read (7), data_write (5).

Agents access via `mcp__dominion__*` tool calls. Never access `.dominion/` files directly.

### Hook Rule

A behavioral guard that runs on specific triggers.

**Composed of:**
- Hookify rule: `.claude/hookify.{name}.local.md` — declarative markdown with YAML frontmatter
- OR native hook: config in `.claude/settings.local.json` under `"hooks"` key, optional script in `.claude/hooks/`

**To create:**
1. Define what behavior to guard, trigger event, warn vs block action
2. For hookify rules: use `/hookify:writing-rules` for correct syntax
3. For native hooks: add to settings.local.json hooks config

### Config Section

Project-specific configuration in TOML.

**Composed of:**
- Section in `.dominion/dominion.toml` — new `[section]` with fields

**To create:**
1. Add section to `.dominion/dominion.toml`
2. Update schema template in `templates/schemas/dominion.toml` if it's a reusable pattern

## Wiring Checklist

When creating any new building block, verify:

- [ ] TOML files parse: `python3 -c "import tomllib; tomllib.load(open('file.toml','rb'))"`
- [ ] References resolve: all markdown link references point to existing files
- [ ] AGENTS.md updated: if agents changed, have Secretary regenerate
- [ ] settings.local.json updated: if new MCP permissions needed
- [ ] Tests pass: `cd mcp && uv run pytest`
