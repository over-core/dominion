# v0.6 Expansion — Design Document

## Overview

v0.6 extends Dominion with specialized agent roles, domain knowledge capture, plugin internalization, and a project direction system. Nine new agent roles activate based on detection data. `/dominion:educate` captures domain knowledge through a 7-phase adaptive interview. `/dominion:study` internalizes external plugins into Dominion-native artifacts. The direction system (maintain/improve/restructure) guides agent behavior at runtime with legacy zone protection.

**Codename:** Expansion
**Branch:** `feat/v0.6-expansion`

## Scope

| # | Feature | Description |
|---|---------|-------------|
| 1 | Specialized role activation (9 roles) | Detection-based, reversible, suggested during improve step |
| 2 | Direction system | Maintain/improve/restructure modes, legacy zones, hookify rules |
| 3 | `/dominion:educate` | Domain Knowledge Capture Protocol (DKCP), 7-phase adaptive interview |
| 4 | `/dominion:study <plugin>` | Plugin internalization, 3-step pipeline with kill gate |
| 5 | Pipeline & infrastructure updates | Init wizard, improve step, detection data, CLI, validation |
| 6 | Tier rename | tier 1/2/3 → full/standard/detected |

**Pipeline change:** No new steps. The 7-step pipeline (discuss→explore→plan→execute→test→review→improve) is unchanged. New skills (`educate`, `study`) are standalone — invoked directly, not as pipeline steps.

**Scope boundary:** No brownfield support, no team features, no multi-repo. Those remain v0.7+.

---

## Feature 1: Specialized Role Activation (9 Roles)

Nine new agent TOML templates, detection-based activation, reversible.

### New Agent Templates

All in `templates/agents/`:

| # | Template | Activated When | Purpose |
|---|----------|---------------|---------|
| 9 | `devops.toml` | CI/CD, Docker, deployment configs | Pipeline design, container optimization, deployment strategies |
| 10 | `frontend-engineer.toml` | Frontend framework detected | Component architecture, state management, accessibility |
| 11 | `database-engineer.toml` | Database, ORM, schema files | Schema design, query optimization, migration authoring |
| 12 | `cloud-engineer.toml` | Terraform, CDK, Pulumi, cloud configs | IaC, IAM, networking, cost optimization |
| 13 | `observability-engineer.toml` | Metrics, tracing, logging config | Monitoring, alerting, SLO/SLI, distributed tracing |
| 14 | `api-designer.toml` | OpenAPI specs, API-heavy projects | Contract-first design, versioning, backward compatibility |
| 15 | `analyst.toml` | Benchmarks, data pipelines, perf-critical code | Measurement, profiling, data quality, metrics visualization |
| 16 | `technical-writer.toml` | Large/team projects | API docs, ADRs, architecture diagrams, changelogs |
| 17 | `release-manager.toml` | Versioned project with release history | Changelog generation, version bumps, release coordination |

Testing specializations (adversarial, TDD, integration, property-based) are NOT separate agents — they are testing styles configured in the Tester's TOML config.

Unsafe/FFI/systems code is handled by the Security Auditor (core agent #7), not a specialized role.

### Detection Data

New file: `data/detection/roles.toml` — maps file/dependency patterns to role names. Consolidates all role activation triggers in one place.

```toml
[meta]
schema_version = 1

[[roles]]
name = "devops"
triggers = [
    { files = ["Dockerfile", "docker-compose.yml", "compose.yml"] },
    { directories = [".github/workflows", ".gitlab-ci.yml", ".circleci"] },
]

[[roles]]
name = "frontend-engineer"
triggers = [
    { frameworks = ["react", "vue", "angular", "svelte", "next", "nuxt"] },
]
```

Existing `data/detection/infrastructure.toml` already has `activates_role` fields — `roles.toml` is the authoritative source. Infrastructure.toml `activates_role` fields remain for backward compatibility but roles.toml takes precedence.

### Init Wizard

New **Section 5: Specialized Roles** (after Section 4: Git Workflow):
- Present detected roles from `data/detection/roles.toml`
- User confirms, adds, or removes roles
- Current Sections 5-9 shift to 6-10

### Improve Step — Role Suggestions

When the Researcher detects new role triggers during the explore step, they're logged as proposals. The improve step's retrospective presents them:

```
New capability detected: Docker configs found.
Recommend activating DevOps agent. Add? [Y/n]
```

User approval → Attendant generates the agent from template.

### Modified Files

- `skills/init/references/wizard-full.md` — add specialized roles section
- `skills/improve/references/retrospective.md` — add role suggestion section
- `skills/explore/SKILL.md` — detect new role triggers during explore

---

## Feature 2: Direction System

Runtime direction checking. Agents read `[direction]` from dominion.toml at runtime, not baked into instructions at init time — direction can change mid-project.

### Schema Addition

Add to `templates/schemas/dominion.toml`:

```toml
[direction]
mode = "maintain"                    # maintain | improve | restructure

[direction.restructure]
# Only populated when mode = "restructure"
target_state = ""                    # description of target architecture
migration_strategy = ""              # strangler-fig | big-bang | incremental

[[direction.restructure.legacy_zones]]
path = ""                            # directory path
policy = "minimal-change"            # minimal-change (only policy for now)
```

### Direction Modes

| Mode | Meaning | Agent behavior |
|------|---------|---------------|
| **Maintain** | Codebase is good, preserve patterns | Match existing style and patterns |
| **Improve** | Mostly good, improve incrementally | Boy scout rule — improve files you touch, don't seek out work |
| **Restructure** | Significant restructuring planned | Check zone before editing. Follow target state, not current patterns |

### Restructure Mode — Legacy Zones

- **Legacy zones defined:** Only those paths get minimal-change policy. Everything else follows target state.
- **No legacy zones defined:** The whole codebase needs restructuring. Agents follow target state everywhere. No minimal-change zones — everything is fair game for improvement toward the target.

### CLI Command

`dominion-cli zone check <path>` — agents call this before editing files:
- Zones defined + path in zone → "legacy, minimal-change"
- Zones defined + path outside zones → "active, follow target state"
- No zones defined → "full restructure, follow target state"
- Not in restructure mode → "no direction constraints"

### Hookify Integration

When mode is `restructure` and legacy zones are defined, generation produces hookify rules:
- Block writes to legacy zones without justification
- Warn when new code imports from legacy modules
- Flag large legacy zone changes as potential scope creep

### Init Wizard Update

Section 2 (Direction) already exists — update naming from evolve/transform to improve/restructure. Follow-up questions for restructure mode already exist (target state, migration strategy, legacy zones).

### New Reference

`skills/orchestrate/references/direction-protocol.md` — how agents read and apply direction at runtime:
- Read `[direction]` from dominion.toml
- Apply mode-specific behavior
- Call `zone check` when in restructure mode before file edits

### Modified Files

- `templates/schemas/dominion.toml` — add `[direction]` section
- `templates/cli-spec.toml` — add `zone check` command
- `skills/init/references/wizard-full.md` — update direction naming (evolve→improve, transform→restructure)
- `skills/init/references/generation.md` — generate hookify rules from direction
- New: `skills/orchestrate/references/direction-protocol.md`

---

## Feature 3: `/dominion:educate` — Domain Knowledge Capture

New skill for capturing domain knowledge through structured interview or external sources.

### DKCP — 7-Phase Adaptive Interview

| Phase | Agent | What happens | Thinking |
|-------|-------|-------------|----------|
| 1. Domain Mapping | Researcher | Identify domain, subdomains, terminology. Use taxonomy for smart follow-ups. Expand via Context7/WebSearch for uncommon domains | Normal |
| 2. Stakeholder Mapping | Researcher | Who uses it, who regulates it, who breaks if it fails | Normal |
| 3. Regulatory Scan | Researcher | Compliance requirements, standards, certifications | High effort |
| 4. Deep Probe | Advisor | Adaptive follow-up on thin or contradictory areas | Ultrathink |
| 5. Artifact Grounding | Researcher | Serena traces domain concepts to actual codebase symbols — anchors knowledge in reality | Normal |
| 6. Knowledge Structuring | Advisor | Organizes captured knowledge into `.dominion/knowledge/` files | High effort |
| 7. Calibration | Advisor | Presents structured knowledge back to user for correction | Normal |

### Source Integration

`--from <source>` flag pulls from external sources:
- Notion (API), Confluence (API), Obsidian (local vault path), URLs (WebFetch), local files
- Researcher extracts, structures, and cross-references against codebase

### Output Routing

Advisor analyzes captured scope and recommends output format:
- **Knowledge files** (`.dominion/knowledge/*.md`) — domain facts, glossaries, constraints
- **Skill** (`.dominion/skills/*.md`) — repeatable procedure from domain workflow
- **Agent** (`.dominion/agents/*.toml` + `.claude/agents/*.md`) — specialized role for ongoing domain work

Flags: `--agent` (force agent output), `--skill` (force skill output), `--from <source>` (pull from external source).

### Domain Taxonomy

New data file: `data/taxonomy/domains.toml` — comprehensive multi-level taxonomy covering major industries, sub-domains, regulatory frameworks. Structured as a question tree.

```toml
[[domains]]
name = "healthcare"
subdomains = ["clinical", "pharma", "medical-devices", "health-it"]
follow_ups = [
    "Clinical trials or patient care?",
    "Subject to HIPAA?",
    "FDA-regulated?"
]

[[domains.subdomains]]
name = "pharma"
follow_ups = [
    "Drug discovery or manufacturing?",
    "Target identification or lead optimization?"
]
```

### New Files

- `skills/educate/SKILL.md` — skill definition with DKCP phases
- `skills/educate/references/dkcp-protocol.md` — detailed phase-by-phase instructions
- `skills/educate/references/source-integration.md` — external source handling
- `skills/educate/references/output-routing.md` — how to decide knowledge vs skill vs agent
- `data/taxonomy/domains.toml` — comprehensive domain taxonomy question tree

---

## Feature 4: `/dominion:study <plugin>` — Plugin Internalization

New skill for evaluating existing plugins and producing Dominion-native artifacts that improve on the originals.

### 3-Step Pipeline

| Step | Agents | Purpose |
|------|--------|---------|
| 1. Read & Assess | Researcher + Security Auditor | Inventory the plugin (skills, agents, hooks). Security scan for prompt injection, data exfiltration, permission escalation. Assess: does this concretely benefit *this project*? |
| 2. Kill Gate | Advisor | Must articulate specific scenarios where the skill fires and what outcome it improves. "Might be useful" doesn't pass. If no concrete benefit — stop here, no wasted tokens. |
| 3. Recreate | Researcher + Reviewer | Create Dominion-native version. Not a copy — must be better by leveraging project knowledge, agent architecture, and critical evaluation of the source's assumptions. |

### Flags

- `--skill <name>` — study one skill from the plugin
- `--agent <name>` — study one agent from the plugin
- Without flags: study the entire plugin

### Kill Gate Strictness

Strict — Advisor must name concrete scenarios where the skill fires and what outcome it improves for this project. Vague "might be useful" doesn't pass.

### Recreation Rules

Step 3 is not a copy. The reference file instructs:
- Identify what's weak in the original
- What assumptions don't hold for this project
- What opportunities the original missed
- Combine with project-specific knowledge and Dominion conventions
- Verify the result integrates with existing agents and governance

### Output

Produces one or more of:
- `.dominion/skills/*.md` — Dominion-native skill
- `.dominion/agents/*.toml` + `.claude/agents/*.md` — Dominion-native agent
- `.dominion/knowledge/*.md` — extracted domain knowledge

### New Files

- `skills/study/SKILL.md` — skill definition with 3-step pipeline
- `skills/study/references/inventory-assessment.md` — step 1 instructions
- `skills/study/references/kill-gate.md` — step 2 benefit threshold evaluation
- `skills/study/references/recreation.md` — step 3 synthesis and improvement

---

## Feature 5: Pipeline & Infrastructure Updates

### Init Wizard

- **Section 2 (Direction):** Update naming — evolve → improve, transform → restructure
- **New Section 5 (Specialized Roles):** Present detected roles, user confirms/adds/removes. Current Sections 5-9 shift to 6-10.

### Improve Step

- **Role suggestions:** Researcher detects new role triggers during explore → logged as proposals → retrospective presents them for user approval → Attendant generates agent from template

### Detection Data

- New `data/detection/roles.toml` — consolidates all role activation triggers
- Existing `data/detection/infrastructure.toml` `activates_role` fields remain for backward compatibility

### CLI Spec

- `dominion-cli zone check <path>` — direction zone checking
- Update spec_version to 0.6

### Validate Checks

- Check 22: `[direction]` section has valid mode value when present
- Check 23: `[direction.restructure]` has `target_state` and `migration_strategy` when mode is `restructure`
- Check 24: Specialized role agent files reference valid templates
- Check 25: Domain taxonomy TOML parses cleanly

### Version Bump

- `plugin.json` and `marketplace.json` → 0.6.0

### Modified Files

- `skills/init/references/wizard-full.md` — direction naming + specialized roles section
- `skills/improve/references/retrospective.md` — role suggestion section
- `skills/explore/SKILL.md` — detect new role triggers during explore
- `templates/cli-spec.toml` — `zone check` command, spec_version bump
- `skills/validate/references/checks.md` — checks 22-25
- `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` → 0.6.0

---

## Feature 6: Tier Rename

Rename internal language tier labels across detection data and skill prose:

| Old | New | Meaning |
|-----|-----|---------|
| Tier 1 | **full** | Full convention capture — style, patterns, error handling |
| Tier 2 | **standard** | Tooling and basic conventions |
| Tier 3 | **detected** | Language detected, minimal convention capture |

### Modified Files

- `data/detection/languages.toml` — tier field values
- `skills/init/references/wizard-full.md` — any references to tier naming
- Any other skill or reference files that mention "Tier 1/2/3"

---

## Deliverables Summary

| Category | Count | Details |
|----------|-------|---------|
| New agent templates | 9 | devops, frontend-engineer, database-engineer, cloud-engineer, observability-engineer, api-designer, analyst, technical-writer, release-manager |
| New skills | 2 | `/dominion:educate` (SKILL.md + 3 references), `/dominion:study` (SKILL.md + 3 references) |
| New orchestrate reference | 1 | `direction-protocol.md` |
| New detection data | 1 | `data/detection/roles.toml` |
| New taxonomy data | 1 | `data/taxonomy/domains.toml` |
| Modified schemas | 1 | `dominion.toml` (+direction) |
| Modified init | 1 | `wizard-full.md` (direction naming + specialized roles section) |
| Modified improve | 1 | `retrospective.md` (role suggestions) |
| Modified explore | 1 | `SKILL.md` (role trigger detection) |
| Modified CLI spec | 1 | `cli-spec.toml` (zone check, spec_version) |
| Modified validate | 1 | `checks.md` (checks 22-25) |
| Modified detection | 1 | `languages.toml` (tier rename) |
| Manifests | 2 | `plugin.json` + `marketplace.json` → 0.6.0 |

**Totals:** ~17 new files, ~9 modified files.

**Version:** 0.6.0 "Expansion"
**Branch:** `feat/v0.6-expansion`
