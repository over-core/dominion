# Structural Awareness

Reference for agents that need to understand Dominion's building blocks. Read this before creating, modifying, or recommending structural changes.

## Building Blocks

### Agent

An autonomous role with defined capabilities, tool access, and governance rules.

**Composed of:**
- `.dominion/agents/{role}.toml` — configuration (model, tools, governance, workflow)
- `.claude/agents/{role}.md` — generated instructions (from TOML by Attendant)
- Entry in `AGENTS.md` — auto-generated roster
- Permissions in `.claude/settings.json` — MCP and tool access

**To create:**
1. Write `.dominion/agents/{role}.toml` (use existing agent TOMLs as reference)
2. Run `dominion-tools agents generate` — generates .md and updates AGENTS.md
3. Update `.claude/settings.json` with required MCP permissions
4. Run `dominion-tools doc generate` to regenerate DOMINION.md

**When to create vs extend:**
- Create a new agent when: ongoing specialized behavior, distinct file ownership, separate governance rules
- Extend an existing agent when: adding a skill or capability to an existing role

### Skill

A repeatable procedure or workflow invoked as a `/dominion:*` command.

**Composed of:**
- `.dominion/skills/{name}.md` — skill file with YAML frontmatter and directive prose
- Optional: `.dominion/skills/{name}/references/*.md` — sub-step instructions

**To create:**
1. Write `.dominion/skills/{name}.md` with frontmatter (`name`, `description`)
2. Write directive instructions (what the LLM should do, not explanations)
3. Use markdown links for sub-steps: [filename.md](references/filename.md)
4. Run `dominion-tools doc generate` to regenerate DOMINION.md

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
3. Run `dominion-tools knowledge sync` to update MEMORY.md

**Budget:** Hot entries load into MEMORY.md. Total hot summary lines must stay under `memory_budget_lines`.

### CLI Command

A command available via `dominion-tools`.

**Composed of:**
- Entry in `.dominion/specs/cli-spec.toml` — command definition (name, description, args, reads, writes, behavior)
- Implementation in the project's `dominion-tools` script

**To create:**
1. Add `[[commands]]` entry to `.dominion/specs/cli-spec.toml`
2. Developer agent implements the command
3. Add to `minimum_commands` list if it should be validated

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
2. Add validation check in `dominion-tools validate`
3. Update schema template in [dominion.toml](../schemas/dominion.toml) if it's a reusable pattern

## Wiring Checklist

When creating any new building block, verify:

- [ ] TOML files parse: `python3 -c "import tomllib; tomllib.load(open('file.toml','rb'))"`
- [ ] References resolve: all markdown link references point to existing files
- [ ] AGENTS.md updated: if agents changed, run `dominion-tools agents generate`
- [ ] DOMINION.md updated: if skills, agents, or config changed, run `dominion-tools doc generate`
- [ ] settings.json updated: if new MCP permissions needed
- [ ] Validate passes: run `dominion-tools validate`

## Extensibility

Users can add custom building blocks beyond the standard set. When a user creates a new structural pattern:
1. Document it in this reference (add a new section)
2. Add validation logic if appropriate
3. The system treats user-defined patterns the same as built-in ones
