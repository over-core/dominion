# Dominion

> Your AI development team, generated from your codebase.

**v0.2.2** | MIT License | Claude Code Plugin

Dominion is a Claude Code plugin that analyzes your project and generates a complete AI development methodology — specialized agents, an MCP server, governance hooks, code conventions, and conditional methodology — all committed to git. The plugin is the author; the artifacts are the runtime. Dominion is needed to create and evolve the setup, but a cloned repo works without it. New developers get best practices on `git clone`.

## What You Get

Run `/dominion:onboard` once and Dominion generates the following in your project:

```
.dominion/
├── dominion.toml              # Project configuration
├── roadmap.toml               # Phase roadmap
├── state.toml                 # Session state (gitignored)
├── style.toml                 # Code conventions
├── agents/
│   ├── researcher/
│   │   ├── agent.toml         # Agent config + methodology section index
│   │   ├── core.md            # Conditional methodology sections (flat)
│   │   └── ...
│   ├── architect/
│   │   └── agent.toml
│   └── ...
├── memory/                    # Per-agent persistent memory
│   ├── researcher.toml
│   └── ...
├── knowledge/
│   └── index.toml             # Domain knowledge registry
└── ...

.claude/
├── agents/                    # Agent dispatch files (thin, MCP-driven)
│   ├── researcher.md
│   ├── architect.md
│   └── ...
├── settings.local.json        # Permissions + governance hooks
└── hooks/
    ├── block-dominion-access.sh
    ├── block-cli-access.sh
    └── verify-agent-submitted.sh

.mcp.json                      # MCP server config (3 lines, committed)
CLAUDE.md                      # Lean project-aware instructions
AGENTS.md                      # Agent roster with dispatch entries
```

Everything is committed to git. The MCP server (`dominion-mcp`) becomes the exclusive interface for reading and writing project state — agents call MCP tools, hooks enforce this mechanically.

## The Pipeline

Dominion drives feature development through a 7-step pipeline. Each step has a dedicated skill and a dispatch mode.

| Step | Skill | Dispatch Mode | Lead Agent | Produces |
|------|-------|--------------|------------|----------|
| 1. Discuss | `/dominion:discuss` | Inline / Panel | Orchestrator | Intent, scope, constraints |
| 2. Research | `/dominion:research` | Subagent | Researcher | research.toml — findings, risks |
| 3. Plan | `/dominion:plan` | Subagent | Architect | plan.toml — tasks, waves, criteria |
| 4. Execute | `/dominion:execute` | Worktree | Developer | Code changes with atomic commits |
| 5. Audit | `/dominion:audit` | Multi-subagent | QA + Security + Analyst | test-report.toml, security-findings.toml |
| 6. Review | `/dominion:review` | Subagent | Reviewer | review.toml — quality findings, verdict |
| 7. Improve | `/dominion:improve` | Panel | All | Improvement proposals, knowledge capture |

Use `/dominion:orchestrate` to drive the full pipeline end-to-end. Pipeline depth adapts to task complexity — trivial tasks skip ceremony, major tasks get panel debates.

## MCP Server

`dominion-mcp` is the methodology engine — it replaces the CLI as the data access layer and adds conditional methodology curation, pipeline state machine, and agent memory.

### 21 MCP Tools

| Category | Tools |
|----------|-------|
| **Agent Lifecycle** | `agent_start`, `agent_submit`, `agent_signal`, `agent_status` |
| **Pipeline** | `pipeline_next`, `step_dispatch`, `phase_status`, `phase_history`, `help` |
| **Data Reads** | `get_config`, `get_style`, `get_plan`, `get_progress`, `get_knowledge`, `search_knowledge`, `get_roadmap` |
| **Data Writes** | `update_progress`, `add_blocker`, `resolve_blocker`, `save_decision`, `save_memory` |

### Conditional Methodology

Agent methodologies are stored as 10x richer conditional sections (language-specific, phase-specific, tool-specific) and curated per invocation:

- **Opus agents** (500k budget): permissive curation — richer context for deep analysis
- **Sonnet agents** (150k budget): strict curation — only precisely relevant sections

### Agent Protocol

Every agent follows the mandatory protocol:

```
SPAWN → agent_start → WORK → agent_submit → VERIFY
```

Agents receive zero methodology at spawn — only "call agent_start." The MCP server delivers everything in one call. Hooks block any alternative path.

## Agents

17 agents (8 core + 9 specialist), each with conditional methodology and model-aware token budgets.

### Core Agents

| Role | Model | Purpose |
|------|-------|---------|
| Researcher (A1) | Opus | Deep codebase and ecosystem analysis |
| Architect (A2) | Opus | Translates research into executable plans |
| Developer (A3) | Sonnet* | Implements plan tasks (Opus override for complex tasks) |
| Quality Auditor (A4) | Sonnet | Dual-mode: primary testing or TDD test audit |
| Reviewer (A5) | Opus | Post-phase quality assessment with audit synthesis |
| Analyst (A7) | Opus | Performance analysis, metrics, measurement |
| Security Auditor (A8) | Opus | Dependency audits, STRIDE, threat modeling. Always active. |
| Secretary | Sonnet | System maintenance, file generation |

### Specialist Agents

| Role | Model | Activated By |
|------|-------|-------------|
| Frontend Engineer (S1) | Sonnet | React, Vue, Svelte, Angular, Next.js |
| API Designer (S2) | Sonnet | OpenAPI, GraphQL, gRPC frameworks |
| Database Engineer (S3) | Sonnet | PostgreSQL, MySQL, SQLite, MongoDB, ORMs |
| DevOps (S4) | Sonnet | Docker, GitHub Actions, Helm Charts |
| Cloud Engineer (S5) | Sonnet | Terraform, Pulumi, CDK, AWS/GCP/Azure |
| Technical Writer (S6) | Sonnet | docs/ directories, ADR directories |
| Observability Engineer (S7) | Sonnet | Prometheus, Grafana, OpenTelemetry |
| Release Manager (S8) | Sonnet | Release workflows, version management |
| Innovation Engineer (S9) | Opus | Opt-in only. TRIZ, SIT, Axiomatic Design. |

## Skills

11 user-facing commands available via `/dominion:*`.

### Pipeline Skills

| Command | Description |
|---------|-------------|
| `/dominion:discuss` | Capture user intent — goals, scope, constraints |
| `/dominion:research` | Researcher-driven codebase analysis |
| `/dominion:plan` | Architect-driven planning with wave grouping |
| `/dominion:execute` | Developer-driven task execution with worktrees |
| `/dominion:audit` | Multi-agent quality audit (testing + security + performance) |
| `/dominion:review` | Reviewer-driven quality assessment |
| `/dominion:improve` | Post-pipeline retrospective and methodology improvement |

### Utility Skills

| Command | Description |
|---------|-------------|
| `/dominion:onboard` | Analyze project and generate AI development methodology |
| `/dominion:orchestrate` | Drive the full pipeline end-to-end |
| `/dominion:status` | Display project status dashboard |
| `/dominion:release` | Generate changelog, PR synopsis, and release notes |

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

This walks through project analysis and a setup wizard. Dominion detects your languages, frameworks, and infrastructure, then generates agents, MCP server config, governance hooks, and conditional methodology.

After onboard completes, **restart your Claude Code session** (required for `.mcp.json` to take effect).

### Run Your First Pipeline

```bash
# Set high effort — subagents inherit the session's effort level,
# and pipeline steps (research, plan, review) benefit significantly
/effort high

# Full pipeline with user control points between steps
/dominion:orchestrate

# Or run individual steps
/dominion:discuss
/dominion:research
/dominion:plan
/dominion:execute
/dominion:audit
/dominion:review
/dominion:improve
```

> **Note:** Claude Code subagents inherit the parent session's thinking effort level. There is no per-agent override. Running pipeline steps at high effort produces significantly better research, planning, and review output. This is a Claude Code platform constraint, not a Dominion limitation.

## Requirements

### Required MCPs

| MCP | Category | Critical | Install |
|-----|----------|----------|---------|
| serena | Code navigation | Yes | See [serena docs](https://github.com/serena-ai/serena) |
| echovault | Cross-agent memory | No | `pip install git+https://github.com/mraza007/echovault.git` |

### Recommended MCPs

| MCP | Category | Install |
|-----|----------|---------|
| context7 | Documentation | `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest` |
| exa | Semantic search + code examples | `claude mcp add --transport http exa https://mcp.exa.ai/mcp` |
| sequential-thinking | Multi-step reasoning | `claude mcp add sequential-thinking -- npx -y @anthropic/sequential-thinking-mcp` |
| github | GitHub operations | `claude mcp add github -- npx -y @anthropic/github-mcp` |

### Required Plugins

| Plugin | Purpose | Install |
|--------|---------|---------|
| hookify | Governance hook creation | `/plugin marketplace install hookify` |
| skill-creator | Eval-driven skill authoring | `/plugin marketplace install skill-creator` |

## Governance

Dominion enforces its protocol mechanically through a 4-layer enforcement stack:

1. **Hooks** — PreToolUse blocks direct `.dominion/` access and legacy CLI usage
2. **MCP** — The only interface for reading/writing project state
3. **Agent Prompt** — Spawn prompt contains zero methodology; `agent_start` delivers everything
4. **Orchestrator** — Verifies submission via `phase_status()` after each agent

## Project Structure

For contributors — this is the plugin's own layout.

```
skills/                    11 user-facing skills (/dominion:* commands)
  onboard/                 Substantial — project analysis + setup wizard
  {step}/                  Thin MCP dispatchers (~10-15 lines each)

templates/
  agents/                  17 agent TOML templates (8 core + 9 specialist)
    {role}/                Agent directory (agent.toml + methodology .md files)
  schemas/                 TOML schema definitions (20 schemas)
  agents/_shared/          Shared methodology sections (core, output-format, tools, rubrics)
  hooks/                   Governance hook scripts + settings template
  mcp-spec.toml            MCP tool specification (21 tools)

mcp/                       dominion-mcp Python package (MCP server)
  dominion_mcp/
    core/                  12 core modules (config, state, plan, complexity, panel, correction, etc.)
    tools/                 4 tool modules (21 MCP tools total)
  tests/                   201 tests

.claude-plugin/
  plugin.json              Plugin manifest
  marketplace.json         Marketplace metadata
```

## Version History

| Version | Highlights |
|---------|------------|
| 0.2.2 | Advanced collaboration — panel mode for multi-perspective debates, course correction with severity-based halt, complexity-adaptive pipeline depth |
| 0.2.1 | Methodology enrichment — complexity detection, skill level adaptation, adaptive requirements, TDD methodology option |
| 0.2.0 | MCP architecture — CLI replaced by MCP server, conditional methodology, governance hooks, agent memory, pipeline state machine, 5 dispatch modes |
| 0.1.1 | Stabilization — agent dispatch protocol, execution resilience, governance fixes |
| 0.1.0 | Initial release — 14 skills, 18 agents, 54 CLI commands, 7-step pipeline |

## License

[MIT](LICENSE)
