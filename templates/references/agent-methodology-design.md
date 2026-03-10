# Agent Methodology Design Guide

Follow these steps when designing a new agent's `[methodology]` section. Each step produces a concrete output that flows into the agent's TOML template. Run this AFTER the DKCP protocol completes — DKCP captures domain knowledge, this guide structures it into phases, methods, and tools.

---

## Step 1: Mode Classification

Determine the agent's operational mode:

**Execute-mode** (default for new agents):
- Agent performs domain-specific work when assigned tasks by the Architect
- Activated when relevant domain is detected in the project
- Receives tasks via plan.toml, produces SUMMARY.md
- All specialist agents use execute-mode

**Pipeline-mode** (extremely rare):
- Agent owns a step in the 7-step orchestration pipeline (discuss, explore, plan, execute, test, review, improve)
- Only create pipeline-mode if replacing an existing pipeline step or inserting a new one
- **STOP and confirm with user** before proceeding with pipeline-mode — this changes the core orchestration flow

Record: `mode = "execute"` or `mode = "pipeline"` for subsequent steps.

---

## Step 2: Phase Design

Design the ordered phases the agent follows when activated.

### Execute-Mode Skeleton

All execute-mode agents share this structure. Design 4-8 phases total:

| Phase | Required? | Standard Pattern |
|-------|-----------|-----------------|
| Task Intake | **Mandatory** | Read plan.toml task + knowledge_refs. Identify scope. Search EchoVault for prior decisions and gotchas related to this domain. |
| Domain-Specific Phases (2-6) | **Required** | Design from DKCP output. See guidance below. |
| Verification | **Mandatory** | Prove correctness. Run relevant checks. Validate output. |
| Handoff | **Mandatory** | Write SUMMARY.md. Save discoveries to EchoVault. Signal if blockers. |

**Designing domain-specific phases** from DKCP output:

1. Read the DKCP Phase 6 output (glossary, constraints, stakeholder map, domain patterns)
2. Identify the agent's core workflow: what does this agent actually DO when given a task?
3. Break the workflow into distinct phases where each phase has:
   - A clear **purpose** (one sentence)
   - Observable **key activities** (bullet list of specific actions)
   - A concrete **output** (artifact, state change, or user-visible result)
4. Common middle phase patterns:
   - **Audit/Assessment** — evaluate current state before changing anything
   - **Design/Planning** — decide approach before implementing
   - **Implementation** — build the thing
   - **Hardening/Optimization** — improve quality after initial implementation

If a phase doesn't produce output, merge it with an adjacent phase.

### Pipeline-Mode Phases

More complex — varies per pipeline step. Read existing pipeline-mode agents as templates:
- Researcher: 5 phases (context loading → architecture mapping → deep analysis → cross-cutting → synthesis)
- Architect: 7 phases (research consumption → WBS → specialist routing → dependency analysis → wave grouping → budget validation → output)
- Developer: 7 phases (task intake → context building → TDD red → implementation → refactor → verification → handoff)

Match phase count and granularity to the pipeline step's complexity.

**Output:** Phase table with columns: Phase | Purpose | Key Activities

---

## Step 3: Method Selection

Select industry-standard methods the agent applies during its phases.

### Principles

1. **Name industry methods, don't invent.** The LLM knows STRIDE, TDD, ATAM, WCAG, SPC, Keep a Changelog. Naming activates the right knowledge. If you can't cite an author, organization, or standard — it's a preference, not a method.

2. **Consumer-driven selection.** Ask: "Who consumes this agent's output?" Select methods that produce useful artifacts for those consumers.
   - Architect consumes → methods that produce structured findings with clear recommendations
   - Developer consumes → methods that produce actionable specifications
   - Reviewer consumes → methods that produce verifiable criteria
   - End users consume → methods that produce user-facing quality

3. **5-8 methods per agent.** Fewer than 5 means the domain isn't covered. More than 8 means the agent is overloaded — split into two agents or demote lesser methods to phase activities.

4. **Avoid generic methods** that apply to all agents (those belong in shared governance). Include only domain-specific methods that require specialized knowledge.

### Method Entry Format

For each method, provide:

| Field | Description |
|-------|-------------|
| **Name** | Canonical name of the method or standard |
| **Source** | Author, organization, or specification (e.g., "Google SRE Book", "semver.org", "Brendan Gregg") |
| **Purpose** | One paragraph: what it does for THIS agent, not a textbook definition. How does the agent apply it? What does it produce? |

### Finding Methods

- Read the DKCP output: which industry standards apply to this domain?
- Check the DKCP Phase 3 (Regulatory Scan): compliance requirements often map to specific methods
- Search existing agent templates (`.dominion/agents/*.toml`) for methods in related domains
- Use WebSearch if needed to identify standard methods for the domain

**Output:** Methods table with columns: Method | Source | Purpose

---

## Step 4: Tool Routing

Define prescriptive tool selection for the agent. Not "consider using" — "use X for Y."

### Canonical Hierarchy

Fill in each row with agent-specific usage. Omit tools that don't apply to this agent (with a brief note why).

| Priority | Tool | Standard Usage |
|----------|------|---------------|
| 1 | dominion-tools (CLI) | **Mandatory for every agent.** All `.dominion/` data reads and writes — plan tasks, signals, summaries, knowledge. |
| 2 | serena (MCP) | Code navigation: symbol relationships, call hierarchies, definitions, references. Primary for code-level queries. Prefer over Grep for code. |
| 3 | Grep / Glob (built-in) | Non-code search: config files, lockfiles, file discovery by pattern. Use for anything that isn't source code symbols. |
| 4 | Bash (built-in) | Run tools, tests, builds, linters, external CLIs. The agent's hands for executing commands. |
| 5 | EchoVault (MCP) | Cross-agent memory: prior decisions, gotchas, patterns. Search on startup, save on completion. |
| 6 | context7 (MCP) | Library/framework documentation, API references, tool-specific docs. |
| 7 | WebSearch / WebFetch (built-in) | Documentation fallback when context7 lacks coverage. Specifications, best practices, advisories. |

For each tool the agent uses, write a one-line "Use For" description **specific to this agent's domain**. Examples:
- Generic (bad): "Search for files"
- Specific (good): "Find Terraform/CDK/Pulumi files, variable definitions, module references, provider configs"

**Output:** Tool routing table with columns: Tool | Use For

---

## Step 5: Research Lens

**Execute-mode agents only.** Pipeline-mode agents skip this step.

The research lens is a static `[research_lens]` section in the agent's TOML template. The Researcher reads it during its cross-cutting phase to expand analysis when this specialist is active.

### Format

```toml
[research_lens]
domain = "{domain_name}"
checklist = [
    "Aspect — specific things to look for, separated by commas",
    ...
]
```

### Guidelines

- **8-15 checklist items.** Fewer is too shallow. More adds noise.
- Each item starts with the **aspect being checked**, followed by a dash and **specific things to look for**.
- Items must be **observable from code analysis** — the Researcher uses serena, Grep, Glob. Don't include items that require runtime data, user interviews, or external service access.
- Items should **inform task scoping** — what the Architect needs to know when routing tasks to this agent.
- Cover the domain's key quality dimensions: what are the most common problems in this domain?

**Output:** Research lens TOML block

---

## Step 6: Cross-Dependency Mapping

Map which existing agents interact with the new agent. Every interaction must name a concrete artifact flow.

### Mandatory Dependencies (All Agents)

These three keystone agents always interact with every specialist:

| Keystone | Interaction |
|----------|-------------|
| **Researcher → New Agent** | Research lens provides domain-specific findings that inform task scoping. Always active when specialist is active. |
| **Architect → New Agent** | Architect routes domain tasks via `specialist_referral` tag. Task includes domain scope and requirements. |
| **Reviewer → New Agent** | Reviewer queries the agent for domain-specific dimensional assessment during review. Agent responds with domain expertise, Reviewer synthesizes into unified review. |

### Domain-Specific Dependencies

1. Read `.dominion/agents/*.toml` — list all existing agents' names and purposes
2. For each existing agent, ask: does this agent produce something the new agent consumes, or vice versa?
3. For each dependency found, write one line: `AgentA → NewAgent: {what artifact flows and why}`
4. Focus on **data flow**, not vague "collaborates with"

Common patterns:
- **Shared concern**: two agents work on the same domain aspect from different angles (e.g., Security Auditor defines requirements, Cloud Engineer implements them)
- **Producer-consumer**: one agent's output is another's input (e.g., API Designer defines contracts, Technical Writer documents them)
- **Boundary definition**: two agents have adjacent scope and need clear ownership lines (e.g., DevOps owns pipelines, Cloud Engineer owns infrastructure beneath them)

**Output:** Cross-dependency list

---

## Step 7: Self-Critique

Before finalizing, run this checklist. If any check fails, revise the relevant section.

| # | Check | Failure Action |
|---|-------|---------------|
| 1 | Does every phase have a clear, observable output? | Merge or split phases until each produces something concrete |
| 2 | Are all methods genuinely industry-standard with citable sources? | Remove methods without sources — they're preferences, not methods |
| 3 | Does the tool routing cover every activity in the phases? | Add missing tools or revise phases to match available tools |
| 4 | Are research lens items observable from code analysis? | Remove items requiring runtime data or user interviews |
| 5 | Does this agent overlap with an existing agent's methodology? | If >50% method overlap → merge into existing agent or differentiate |
| 6 | Is the phase count between 4-8 (execute-mode)? | Merge if >8, split if <4 |
| 7 | Does every cross-dependency name a specific artifact? | Replace vague "collaborates with" with concrete data flows |
| 8 | Would the Reviewer know what to ask this agent? | If not, the research lens or cross-dependency is too vague |

---

## Output Format

Present the final proposal including these TOML sections:

```toml
[methodology]
mode = "execute"  # or "pipeline"
# Phase table (rendered as markdown in the proposal, stored in TOML as structured data)

[methodology.tool_routing]
# Tool | Use For (one line per tool)

[methodology.methods]
# Method | Source | Purpose (one entry per method)

[research_lens]  # execute-mode only
domain = "{domain}"
checklist = [...]
```

Plus cross-dependency notes as free text (these inform the agent's generated `.claude/agents/{role}.md` instructions, not stored in TOML).
