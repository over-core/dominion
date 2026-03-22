# Dominion

> Your AI development team, generated from your codebase.

**v0.4.2** | MIT License | Claude Code Plugin

Dominion is a Claude Code plugin that analyzes your project and generates a complete AI development context — specialized agents, an MCP server, governance hooks, and code conventions — all committed to git. The plugin is the author; the artifacts are the runtime. Dominion is needed to create and evolve the setup, but a cloned repo works without it. New developers get the full context on `git clone`.

## What You Get

Run `/dominion:onboard` once and Dominion generates the following in your project:

```
.dominion/
├── dominion.toml              # Project configuration
├── style.toml                 # Code conventions
├── agents/
│   ├── researcher.toml        # Agent config (role, model, MCPs, hard stops)
│   ├── architect.toml
│   ├── developer.toml
│   └── ...                    # 7 roles total
├── heuristics/
│   ├── research.md            # Step-specific methodology + engineering practices
│   ├── plan.md
│   ├── developer.md           # Role-specific heuristics for specialists
│   └── ...
├── knowledge/
│   └── index.toml             # Domain knowledge registry
└── phases/                    # Pipeline state (gitignored)

.claude/
├── agents/                    # Agent dispatch files (thin, MCP-driven)
│   ├── researcher.md
│   ├── architect.md
│   └── ...
├── settings.local.json        # Permissions + governance hooks
└── hooks/
    └── dominion-governance.sh

.mcp.json                      # MCP server config (committed)
CLAUDE.md                      # Project-aware instructions
AGENTS.md                      # Agent roster with dispatch entries
```

Everything is committed to git. The MCP server (`dominion-mcp`) prepares context via CLAUDE.md files; agents read the filesystem directly. Hooks block `.dominion/` writes — agents write via MCP tools only.

## The Pipeline

Dominion drives feature development through a complexity-adaptive pipeline. Depth adapts to the task — trivial tasks execute directly, complex tasks get the full cycle.

| Step | Skill | Lead Agent | Produces |
|------|-------|------------|----------|
| 1. Discuss | `/dominion:discuss` | Orchestrator | Intent, scope, constraints |
| 2. Research | `/dominion:research` | Researcher | Structured findings, risks |
| 3. Plan | `/dominion:plan` | Architect | Tasks with wave grouping, success criteria |
| 4. Execute | `/dominion:execute` | Developer | Code changes with atomic commits |
| 5. Review | `/dominion:review` | Reviewer + Specialists | Quality verdict, security/perf findings |
| 6. Improve | `/dominion:improve` | Orchestrator | Knowledge capture, methodology updates |

Use `/dominion:orchestrate` to drive the full pipeline end-to-end. The orchestrator assesses complexity and selects the appropriate depth:

| Complexity | Steps |
|------------|-------|
| Trivial | Execute only |
| Moderate | Research → Plan → Execute → Review |
| Complex | Full 6-step pipeline |
| Major | Full pipeline + panel debates |
| Specified | Plan → Execute → Review (spec already exists) |

## MCP Server

`dominion-mcp` is the context engine — it prepares agent context as CLAUDE.md files on the filesystem and manages pipeline state.

### 11 MCP Tools

| Category | Tools |
|----------|-------|
| **Setup** | `start_phase`, `prepare_step`, `prepare_task` |
| **Submit** | `submit_work`, `signal_blocker` |
| **Progress** | `get_progress`, `quality_gate`, `assess_complexity`, `advance_step`, `save_decision` |
| **Knowledge** | `save_knowledge` |

### Context Delivery

MCP is the context preparer; the filesystem is the context delivery mechanism. `prepare_step` and `prepare_task` generate CLAUDE.md files that agents read directly. Agent heuristics include step methodology, engineering practices, and role-specific guidance — 150–260 lines served per agent.

### Agent Protocol

Every agent follows the mandatory protocol:

```
SPAWN → read CLAUDE.md → WORK → submit_work → VERIFY
```

The MCP server writes context to the filesystem before agents spawn. Hooks block direct `.dominion/` writes — agents submit results via MCP tools.

## Agents

7 agent roles, deployed per project based on detection results.

| Role | Model | Purpose |
|------|-------|---------|
| Researcher | Opus | Deep codebase analysis, framework audit, pattern detection |
| Architect | Opus | Task decomposition, wave design, dependency planning |
| Developer | Sonnet | Implementation with TDD, self-verification, atomic commits |
| Reviewer | Opus | Cross-cutting code review across security, performance, architecture |
| Security Auditor | Opus | OWASP Top 10, CWE matching, dependency scanning, threat modeling |
| Analyst | Opus | Quantitative performance analysis, N+1 detection, scalability |
| Innovation Engineer | Opus | Opt-in. TRIZ, TOC, SIT, first principles, SCAMPER |

Reviewer and analyst roles can create temporary analysis scripts but cannot modify source code files. Developer agents are restricted to files listed in their assignment to prevent merge conflicts during parallel worktree execution.

## Skills

10 user-facing commands available via `/dominion:*`.

### Pipeline Skills

| Command | Description |
|---------|-------------|
| `/dominion:discuss` | Capture intent — goals, scope, constraints, panel debate at complex+ |
| `/dominion:research` | Codebase analysis producing structured findings |
| `/dominion:plan` | Task decomposition with wave grouping and success criteria |
| `/dominion:execute` | Parallel worktree implementation with wave grouping |
| `/dominion:review` | Cross-cutting review with specialist support (security, performance) |
| `/dominion:improve` | Add project-specific knowledge via conversation |

### Utility Skills

| Command | Description |
|---------|-------------|
| `/dominion:onboard` | Analyze project and generate AI development context |
| `/dominion:orchestrate` | Drive the full pipeline end-to-end |
| `/dominion:status` | Display pipeline status dashboard |
| `/dominion:ship` | Automated ship — sync, test, commit, push, create PR |

## Getting Started

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed and configured

### Installation

```bash
# Add the marketplace source (once)
/plugin marketplace add over-core/dominion

# Install the plugin
/plugin install dominion
```

### Initialize Your Project

```bash
/dominion:onboard
```

This walks through project analysis and a setup wizard. Dominion detects your languages, frameworks, and infrastructure, then generates agents, MCP server config, governance hooks, and heuristics.

After onboard completes, **restart your Claude Code session** (required for `.mcp.json` to take effect). Then run `/dominion:orchestrate` to start your first pipeline.

### Run Your First Pipeline

```bash
# Set high effort — subagents inherit the session's effort level
/effort high

# Full pipeline with user control points between steps
/dominion:orchestrate

# Or run individual steps
/dominion:discuss
/dominion:research
/dominion:plan
/dominion:execute
/dominion:review
/dominion:improve
```

> **Note:** Claude Code subagents inherit the parent session's thinking effort level. There is no per-agent override. Running pipeline steps at high effort produces significantly better research, planning, and review output.

## Requirements

### Required MCPs

| MCP | Category | Install |
|-----|----------|---------|
| serena | Code navigation | See [serena docs](https://github.com/oraios/serena). Add `--project .` to args for worktree support. |

### Recommended MCPs

| MCP | Category | Install |
|-----|----------|---------|
| echovault | Cross-agent memory | See [echovault docs](https://github.com/mraza007/echovault) |
| context7 | Documentation | `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest` |
| exa | Semantic search + code examples | `claude mcp add --transport http exa https://mcp.exa.ai/mcp` |
| sequential-thinking | Multi-step reasoning | `claude mcp add sequential-thinking -- npx -y @anthropic/sequential-thinking-mcp` |
| github | GitHub operations | `claude mcp add github -- npx -y @anthropic/github-mcp` |

### Required Plugins

| Plugin | Purpose | Install |
|--------|---------|---------|
| hookify | Governance hook creation | `/plugin marketplace install hookify` |

### Recommended Tools

| Tool | Purpose | Install |
|------|---------|---------|
| rtk | CLI proxy — 60-90% Bash output token savings | See [rtk docs](https://github.com/tomoam/rtk) |

## Governance

Dominion enforces its protocol through a 3-layer enforcement stack:

1. **Hooks** — PreToolUse blocks direct `.dominion/` writes
2. **MCP** — Context preparation and result submission interface
3. **Orchestrator** — Verifies submission via `quality_gate()` after each agent, deduplicates stale findings

## Project Structure

For contributors — this is the plugin's own layout.

```
skills/                    10 user-facing skills (/dominion:* commands)
  onboard/                 Substantial — project analysis + setup wizard
    data/                  Detection data (languages, frameworks, registry, agents)
    data/heuristics/       Step + role-specific methodology heuristics
    references/            Sub-step instructions (detection, generation, interview, etc.)
  {step}/                  Pipeline step dispatchers

mcp/                       dominion-mcp Python package (MCP server)
  dominion_mcp/
    core/                  7 core modules (config, state, filesystem, prepare, complexity, panel)
    tools/                 4 tool modules (11 MCP tools)
  tests/                   115 tests

.claude-plugin/
  plugin.json              Plugin manifest
  marketplace.json         Marketplace metadata
```

## Version History

| Version | Highlights |
|---------|------------|
| 0.4.2 | Concerns remediation — quality gate dedup, worktree branch verification, relaxed file ownership for reviewer/analyst, rtk recommendation, Serena `--project` flag, enriched agent heuristics with methodology and engineering practices |
| 0.4.0 | Pipeline hardening — stubs-first TDD, specified complexity level, post-mortem fixes from production use |
| 0.3.0 | Context engine architecture — filesystem-based context delivery, MCP as context preparer, heuristics replace conditional methodology, 11 tools (down from 21) |
| 0.2.2 | Advanced collaboration — panel mode, course correction, complexity-adaptive pipeline depth |
| 0.2.0 | MCP architecture — CLI replaced by MCP server, conditional methodology, governance hooks, agent memory |
| 0.1.0 | Initial release — 14 skills, 18 agents, 54 CLI commands, 7-step pipeline |

## License

[MIT](LICENSE)
