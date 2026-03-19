# Agent Generation (v0.3.0)

## Step 1: Deploy Agent TOMLs

Read `skills/onboard/data/agents.toml` roster. For each agent, generate a flat `.toml` file:

Write to `.dominion/agents/{role}.toml`:

```toml
[agent]
name = "{name}"
role = "{role}"
model = "{model}"
purpose = "{purpose}"

[tools.mcps]
preferred = [{preferred_mcps filtered by config.toml [tools].available}]
optional = [{optional_mcps filtered by config.toml [tools].available}]

[governance]
hard_stops = [{hard_stops from roster}]

[workflow]
produces = "{produces}"
```

Filter MCP lists: only include MCPs that are in `config.toml [tools].available`.

All 7 agents deployed by default. ~20 lines each.

## Step 2: Render Agent .md Briefs

For each agent, generate a thin `.claude/agents/{role}.md`:

```markdown
---
model: {model}
---
# {Name}
You are a Dominion {role} agent. Your task context is provided in your prompt or in a CLAUDE.md file.
Follow hard_stops from your context. Submit work via mcp__dominion__submit_work() when complete.
Summary is REQUIRED.
```

Write to `.claude/agents/{role}.md`.

## Step 3: Generate AGENTS.md

Write `.claude/agents/AGENTS.md`:

```markdown
# Dominion Agents
Available agents for this project. Each receives context via CLAUDE.md.
- researcher -- Codebase analysis and research synthesis
- architect -- Planning, task decomposition, wave design
- developer -- Implementation + self-verification
- reviewer -- Cross-cutting code review
- security-auditor -- Security-focused analysis
- analyst -- Performance/architecture quantitative analysis
- innovation-engineer -- Creative contradiction analysis
```

## Verification

- `.dominion/agents/*.toml` — 7 files, all TOML-parse
- `.claude/agents/*.md` — 7 files + AGENTS.md
- Each agent TOML has [agent], [governance], [workflow] sections
- Each agent TOML is <=25 lines
