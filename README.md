# Dominion

> Your AI development team, generated from your codebase.

**v0.1.1** | MIT License | Claude Code Plugin

Dominion is a Claude Code plugin that analyzes your project and generates a complete AI development methodology — specialized agents, curated tools, governance rules, code conventions, git workflow, and a CLI toolkit — all committed to git. The plugin is the author; the artifacts are the runtime. Dominion is needed to create and evolve the setup, but a cloned repo works without it. New developers get best practices on `git clone`. The methodology improves itself after every development phase.

## What You Get

Run `/dominion:init` once and Dominion generates the following in your project:

```
.dominion/
├── dominion.toml              # Project configuration
├── roadmap.toml               # Phase roadmap
├── state.toml                 # Session state (gitignored)
├── style.toml                 # Code conventions
├── metrics.toml               # Quality metrics
├── release-spec.toml          # Release configuration
├── knowledge/
│   └── index.toml             # Domain knowledge registry
└── ...

.claude/
├── agents/                    # Agent instruction files
│   ├── researcher.md
│   ├── architect.md
│   ├── developer.md
│   └── ...
├── settings.local.json        # Permissions and tool access
└── commands/
    └── dominion-cli/        # CLI toolkit (54 commands)

CLAUDE.md                      # Project-aware AI instructions
AGENTS.md                      # Agent roster documentation
DOMINION.md                    # Project overview cheatsheet
```

Everything is committed to git. The CLI toolkit becomes the exclusive interface for reading and writing project state — no agent edits TOML files directly.

## The Pipeline

Dominion drives feature development through a 7-step pipeline. Each step has a dedicated skill and a lead agent.

| Step | Skill | Lead Agent | Produces |
|------|-------|------------|----------|
| 1. Discuss | `/dominion:discuss` | Advisor | Intent, scope, constraints, priorities |
| 2. Explore | `/dominion:explore` | Researcher | research.toml — findings, risks, opportunities |
| 3. Plan | `/dominion:plan` | Architect | plan.toml — tasks, waves, dependencies, criteria |
| 4. Execute | `/dominion:execute` | Developer | Code changes with atomic commits |
| 5. Test | `/dominion:test` | Tester | test-report.toml — criteria results, coverage gaps |
| 6. Review | `/dominion:review` | Reviewer | review.toml — quality findings, architecture compliance |
| 7. Improve | `/dominion:improve` | All | Improvement proposals, knowledge capture |

Use `/dominion:orchestrate` to drive the full pipeline end-to-end. It supports auto-mode (`--auto`) for autonomous execution with circuit breakers, checkpoint resume, and direction-aware step routing.

For small, well-scoped changes that don't need the full ceremony, use `/dominion:quick`.

## Agents

Dominion generates 18 agents, each with industry-standard methodology, prescribed tool routing, and structured research protocols. Agents interact with project state exclusively through the `dominion-cli` CLI.

### Core Agents

Always present in every Dominion project.

| Role | Model | Purpose |
|------|-------|---------|
| Researcher (A1) | Opus | Deep codebase and ecosystem analysis. Structured findings with evidence grades. |
| Architect (A2) | Opus | Translates research into executable plans with wave grouping and dependency ordering. |
| Developer (A3) | Sonnet | Implements plan tasks with atomic commits, following project conventions. |
| Tester (A4) | Sonnet | Writes tests, validates acceptance criteria, identifies coverage gaps. |
| Reviewer (A5) | Opus | Post-phase quality assessment: code quality, architecture compliance, cross-task patterns. |
| Advisor (A6) | Opus | Human-facing interface. Onboards developers, explains decisions, manages preferences. |
| Analyst (A7) | Sonnet | Benchmarks, regression detection, metrics visualization, data quality validation. |
| Security Auditor (A8) | Opus | Dependency audits, permission reviews, crypto/auth/unsafe code analysis. Always active. |
| Secretary | Sonnet | System maintenance. Generates agent files, manages AGENTS.md, handles session lifecycle. |

### Specialist Agents

Activated when Dominion detects relevant languages, frameworks, or infrastructure in your project.

| Role | Model | Activated By |
|------|-------|-------------|
| Frontend Engineer (S1) | Sonnet | React, Vue, Svelte, Angular, Next.js, Nuxt |
| API Designer (S2) | Opus | OpenAPI, GraphQL, gRPC frameworks |
| Database Engineer (S3) | Sonnet | PostgreSQL, MySQL, SQLite, MongoDB, ORMs, migration directories |
| DevOps (S4) | Sonnet | Docker, GitHub Actions, GitLab CI, Helm Charts |
| Cloud Engineer (S5) | Sonnet | Terraform, Pulumi, CDK, AWS/GCP/Azure |
| Technical Writer (S6) | Sonnet | docs/ directories, ADR directories |
| Observability Engineer (S7) | Sonnet | Prometheus, Grafana, DataDog, New Relic |
| Release Manager (S8) | Sonnet | Release workflows, version management |
| Innovation Engineer (S9) | Opus | Opt-in only (user-requested) |

The Innovation Engineer applies structured invention methodologies (TRIZ, SIT, Axiomatic Design, TOC, Morphological Analysis) to resolve engineering contradictions and trade-offs. It operates in dual mode: pipeline (solving problems) and improve (auditing the methodology itself).

## Skills

14 user-facing commands available via `/dominion:*`.

### Pipeline Skills

| Command | Description |
|---------|-------------|
| `/dominion:discuss` | Capture user intent — goals, scope, constraints, priorities |
| `/dominion:explore` | Researcher-driven codebase analysis producing structured findings |
| `/dominion:plan` | Architect-driven planning with wave grouping and acceptance criteria |
| `/dominion:execute` | Developer-driven parallel task execution with worktrees and signals |
| `/dominion:test` | Tester-driven acceptance validation and coverage gap analysis |
| `/dominion:review` | Reviewer-driven quality assessment with improvement proposals |
| `/dominion:improve` | Post-pipeline retrospective and ad-hoc methodology expansion |

### Utility Skills

| Command | Description |
|---------|-------------|
| `/dominion:init` | Analyze your project and generate the full AI development methodology |
| `/dominion:orchestrate` | Drive the full pipeline end-to-end with auto-resume and user control points |
| `/dominion:validate` | Check config integrity, agent consistency, and CLI completeness |
| `/dominion:status` | Display project status dashboard — phase progress, blockers, backlog |
| `/dominion:quick` | Lightweight task execution for small, well-scoped changes |
| `/dominion:claim` | Merge Dominion into a project with an existing Claude Code setup |
| `/dominion:release` | Generate changelog, PR synopsis, and release notes. Optionally publish. |

## CLI Toolkit

`dominion-cli` is the exclusive data access layer for all `.dominion/` TOML files. It ships pre-built with the plugin and is installed during `/dominion:init`. All 18 agents read and write project state through CLI commands — no agent edits TOML files directly.

### Installation

The CLI is installed automatically during init. To install manually:

```bash
cd your-project
uv tool install ./path-to-dominion/cli
```

### Usage

```bash
# Check current pipeline position
dominion-cli state position

# Resume context at session start
dominion-cli state resume

# List active agents
dominion-cli agents list

# Show task details for the current plan
dominion-cli plan task 1-03

# Raise a blocker signal
dominion-cli signal blocker --task 1-03 --reason "API schema undefined" --level phase

# Read any TOML value (generic escape hatch)
dominion-cli data get dominion.toml --key project.name

# Write any TOML value
dominion-cli data set state.toml --key position.step --value '"execute"'

# All commands support JSON output
dominion-cli state position --json
dominion-cli agents list --json
```

### Command Reference

**54 commands** across 22 groups. All commands support `--json` for machine-readable output.

| Group | Commands | Description |
|-------|----------|-------------|
| `state` | `resume`, `position`, `update`, `checkpoint`, `decision`, `decisions`, `defer`, `deferred`, `blockers` | Session position, decisions log, blockers, checkpoints, deferred items |
| `agents` | `list`, `show`, `generate` | List agents, show config, regenerate `.claude/agents/*.md` and `AGENTS.md` |
| `plan` | `task`, `wave`, `deps`, `handoff`, `index`, `validate` | Task details, wave view, dependency graph, handoffs, plan validation |
| `signal` | `blocker`, `warning`, `list`, `resolve` | Raise/resolve blockers and warnings between agents |
| `research` | `findings`, `finding`, `opportunities`, `summary` | Filter findings by severity, view opportunities, research summaries |
| `phase` | `init`, `status`, `progress` | Initialize phases, view status, track task completion |
| `wave` | `create`, `status`, `merge` | Create wave directories, track wave progress, trigger merges |
| `report` | `create`, `finalize` | Create and finalize test/review artifacts |
| `backlog` | `add`, `list`, `suggest` | Capture ideas, filter by priority/status, get smart suggestions |
| `metrics` | `show`, `trends`, `baseline` | Phase metrics, cross-phase trends, baseline measurements |
| `improve` | `list`, `show`, `update` | List proposals, show details, update proposal status |
| `auto` | `readiness`, `decisions`, `start`, `stop`, `log` | Pre-flight checks, autonomous decision logging, auto mode control |
| `security` | `scan`, `findings`, `finding`, `track` | Run security scans, list/show findings, track across phases |
| `release` | `prepare`, `publish`, `status` | Prepare changelog, publish release, check release spec |
| `doc` | `generate`, `show` | Generate and display DOMINION.md project overview |
| `zone` | `check` | Check direction zone for file paths |
| `profile` | `show`, `set`, `tick` | View/update user preferences, increment session count |
| `roadmap` | `show`, `phases` | Display roadmap summary and phase objectives |
| `style` | `check` | Check code against style.toml conventions |
| `knowledge` | `sync`, `search` | Sync MEMORY.md from knowledge index, search by topic |
| `data` | `get`, `set` | Generic read/write for any `.dominion/` TOML file (escape hatch) |
| *(top-level)* | `validate`, `rollback`, `history` | Config integrity check, rollback to safe boundary, commit history |

### Key Design Principles

- **CLI is the only interface** — agents never read or write `.dominion/` TOML files directly
- **`data get`/`data set`** are the generic escape hatch — when `/dominion:improve` creates a new TOML file type, agents can immediately access it without waiting for a dedicated command
- **Path traversal protection** — `data get`/`data set` refuse `..` and absolute paths outside `.dominion/`
- **Agent discovery** — `agents generate` reads `cli-spec.toml` to produce a "CLI Commands Available" section in each agent's `.md` file, with command descriptions and the governance rule

## Project Detection

Dominion adapts to your project by analyzing what's in it. Detection tables identify languages, frameworks, and infrastructure to customize agents, conventions, and tool configurations.

### Languages (20)

Three tiers of support:
- **Full** — deep conventions, formatters, linters, test runners, LSP config (Rust, Python, TypeScript, Go, Java, Kotlin, C#, Ruby, PHP, Elixir, Clojure, Scala)
- **Standard** — solid detection with basic conventions (C++, C, Swift, Haskell, Dart, Lua, R, and more)
- **Detected** — file detection and extension mapping

### Frameworks (33)

Detected across categories: web, ORM, testing, async runtime, validation, serialization, template engines.

Examples: Axum, Actix, FastAPI, Django, Flask, Next.js, Nuxt, Express, Spring Boot, Gin, React, Vue, Svelte, SQLAlchemy, Prisma, Diesel.

### Infrastructure (22)

Detected across categories: containerization, CI/CD, cloud, databases, observability, infrastructure-as-code.

Examples: Docker, Podman, GitHub Actions, GitLab CI, Terraform, Pulumi, PostgreSQL, MongoDB, Redis, Prometheus, Grafana, Kubernetes.

Detection results drive specialist agent activation, convention generation, and tool routing decisions.

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
/dominion:init
```

This walks through project analysis and a setup wizard. Dominion detects your languages, frameworks, and infrastructure, then generates agents, conventions, CLI toolkit, and governance rules tailored to your project.

### Run Your First Pipeline

```bash
# Full pipeline with user control points between steps
/dominion:orchestrate

# Or run individual steps
/dominion:discuss
/dominion:explore
/dominion:plan
/dominion:execute
/dominion:test
/dominion:review
/dominion:improve
```

### Quick Tasks

For small changes that don't need the full pipeline:

```bash
/dominion:quick
```

## Requirements

### Required MCPs

| MCP | Category | Critical | Install |
|-----|----------|----------|---------|
| serena | Code navigation | Yes | See [serena docs](https://github.com/serena-ai/serena) |
| echovault | Cross-agent memory | No | `pip install git+https://github.com/mraza007/echovault.git` |
| context7 | Documentation | No | `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest` |

### Required Plugins

| Plugin | Purpose | Install |
|--------|---------|---------|
| hookify | Governance hook creation | `/plugin marketplace install hookify` |
| skill-creator | Eval-driven skill authoring | `/plugin marketplace install skill-creator` |

### Recommended MCPs

| MCP | Category | Install |
|-----|----------|---------|
| sequential-thinking | Multi-step reasoning | `claude mcp add sequential-thinking -- npx -y @anthropic/sequential-thinking-mcp` |
| github | GitHub operations | `claude mcp add github -- npx -y @anthropic/github-mcp` |

When a critical MCP (serena) is unavailable, Dominion halts with an error. Non-critical MCPs degrade gracefully — agents fall back to alternative tools with reduced effectiveness.

## Project Structure

For contributors — this is the plugin's own layout.

```
skills/                    14 user-facing skills (/dominion:* commands)
  {name}/
    SKILL.md               Skill definition with YAML frontmatter
    references/            Sub-step instruction files

templates/
  agents/                  18 agent TOML templates (9 core + 9 specialist)
  schemas/                 18 TOML schema definitions
  references/              11 shared reference files
  cli-spec.toml            CLI specification (54 commands)
  dominion-md.md           Project overview template

data/detection/
  languages.toml           20 language detection entries
  frameworks.toml          33 framework detection entries
  infrastructure.toml      22 infrastructure detection entries
  roles.toml               10 specialist role activation rules

registry/
  registry.toml            Curated MCP, plugin, and LSP evaluations

.claude-plugin/
  plugin.json              Plugin manifest
  marketplace.json         Marketplace metadata
```

This is not a traditional codebase. There is almost no application code. The product is:
- **Skill files** (markdown) — instructions Claude follows during `/dominion:*` commands
- **TOML data** — detection tables, agent templates, schemas, CLI specification
- **Reference files** (markdown) — reusable sub-step instructions referenced by skills

## Version History

| Version | Highlights |
|---------|------------|
| 0.1.1 | Stabilization — agent dispatch protocol, execution resilience, governance fixes, dependency management |
| 0.1.0 | Initial release — 14 skills, 18 agents, 54 CLI commands, 7-step pipeline, auto mode, brownfield claim, improvement loop |

## License

[MIT](LICENSE)
