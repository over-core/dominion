# Structural Awareness

Reference for agents that need to understand Dominion's building blocks. Read this before creating, modifying, or recommending structural changes.

## Building Blocks

### Agent

An autonomous role with defined capabilities, tool access, and governance rules.

**Composed of:**
- `.dominion/agents/{role}.toml` — configuration (model, tools, governance, workflow)
- `.claude/agents/{role}.md` — generated instructions (from TOML by Secretary)
- Entry in `AGENTS.md` — auto-generated roster
- Permissions in `.claude/settings.json` — MCP and tool access

**To create:**
1. Write `.dominion/agents/{role}.toml` (use existing agent TOMLs as reference)
2. If adding methodology: follow [agent-methodology-design.md](agent-methodology-design.md) for `[methodology]`, `[methodology.tool_routing]`, `[methodology.methods]`, and `[research_lens]` sections
3. Run `dominion-cli agents generate` — generates .md and updates AGENTS.md
4. Update `.claude/settings.json` with required MCP permissions
5. Run `dominion-cli doc generate` to regenerate DOMINION.md

**When to create vs extend:**
- Create a new agent when: ongoing specialized behavior, distinct file ownership, separate governance rules
- Extend an existing agent when: adding a skill or capability to an existing role

### Skill

A repeatable procedure or workflow invoked as a `/dominion:*` command.

**Composed of:**
- `.dominion/skills/{name}.md` — skill file with YAML frontmatter and directive prose
- Optional: `.dominion/skills/{name}/references/*.md` — sub-step instructions

**To create:**
1. Define architecture: name, purpose, reference files needed, governance rules (Dominion pipeline Steps 1-5)
2. Author and validate: invoke `/skill-creator` with the architecture context — it writes the SKILL.md, runs eval loops, and optimizes the description for triggering (requires skill-creator plugin — install with `/plugin marketplace install skill-creator`)
3. Use markdown links for sub-steps: `[filename.md](references/filename.md)`
4. Run `dominion-cli doc generate` to regenerate DOMINION.md

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
3. Run `dominion-cli knowledge sync` to update MEMORY.md

**Budget:** Hot entries load into MEMORY.md. Total hot summary lines must stay under `memory_budget_lines`.

### CLI Command

A command available via `dominion-cli`.

**Composed of:**
- Entry in `.dominion/specs/cli-spec.toml` — command definition (name, description, args, reads, writes, behavior)
- Built-in implementation in the dominion-cli package (for core commands)
- OR generic access via `dominion-cli data get/set` (for project-specific data)

**To create:**
1. Add `[[commands]]` entry to `.dominion/specs/cli-spec.toml`
2. Add to `minimum_commands` list if it should be validated
3. For data access (read/write a TOML file): use `dominion-cli data get <file>` and `dominion-cli data set <file>` — no code changes needed
4. For complex operations (aggregation, cross-file validation): record as a plugin feature request — use existing commands as workaround until next plugin version

### Hook Rule

A behavioral guard that runs on specific triggers (pre-commit, tool calls, etc.).

**Composed of:**
- Hookify rule: `.claude/hookify.{name}.local.md` — declarative markdown with YAML frontmatter (preferred, requires hookify plugin)
- OR native hook: config in `.claude/settings.json` under `"hooks"` key, optional script in `.claude/hooks/`

**To create:**
1. Define architecture: what behavior to guard, trigger event, warn vs block action (Dominion pipeline Steps 1-5)
2. Author the rule: invoke `/hookify:writing-rules` for correct hookify rule syntax (requires hookify plugin — install with `/plugin marketplace install hookify`)
3. Test the rule fires correctly

### Config Section

Project-specific configuration in TOML.

**Composed of:**
- Section in `.dominion/dominion.toml` — new `[section]` with fields

**To create:**
1. Add section to `.dominion/dominion.toml`
2. Add validation check in `dominion-cli validate`
3. Update schema template in [dominion.toml](../schemas/dominion.toml) if it's a reusable pattern

## Wiring Checklist

When creating any new building block, verify:

- [ ] TOML files parse: `python3 -c "import tomllib; tomllib.load(open('file.toml','rb'))"`
- [ ] References resolve: all markdown link references point to existing files
- [ ] AGENTS.md updated: if agents changed, run `dominion-cli agents generate`
- [ ] DOMINION.md updated: if skills, agents, or config changed, run `dominion-cli doc generate`
- [ ] settings.json updated: if new MCP permissions needed
- [ ] Validate passes: run `dominion-cli validate`

## Extensibility

Users can add custom building blocks beyond the standard set. When a user creates a new structural pattern:
1. Document it in this reference (add a new section)
2. Add validation logic if appropriate
3. The system treats user-defined patterns the same as built-in ones
