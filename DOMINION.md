# Dominion — Design Document

> Your AI development team, generated from your codebase.

**Status:** Design phase
**Origin:** Born from the practical experience of building a complex project with AI agents, after discovering the limitations of existing solutions (GSD's blind subagents, MCP context loss, architectural drift from unsupervised agents).

---

## Table of Contents

- [Key Terms](#key-terms)
1. [Vision & Positioning](#1-vision--positioning)
2. [Architecture](#2-architecture)
3. [Initialization](#3-initialization)
4. [Agent System](#4-agent-system)
5. [Methodology Pipeline](#5-methodology-pipeline)
6. [Tool Ecosystem](#6-tool-ecosystem)
7. [CLI Tooling](#7-cli-tooling)
8. [Project Configuration](#8-project-configuration)
9. [User Experience](#9-user-experience)
10. [Security Model](#10-security-model)
11. [Roadmap](#11-roadmap)
12. [Known Risks & Mitigations](#12-known-risks--mitigations)

### Key Terms

| Term | Meaning |
|------|---------|
| **Phase** | A major unit of work with a goal (e.g., "Group Chat & Social"). Contains multiple plans/tasks. |
| **Plan** | A structured task within a phase, defined in plan.toml. Has acceptance criteria, file ownership, dependencies. |
| **Task** | Synonym for plan in execution context. One task = one Developer agent = one atomic commit. |
| **Wave** | A group of tasks with no mutual dependencies, executed in parallel. Phases are split into sequential waves. |
| **Step** | A pipeline stage: discuss, explore, plan, execute, test, review, improve. |
| **Signal** | Real-time communication between agents: blockers (halt) or warnings (FYI). |
| **CLI Spec** | Language-agnostic command specification (`.dominion/specs/cli-spec.toml`) that agents implement at init. |
| **Handoff** | Targeted note from one task to a downstream task, attached to plan.toml. |
| **Attendant** | System-facing agent that maintains artifacts: generates .md from TOML, manages settings, handles session lifecycle. |

---

## 1. Vision & Positioning

### The Problem

Claude Code is powerful. Configuring it shouldn't be a project.

A developer installs Claude Code and faces an invisible maze: MCPs exist but there's no guide to which ones matter. Plugins exist but quality varies wildly — will a Python agent write idiomatic code or unreadable spaghetti? GSD looks promising until its subagents lose MCP access mid-session. Hooks, agents, skills, CLAUDE.md, AGENTS.md — all powerful, none discoverable.

Teams compound the problem. One developer builds a productive setup over weeks of trial and error. Their teammate has no idea what was configured or why. A new hire joins without prior AI-development experience and nobody has budget for a consultant to run "AI integration sessions."

The knowledge of how to work effectively with Claude Code is itself the product — not just the tooling, but the methodology, baked into configuration that teams commit and share.

### The Solution

Dominion analyzes your project and generates a complete AI development methodology: specialized agents, curated tools, governance rules, code conventions, git workflow, and a CLI toolkit — all committed to git. New developers get best practices on `git clone`. The system improves itself after every phase.

### One-Liner

**Dominion** — commit your AI methodology to git. Every developer gets best practices automatically.

### The 4X Metaphor

Dominion maps to the 4X strategy genre — eXplore, eXpand, eXploit, eXterminate:

| Phase | 4X | Agent | Action |
|-------|-----|-------|--------|
| Research | eXplore | Researcher | Discover the project, analyze the codebase and ecosystem |
| Plan | eXpand | Architect | Design the expansion, plan the approach |
| Execute | eXploit | Developer + Tester | Exploit the plan, implement and validate |
| Review | eXterminate | Reviewer | Exterminate bugs, defects, drift |

### Target Audience

| Audience | Message |
|----------|---------|
| Solo dev, new to Claude Code | Go from zero to productive in one command |
| Solo dev, experienced | Systematize what you've been doing manually |
| Team lead | Give every developer your best practices on day one |
| Consultant / AI adoption lead | Deploy a proven AI methodology across projects |

### Key Differentiators

| Problem | What people do now | Dominion |
|---------|-------------------|----------|
| "What MCPs should I use?" | Read Discord for hours | Curated recommendations based on your stack |
| "How do I set up agents?" | Copy someone's AGENTS.md or use GSD | Generated from your project's actual structure |
| "My teammate doesn't know my setup" | Pair programming / wiki pages | `git clone` — everything works |
| "Agents keep drifting from architecture" | Hope for the best | Governance rules with hard stops |
| "I'm burning tokens reading huge docs" | Accept it | CLI tools for surgical document access |
| "I don't know best practices for my language" | Learn over years | Encoded in generated CLAUDE.md |
| "New plugin dropped, should I use it?" | FOMO + trial and error | Registry with community ratings |
| "My agents reverse-engineer APIs from source" | Didn't even notice | Documentation fallback chain with enforcement |

---

## 2. Architecture

### Design Principle

The plugin is the **author**. The artifacts are the **runtime**.

A developer who clones the repo gets a working AI methodology without installing Dominion — CLAUDE.md, AGENTS.md, hooks, and the CLI tool are all self-contained. Dominion is only needed to create, evolve, and improve the setup.

### Component Diagram

```
+--------------------------------------------------+
|  Dominion Plugin (Claude Code)                   |
|  +------------+ +------------+ +---------------+ |
|  | Discovery  | | Generator  | | Improvement   | |
|  | Engine     | | Engine     | | Loop          | |
|  +------------+ +------------+ +---------------+ |
|       |               |               |          |
|  Researcher     Attendant/CLI     Reviewer       |
|  analyzes        produces        proposes        |
|  project         artifacts       upgrades        |
+------------------------+-------------------------+
                         | generates
                         v
+--------------------------------------------------+
|  Project Artifacts (committed to git)            |
|  +----------+ +----------+ +------------------+ |
|  | CLAUDE.md| | AGENTS.md| | .claude/         | |
|  | (rules,  | | (team,   | |  agents/*.md     | |
|  | practice)| | roles)   | |  settings.json   | |
|  +----------+ +----------+ +------------------+ |
|  +-------------------+ +----------------------+ |
|  | dominion-tools/   | | .dominion/           | |
|  | (CLI in project   | |  dominion.toml       | |
|  |  language)        | |  agents/*.toml       | |
|  +-------------------+ |  phases/             | |
|                         |  skills/             | |
|                         |  templates/          | |
|                         |  registry.toml       | |
|                         +----------------------+ |
+--------------------------------------------------+

+--------------------------------------------------+
|  User-Local (never committed)                    |
|  ~/.claude/.dominion/                            |
|    user-profile.toml                             |
|    global-preferences.toml                       |
|    registry-overrides.toml                       |
+--------------------------------------------------+
```

### Dependencies (Official SDKs Only)

- **Claude Code Plugin SDK** — plugin structure, settings, lifecycle
- **Claude Agent SDK** — spawning and managing agents via `claude --agent`
- **Skill development tools** — creating custom skills in official format
- **MCP client** — checking available MCPs, configuring them

### Platform Dependencies

Dominion v1 targets Claude Code exclusively. The following Claude Code mechanisms are load-bearing:

| Mechanism | Dominion usage |
|-----------|---------------|
| `.claude/agents/*.md` format | Agent instruction delivery |
| `claude --agent <name>` | Agent spawning with full MCP access |
| `CLAUDE.md` auto-loading | Project instructions in every session (including spawned agents) |
| `~/.claude/projects/<hash>/memory/MEMORY.md` | Hot cache auto-loading (zero-cost retrieval) |
| `.claude/settings.json` | Permission pre-approval for MCP and CLI tools |
| `.claude/hooks/` | Hookify rules for governance enforcement |
| Claude Code Plugin SDK | Plugin lifecycle, skills, commands |
| Claude Agent SDK | Agent management and spawning |
| Skill development tools | Custom skill creation in official format |

Future versions may abstract platform dependencies to support other AI coding tools (Cursor, Windsurf, Copilot). v1 does not — deep Claude Code integration is intentional.

### Directory Responsibilities

| Directory | Committed | Purpose |
|-----------|-----------|---------|
| `.dominion/` | Yes | Config, agent definitions (.toml), phases, skills, templates, metrics, registry, signals |
| `.dominion/knowledge/` | Yes | Portable project knowledge: gotchas, API patterns, debugging history, decision archive |
| `.dominion/signals/` | Yes | Transient blocker/warning files for inter-agent communication (cleared after resolution) |
| `.dominion/specs/` | Yes | CLI command specification (`cli-spec.toml`) + output schemas |
| `dominion-tools/` | Yes | CLI source code in project's own language (implemented from spec at init) |
| `.claude/agents/` | Yes | Agent instruction files (.md) |
| `.claude/settings.json` | Yes | Pre-approved MCP permissions, tool allow-lists |
| `.claude/hooks/` | Yes | Hookify rules for governance enforcement |
| `~/.claude/projects/.../memory/` | **No** | Project MEMORY.md — auto-loaded hot cache, hydrated from `.dominion/knowledge/` |
| `~/.claude/.dominion/` | **No** | User profile, global preferences, personal tool opinions |

---

## 3. Initialization

### 3.1 Greenfield — `dominion init`

Two modes: **quick start** (reasonable defaults, minimal questions) and **full setup** (comprehensive interrogation). The wizard offers quick start by default and suggests full setup is available for those who want fine-grained control.

**Flow:**

```
dominion init
  -> Researcher performs project discovery
     (languages, frameworks, infra, patterns, quality, team conventions)
  -> Wizard cross-references registry for tool recommendations
  -> Wizard presents curated recommendations
  -> User approves / adjusts
  -> Generator produces all artifacts
  -> dominion-tools built from source
  -> dominion validate confirms everything works
```

**Example quick start session:**

```
> /dominion:init

  Analyzing project...
  Rust (5 crates), Python (tooling), Docker, GitHub, PostgreSQL

  Recommended setup:
    Agents:  Researcher, Architect, Developer, Tester, Reviewer, Advisor, Security Auditor, Attendant
    MCPs:    context7, serena, sequential-thinking, github
    Git:     conventional commits, squash merge, branch protection
    Style:   rustfmt + clippy, ruff + pyrefly, thiserror/anyhow

  Generate with these defaults? [Y / full setup / customize]
```

**Example full setup** covers: direction/intent, detailed style preferences, git workflow, knowledge bases, tool-by-tool MCP review, specialized role selection, do's and don'ts free text.

### 3.2 Brownfield — `dominion claim`

For projects with an existing Claude Code setup. Dominion detects everything already configured and proposes a claim plan.

**Claim principles:**

| Principle | Rule |
|-----------|------|
| Never delete user work | Existing rules, hooks, configs are sacred. Merge, never replace |
| Detect, don't assume | Custom MCP found? Preserve it. Unknown? Ask |
| Flag conflicts, don't resolve | GSD vs Dominion orchestration? Present the conflict, user decides |
| Adopt existing CLI tools | Project already has a CLI? Register and extend, don't compete |
| Diff-based changes | Show exactly what changes, additions, and reorganizations are proposed |
| Idempotent | Running claim twice doesn't break anything |

**Claim detects and handles:**

- `CLAUDE.md` — merges existing rules into Dominion's structure, preserves all custom rules
- `AGENTS.md` — upgrades to structured format, renames agents to Dominion conventions
- `.claude/settings.json` — extends with new MCP permissions, preserves existing
- `.claude/hooks/` — preserves existing hookify rules, adds Dominion lifecycle hooks
- MCPs (including custom/unknown) — preserves all, suggests additions
- Plugins — preserves compatible ones, flags conflicts
- Existing CLI tools — adopts as Dominion-managed, proposes extensions

Post-claim, `.dominion/dominion.toml` records what was preserved, what was added, and what was user-original. Future upgrades know not to touch user-original content.

---

## 4. Agent System

### 4.1 Core Team (8 Agents — Always Present)

| # | Agent | Faces | Model | Color | Purpose |
|---|-------|-------|-------|-------|---------|
| 1 | **Researcher** | Codebase + ecosystem | opus | cyan | Deep codebase and ecosystem analysis. Produces research.toml with findings, risks, and recommendations. Detects ecosystem opportunities (better tools, deprecated deps, emerging patterns) |
| 2 | **Architect** | Plans + designs | opus | blue | Translates research into executable plans with verified file references, dependency ordering, and wave grouping. Produces plan.toml files. Instructions adapt to project domain (distributed systems, frontend, embedded, etc.) |
| 3 | **Developer** | Code | sonnet | green | Implements plan tasks with atomic commits. Follows plan exactly, documents tool usage and friction in SUMMARY.md. Escalates architectural decisions, never makes them |
| 4 | **Tester** | Code + specs | sonnet | yellow | Writes and maintains tests: unit, integration, property-based, edge cases. Produces test-report.toml with coverage analysis and gap identification. Validates acceptance criteria from plans. Always available, activated during `/dominion:test` and on-demand |
| 5 | **Reviewer** | Code + process | opus | red | Post-phase quality verification: code quality, architecture compliance, process adherence, test coverage. Produces review.toml with findings and improvement proposals for agent instructions and tooling |
| 6 | **Advisor** | Human | opus | magenta | Human-facing interface. Onboards new developers, explains system decisions in context, manages user profiles, controls progressive disclosure. Collects structured phase feedback |
| 7 | **Security Auditor** | Skills + deps + permissions + unsafe code | opus | red | Evaluates foreign skills/agents/plugins for internalization. Audits dependencies for vulnerabilities. Validates MCP permission scopes. Reviews crypto, auth, `unsafe` blocks, FFI boundaries, `no_std` code, raw pointer usage, custom allocators, and memory safety invariants |
| 8 | **Attendant** | System + artifacts | sonnet | blue | System maintenance agent. Generates agent .md files from TOML, manages AGENTS.md and settings.json, handles session lifecycle hooks, inter-wave checkpoints, MEMORY.md hydration, and applies approved improvement proposals |

**The Researcher** actively looks for ecosystem opportunities — not just cataloging what the project uses, but evaluating whether better alternatives exist. When the Researcher identifies an opportunity (e.g., "argparse could be replaced by Typer"), the recommendation flows through the paper trail: research.toml documents the finding, the Reviewer validates it against real code evidence in review.toml, and the Advisor presents it to the user during `/dominion:improve`.

**The Advisor agent** faces the human, not the code. Responsibilities:

- Explain phase results in plain language, translate technical changes into human-readable summaries
- Onboard new developers to the project and Dominion setup
- Answer "why" questions about agent decisions, summarize colleague PRs and changes
- Maintain user profile based on explicit preferences and structured phase feedback
- Manage progressive disclosure — introduce features gradually across sessions
- Conduct phase retrospectives — collect targeted feedback at defined touchpoints
- Present improvement proposals for user approval

**The Attendant agent** faces the system, not the human. Responsibilities:

- Generate `.claude/agents/*.md` from `.dominion/agents/*.toml` (hybrid model — see §4.3)
- Regenerate AGENTS.md when agent config changes
- Generate CLAUDE.md at init (ultrathink, one-time synthesis)
- Manage `.claude/settings.json` permissions
- Session lifecycle hooks (state.toml update on start/end)
- Inter-wave checkpoints (hydrate MEMORY.md, apply handoffs)
- Apply accepted improvement proposals (update TOML, regenerate affected .md files, sync style stores)

**Advisor vs Attendant:** The Advisor decides *what* to propose to the human. The Attendant executes *how* to apply it to the system. During init, the Attendant generates all artifacts; the Advisor explains what was generated. During `/dominion:improve`, the Advisor presents proposals; the Attendant applies accepted ones.

### 4.2 Specialized Roles (9 — Activated by Project Type)

| # | Role | Activated When | Purpose |
|---|------|---------------|---------|
| 9 | **DevOps** | CI/CD, Docker, deployment configs | Pipeline design, container optimization, build caching, deployment strategies. Produces and maintains CI/CD configs and Dockerfiles |
| 10 | **Frontend Engineer** | Frontend framework detected | Component architecture, state management, styling patterns, accessibility compliance, frontend build tooling and optimization |
| 11 | **Database Engineer** | Database, ORM, schema files | Schema design and normalization, query optimization, migration authoring and chain validation, index analysis. Covers SQL and NoSQL |
| 12 | **Cloud Engineer** | Terraform, CDK, Pulumi, cloud configs | Infrastructure-as-code authoring, IAM policy design, networking topology, managed service configuration, cost optimization |
| 13 | **Observability Engineer** | Metrics, tracing, logging configuration | Monitoring stack setup, alert rule authoring, SLO/SLI definition, distributed trace instrumentation, dashboard design |
| 14 | **API Designer** | OpenAPI specs, API-heavy projects | Contract-first API design, versioning strategy, schema validation, REST/GraphQL/gRPC patterns, backward compatibility analysis |
| 15 | **Analyst** | Benchmarks, data pipelines, metrics, performance-critical code | Combines measurement disciplines: benchmark authoring, regression detection, flame graph analysis, allocation profiling, data quality validation, query performance analysis, schema evolution tracking, and project metrics visualization. Produces structured findings with measured impact |
| 16 | **Technical Writer** | Large/team projects | API documentation, ADRs, architecture diagrams (Mermaid/D2), changelogs, onboarding guides. Keeps docs in sync with code changes |
| 17 | **Release Manager** | Versioned project with release history | Changelog generation, semantic version bumps, release note drafting, tag management, release branch coordination |

**Testing specializations** (adversarial, TDD, integration, property-based) are not separate agents — they are **testing styles** configured in the Tester's TOML config. The wizard proposes a testing style during init based on project characteristics, and users can request additional styles through the Advisor at any time.

```toml
# Example: Tester TOML with testing styles
[testing]
styles = ["unit", "integration", "property-based"]
# Available: unit, integration, adversarial, tdd, property-based, e2e, contract, fuzz
# Proposed at init based on project type, adjustable via Advisor
```

**Unsafe/FFI/systems code** is handled by the Security Auditor (core #7), whose scope includes memory safety review, FFI boundary correctness, and concurrency primitive validation — alongside skills/deps/permissions/crypto.

Roles are templates. The wizard instantiates them with project-specific config (file ownership, tools, governance rules). Users can also create fully custom agents.

### 4.3 Definitions & Generated Artifacts

Each agent has one source of truth and two generated artifacts:

```
.dominion/agents/developer.toml     # source of truth (config)
.claude/agents/developer.md         # generated: agent instructions (for the agent)
AGENTS.md                           # generated: roster view (for humans/orchestrator)
```

**The TOML drives both outputs.** The Attendant reads the config and renders:
- `.claude/agents/*.md` — system prompt with startup sequence, tool routing, governance rules baked in
- `AGENTS.md` — human-readable roster (§4.3.1)

```
                                  ┌──→  .claude/agents/*.md  (agent reads this)
.dominion/agents/*.toml  ──→  Attendant
       (truth)                    └──→  AGENTS.md  (human/orchestrator reads this)
```

**Example `developer.toml`:**

```toml
[agent]
name = "Developer"
role = "developer"
model = "sonnet"
color = "green"
purpose = "Implement plan tasks with atomic commits, following code conventions"

[tools.mcps]
required = ["serena", "context7"]
optional = ["sequential-thinking"]
# MCPs are recommended from the official Claude MCP catalog if user has none.
# If user has custom MCPs already installed, they are incorporated here.

[tools.documentation]
# Ordered fallback chain for API docs. Language/framework-specific.
fallback = ["context7", "official-docs", "serena-memories", "stop-and-ask"]
# Agents should never parse library source code as default — last resort only.

[tools.skills]
custom = []  # populated during init if project needs domain-specific skills

[tools.cli]
commands = ["dominion-tools doc read", "dominion-tools doc write", "dominion-tools context"]

[governance]
architectural_decisions = "stop-and-report"
file_ownership = ["src/networking/", "src/database/"]
hard_stops = ["wire-format-changes", "new-tier3-deps"]

[workflow]
commit_style = "atomic"
pre_commit = ["fmt", "lint", "test"]    # language-specific: populated from style.toml
produces = "SUMMARY.md"
```

**How TOML config becomes agent instructions (hybrid model):**

Agent `.md` files have two parts: a **rigid scaffold** (deterministic, generated by the CLI tool) and a **free-form section** (LLM-synthesized, preserved across regeneration).

**Rigid scaffold** — mechanical translation from TOML, rebuilt on every `dominion-tools agents generate`:

| TOML section | Generated as |
|---|---|
| `[tools.mcps]` | `ToolSearch` calls in the mandatory startup sequence |
| `[tools.documentation]` | Documentation fallback chain with stop-and-ask terminal |
| `[tools.skills]` | Inline instructions or `@` file references in the body |
| `[tools.cli]` | Available commands listed in tool routing section |
| `[governance]` | Hard stops and escalation rules |
| `[workflow]` | Pre-commit gates, commit conventions, output requirements |
| `[agent]` | Frontmatter (`name`, `model`, `color`, `description`) |

**Free-form section** — synthesized by the Attendant at init, updated during agent evolution. Never touched by routine regeneration:

```markdown
## Role & Behavioral Instructions
<!-- GENERATED AT INIT — preserved on regeneration, updated during agent evolution -->
You are a Developer agent specializing in [project domain]...

## Domain Context
<!-- UPDATED DURING AGENT EVOLUTION — diff shown for approval -->
[Project-specific patterns, gotchas, conventions learned over phases]
```

**Regeneration rule:** `dominion-tools agents generate` rebuilds the rigid scaffold deterministically from TOML. It **never touches** the free-form sections. Free-form sections are only re-synthesized when explicitly triggered (agent evolution, `/dominion:educate`) and the diff is shown for user approval.

Agent `.md` files include a header: `<!-- Generated by Dominion from .dominion/agents/developer.toml — scaffold sections will be overwritten on regeneration. To customize, ask the Advisor or edit the free-form sections. -->`

The agent never reads its `.toml` — it follows its `.md` instructions. The TOML is the blueprint the Attendant uses to build those instructions.

### 4.3.1 AGENTS.md — Generated Roster

`AGENTS.md` is **auto-generated** from `.dominion/agents/*.toml` — never hand-edited. It serves as a human-readable overview of the active agent team and a quick-reference for the orchestrator. Generation flow shown in §4.3 above.

**Regeneration triggers:** init, agent activation/deactivation, agent evolution (§4.5). The Attendant triggers regeneration; the CLI tool (`dominion-tools agents generate`) does the deterministic rebuild.

**Sections:**

1. **Header** — project name, generation timestamp, "auto-generated by Dominion — do not edit manually"
2. **Active roster table** — name, model, one-line purpose. Only activated agents (core + specialists)
3. **File ownership map** — directory → agent. Shows who owns what at a glance
4. **Governance summary** — hard stops and escalation protocol (compact, references CLAUDE.md for full rules)
5. **Spawning reference** — per agent: invocation command, MCP tools, what it produces

**Not included** (lives elsewhere):
- Behavioral instructions → `.claude/agents/*.md`
- Full TOML config → `.dominion/agents/*.toml`
- Inactive/available roles → `dominion-tools agents list --available`
- Evolution history → `improvements.toml`

**Principle:** AGENTS.md shows *what exists and who owns what*. It doesn't explain how agents work internally — that's their individual files. If a human wants context beyond what's shown, they ask the Advisor.

### 4.3.2 CLAUDE.md — Generated Once, Human-Owned

Unlike AGENTS.md (continuously regenerated), CLAUDE.md is **generated as a draft at init, walked through with the user section by section, then owned by the human**. The Attendant produces the initial draft using ultrathink — synthesizing codebase analysis, style capture, convention detection, git workflow, governance rules, and user interview answers. The Advisor then reviews each section with the user: "Here's what I generated for your error handling conventions. Does this match how you work?" The user approves, edits, or rejects each section. After that, the human owns the result and can edit freely.

**Auto-loading:** CLAUDE.md is auto-loaded by Claude Code for all sessions, including agents spawned via `claude --agent` in worktrees (since CLAUDE.md is a committed file present in every worktree). No explicit read is needed in agent startup sequences, though agents may reference specific sections for reinforcement.

**Why not auto-generated like AGENTS.md:** AGENTS.md is a roster (data → view). CLAUDE.md is a manifesto (values + rules + style). It carries the developer's voice and preferences. Manifestos shouldn't be auto-regenerated after the first draft.

**Generation inputs:** project analysis, `style.toml`, `dominion.toml` (`[project]` + `[direction]`), user interview answers, detected conventions.

**Sections (target 150-300 lines):**

1. **Project** — what this is, tech stack, key decisions (compact, not a README)
2. **Mandatory rules** — hard stops, things that are never acceptable
3. **Language conventions** — per detected language, coding style, error handling, testing
4. **Tool routing** — which MCP tools to use when, CLI preferences, API doc lookup chain
5. **Git conventions** — branch naming, commit format, merge strategy, PR process
6. **Quality gates** — what must pass before committing
7. **Decision framework** — decide autonomously / flag and continue / stop and ask
8. **Observability** — tracing, metrics, logging expectations (if applicable)

**Not included** (lives elsewhere): agent roster (AGENTS.md), roadmap/progress (`roadmap.toml`, `state.toml`), detailed style rules (`style.toml`), project config (`dominion.toml`), domain knowledge (`.dominion/knowledge/`).

**Brownfield (`dominion claim`):** For projects with an existing CLAUDE.md, Dominion merges its generated sections with existing rules — preserving everything user-written, adding Dominion sections alongside. The merged result is presented as a diff for approval. After claim, ownership model is the same as init: human-owned.

**Post-init evolution:** The Advisor proposes changes as explicit diffs — urgent changes (missing hard stop discovered by Reviewer) as immediate proposals, routine refinements batched in `improvements.toml` for session-start review. Human approves or rejects each change. The Attendant applies accepted changes. The human's own edits are never overwritten.

### 4.4 Agent Governance

**Hard stops (agents STOP and report back):**

| If an agent is about to... | Rule |
|----------------------------|------|
| Make an architectural decision | STOP — human owns architecture |
| Use an unapproved dependency | STOP — check registry/architecture doc |
| Change wire format or stored data format | STOP — affects interoperability |
| Skip a required protocol step | STOP — security property removal needs approval |
| Deviate from the plan without documenting why | STOP — plan is the contract |

**Escalation protocol:**

1. Agent STOPS — does not proceed with deviation
2. Agent reports back: what the spec says, what's actually needed, and why
3. Orchestrator evaluates — if genuine spec issue, asks the human
4. Human decides — spec updated, then agent resumes

**File ownership:** Each agent owns exclusive write access to specific directories. No two agents touch the same files in the same wave. Shared types/interfaces are defined by the orchestrator first, committed, then agents implement against them.

### 4.5 Agent Evolution

Agent instructions evolve with the project. As the codebase grows, conventions solidify, and new patterns emerge, the agents that work on it should reflect those changes.

**How agents evolve:**

1. **Role activation** — Researcher discovers new project characteristics (database added, unsafe code introduced, CI pipeline created). Specialized roles auto-activate based on detection triggers. Reversible, no approval needed.
2. **Instruction refinement** — Developers report friction in SUMMARY.md ("had to look up X pattern repeatedly", "plan didn't account for Y concern"). Reviewer aggregates patterns across tasks into instruction improvement proposals. Applied after user approval.
3. **Style drift correction** — Code conventions emerge that weren't captured at init. Style capture re-runs, `style.toml` and agent instructions update to match observed patterns. Applied after user approval.
4. **Tool configuration** — Dependencies change, new frameworks appear. Documentation fallback chain updates, agent tool configs adjust. Applied after user approval.
5. **Architect domain adaptation** — The Architect's behavioral instructions adapt to the project domain. A distributed systems project gets failure mode analysis and consensus requirements. A frontend project gets component hierarchy and state flow guidance. This happens at init and refines over phases.

**Evolution approval rules:**

| Change type | Auto-apply? |
|-------------|-------------|
| New specialized role activation | Yes — detection-based, reversible |
| Style rule addition from observed patterns | Propose — user confirms |
| Agent instruction refinement | Propose — user confirms |
| Tool/MCP recommendation | Propose — user confirms |
| Removing a governance hard stop | **Never** — human only |

**The Reviewer proposes, the Advisor presents, the Attendant applies.** No agent modifies its own instructions autonomously. Evolution flows through the standard improvement loop (§5.4).

### 4.6 Custom Agent & Skill Creation

Two commands for extending Dominion's capabilities beyond the built-in roster.

#### `/dominion:educate` — Domain Knowledge Capture

Teaches Dominion domain knowledge from humans, documentation, or external sources. Uses the **Domain Knowledge Capture Protocol (DKCP)** — a 7-phase adaptive interview:

| Phase | What happens | Thinking level |
|-------|-------------|----------------|
| 1. **Domain Mapping** | Researcher identifies the domain, subdomains, and terminology | Normal |
| 2. **Stakeholder Mapping** | Who uses this, who regulates it, who breaks if it fails | Normal |
| 3. **Regulatory Scan** | Compliance requirements, standards, certifications | High effort |
| 4. **Deep Probe** | Adaptive follow-up on areas where captured knowledge is thin or contradictory | Ultrathink |
| 5. **Artifact Grounding** | Serena traces domain concepts to actual codebase symbols — anchors knowledge in reality | Normal |
| 6. **Knowledge Structuring** | Organizes captured knowledge into `.dominion/knowledge/` files | High effort |
| 7. **Calibration** | Presents structured knowledge back to user/expert for correction | Normal |

**Source integration:** `--from <source>` pulls from Notion (API), Confluence (API), Obsidian (local vault path), URLs (WebFetch), or local files. Researcher extracts, structures, and cross-references against codebase.

**Output routing:** Advisor analyzes captured scope and recommends:
- **Knowledge files** (`.dominion/knowledge/*.md`) — domain facts, glossaries, constraints
- **Skill** (`.dominion/skills/*.md`) — repeatable procedure extracted from domain workflow
- **Agent** (`.dominion/agents/*.toml` + `.claude/agents/*.md`) — specialized role needed for ongoing domain work. Attendant creates the TOML config and generates the agent instructions from it (§4.3).

Flags: `--agent` (force agent output), `--skill` (force skill output), `--from <source>` (pull from external source).

#### `/dominion:study <plugin>` — Plugin Internalization

Evaluates an existing plugin's skills/agents, security-reviews them, and produces Dominion-native artifacts that are refined beyond the original. Foreign plugin can be uninstalled afterward.

**Study pipeline (3 steps):**

| Step | Who | Purpose |
|------|-----|---------|
| 1. **Read & Assess** | Researcher + Security Auditor | Inventory the plugin (skills, agents, hooks). Security scan for prompt injection, data exfiltration, permission escalation. Assess: does this concretely benefit *this project*? |
| 2. **Kill Gate** | Advisor | "Does this pass the benefit threshold?" Must articulate specific scenarios where the skill fires and what outcome it improves. If no — stop here, no wasted tokens. |
| 3. **Recreate** | Researcher + Reviewer | Create Dominion-native version that critically tests and improves on the original. Combine studied patterns with project knowledge, agent architecture, and domain expertise. The studied skill is input, not template. Identify what's weak, what assumptions don't hold, what opportunities the original missed. Verify the result follows Dominion conventions. |

Step 2 is the gate. If a studied skill doesn't concretely benefit the project, the pipeline stops — no synthesis, no wasted tokens.

The recreation (Step 3) is not a copy — it must produce a better result than the original by leveraging project-specific knowledge, tighter integration with the agent model, and critical evaluation of the source material's assumptions.

Flags: `--skill <name>` (study one skill), `--agent <name>` (study one agent).

#### Domain Taxonomy

Dominion ships with a **question tree**, not a knowledge base. Enough structure to ask smart follow-ups during educate interviews (e.g., "You mentioned drug discovery — are you in target identification or lead optimization?"). The taxonomy expands dynamically: Researcher uses Context7/WebSearch for uncommon domains encountered during DKCP Phase 1.

---

## 5. Methodology Pipeline

### 5.1 Phase Lifecycle

**The pipeline:**

```
discuss → explore → plan → execute (waves) → test → review → improve
```

**Two ways to drive it:**

```
/dominion:orchestrate              # full pipeline, auto-resume from state.toml
/dominion:orchestrate --auto       # full pipeline, unattended (overnight)
```

Or step-by-step (individual commands):

```
/dominion:discuss   ->  Advisor      ->  Intent captured in dominion.toml / phase context
/dominion:explore   ->  Researcher   ->  research.toml (+ assumption verification)
/dominion:plan      ->  Architect    ->  plan.toml (wave-grouped, with assumptions section)
/dominion:execute   ->  Developer(s) ->  Code + SUMMARY.md + backlog + auto-state update
/dominion:test      ->  Tester       ->  test-report.toml
/dominion:review    ->  Reviewer     ->  review.toml + milestone audit when applicable
/dominion:improve   ->  All          ->  CLI extensions, config upgrades, new tools
```

Other commands (outside the pipeline):

```
/dominion:quick     ->  Developer    ->  Lightweight task, skip ceremony
/dominion:roadmap   ->  Advisor      ->  View/modify roadmap, add phases, audit milestones
/dominion:educate   ->  Advisor+Researcher -> Agent, skill, or knowledge files from domain knowledge
/dominion:study     ->  SecAuditor+Researcher+Attendant -> Dominion-native skills from existing plugins
```

**`/dominion:orchestrate`** — chains the full pipeline: discuss→explore→plan→execute→test→review→improve. Reads state.toml to determine current position and auto-resumes from where the phase left off. No `--from` or `--phase` flags needed — the state tracks everything.

```
/dominion:orchestrate

  Attendant: Phase 3 — reading state.toml...
    ✓ discuss (complete)
    ✓ explore (complete)
    ✓ plan (complete)
    ◐ execute (wave 2, blocked on task 03-07)
    ○ test
    ○ review
    ○ improve

    Blocker on task 03-07 resolved. Resuming execute, wave 2.
```

If no phase is in progress, orchestrate starts from discuss on the next roadmap phase.

**`/dominion:orchestrate --auto`** — unattended mode for overnight runs. Before starting, the Attendant checks that all expected tool permissions are pre-approved in settings.json, filling gaps if needed. Chains all steps automatically. Halts only on governance hard stops (architecture, security, data format). Logs all autonomous decisions for morning review. Queues improvement proposals instead of presenting them.

```
/dominion:orchestrate --auto

  Attendant: Auto mode. Checking readiness...
    Settings.json: 25 tool patterns pre-approved. No gaps.
    Hard stops: architecture, security, data format changes.
    Circuit breakers: 3 retries, 50k tokens per task.

    Running Phase 3. Will report when done or blocked.
```

**Individual step commands** — for manual control or redoing a step. Running `/dominion:explore` manually will redo exploration even if research.toml exists. After a manual step, `/dominion:orchestrate` picks up from the next step.

**`/dominion:discuss`** — Advisor asks the user about goals, constraints, and preferences for the next phase. References roadmap.toml for context. Captures human intent that pure codebase analysis would miss. Output feeds into Researcher's exploration scope.

**`/dominion:quick`** — for small tasks that don't need the full ceremony. Developer handles directly, writes a minimal SUMMARY.md, commits. No Researcher, no Architect, no wave planning. Still follows code conventions and commit style. Still goes through Reviewer if the change touches governance-sensitive files.

**`/dominion:educate`** — teach Dominion domain knowledge from humans, docs, or external sources (Notion, Confluence, Obsidian, URLs). Uses the Domain Knowledge Capture Protocol (§4.6). Advisor recommends output format (agent, skill, or knowledge files) based on captured scope. Flags: `--agent` (force agent), `--skill` (force skill), `--from <source>` (pull from external source).

**`/dominion:study <plugin>`** — evaluate an existing plugin's skills/agents through an 8-phase pipeline (§4.6) with extended thinking at critical stages. Security-reviews them, assesses whether they concretely benefit *this project* (kills anything that doesn't pass), then synthesizes Dominion-native artifacts refined beyond the originals. Flags: `--skill <name>` (one skill), `--agent <name>` (one agent). Foreign plugin can be uninstalled afterward.

**`/dominion:test`** — the Tester agent runs after execution completes. It:
1. Runs the project's existing test suite to verify nothing is broken
2. Validates acceptance criteria from plan.toml against the actual code (does each task's `done` criteria hold?)
3. Identifies test gaps — new code paths without test coverage
4. Writes new tests for uncovered paths when possible
5. Produces `test-report.toml` with: pass/fail counts, coverage delta, gaps identified, new tests written

**`/dominion:review`** — the Reviewer agent examines the full phase output. Inputs: code diff (phase branch vs main), test-report.toml, all summaries. It evaluates:
1. **Code quality** — style compliance, error handling, complexity
2. **Architecture compliance** — does the implementation match the plan and project conventions?
3. **Process adherence** — did Developers follow governance? Are SUMMARY.md files complete?
4. **Test coverage** — are gaps identified by the Tester acceptable?
5. **Cross-task issues** — patterns visible only when viewing all changes together
6. Produces `review.toml` with findings and improvement proposals (§5.4)
7. If a milestone boundary is reached, runs a milestone audit against `roadmap.toml` success criteria

**`/dominion:improve`** — Advisor presents review proposals to the user. Accepted proposals are implemented through the standard agent pipeline (Researcher validates, Architect plans, Developer builds, Attendant applies config changes). Changes target Dominion's own config: CLI commands, agent instructions, governance rules, hooks — not the project code.

**Assumption verification** — before execution begins, the Researcher validates assumptions listed in plan.toml. If an assumption is wrong (e.g., "the database supports nested transactions" — it doesn't), the plan is revised BEFORE Developer agents waste tokens on an impossible approach.

### 5.2 Wave-Based Parallel Execution

Plans are grouped into waves by dependency. Within a wave, agents execute in parallel using git worktrees with full MCP access:

1. Architect groups plans into waves (`dominion-tools plan index`)
2. For each wave, create worktrees for parallel execution
3. Spawn `claude --agent developer` per worktree (parallel, full MCP)
4. Merge worktree branches after wave completes
5. **Inter-wave checkpoint** — Attendant scans summaries, updates MEMORY.md and plan.toml handoffs
6. Proceed to next wave (Developers start informed)
7. After final wave: run Tester + Reviewer on merged result

**Inter-wave checkpoint (lightweight, not a full review):**

Between each wave, the Attendant performs a quick scan of completed summaries:

```
Wave 1 complete → merge
  │
  ▼
INTER-WAVE CHECKPOINT (~30 seconds)
  Attendant reads wave 1 summaries/task-*.md
  → Extracts gotchas → updates MEMORY.md (hot cache for next wave)
  → Applies targeted handoff notes to plan.toml downstream tasks
  │
  ▼
Wave 2 starts — Developers have:
  MEMORY.md (auto-loaded, free) with wave 1 gotchas
  plan.toml task (via CLI) with handoff notes from upstream tasks
```

This is NOT a review — no quality assessment, no improvement proposals. Just knowledge transfer between waves. The full review happens after all waves complete.

**Worktree lifecycle:**

1. Orchestrator creates worktrees: `git worktree add .worktrees/dominion-<task-id> -b dominion/<task-id>`
2. Each Developer agent runs in its own worktree directory with full MCP access
3. On task completion, Developer commits to the worktree branch
4. After all wave tasks complete, orchestrator merges worktree branches into the phase branch (`git merge --no-ff dominion/<task-id>`)
5. If merge conflicts occur: orchestrator halts, presents conflict to user. Agents do not resolve merge conflicts — that requires cross-task understanding
6. After successful merge, worktrees are cleaned up: `git worktree remove .worktrees/dominion-<task-id>`

`.worktrees/` is gitignored. Naming convention: `dominion-<task-id>` (e.g., `dominion-02-03`).

**Agent spawning:** The orchestrator (main Claude session or `/dominion:orchestrate`) spawns agents via `claude --agent <role>` with the task prompt as input. The agent reads its `.claude/agents/<role>.md` instructions, which contain the startup sequence generated from TOML config (§4.3).

**Agent failure handling:**

| Failure | Detection | Response |
|---------|-----------|----------|
| Token limit hit | Circuit breaker (§5.8) | Task marked incomplete in progress.toml, blocker signal raised |
| Agent crash / network error | No SUMMARY.md produced within timeout | Orchestrator retries once, then marks task as failed |
| Stuck in loop (3+ retries on same error) | Circuit breaker | Task halted, blocker signal raised with error context |
| Bad output (tests fail) | Quality gates in agent instructions | Agent retries with error feedback. After max retries, task marked failed |

Failed tasks don't block the entire wave — only tasks that depend on the failed task are paused. The orchestrator presents failures to the user for triage.

### 5.3 Inter-Agent Communication

**Core principle: agents PRODUCE signals and self-halt. The orchestrator CONSUMES signals and halts others.** LLM agents don't have polling loops — they execute sequentially. The signal mechanism is designed around this constraint.

#### Signal Types

| Signal | Effect | Example |
|--------|--------|---------|
| **Warning** | FYI to other agents — no halt, logged for review | "DB schema has extra index — queries may be slower than expected" |
| **Task blocker** | One task halts, others continue | "This API doesn't support pagination as assumed" |
| **Wave blocker** | All wave agents stop | "Shared types are wrong, all agents building on broken foundation" |
| **Phase blocker** | Entire phase paused | "Architecture spec contradicts what we need" |
| **Critical halt** | Everything stops, all modes | "Security vulnerability discovered in core dependency" |

#### Signal Mechanism

**Producer (agents):** When a Developer hits a problem, it writes a signal file via CLI and halts itself:

```bash
# Warning — FYI, no halt
dominion-tools signal warning --task 02-01 \
  "Extra index on users table — queries may be slower than expected"

# Blocker — agent writes signal and self-halts
dominion-tools signal blocker --level wave --task 02-03 \
  --reason "UserProfile type missing required field for OAuth flow"
# Creates .dominion/signals/blocker-02-03.toml
# Agent halts itself and writes partial SUMMARY.md
```

**Signal file format:**

```toml
[signal]
type = "blocker"           # blocker | warning
level = "wave"             # task | wave | phase | critical
task = "02-03"
agent = "Developer"
timestamp = "2026-03-07T14:30:00Z"
reason = "UserProfile type missing required field for OAuth flow"
affects = ["02-04", "02-05"]  # computed from dependency graph
```

**Consumer (orchestrator):** The orchestrator is running — it spawned the agents. While waiting for agents to complete, it polls `.dominion/signals/` periodically. On detection:

| Level | Orchestrator action |
|-------|-------------------|
| Task blocker | Pauses only dependent tasks |
| Wave blocker | Kills/pauses all wave agents |
| Phase blocker | Kills all agents, pauses phase |
| Critical halt | Kills everything immediately |

**Backup (pre-commit hook):** `.githooks/pre-commit` runs `dominion-tools signal list --json --affecting <task-id>`. If a blocker exists that affects this task's dependencies, the commit is rejected. Catches the case where the orchestrator hasn't acted yet.

Failed tasks don't block the entire wave — only tasks that depend on the failed task are paused. The orchestrator presents failures to the user for triage.

How blockers are handled depends on the autonomy mode — see §5.8.

#### Handoff Notes (Between Waves)

Developer A writes targeted handoff notes for downstream tasks:

```bash
dominion-tools plan handoff 02-01 --to 02-03 \
  "Connection pool is unbounded. Add max-connections or it leaks."
```

This attaches the note to task 02-03 in plan.toml. When Dev C queries their task:

```
dominion-tools plan task 02-03

  Task 02-03: Database migration handlers
  Wave: 2
  Depends on: 02-01 (complete)

  ⚠ Handoff from 02-01:
    "Connection pool is unbounded. Add max-connections or it leaks."
```

Combined with the inter-wave checkpoint (§5.2), wave 2 Developers start with both targeted handoffs (plan.toml) and universal gotchas (MEMORY.md).

### 5.4 The Improvement Loop

After every review phase, the Reviewer produces improvement proposals in review.toml. These are evaluated and implemented through the standard pipeline:

```toml
# review.toml — improvement proposals section

[[proposals]]
id = "P1"
type = "tooling"
title = "New CLI command: dominion-tools context <task-id>"
evidence = ["summaries/task-02-01.md", "summaries/task-02-04.md"]
reason = "Developer agents ran 3 separate lookups per task (x8 tasks). ~12,000 tokens wasted."
status = "pending"

[[proposals]]
id = "P2"
type = "governance"
title = "Hookify rule: warn on missing #[instrument]"
evidence = ["4 async I/O functions without tracing in review"]
reason = "Reviewer caught manually — should be automated."
status = "pending"

[[proposals]]
id = "P3"
type = "convention"
title = "Prefer &str in internal helpers"
evidence = ["summaries/task-02-02.md", "summaries/task-02-05.md"]
reason = "3 instances of unnecessary String allocation flagged."
status = "pending"
```

Proposals are presented to the user — never auto-applied:

```
/dominion:improve

  3 improvement proposals from Phase 2 review:
  [Accept / Reject / Modify] for each
```

Accepted proposals are implemented through the standard agent pipeline (Researcher validates, Architect plans, Developer builds, Attendant applies config changes), committed, and available for the next phase.

**Improvement journal:** All accepted and rejected proposals are logged in `.dominion/improvements.toml` with outcomes. Rejected proposals aren't re-proposed. Accepted proposals that get rolled back are flagged for review.

### 5.5 Document Ownership Map

**This is the authoritative reference for document ownership.** Individual sections (§4.3, §5.9, etc.) describe generation model and rationale — this table is the single source of truth for who creates, maintains, and reads each artifact. TOML files are accessed via `dominion-tools` CLI (surgical queries). Markdown files are read directly.

**Phase documents (per phase, in `.dominion/phases/<N>/`):**

| Document | Format | Created by | Read by | Accessed via |
|----------|--------|-----------|---------|-------------|
| `research.toml` | TOML | Researcher | Architect, Reviewer | `dominion-tools research` |
| `plan.toml` | TOML | Architect | Developer, Tester, Reviewer | `dominion-tools plan` |
| `progress.toml` | TOML | Developer (auto on commit) | All agents, rollback | `dominion-tools history` |
| `test-report.toml` | TOML | Tester | Reviewer | `dominion-tools report` |
| `review.toml` | TOML | Reviewer | Advisor, human | `dominion-tools report` |
| `summaries/task-*.md` | Markdown | Developer (one per task) | Reviewer, Attendant (inter-wave) | Read tool |

**Phase directory structure:**

```
.dominion/phases/2/
├── research.toml
├── plan.toml
├── progress.toml
├── test-report.toml
├── review.toml
└── summaries/
    ├── task-02-01.md
    ├── task-02-02.md
    └── task-02-03.md
```

**SUMMARY.md template** — the only markdown phase document. Developers document their task execution including tool usage, friction, and handoff notes. This feeds both the inter-wave checkpoint (§5.2) and the improvement loop (§5.4):

```markdown
# SUMMARY — Task <ID>: <Title>

## What was done
- <concise description of implemented changes>

## Tools used
- <MCP/CLI tools used and for what purpose>

## Friction encountered
- **Knowledge gap:** <missing docs, unfamiliar API>
- **Boilerplate:** <repetitive patterns needing abstraction>
- **Plan issue:** <assumptions that were wrong, scope underestimated>
- **Tooling:** <tool failures, slow workflows>

## Deviations from plan
- <any deviations and why>

## Handoff notes
- <context the next Developer or wave needs>

## Backlog items discovered
- [ ] <out-of-scope work tagged for future>
```

The "Friction encountered" section uses categories to help the Reviewer identify patterns across tasks (e.g., three Developers reporting "knowledge gap" for the same crate → systemic documentation issue).

**Project documents:**

| Document | Format | Created by | Maintained by | Read by | Accessed via |
|----------|--------|-----------|---------------|---------|-------------|
| `CLAUDE.md` | MD | Dominion init (ultrathink, one-time) | Human-owned; Advisor proposes diffs | All agents, Claude Code | Auto-loaded |
| `AGENTS.md` | MD | Auto-generated (`dominion-tools agents generate`) | Attendant (triggers regen) | All agents, human | Read tool |
| `dominion.toml` | TOML | Dominion init | Attendant | All agents | CLI |
| `roadmap.toml` | TOML | Dominion init | Attendant (auto-computed) | All agents, human | CLI, `/dominion:roadmap` |
| `state.toml` | TOML | Attendant (auto) | Attendant (session hooks) | All agents | CLI |
| `backlog.toml` | TOML | Developer | Attendant (prioritization) | Architect | CLI |
| `style.toml` | TOML | Dominion init | Reviewer→Attendant | Hooks, CLI | CLI |
| `registry.toml` | TOML | Ships with Dominion | Dominion updates | Security Auditor, Advisor | CLI |
| `metrics.toml` | TOML | Reviewer | Reviewer (after phase) | Advisor, Analyst | CLI |
| `improvements.toml` | TOML | Reviewer | Attendant (status) | All agents | CLI |

**Agent definitions:**

| Document | Format | Created by | Maintained by | Read by |
|----------|--------|-----------|---------------|---------|
| `.dominion/agents/*.toml` | TOML | Dominion init / `/dominion:educate` | Attendant | Agent spawner |
| `.claude/agents/*.md` | MD | Dominion init / `/dominion:educate` | Attendant | Spawned agents |
| `.dominion/skills/*.md` | MD | `/dominion:study` / `/dominion:educate` | Attendant | Spawned agents |
| `.dominion/knowledge/*.md` | MD | Any agent / Reviewer (curation) | Reviewer | Agents as needed |
| `.dominion/templates/*.md` | MD | Dominion init | Reviewer | All agents |

**Infrastructure:**

| Document | Format | Created by | Maintained by | Read by |
|----------|--------|-----------|---------------|---------|
| `.claude/settings.json` | JSON | Dominion init | Attendant | Claude Code |
| `.claude/hooks/*` | MD | Dominion init | Reviewer | Claude Code |
| `.githooks/*` | Shell | Dominion init | DevOps | Git |

**Knowledge layer (see §5.9):**

| Document | Format | Location | Maintained by | Read by |
|----------|--------|----------|---------------|---------|
| `MEMORY.md` | MD | `~/.claude/projects/.../memory/` (local) | Reviewer + Attendant (inter-wave) | All agents (auto-loaded, free) |
| `knowledge/*.md` | MD | `.dominion/knowledge/` (in git) | Reviewer (curation) | Agents as needed |

**User-local (never committed):**

| Document | Created by | Maintained by | Read by |
|----------|-----------|---------------|---------|
| `~/.claude/.dominion/user-profile.toml` | Attendant (first session) | Attendant (continuously) | Advisor |
| `~/.claude/.dominion/global-preferences.toml` | Attendant (on promote) | Attendant | Dominion init |
| `~/.claude/.dominion/registry-overrides.toml` | Attendant (on user rating) | Attendant | Dominion init |

**Key principle:** The Reviewer is the primary *proposer* of document changes (through improvement proposals). The Advisor *presents* proposals to the user. The Attendant is the primary *applier* (after user approval). No agent modifies project-level documents autonomously — everything flows through the proposal → approval → apply cycle.

### 5.6 Structured State Management

Project management data is stored in TOML (structured, CLI-accessible), not markdown. Agents interact with it through `dominion-tools`, never reading or writing entire files.

**`dominion.toml`** — unified project configuration (project identity + direction + operational config):

```toml
[meta]
schema_version = 1              # bumped on breaking format changes

[project]
name = "MyProject"
vision = "Brief description of what this project does"
target_users = "Who uses this and why"

[project.constraints]
team_size = "solo + AI agents"
hard_rules = ["No proprietary dependencies", "All encryption in pure Rust"]

[[project.success_criteria]]
description = "Encrypted 1:1 and group text chat"
status = "done"

[[project.success_criteria]]
description = "Encrypted group voice calls (5+ participants)"
status = "pending"

[direction]
mode = "improve"               # maintain | improve | restructure

[direction.restructure]
# Only populated when mode = "restructure"
target_state = "Migrate from monolith to microservices"
migration_strategy = "strangler-fig"

[[direction.restructure.legacy_zones]]
path = "src/legacy/"
policy = "minimal-touch"

# [documentation], [autonomy], [claim], [cli], [mcps] sections — see §5.8, §6.2
```

**`research.toml`** — Researcher output, structured findings:

```toml
[meta]
schema_version = 1
phase = 2

[[findings]]
id = "F1"
severity = "high"
category = "architecture"
title = "Connection pool lacks TTL cleanup"
description = "NetworkClient creates connections but never expires idle ones"
evidence = ["src/networking/client.rs:142", "src/networking/pool.rs:58"]
recommendation = "Add configurable idle timeout with default 300s"

[[findings]]
id = "F2"
severity = "medium"
category = "dependency"
title = "crypto crate v0.9 deprecated"
description = "Upstream recommends migration to v1.0 — breaking API changes"
evidence = ["Cargo.toml:24"]
recommendation = "Plan migration in next phase"

[[opportunities]]
id = "O1"
title = "Replace hand-rolled config parser with figment"
benefit = "Reduces 200 lines to ~30, adds env var support"
effort = "low"

[[assumptions]]
id = "A1"
text = "Database supports nested transactions"
status = "unverified"           # unverified | verified | false
verified_by = ""
```

**`plan.toml`** — Architect output, wave-grouped executable plan:

```toml
[meta]
schema_version = 1
phase = 2
title = "Group Chat & Social"

[[tasks]]
id = "02-01"
title = "Refactor NetworkClient for concurrency"
wave = 1
depends_on = []
agent = "Developer"
file_ownership = ["src/networking/"]

[tasks.acceptance]
criteria = [
  "NetworkClient is Send + Sync",
  "All existing tests pass",
  "New concurrency test with 3 parallel callers",
]
verify_command = "cargo nextest run -p core --test concurrency"

[[tasks.assumptions]]
ref = "A1"              # references research.toml assumption

[[tasks]]
id = "02-03"
title = "Database migration handlers"
wave = 2
depends_on = ["02-01"]
agent = "Developer"
file_ownership = ["src/database/"]

[tasks.acceptance]
criteria = [
  "Migration up/down for all Phase 2 entities",
  "Rollback tested",
]

[[tasks.handoffs]]
from = "02-01"
note = ""               # populated by Developer during execution
```

**`dominion.toml`** — unified project configuration. Combines project identity, operational config, and project direction into one file. Sections:
- `[project]` — name, vision, target users, success criteria, constraints
- `[direction]` — mode (maintain/improve/restructure), legacy zones, migration strategy
- `[documentation]` — fallback chain (§6.2)
- `[autonomy]` — circuit breakers and replan constraints (§5.8)
- `[claim]` — provenance (what was user-original vs Dominion-added)
- `[cli]` — spec version
- `[mcps]` — MCP and plugin configuration

**`roadmap.toml`** — milestones, phases, progress (auto-computed from plan completion):

```toml
[[milestones]]
name = "Ship v1"
target = "12 months"

[[milestones.phases]]
number = 1
name = "Foundation"
status = "complete"
plans_total = 7
plans_complete = 7

[[milestones.phases]]
number = 2
name = "Group Chat & Social"
status = "in-progress"
plans_total = 9
plans_complete = 6
```

**`state.toml`** — computed from ground truth, auto-maintained by Attendant + session hooks. Drives `/dominion:orchestrate` resume logic:

```toml
[position]
phase = 2
step = "execute"           # discuss | explore | plan | execute | test | review | improve
wave = 3
current_task = "02-05"
status = "active"          # active | blocked | complete
last_session = "2026-03-06"

[lock]
session_id = "abc123"       # set by /dominion:orchestrate, cleared on session end
locked_at = "2026-03-06T14:30:00Z"
expires_after_hours = 8     # matches circuit breaker session_time_limit_hours

[blocker]
task = "02-03"
level = "task"             # task | wave | phase | critical
reason = "API incompatibility needs Architect review"

[outstanding]
deferred = ["BP-01: ConnectionManager concurrency refactor"]

[[decisions]]
id = 14
phase = 1
task = "01-03"
agent = "Developer"
text = "DB driver reserves 'token' as keyword — use $auth_token instead"
tags = ["database", "gotcha"]
```

The `step` field tells `/dominion:orchestrate` exactly where to resume.

**Multi-developer concurrency (v1 limitation):** state.toml supports a single-writer lock. When `/dominion:orchestrate` starts, it claims the lock. A second session attempting orchestrate sees: "Phase 3 is being executed by another session. Use `/dominion:quick` for independent work." The lock auto-expires after `expires_after_hours`. `/dominion:quick` doesn't need the lock — it's atomic and doesn't advance phase state. Full multi-developer phase coordination (parallel phase ownership, concurrent wave execution) is planned for v1.x. When a step completes, state.toml auto-advances to the next step. When a blocker is resolved, status changes from "blocked" to "active" and orchestrate continues.

**`backlog.toml`** — ideas captured during execution, auto-tagged, suggested during planning:

```toml
[[items]]
id = 1
text = "Refactor NetworkClient for connection pooling"
tags = ["networking", "concurrency"]
source_task = "02-03"
mentioned_in_summaries = 2
priority = "high"
```

**`metrics.toml`** — phase-level quality and process metrics, generated by the Reviewer after each phase review:

```toml
[phase]
number = 2

[quality]
tests_added = 47
tests_passing = 47
clippy_warnings = 0
coverage_delta = "+12%"

[process]
tasks_completed = 9
tasks_replanned = 1
blockers_encountered = 2
average_tokens_per_task = 28000
improvement_proposals = 3

[trends]
tokens_per_task_delta = "-15%"    # vs previous phase
blocker_rate_delta = "-50%"
```

Used by the Advisor to track project health over time and by the Analyst (if activated) for deeper analysis. The `/dominion:improve` step references trends to validate whether past improvements had measurable impact.

**Why structured data over markdown:**

| Aspect | Markdown (GSD approach) | TOML + CLI (Dominion approach) |
|--------|------------------------|-------------------------------|
| Updating one field | Read entire file, edit, write back | `dominion-tools state update --wave 3` |
| Searching decisions | Agent reads all decisions to find relevant one | `dominion-tools state decisions --tags database` |
| Progress tracking | Manually typed percentages | Computed from file existence |
| Staleness | Goes stale if human forgets to update | Derived from ground truth, never stale |
| Token cost | ~2000 tokens to read STATE.md | ~200 tokens for CLI output |

**Session lifecycle (automatic via hooks):**

```
Session start:
  → Attendant runs dominion-tools state resume
  → Advisor presents: "Phase 2, Wave 3. Last: Task 02-05 done, Tester pending.
     1 blocker. 2 backlog items."
  → Adapts verbosity to user level

Session end:
  → Attendant computes delta from git log + files written
  → Updates state.toml position
  → Notes unfinished work
  → No explicit "pause" command needed
```

### 5.7 Commit Tracking & Rollback

Every wave and task records git commit boundaries in `.dominion/phases/<N>/progress.toml`:

```toml
[phase]
number = 2
started_at = "abc1234"

[[waves]]
number = 1
status = "complete"
started_at = "abc1234"
completed_at = "def5678"
merge_commit = "def5678"

[[waves.tasks]]
id = "02-01"
agent = "Developer"
status = "complete"
commits = ["aaa1111", "aaa2222"]
worktree_branch = "dominion/02-01"

[[waves]]
number = 2
status = "in-progress"
started_at = "def5678"

[[waves.tasks]]
id = "02-03"
agent = "Developer"
status = "blocked"
commits = ["ccc4444"]
blocker = "wave-blocker-02-03"
```

**Rollback commands:**

```bash
# Roll back to stable state before Wave 2
dominion-tools rollback --to-wave 1
# → "Wave 1 completed at def5678. Discard Wave 2 work (3 commits)? [Y/n]"

# Roll back a single task
dominion-tools rollback --task 02-03
# → "Task 02-03 has 1 commit (ccc4444). Revert? [Y/n]"

# Roll back entire phase
dominion-tools rollback --to-phase 1
# → "Discard ALL Phase 2 work (9 commits)? [Y/n]"

# View the commit map
dominion-tools history --phase 2
# Phase 2: Group Chat & Social
#   Wave 1 [complete]: abc1234 → def5678 (3 commits)
#     02-01: aaa1111, aaa2222
#     02-02: bbb3333
#   Wave 2 [in-progress]: def5678 → ... (1 commit)
#     02-03: ccc4444 (BLOCKED)
#     02-04: not started
```

Commit hashes are recorded automatically on task/wave completion — a byproduct of the workflow, not a manual step.

### 5.8 Autonomy Modes

Autonomy level and governance rules are independent. Autonomy controls whether agents continue without human input. Governance controls what decisions agents are allowed to make — regardless of mode.

**Two modes, driven by `/dominion:orchestrate`:**

| Mode | Command | Blocker behavior | User present? |
|------|---------|-----------------|---------------|
| **Interactive** | `/dominion:orchestrate` | Pause between steps, user approves each | Yes |
| **Auto** | `/dominion:orchestrate --auto` | Chain all steps, halt only on governance hard stops, attempt resolution for implementation blockers | No |

In interactive mode, the user drives step-by-step (or orchestrate pauses between each). In auto mode, the full pipeline runs unattended — agents attempt implementation blockers, log autonomous decisions, and halt only when governance requires it.

**Governance hard stops fire in both modes:**

- Cannot change architecture (crate boundaries, protocols)
- Cannot change wire format or stored data format
- Cannot add unapproved dependencies
- Cannot bypass Security Auditor on internalization
- Critical halts stop everything regardless of mode

**Circuit breakers (both modes) — prevent waste:**

```toml
[autonomy.circuit_breakers]
max_tokens_per_task = 50000
max_retry_attempts = 3
max_cascade_replans = 2
max_scope_expansion_percent = 20
session_time_limit_hours = 8        # 0 = no limit
```

**Replan constraints — what the Architect can change in auto mode:**

```toml
[autonomy.replan_constraints]
can_change_implementation_approach = true
can_substitute_approved_dependencies = true
can_reorder_tasks_within_wave = true
can_split_task = true
cannot_expand_phase_scope = true
cannot_add_new_dependencies = true
cannot_modify_architecture = true
cannot_change_file_ownership = true
```

**Autonomous decision audit trail:**

In auto mode, every autonomous decision is logged in `state.toml`:

```toml
[[autonomous_decisions]]
id = 1
timestamp = "2026-03-07T03:42:00Z"
task = "02-05"
agent = "Architect"
type = "task-replan"
original = "Use driver-level connection pool"
changed_to = "Use single connection with reconnect logic"
reason = "Driver does not support connection pooling natively"
constraints_checked = ["no scope expansion", "no new deps", "no arch change"]
```

User reviews autonomous decisions at next session start:

```bash
dominion-tools state autonomous-decisions --session last
# "2 autonomous decisions were made overnight:
#  1. Task 02-05 replanned: connection pool → single connection
#  2. Task 02-07 split into 02-07a and 02-07b (too large)
#  Review? [Y/skip]"
```

Disagreed decisions are rolled back. If the same type gets rolled back repeatedly, the improvement loop learns to escalate that category in the future.

**`--auto` readiness check:** Before starting auto mode, the Attendant verifies that all expected tool permissions are pre-approved in settings.json. If gaps are found, the Attendant offers to add them specifically — avoiding the need for blanket permission bypass.

### 5.9 Knowledge Layer

Three-tier knowledge architecture. Project knowledge persists across sessions, machines, and team members.

**Tier 1: Hot cache (auto-loaded, free)**

`~/.claude/projects/<hash>/memory/MEMORY.md` — Claude Code auto-loads this into every conversation. No tool call needed, zero token retrieval cost. Capped at 200 lines.

Contains: active gotchas, key decisions, current phase pointer, documentation fallback chain for this project's stack, and pointers to detailed knowledge files.

**Tier 2: Knowledge base (in git, on-demand)**

`.dominion/knowledge/*.md` — detailed topic files committed to the repository. Portable, shareable, version-controlled. Read by agents only when MEMORY.md's summary isn't enough.

Example files: `database-gotchas.md`, `api-patterns.md`, `debugging-history.md`, `decision-archive.md`.

**Tier 3: User profile (local, never committed)**

`~/.claude/.dominion/` — cross-project user preferences, experience level, communication style. Valid everywhere, never project-specific knowledge.

**Knowledge lifecycle:**

```
Developer discovers gotcha → documents in SUMMARY.md
  → Reviewer sees pattern across tasks → promotes to MEMORY.md + .dominion/knowledge/
    → Every future session starts knowing the gotcha (free, auto-loaded)
      → When MEMORY.md nears 200 lines → Reviewer demotes resolved items to knowledge files
```

**Hydration index (`.dominion/knowledge/index.toml`):**

Controls what gets promoted to the MEMORY.md hot cache:

```toml
[meta]
last_hydrated = "2026-03-07"
memory_budget_lines = 200

[[entries]]
file = "database-gotchas.md"
hot = true                    # include in MEMORY.md
priority = 1
summary = """
- Use types::Value not serde_json::Value for DB take()
- time::now() for timestamps, never bind DateTime directly
- 'token' is reserved — use $auth_token
"""

[[entries]]
file = "api-patterns.md"
hot = false                   # too detailed for hot cache — pointer only
priority = 3

[[entries]]
file = "crypto-decisions.md"
hot = true
priority = 2
summary = """
- RustCrypto over libsignal (unstable API)
- Standard key derivation, no custom extensions
"""
```

**MEMORY.md template (generated by hydration):**

```markdown
# Project Memory
## Current State
Phase: 2 | Step: execute | Wave: 3 | Task: 02-05

## Documentation Chain
1. context7 → 2. official docs (WebFetch) → 3. serena memories → 4. STOP AND ASK

## Active Knowledge
<!-- Hydrated from .dominion/knowledge/index.toml (hot entries) -->
[summaries from hot entries, ordered by priority]

## Detailed Knowledge (read on demand)
- .dominion/knowledge/api-patterns.md — crate API reference patterns
- .dominion/knowledge/debugging-history.md — past debugging sessions
```

The Reviewer manages `hot` flags during the improvement loop. When MEMORY.md approaches the budget, the Reviewer demotes lower-priority entries (`hot = false`).

**Hydration (one-time per machine):**

New developer clones the repo → runs `dominion claim` → reads `.dominion/knowledge/index.toml` → builds their local MEMORY.md from hot entries. Every session after that: free.

**Scoping rule:** Dominion writes project knowledge to project MEMORY.md only. Never touches global `~/.claude/memory/MEMORY.md` — that's the user's space. Project-specific gotchas in global memory would pollute every other project.

**Document ownership:** See §5.5 for the complete ownership table. Key rule: Dominion never touches global MEMORY.md — that's the user's space.

---

## 6. Tool Ecosystem

### 6.1 MCP & Plugin Curation

**The registry — `.dominion/registry.toml`:**

Ships with Dominion, updated with releases. Contains curated evaluations of MCPs, plugins, and skills.

```toml
[mcps.context7]
category = "documentation"
rating = 4.8
platforms = ["linux", "macos", "windows"]
agent_affinity = ["Researcher", "Architect", "Developer"]
notes = "Must call resolve-library-id before query-docs."

[mcps.serena]
category = "code-navigation"
rating = 4.5
platforms = ["linux", "macos", "windows"]
agent_affinity = ["Researcher", "Architect", "Developer", "Reviewer"]
memory_policy = "Structured API references only (api/<crate-name>)."

[mcps.echovault]
category = "memory"
rating = 4.2
platforms = ["linux"]
platform_issues = { macos = "Not available natively, Docker workaround possible" }

[mcps.sequential-thinking]
category = "reasoning"
rating = 4.7
agent_affinity = ["Researcher", "Architect", "Security Auditor"]

[plugins.superpowers]
category = "methodology"
rating = 4.6
compatible_with_dominion = true
recommended_skills = ["brainstorming", "writing-plans", "systematic-debugging"]

[plugins.gsd]
category = "methodology"
rating = 3.2
compatible_with_dominion = "partial"
conflicts = ["dominion agent orchestration — GSD subagents lack MCP access"]
```

**Registry update mechanism:**

v1: registry.toml updates with each Dominion plugin release — no network dependency, no separate fetch command. Between releases, users override ratings via `~/.claude/.dominion/registry-overrides.toml` (personal) or propose project-level overrides through the Advisor. `dominion validate` warns if the bundled registry is older than a configurable threshold.

**Registry evolution:**

| Version | Registry | Source |
|---------|----------|--------|
| v1 | Bundled, static. Updates with plugin releases | Maintained by Dominion team |
| v1.x | Community ratings | Users submit via `dominion rate <tool>` — natural language feedback evaluated into structured ratings |
| v2 | AI-evaluated | Researcher agent can assess new tools by reading their docs and repo health |

**How the wizard uses the registry:**

Researcher analyzes the project, wizard cross-references the registry, presents curated recommendations grouped by necessity (recommended / optional / not recommended with reasons). User approves tool-by-tool or accepts all defaults.

### 6.2 Documentation Governance

**The fallback chain — a first-class concept:**

Every Dominion project gets a defined, ordered lookup chain for API documentation. Agents follow it mechanically. No improvisation.

```toml
# .dominion/dominion.toml [documentation]

[[documentation.sources]]
name = "context7"
type = "mcp"
priority = 1

[[documentation.sources]]
name = "serena-memories"
type = "mcp"
priority = 2

[[documentation.sources]]
name = "docs-rs"
type = "web"
url_pattern = "https://docs.rs/{crate}/latest/{crate_underscored}/"
priority = 3

[[documentation.sources]]
name = "official-docs"
type = "web"
urls = { framework = "https://docs.example.com" }
priority = 4

[[documentation.sources]]
name = "team-knowledge-base"
type = "custom"
description = "User-configured — Obsidian, Notion, internal wiki, RAG service, etc."
priority = 5

[documentation.fallback]
action = "stop-and-ask"
message = "Could not find docs. Do NOT read source files or trial-and-error compile."
```

The knowledge base question during init includes an open-ended "Other" option for services that don't exist yet. Users describe their setup in free text and Dominion generates the appropriate source entry.

**When context7 is unavailable:** Developer agents fall back to official documentation via WebFetch (e.g., docs.rs for Rust crates, official framework docs). Parsing library source code is the **last resort** — agents should never default to reading `node_modules/`, `.venv/lib/`, or `~/.cargo/registry/` to learn APIs. The fallback chain is ordered and the terminal action is always stop-and-ask.

**Prohibited behaviors — enforced by hooks:**

| Behavior | Detection | Enforcement |
|----------|-----------|-------------|
| Source diving | Reading `~/.cargo/registry/`, `node_modules/`, `.venv/lib/` for API learning | Hook: BLOCK |
| Trial-and-error compilation | 3+ build cycles without reading docs between them | Review: FLAG |
| API hallucination | Using unfamiliar crate API with no prior doc lookup | Review: FLAG |

Hooks are generated as hookify rules during init, mechanically preventing the most damaging behaviors.

### 6.3 Permission Management

During init, the Attendant generates `.claude/settings.json` with pre-approved MCP commands and CLI tool permissions:

```jsonc
{
  "permissions": {
    "allow": [
      // Dominion CLI — wildcarded, new commands work immediately
      "Bash(dominion-tools *)",

      // MCP read operations — safe to auto-approve
      "mcp__serena__get_symbols_overview",
      "mcp__serena__find_symbol",
      "mcp__serena__activate_project",
      "mcp__serena__read_memory",
      "mcp__context7__resolve-library-id",
      "mcp__context7__query-docs",
      "mcp__echovault__memory_search",
      "mcp__echovault__memory_context"
      // ... all safe read operations
    ]
  }
}
```

Write operations and destructive MCP commands require human approval. The principle: agents should never stall on permission prompts for their own tooling or for read-only operations.

---

## 7. CLI Tooling

### 7.1 Spec-Driven CLI Generation

`dominion-tools/` lives at the project root — visible, auditable, not hidden in a dotfile directory. It is implemented in the **project's own language** using the project's own build system.

**Dominion ships a spec, not scaffolds.** The CLI is never distributed as a binary or a per-language template. Instead:

1. Dominion ships `.dominion/specs/cli-spec.toml` — a comprehensive command specification
2. At init, after the core agent team is configured, the Developer agent's **first task** is: "Implement dominion-tools per cli-spec.toml in [detected language]"
3. The Tester validates the implementation against the spec
4. The CLI is committed to `dominion-tools/`

This is the agent team's **proving ground** — if they can build a CLI from a spec, the methodology works. It also serves as a natural demo case for `--auto` mode in later versions.

**The spec defines** every command: name, arguments, TOML paths to read/write, output JSON schema, behavior, and error cases:

```toml
[meta]
spec_version = 1
minimum_commands = ["validate", "state resume", "plan task"]

[[commands]]
name = "state resume"
description = "Display current position for session start"
reads = [".dominion/state.toml", ".dominion/roadmap.toml"]
output_schema = "schemas/state-resume.json"
behavior = """
Read state.toml position. Format as:
Phase N, Step S, Wave W. Last: Task T status.
N blockers. M backlog items.
"""

[[commands]]
name = "signal blocker"
description = "Raise a blocker signal"
args = ["--level", "--task", "--reason"]
writes = [".dominion/signals/blocker-{task}.toml"]
output_schema = "schemas/signal-created.json"
```

**Chicken-and-egg resolution:** During init (before the CLI exists), agents use raw Read/Write tools to interact with TOML files. Once the CLI is built and passes `dominion validate`, all subsequent work uses it.

**Language independence:** The spec is language-agnostic. Any language with TOML parsing and JSON output can implement it. Multi-language projects pick a primary language for the CLI — the wizard recommends based on what the project is mostly written in.

**Output format:** Every command supports two output modes:
- **Default (TTY):** human-readable formatted output
- **`--json` flag:** machine-readable JSON for agent consumption. Agent startup sequences always use `--json`.

**CLI updates when Dominion updates:**

1. `dominion validate` detects missing commands by comparing spec version against implemented commands
2. Attendant proposes adding the new commands
3. User approves — Developer agent implements new commands in the existing CLI
4. User-added custom commands are never touched

**CLI updates from improvement loop:**

When the Reviewer proposes a new command (§7.4), the Developer agent implements it as a new function in the existing CLI codebase. Standard plan→execute→review cycle — the CLI is just another part of the project. Users are encouraged to create custom commands for their project's specific needs.

### 7.2 Baseline Commands

Generated during init for every project:

```
# Document ops (for SUMMARY.md and other markdown files)
dominion-tools doc read <file> --section <heading>
dominion-tools doc write <file> --section <heading> --content <text>
dominion-tools doc append <file> --section <heading> --content <text>
dominion-tools doc list <file>
dominion-tools doc template <type>

# Research (query research.toml)
dominion-tools research findings --severity <level>  # filter by severity
dominion-tools research finding <id>                 # single finding detail
dominion-tools research opportunities                # list opportunities
dominion-tools research summary                      # auto-generated overview

# Plan (query/update plan.toml)
dominion-tools plan task <id>                        # task details + handoffs
dominion-tools plan task <id> --files                # file ownership
dominion-tools plan task <id> --criteria             # acceptance checklist
dominion-tools plan wave <N>                         # all tasks in wave
dominion-tools plan deps <id>                        # what blocks this task
dominion-tools plan assumptions                      # unverified assumptions
dominion-tools plan assumptions --verify <id>        # mark assumption verified
dominion-tools plan handoff <from> --to <to> "<msg>" # targeted handoff note
dominion-tools plan index                            # group plans into waves
dominion-tools plan validate <file>                  # validate plan structure

# Phase & wave
dominion-tools phase init <N> --title <name>
dominion-tools phase status
dominion-tools phase progress <N>
dominion-tools wave create <N>
dominion-tools wave status
dominion-tools wave merge

# Signals (within-wave communication)
dominion-tools signal blocker --level <level> --task <id> --reason "<text>"
dominion-tools signal warning --task <id> "<message>"
dominion-tools signal list                           # check current signals

# Navigation
dominion-tools context <path>
dominion-tools ownership <file>

# Agents
dominion-tools agents list                              # active agents (default)
dominion-tools agents list --available                  # all roles (core + specialized), marks which are active
dominion-tools agents show <role>                       # full config dump for one agent
dominion-tools agents generate                          # regenerate AGENTS.md from .toml files
dominion-tools agents lint                              # validate agent configs

# Quality
dominion-tools style check <language> <convention>
dominion-tools style list <language>
dominion-tools zone check <path>

# Reports
dominion-tools report create <type> <phase>
dominion-tools report finalize <file>

# State
dominion-tools state resume                          # session start context
dominion-tools state position                        # where are we
dominion-tools state update --phase <N> --wave <N>   # update position
dominion-tools state decisions --tags <tag>           # filtered decision search
dominion-tools state decisions --phase <N>            # decisions by phase
dominion-tools state blockers                        # what's stuck
dominion-tools state autonomous-decisions --session last

# Project
dominion-tools project summary                       # one-paragraph overview
dominion-tools project criteria                      # success criteria with status

# Roadmap
dominion-tools roadmap status                        # bird's eye (auto-computed)
dominion-tools roadmap phase <N>                     # detailed phase view
dominion-tools roadmap next                          # what's next
dominion-tools roadmap insert-phase --after <N>      # mid-project insertion
dominion-tools roadmap remove-phase <N>              # remove and renumber
dominion-tools roadmap audit-milestone <N>           # check against success criteria

# Backlog
dominion-tools backlog add --tags <tags> "<text>"    # capture during work
dominion-tools backlog list                          # view all
dominion-tools backlog suggest --phase <N>           # smart suggestions for planning

# Rollback & history
dominion-tools rollback --to-wave <N>                # roll back to wave boundary
dominion-tools rollback --task <id>                  # revert single task
dominion-tools rollback --to-phase <N>               # roll back entire phase
dominion-tools history --phase <N>                   # commit map

# Knowledge
dominion-tools knowledge index                       # view hot cache index
dominion-tools knowledge hydrate                     # rebuild MEMORY.md from index

# Metrics & validation
dominion-tools metrics trends                        # improvement over time
dominion-tools validate                              # full integrity check (see below)
dominion-tools rate <tool> "<feedback>"               # rate an MCP/plugin (v1.0+)
```

**`dominion validate` checks:**
1. All TOML files parse without errors and match expected schema versions
2. Agent TOML configs reference files that exist (skills, ownership paths)
3. `.claude/agents/*.md` files exist for every `.dominion/agents/*.toml`
4. CLI implementation covers all commands in cli-spec.toml (flags missing commands)
5. settings.json has required MCP permissions for active agents
6. Hooks reference valid paths and aren't orphaned
7. AGENTS.md matches current TOML state (flags if regeneration needed)

**TOML files are accessed via CLI, not read directly.** Instead of an agent reading a full research.toml to find one finding:

```bash
# Query one finding — ~200 tokens
dominion-tools research finding F1

# vs reading entire research.toml — ~2000 tokens
```

For SUMMARY.md (the only markdown phase document), section-based access still applies:

```bash
dominion-tools doc read summaries/task-02-01.md --section "Friction encountered"
```

Agents interact with document **sections** or **CLI queries**, not entire files.

### 7.3 Project-Specific Commands

The Researcher analyzes the project during init and proposes tailored commands:

| Project has... | Proposed command | Purpose |
|----------------|-----------------|---------|
| Multiple Rust crates | `dominion-tools crate-deps <name>` | Workspace dependency tree |
| Docker Compose | `dominion-tools services status` | Service health check |
| Database migrations | `dominion-tools migrations check` | Migration chain integrity |
| Proto/gRPC files | `dominion-tools proto-check` | Proto compilation, breaking changes |
| CI pipeline | `dominion-tools ci simulate` | Local CI dry-run |

### 7.4 Self-Improving CLI

Through the improvement loop, agents propose new commands when they detect repetitive operations. The proposal flows through the standard pipeline: Reviewer identifies friction, Researcher validates, Architect plans, Developer implements, user approves.

### 7.5 Interface Principle

**Human interface:** natural language + `/dominion:*` skills. Humans say "remember I prefer f-strings everywhere" and the Advisor handles it.

**Agent interface:** `dominion-tools` CLI + `.dominion/` config files. Agents call commands programmatically for deterministic, token-efficient operations.

Humans never need to type CLI commands or edit TOML directly (though they can). The CLI exists for agents to call.

---

## 8. Project Configuration

### 8.1 Code Style

Code style has layers that require different enforcement:

| Layer | Example | Enforced by |
|-------|---------|-------------|
| Formatting | Indentation, line length | Formatter (rustfmt, ruff, prettier) |
| Linting | Unused imports, unsafe patterns | Linter (clippy, ruff, eslint) |
| Conventions | f-strings over %, iterators over loops | CLAUDE.md + agent instructions |
| Taste | "Don't over-abstract", "keep it simple" | Agent behavioral instructions |
| Project-specific | "All DB calls through repository pattern" | Agent memory + code examples |

Formatters and linters handle layers 1-2. Dominion handles layers 3-5.

**`style.toml` — machine-readable convention store:**

```toml
[meta]
schema_version = 1

[languages.rust]
edition = "2021"
formatter = "rustfmt"
linter = "clippy"
error_handling = { libraries = "thiserror", binaries = "anyhow" }
async_runtime = "tokio"
test_runner = "cargo nextest"
pre_commit = ["cargo fmt --check", "cargo clippy --all-targets -- -D warnings", "cargo nextest run"]

[languages.rust.conventions]
max_function_lines = 50
max_file_lines = 500
unwrap_policy = "test-only"         # never | test-only | justified
doc_comments = "all-public"         # all-public | non-trivial | none
tracing = "async-io"                # async-io | all-public | none

[languages.python]
package_manager = "uv"
formatter = "ruff format"
linter = "ruff check"
type_checker = "pyrefly"
test_runner = "pytest"
pre_commit = ["uv run ruff check .", "uv run ruff format --check .", "uv run pyrefly check ."]

[languages.python.conventions]
type_hints = "all-signatures"
string_formatting = "f-strings"
cli_framework = "click + rich"

[taste]
# Free-text preferences that resist formalization
dos = ["Prefer iterators/combinators over loops", "Keep it simple"]
donts = ["Don't over-abstract", "Don't add features beyond what's asked"]
```

**Style capture during init:**

The wizard asks language-specific preferences (with multiple choice for common decisions and free text for do's/don'ts). For brownfield projects (`dominion claim`), the Researcher **analyzes the existing codebase** first and confirms detected patterns rather than interrogating from scratch.

**Two stores for conventions:**

| Store | Who reads it | Purpose |
|-------|-------------|---------|
| `CLAUDE.md` | Humans + Claude Code main session + spawned agents | Source of truth, always in context (auto-loaded everywhere) |
| `.dominion/style.toml` | `dominion-tools`, hooks, CI | Machine-readable for automated checks |

Both stay in sync. When a convention is added or changed (through the improvement loop or user request), `style.toml` updates automatically via the Attendant. CLAUDE.md updates via Advisor-proposed diff applied by the Attendant (human approves, since CLAUDE.md is human-owned per §4.3.2). No separate `code-conventions.md` skill — CLAUDE.md is auto-loaded by Claude Code in every session including spawned agents, making a duplicate skill file redundant.

**Style evolution:** The Reviewer can propose new conventions when it detects recurring patterns across reviews. User approves, convention added to both stores automatically.

### 8.2 Git Workflow

Dominion captures the full git lifecycle during init:

- **Branching strategy** — trunk-based, GitHub Flow, GitFlow, or custom
- **Commit conventions** — conventional commits, ticket-prefixed, or free-form
- **Merge strategy** — squash, rebase, or merge commits
- **Code review process** — all changes, major only, or agents review for solo devs
- **PR/MR description templates** — generated or user-provided
- **Release workflow** — semver, calver, or custom
- **Pet peeves and hard rules** — free text (e.g., "never force push to main")

If the user doesn't have established practices, Dominion recommends sensible defaults for their project type and team size.

**Generated artifacts:**

- `.githooks/pre-commit` — format, lint, test validation, commit message format
- `.githooks/commit-msg` — conventional commit validation, scope checking
- `.dominion/templates/pull-request.md` — PR description template
- `CLAUDE.md` git section — conventions for agents to follow

**Agent git capabilities:**

- Developer: atomic commits, convention-compliant messages, PR description drafting
- Reviewer: summarize colleague's PR for quick human review, write review comments
- Advisor: explain what changed in plain language, generate synopsis of branch changes
- Release Manager (specialized): changelogs from commits, version bumps, release notes

### 8.3 Project Direction

For projects undergoing restructuring, Dominion captures the team's intent in the `[direction]` section of `dominion.toml`.

**Three modes:**

| Mode | Meaning | Agent behavior |
|------|---------|---------------|
| **Maintain** | Codebase is good, preserve patterns | Match existing style and patterns |
| **Improve** | Mostly good, improve incrementally | Boy scout rule — improve files you touch, don't go on refactoring sprees |
| **Restructure** | Significant restructuring planned | Current patterns may be wrong. Follow target state, not current state |

**Restructure mode** introduces:

- **Legacy zones** — directories where agents apply minimal-touch policy. Don't learn patterns from legacy code. Don't refactor. Only fix what's asked.
- **Target state** — description of what the project should look like. New code follows target conventions strictly.
- **Migration strategy** — strangler-fig, big-bang, or incremental.
- **Zone checking** — `dominion-tools zone check <path>` tells agents whether they're in a legacy or new zone and what rules apply.

**Hookify rules from direction:** Legacy zone protection rules are generated automatically — blocking writes to legacy zones without justification, warning when new code imports from legacy modules, flagging large legacy zone changes as potential scope creep.

Direction configuration lives in the `[direction]` section of `dominion.toml` — see §5.6 for the full example.

---

## 9. User Experience

### 9.1 User Profiling

Dominion stores user preferences and experience level across sessions. Profiles are **strictly local** — stored in `~/.claude/.dominion/user-profile.toml`, never committed to git, never shared.

**v1 profile — explicit preferences only:**

```toml
[user]
experience_level = "intermediate"    # beginner | intermediate | advanced

[user.preferences]
git_style = "conventional-commits"
merge_strategy = "squash"
string_formatting = "f-strings"
verbosity = "concise"

[user.tool_opinions]
context7 = { rating = 5, notes = "essential" }
gsd = { rating = 2, notes = "unreliable with MCPs" }
```

The profile stores what the user **explicitly tells** Dominion — preferences, tool ratings, and a self-assessed or Advisor-estimated experience level. No behavioral tracking, no interest profiling, no pattern inference from observed actions.

**Why not behavioral tracking in v1:** Inferring patterns from behavior (e.g., "user rarely asks for explanations" → reduce verbosity) creates accuracy risks (maybe they stopped asking because explanations were bad) and feedback loops (fewer explanations → fewer opportunities to ask → "confirmed" pattern). Explicit preferences deliver 80% of the adaptation value without the complexity.

**Level adaptation:**

| Level | Init behavior | Proposals | Advisor behavior |
|-------|--------------|-----------|----------------|
| Beginner | Full explanations, recommends defaults | Detailed: what, why, what it means | Proactive: teaches best practices in context |
| Intermediate | Brief explanations, suggests with rationale | Medium: what and why | On request + critical alerts |
| Advanced | Skip to choices, respect preferences | Terse: "New: X. [Y/n]" | Silent unless asked or critical |

**Level changes over time.** Users can adjust their level explicitly ("I'm comfortable now, treat me as advanced"). The Advisor may also suggest a level change based on simple heuristics (e.g., user consistently overrides defaults → suggest upgrading to advanced).

**v1.x — richer profiling (planned):** Behavioral pattern tracking (`observed_patterns`), interest/engagement profiling, confidence scoring. These will be opt-in and transparent — the user can view and edit any inferred data.

### 9.2 Progressive Disclosure

Features are not dumped on the user in one go. The system grows with the team:

- **Session 1:** Basic setup — agents, conventions, git hooks, tool routing
- **Sessions 2-5:** Improvement proposals start appearing as friction is detected
- **Sessions 5+:** System stabilizes, proposals become rare, agents are efficient
- **New tool appears:** Dominion notices and suggests if relevant to project type

The Advisor agent is responsible for pacing feature introduction. It reads the user profile on session start (via hook) and adjusts its behavior accordingly.

### 9.3 Cross-Project Learning

Global preferences travel with the user, not the project:

```
~/.claude/.dominion/
  global-preferences.toml     # style choices that apply everywhere
  user-profile.toml            # experience level, explicit preferences, tool opinions
  registry-overrides.toml      # personal tool ratings
```

When a user starts a new project with `dominion init`, the wizard detects existing global preferences:

```
Found global preferences. Applying:
  conventional commits, squash merge, f-strings, thiserror/anyhow

Skip to project-specific questions? [Y / full setup]
```

Users can promote a project-specific preference to global: "I always want this" — the Attendant updates `global-preferences.toml`. Project conventions take precedence over global preferences when they conflict.

---

## 10. Security Model

### Trust Principle

**Dominion is a walled garden that imports knowledge, not code.**

| Source | Trust level | How Dominion uses it |
|--------|------------|---------------------|
| Official Claude Code SDK | Trusted | Used directly — plugin API, agent spawning |
| Official MCPs (context7, GitHub, etc.) | Trusted | Configured directly, commands whitelisted |
| Third-party plugins/skills | **Untrusted** | Evaluated, then recreated as Dominion-native skills |
| Community MCP servers | **Untrusted** | Recommended with warnings, user installs and reviews |
| User-written rules | Trusted | Incorporated directly |

### Skill Internalization

When Dominion evaluates a foreign skill or agent and finds it useful, it does NOT reference the foreign code at runtime. Instead:

1. Security Auditor reviews the foreign skill's source for threats (network calls, credential access, file ops outside project, prompt override attempts)
2. Researcher evaluates relevance and quality
3. Extract relevant patterns and instructions
4. Generate a Dominion-native skill in `.dominion/skills/` using official skill format
5. User reviews the generated skill
6. Attendant assigns to relevant agents via `.dominion/agents/*.toml`

The foreign plugin can be uninstalled afterward. What remains is Dominion-native, version-controlled, auditable.

### No Binaries, No Opaque Code

- `dominion-tools/` is source code in the project's language — fully readable and auditable
- `.dominion/skills/` are markdown files — reviewable by any developer
- No pre-compiled binaries are ever checked into the project
- No dependency on external services at runtime (MCPs are user-installed and user-approved)

### MCP Permissions

- Official MCPs: read operations auto-approved in `settings.json`
- Third-party MCPs: recommended with warnings, write operations require human approval
- Unknown MCPs (found during claim): preserved but not auto-whitelisted

---

## 11. Roadmap

### v0.1 — Genesis

Generate a working setup. One command, useful output.

| Feature | Description |
|---------|-------------|
| `dominion init` (greenfield, quick start + full setup) | Project analysis, wizard interview, artifact generation |
| Core 8 agents with .toml + .md definitions | Researcher, Architect, Developer, Tester, Reviewer, Advisor, Security Auditor, Attendant |
| CLAUDE.md generation (walkthrough with Advisor) | Draft synthesized from analysis, reviewed section-by-section with user |
| AGENTS.md generation (auto from TOML) | Roster view, regenerated on changes |
| CLI spec shipped, implemented by agents at init | First demo of the agent team — proving ground |
| `dominion validate` | Config integrity, agent consistency, CLI completeness |
| State management (state.toml) | Session resume, position tracking |
| Documentation fallback chain | Ordered lookup with stop-and-ask terminal |

### v0.2 — Pipeline

Run the methodology end-to-end, one wave at a time.

| Feature | Description |
|---------|-------------|
| `/dominion:orchestrate` (interactive) | Full pipeline: discuss → explore → plan → execute → test → review |
| Single-wave execution | Sequential task execution, no parallelism yet |
| `/dominion:quick` | Lightweight tasks, skip ceremony |
| Session lifecycle hooks | Auto-resume, auto-checkpoint |
| Commit tracking + basic rollback | Progress.toml, wave/task/phase rollback |
| Git workflow capture + hooks + PR templates | Branch naming, commit format, merge strategy, pre-commit |
| MCP curation + settings.json permissions | Recommended from official catalog, custom MCPs incorporated |

### v0.3 — Parallel Execution

Waves run in parallel. Agents communicate.

| Feature | Description |
|---------|-------------|
| Wave-based parallel execution | Git worktrees, `claude --agent` per worktree |
| Inter-wave checkpoints | Attendant hydrates MEMORY.md, applies handoffs |
| Blocker signals | Producer/consumer model, orchestrator-mediated |
| Multi-wave execution | Full dependency-ordered wave pipeline |

### v0.4 — Learning

The system improves itself.

| Feature | Description |
|---------|-------------|
| Improvement loop | Reviewer proposes, user approves, Attendant applies |
| Agent evolution | Instruction refinement, style drift correction |
| `/dominion:improve` | Present and apply accepted proposals |
| Knowledge layer | MEMORY.md hot cache + knowledge files + hydration index |
| Metrics collection | Phase-level quality and process metrics |
| Phase retrospective | Advisor structured feedback at defined touchpoints |

### v0.5 — Autonomy

Unattended overnight runs.

| Feature | Description |
|---------|-------------|
| Auto mode (`--auto`) | Full pipeline, halt only on governance hard stops |
| Circuit breakers | Token budget, retry limits, cascade limits |
| Autonomous decision audit trail | Logged, reviewable, rollback-able |
| Assumption verification | Researcher validates before execution begins |
| Degraded mode | Graceful fallback when MCPs unavailable |

### v0.6 — Extension

Specialized roles. External knowledge capture.

| Feature | Description |
|---------|-------------|
| Specialized role activation (9 roles) | Detection-based, reversible |
| `/dominion:educate` | Domain knowledge capture (DKCP) |
| `/dominion:study` | Plugin internalization (3-step pipeline) |
| Direction system | Maintain/improve/restructure, legacy zones |

### v0.7 — Adoption

Brownfield support. Team features.

| Feature | Description |
|---------|-------------|
| `dominion claim` (brownfield) | Detect, merge, preserve existing setups |
| User profiling | Explicit preferences, experience level |
| Cross-project preferences | Global config travels with user |
| Progressive disclosure | Feature layering paced by Advisor |
| Multi-developer locking | Single-writer lock on state.toml |
| Registry (bundled, static) | Curated MCP/plugin evaluations |

### v1.0 — Production

Stability, community, polish.

| Feature | Description |
|---------|-------------|
| Community registry | User ratings via `dominion rate`, natural language feedback |
| Cost estimation | Token/cost estimates before spawning agents |
| `dominion dry-run` | Simulated phase execution |
| Documentation and guides | Onboarding, admin, troubleshooting |
| PR synopsis + changelog generation | Agent git capabilities |

---

## 12. Known Risks & Mitigations

### Scope Creep

**Risk:** The design is ambitious. Building everything at once produces a meta-framework more complex than doing things manually.

**Mitigation:** v1 is ruthlessly scoped. The wizard must produce something useful in under 5 minutes. Quick start mode with reasonable defaults is the primary path. Full setup is available but not required.

### Config Fatigue

**Risk:** Too many TOML files, too many conventions, too much "configuration as code."

**Mitigation:** The human interface is natural language. Users talk to the Advisor, not to config files. TOML is the machine interface — agents and CLI tools read it. Humans only see it if they go looking.

### Stale Registry

**Risk:** Bundled registry goes stale between releases. New MCPs appear, existing ones break, ratings change.

**Mitigation:** v1 ships with a conservative, well-tested registry. Community ratings in v1.x keep it current. Dominion notifies when its registry is older than a configurable threshold.

### Agent Quality Variance

**Risk:** Agents produce inconsistent code quality across projects and languages.

**Mitigation:** Conventions are generated per-language with best practices. The Reviewer catches deviations. The improvement loop tightens conventions based on real findings. Over time, agent output converges to project standards.

### Dominion Plugin Updates

**Risk:** Plugin updates break existing `.dominion/` configs.

**Mitigation:** Config files have a version field. Template versioning — new documents use new templates, old documents are not retroactively upgraded. User customizations to templates are preserved — Dominion only adds, never overwrites user additions.

### Privacy

**Risk:** User profiles or team dynamics leak into git.

**Mitigation:** User profiles are strictly `~/.claude/.dominion/` — local only, never committed. Project `.dominion/` contains zero personal data. No team roster in git. Role-based access (who can approve improvements) is handled by git's own mechanisms (branch protection, CODEOWNERS, PR approvals).

### Over-Reliance on Agents

**Risk:** Developers stop thinking and trust agents blindly.

**Mitigation:** The Advisor adapts to the user — but governance rules exist regardless of level. Hard stops fire for everyone. The Reviewer catches drift for everyone. Dominion enhances judgment, it doesn't replace it.

### Agent Failure Cascade

**Risk:** One agent fails, cascading failures waste tokens across the wave.

**Mitigation:** Circuit breakers (§5.8) cap retries per task. Failed tasks raise blocker signals — only dependent tasks pause, not the entire wave. The orchestrator presents failures for triage rather than retrying indefinitely. Progress.toml records exactly which commits belong to which task, enabling surgical rollback of failed work.

### Degraded Mode

**Risk:** MCPs go offline (Context7 down, Serena can't activate, echovault unreachable). Agents stall or hallucinate.

**Mitigation:** The documentation fallback chain (§6.2) is ordered — if source 1 fails, try source 2. If all sources fail, the agent stops and asks (never improvises). For non-critical MCPs (echovault), agents continue without them and note the gap in SUMMARY.md. For critical MCPs (serena for code navigation), agents halt the task and signal a blocker. `dominion validate` checks MCP availability proactively.

### Cost Awareness

**Risk:** Spawning opus agents with ultrathink for every phase burns through token budgets. Solo developers on limited budgets get surprised.

**Mitigation:** Circuit breakers cap per-task token spend (§5.8). The Advisor can estimate cost before spawning a wave: "Wave 2 has 4 tasks across 4 Developer agents (sonnet) + 1 Reviewer (opus). Estimated: ~120k tokens. Proceed?" Model selection in agent TOML is deliberate — Developers use sonnet (cheaper, fast), only Researcher/Architect/Reviewer use opus. Users can override model selection per agent in their TOML config.

### Token Economics

**Risk:** Init spawns multiple opus-level agents. Solo developers on limited plans get surprised by the cost of setup.

**Estimated token costs for init (v0.1):**

| Step | Agent(s) | Model | Estimated tokens |
|------|----------|-------|-----------------|
| Project discovery | Researcher | opus | ~30K |
| CLAUDE.md draft generation | Attendant | opus (ultrathink) | ~50K |
| CLAUDE.md walkthrough | Advisor | opus | ~15K |
| Agent TOML + MD generation (8 agents) | Attendant | sonnet | ~40K (8 × ~5K) |
| CLI implementation from spec | Developer | sonnet | ~50K |
| CLI validation | Tester | sonnet | ~20K |
| **Total init** | | | **~200K tokens** |

**Per-phase execution estimates (v0.2+):**

| Step | Agent(s) | Model | Estimated tokens |
|------|----------|-------|-----------------|
| Discuss | Advisor | opus | ~10K |
| Explore | Researcher | opus | ~30K |
| Plan | Architect | opus | ~25K |
| Execute (per task) | Developer | sonnet | ~30-50K |
| Test | Tester | sonnet | ~20K |
| Review | Reviewer | opus | ~30K |
| **Typical phase (5 tasks)** | | | **~250-350K tokens** |

**Mitigation:** Before init starts, Dominion displays the estimate: "Init will spawn ~5 agents and use approximately 200K tokens. Proceed?" Circuit breakers (§5.8) cap per-task spend during execution. Model selection is deliberate — Developers/Tester/Attendant use sonnet (cheaper, fast), only Researcher/Architect/Reviewer/Advisor/Security Auditor use opus. Users can override model selection per agent in TOML config.

### Eject / Uninstall

**Risk:** User wants to stop using Dominion. Are they locked in?

**Mitigation:** All generated artifacts (CLAUDE.md, AGENTS.md, `.claude/agents/*.md`, hooks, CLI tool) are standard Claude Code files that work without the Dominion plugin installed. The plugin is only needed to create, evolve, and regenerate the setup. Uninstalling Dominion leaves a fully functional AI development methodology — it just stops improving itself. `.dominion/` can be deleted or kept as reference. No lock-in, no runtime dependency.

---

## Appendix: Origin

Design grounded in practical failures from building a multi-crate Rust project with AI agents over several months:

1. **Subagent tool blindness** — orchestration frameworks spawn subagents that lose MCP access. Dominion solution: agents spawned via `claude --agent` with full MCP, TOML-driven startup sequences.
2. **Silent architectural drift** — agents "make it work" instead of flagging spec discrepancies. 11 critical deviations in one phase. Dominion solution: governance hard stops, escalation protocol.
3. **API reverse-engineering** — agents read `~/.cargo/registry/` source instead of docs. Dominion solution: documentation fallback chain, prohibited behavior hooks.
4. **Context exhaustion** — 3000-line architecture doc consumed every agent's context. Dominion solution: CLI tools for surgical section access (~200 tokens vs ~2000).
5. **Zero methodology transfer** — weeks of agent infrastructure, not reusable. Dominion solution: generate everything from codebase analysis.
