# v0.6 Expansion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add specialized agent roles, domain knowledge capture, plugin internalization, and project direction system to Dominion.

**Architecture:** Schema-heavy approach — create detection data, agent templates, and schema extensions first, then build skill prose on top. Two new standalone skills (`educate`, `study`), one new orchestrate reference (`direction-protocol`), and modifications to init, explore, and improve skills.

**Tech Stack:** TOML data files, markdown skill/reference files. No application code.

---

### Task 1: Tier Rename in Detection Data

Rename tier 1/2/3 → full/standard/detected in language detection tables.

**Files:**
- Modify: `data/detection/languages.toml`

**Step 1: Update tier labels**

In `data/detection/languages.toml`:
- Change the `[meta]` comment from `# Tiers: 1 = deep conventions, 2 = solid detection + basic conventions, 3 = detection only` to `# Levels: full = deep conventions, standard = solid detection + basic conventions, detected = detection only`
- Replace every `tier = 1` with `level = "full"`
- Replace every `tier = 2` with `level = "standard"`
- Replace every `tier = 3` with `level = "detected"`
- Update section comments: `# === TIER 1: Deep support ===` → `# === Full: Deep support ===`, etc.

**Step 2: Validate TOML**

Run: `python3 -c "import tomllib; tomllib.load(open('data/detection/languages.toml','rb')); print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add data/detection/languages.toml
git commit -m "refactor(detection): rename tier 1/2/3 to full/standard/detected"
```

---

### Task 2: Tier References in Skill Prose

Update any references to "Tier 1/2/3" in skill and reference files.

**Files:**
- Modify: `skills/init/references/wizard-full.md` (Section 3 references tiers)
- Modify: Any other files referencing tiers (search first)

**Step 1: Find all tier references**

Run: `grep -ri "tier [123]" skills/ templates/ data/ --include="*.md" --include="*.toml" -l`

Update each match:
- "Tier 1" → "full" (or "full-level" in prose)
- "Tier 2" → "standard" (or "standard-level" in prose)
- "Tier 3" → "detected" (or "detected-level" in prose)

In `skills/init/references/wizard-full.md` Section 3:
- Change: `For each Tier 1 language, present detected conventions and ask to confirm or change.`
- To: `For each full-level language, present detected conventions and ask to confirm or change.`
- Change: `For each Tier 2 language, present detected tooling and ask for any convention preferences.`
- To: `For each standard-level language, present detected tooling and ask for any convention preferences.`

**Step 2: Validate changed files**

For any modified TOML files:
Run: `python3 -c "import tomllib; tomllib.load(open('FILE','rb')); print('OK')"`

**Step 3: Commit**

```bash
git add -A
git commit -m "refactor(skills): update tier references to full/standard/detected"
```

---

### Task 3: Role Detection Data

Create `data/detection/roles.toml` — the authoritative source for specialized role activation triggers.

**Files:**
- Create: `data/detection/roles.toml`

**Step 1: Create roles.toml**

```toml
[meta]
schema_version = 1
# Role activation triggers for specialized agents
# Cross-references infrastructure.toml activates_role but is the authoritative source

# === DevOps ===

[[roles]]
name = "devops"
agent_template = "devops.toml"
description = "Pipeline design, container optimization, deployment strategies"
triggers = [
    { files = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml", "Containerfile"] },
    { directories = [".github/workflows", ".circleci"] },
    { files = [".gitlab-ci.yml", "Jenkinsfile"] },
    { files = ["Chart.yaml"] },
]

# === Frontend Engineer ===

[[roles]]
name = "frontend-engineer"
agent_template = "frontend-engineer.toml"
description = "Component architecture, state management, accessibility"
triggers = [
    { frameworks = ["react", "vue", "svelte", "angular"] },
    { frameworks = ["nextjs", "nuxt"] },
    { npm_deps = ["@testing-library/react", "@storybook/react"] },
]

# === Database Engineer ===

[[roles]]
name = "database-engineer"
agent_template = "database-engineer.toml"
description = "Schema design, query optimization, migration authoring"
triggers = [
    { infrastructure = ["postgresql", "mysql", "sqlite", "mongodb"] },
    { frameworks = ["sqlx", "diesel", "sea-orm", "sqlalchemy", "prisma", "drizzle", "gorm"] },
    { files = ["migrations/", "db/migrate/", "alembic/", "prisma/schema.prisma"] },
]

# === Cloud Engineer ===

[[roles]]
name = "cloud-engineer"
agent_template = "cloud-engineer.toml"
description = "IaC, IAM, networking, cost optimization"
triggers = [
    { infrastructure = ["terraform", "pulumi", "cdk"] },
    { files = ["serverless.yml", "sam-template.yaml", "cloudformation.yaml"] },
    { file_extensions = [".tf"] },
]

# === Observability Engineer ===

[[roles]]
name = "observability-engineer"
agent_template = "observability-engineer.toml"
description = "Monitoring, alerting, SLO/SLI, distributed tracing"
triggers = [
    { infrastructure = ["prometheus", "grafana", "opentelemetry"] },
    { npm_deps = ["@opentelemetry/sdk-node", "prom-client"] },
    { pyproject_deps = ["opentelemetry-sdk", "prometheus-client"] },
    { cargo_deps = ["opentelemetry", "tracing-opentelemetry"] },
]

# === API Designer ===

[[roles]]
name = "api-designer"
agent_template = "api-designer.toml"
description = "Contract-first design, versioning, backward compatibility"
triggers = [
    { infrastructure = ["openapi", "grpc", "graphql"] },
    { files = ["openapi.yaml", "openapi.json", "swagger.yaml", "swagger.json"] },
    { file_extensions = [".proto", ".graphql", ".gql"] },
]

# === Analyst ===

[[roles]]
name = "analyst"
agent_template = "analyst.toml"
description = "Measurement, profiling, data quality, metrics visualization"
triggers = [
    { files = ["benchmarks/", "benches/", "perf/"] },
    { cargo_deps = ["criterion"] },
    { pyproject_deps = ["pandas", "numpy", "polars", "dask"] },
    { npm_deps = ["d3", "chart.js", "recharts"] },
]

# === Technical Writer ===

[[roles]]
name = "technical-writer"
agent_template = "technical-writer.toml"
description = "API docs, ADRs, architecture diagrams, changelogs"
triggers = [
    { project_trait = "team" },
    { files = ["docs/", "doc/", "documentation/"] },
    { files = ["mkdocs.yml", "docusaurus.config.js", ".readthedocs.yml"] },
]

# === Release Manager ===

[[roles]]
name = "release-manager"
agent_template = "release-manager.toml"
description = "Changelog generation, version bumps, release coordination"
triggers = [
    { files = ["CHANGELOG.md", "CHANGES.md", "HISTORY.md"] },
    { files = [".releaserc", ".releaserc.json", "release.config.js"] },
    { project_trait = "versioned" },
]
```

**Step 2: Validate TOML**

Run: `python3 -c "import tomllib; tomllib.load(open('data/detection/roles.toml','rb')); print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add data/detection/roles.toml
git commit -m "feat(detection): add role activation triggers for 9 specialized agents"
```

---

### Task 4: Specialized Agent Templates (DevOps, Frontend, Database)

Create first 3 of 9 specialized agent TOML templates.

**Files:**
- Create: `templates/agents/devops.toml`
- Create: `templates/agents/frontend-engineer.toml`
- Create: `templates/agents/database-engineer.toml`

**Step 1: Create devops.toml**

Follow the structure of existing templates (e.g., `developer.toml`). Key fields:

```toml
[agent]
name = "DevOps"
role = "devops"
model = "sonnet"
color = "blue"
purpose = "Pipeline design, container optimization, build caching, deployment strategies. Produces and maintains CI/CD configs and Dockerfiles."

[tools.mcps]
required = ["{{required_mcps}}"]
optional = ["{{optional_mcps}}"]

[tools.documentation]
fallback = ["{{fallback_chain}}"]

[tools.skills]
custom = []

[tools.cli]
commands = ["dominion-cli signal", "dominion-cli doc"]

[governance]
architectural_decisions = "stop-and-report"
file_ownership = ["{{file_ownership}}"]
hard_stops = ["{{hard_stops}}"]

[workflow]
commit_style = "atomic"
pre_commit = ["{{pre_commit_commands}}"]
produces = "SUMMARY.md"
```

**Step 2: Create frontend-engineer.toml**

```toml
[agent]
name = "Frontend Engineer"
role = "frontend-engineer"
model = "sonnet"
color = "cyan"
purpose = "Component architecture, state management, styling patterns, accessibility compliance, frontend build tooling and optimization."

[tools.mcps]
required = ["{{required_mcps}}"]
optional = ["{{optional_mcps}}"]

[tools.documentation]
fallback = ["{{fallback_chain}}"]

[tools.skills]
custom = []

[tools.cli]
commands = ["dominion-cli signal", "dominion-cli doc"]

[governance]
architectural_decisions = "stop-and-report"
file_ownership = ["{{file_ownership}}"]
hard_stops = ["{{hard_stops}}"]

[workflow]
commit_style = "atomic"
pre_commit = ["{{pre_commit_commands}}"]
produces = "SUMMARY.md"
```

**Step 3: Create database-engineer.toml**

```toml
[agent]
name = "Database Engineer"
role = "database-engineer"
model = "sonnet"
color = "orange"
purpose = "Schema design and normalization, query optimization, migration authoring and chain validation, index analysis. Covers SQL and NoSQL."

[tools.mcps]
required = ["{{required_mcps}}"]
optional = ["{{optional_mcps}}"]

[tools.documentation]
fallback = ["{{fallback_chain}}"]

[tools.skills]
custom = []

[tools.cli]
commands = ["dominion-cli signal", "dominion-cli doc"]

[governance]
architectural_decisions = "stop-and-report"
file_ownership = ["{{file_ownership}}"]
hard_stops = ["{{hard_stops}}"]

[workflow]
commit_style = "atomic"
pre_commit = ["{{pre_commit_commands}}"]
produces = "SUMMARY.md"
```

**Step 4: Validate all three**

Run for each file:
```bash
python3 -c "import tomllib; tomllib.load(open('templates/agents/devops.toml','rb')); print('OK')"
python3 -c "import tomllib; tomllib.load(open('templates/agents/frontend-engineer.toml','rb')); print('OK')"
python3 -c "import tomllib; tomllib.load(open('templates/agents/database-engineer.toml','rb')); print('OK')"
```

**Step 5: Commit**

```bash
git add templates/agents/devops.toml templates/agents/frontend-engineer.toml templates/agents/database-engineer.toml
git commit -m "feat(templates): add devops, frontend-engineer, database-engineer agent templates"
```

---

### Task 5: Specialized Agent Templates (Cloud, Observability, API)

Create next 3 specialized agent TOML templates.

**Files:**
- Create: `templates/agents/cloud-engineer.toml`
- Create: `templates/agents/observability-engineer.toml`
- Create: `templates/agents/api-designer.toml`

**Step 1: Create cloud-engineer.toml**

```toml
[agent]
name = "Cloud Engineer"
role = "cloud-engineer"
model = "sonnet"
color = "yellow"
purpose = "Infrastructure-as-code authoring, IAM policy design, networking topology, managed service configuration, cost optimization."

[tools.mcps]
required = ["{{required_mcps}}"]
optional = ["{{optional_mcps}}"]

[tools.documentation]
fallback = ["{{fallback_chain}}"]

[tools.skills]
custom = []

[tools.cli]
commands = ["dominion-cli signal", "dominion-cli doc"]

[governance]
architectural_decisions = "stop-and-report"
file_ownership = ["{{file_ownership}}"]
hard_stops = ["{{hard_stops}}"]

[workflow]
commit_style = "atomic"
pre_commit = ["{{pre_commit_commands}}"]
produces = "SUMMARY.md"
```

**Step 2: Create observability-engineer.toml**

```toml
[agent]
name = "Observability Engineer"
role = "observability-engineer"
model = "sonnet"
color = "magenta"
purpose = "Monitoring stack setup, alert rule authoring, SLO/SLI definition, distributed trace instrumentation, dashboard design."

[tools.mcps]
required = ["{{required_mcps}}"]
optional = ["{{optional_mcps}}"]

[tools.documentation]
fallback = ["{{fallback_chain}}"]

[tools.skills]
custom = []

[tools.cli]
commands = ["dominion-cli signal", "dominion-cli doc"]

[governance]
architectural_decisions = "stop-and-report"
file_ownership = ["{{file_ownership}}"]
hard_stops = ["{{hard_stops}}"]

[workflow]
commit_style = "atomic"
pre_commit = ["{{pre_commit_commands}}"]
produces = "SUMMARY.md"
```

**Step 3: Create api-designer.toml**

```toml
[agent]
name = "API Designer"
role = "api-designer"
model = "opus"
color = "purple"
purpose = "Contract-first API design, versioning strategy, schema validation, REST/GraphQL/gRPC patterns, backward compatibility analysis."

[tools.mcps]
required = ["{{required_mcps}}"]
optional = ["{{optional_mcps}}"]

[tools.documentation]
fallback = ["{{fallback_chain}}"]

[tools.skills]
custom = []

[tools.cli]
commands = ["dominion-cli signal", "dominion-cli doc"]

[governance]
architectural_decisions = "stop-and-report"
file_ownership = ["{{file_ownership}}"]
hard_stops = ["{{hard_stops}}"]

[workflow]
commit_style = "atomic"
pre_commit = ["{{pre_commit_commands}}"]
produces = "SUMMARY.md"
```

**Step 4: Validate all three**

```bash
python3 -c "import tomllib; tomllib.load(open('templates/agents/cloud-engineer.toml','rb')); print('OK')"
python3 -c "import tomllib; tomllib.load(open('templates/agents/observability-engineer.toml','rb')); print('OK')"
python3 -c "import tomllib; tomllib.load(open('templates/agents/api-designer.toml','rb')); print('OK')"
```

**Step 5: Commit**

```bash
git add templates/agents/cloud-engineer.toml templates/agents/observability-engineer.toml templates/agents/api-designer.toml
git commit -m "feat(templates): add cloud-engineer, observability-engineer, api-designer agent templates"
```

---

### Task 6: Specialized Agent Templates (Analyst, Technical Writer, Release Manager)

Create final 3 specialized agent TOML templates.

**Files:**
- Create: `templates/agents/analyst.toml`
- Create: `templates/agents/technical-writer.toml`
- Create: `templates/agents/release-manager.toml`

**Step 1: Create analyst.toml**

```toml
[agent]
name = "Analyst"
role = "analyst"
model = "sonnet"
color = "white"
purpose = "Benchmark authoring, regression detection, flame graph analysis, allocation profiling, data quality validation, query performance analysis, schema evolution tracking, project metrics visualization. Produces structured findings with measured impact."

[tools.mcps]
required = ["{{required_mcps}}"]
optional = ["{{optional_mcps}}"]

[tools.documentation]
fallback = ["{{fallback_chain}}"]

[tools.skills]
custom = []

[tools.cli]
commands = ["dominion-cli signal", "dominion-cli doc", "dominion-cli metrics show", "dominion-cli metrics trends"]

[governance]
architectural_decisions = "stop-and-report"
file_ownership = ["{{file_ownership}}"]
hard_stops = ["{{hard_stops}}"]

[workflow]
commit_style = "atomic"
pre_commit = ["{{pre_commit_commands}}"]
produces = "SUMMARY.md"
```

**Step 2: Create technical-writer.toml**

```toml
[agent]
name = "Technical Writer"
role = "technical-writer"
model = "sonnet"
color = "gray"
purpose = "API documentation, ADRs, architecture diagrams (Mermaid/D2), changelogs, onboarding guides. Keeps docs in sync with code changes."

[tools.mcps]
required = ["{{required_mcps}}"]
optional = ["{{optional_mcps}}"]

[tools.documentation]
fallback = ["{{fallback_chain}}"]

[tools.skills]
custom = []

[tools.cli]
commands = ["dominion-cli signal", "dominion-cli doc"]

[governance]
architectural_decisions = "stop-and-report"
file_ownership = ["{{file_ownership}}"]
hard_stops = ["{{hard_stops}}"]

[workflow]
commit_style = "atomic"
pre_commit = ["{{pre_commit_commands}}"]
produces = "SUMMARY.md"
```

**Step 3: Create release-manager.toml**

```toml
[agent]
name = "Release Manager"
role = "release-manager"
model = "sonnet"
color = "gold"
purpose = "Changelog generation from commits, semantic version bumps, release note drafting, tag management, release branch coordination."

[tools.mcps]
required = ["{{required_mcps}}"]
optional = ["{{optional_mcps}}"]

[tools.documentation]
fallback = ["{{fallback_chain}}"]

[tools.skills]
custom = []

[tools.cli]
commands = ["dominion-cli signal", "dominion-cli doc", "dominion-cli history"]

[governance]
architectural_decisions = "stop-and-report"
file_ownership = ["{{file_ownership}}"]
hard_stops = ["{{hard_stops}}"]

[workflow]
commit_style = "atomic"
pre_commit = ["{{pre_commit_commands}}"]
produces = "SUMMARY.md"
```

**Step 4: Validate all three**

```bash
python3 -c "import tomllib; tomllib.load(open('templates/agents/analyst.toml','rb')); print('OK')"
python3 -c "import tomllib; tomllib.load(open('templates/agents/technical-writer.toml','rb')); print('OK')"
python3 -c "import tomllib; tomllib.load(open('templates/agents/release-manager.toml','rb')); print('OK')"
```

**Step 5: Commit**

```bash
git add templates/agents/analyst.toml templates/agents/technical-writer.toml templates/agents/release-manager.toml
git commit -m "feat(templates): add analyst, technical-writer, release-manager agent templates"
```

---

### Task 7: Direction Schema

Update dominion.toml schema template with the `[direction]` section using new naming.

**Files:**
- Modify: `templates/schemas/dominion.toml`

**Step 1: Update direction section**

The file already has a `[direction]` section (lines 21-31) with old naming. Update it:

Change:
```toml
[direction]
mode = "evolve"                     # maintain | evolve | transform

# Only populated when mode = "transform"
[direction.transform]
target_state = ""
migration_strategy = ""            # strangler-fig | big-bang | incremental

[[direction.transform.legacy_zones]]
path = ""
policy = "minimal-touch"
```

To:
```toml
[direction]
mode = "maintain"                   # maintain | improve | restructure

# Only populated when mode = "restructure"
[direction.restructure]
target_state = ""                   # description of target architecture
migration_strategy = ""             # strangler-fig | big-bang | incremental

[[direction.restructure.legacy_zones]]
path = ""                           # directory path
policy = "minimal-change"           # minimal-change (only policy for now)
```

**Step 2: Validate TOML**

Run: `python3 -c "import tomllib; tomllib.load(open('templates/schemas/dominion.toml','rb')); print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add templates/schemas/dominion.toml
git commit -m "feat(schemas): update direction section naming to maintain/improve/restructure"
```

---

### Task 8: Direction Protocol Reference

Create the runtime direction protocol that agents follow.

**Files:**
- Create: `skills/orchestrate/references/direction-protocol.md`

**Step 1: Create direction-protocol.md**

```markdown
# Direction Protocol

How agents read and apply project direction at runtime.

## Reading Direction

At the start of any task that modifies code, read `.dominion/dominion.toml` `[direction]`:
- `mode` — maintain | improve | restructure

If `[direction]` section does not exist, default to `maintain` behavior.

## Mode: Maintain

- Match existing style and patterns in the files you edit
- Do not proactively improve code outside the task scope
- Do not suggest refactoring unless explicitly asked
- Preserve conventions even if you'd prefer different ones

## Mode: Improve

- Boy scout rule — leave files better than you found them
- When editing a file: fix obvious issues (naming, dead code, missing types) in the code you touch
- Do NOT seek out files to improve — only improve files the task requires editing
- Do NOT refactor across module boundaries
- Log improvements made in SUMMARY.md under a "Boy Scout Improvements" section

## Mode: Restructure

Read `[direction.restructure]` for target state and migration strategy.

### Zone Checking

Before editing any file, determine which zone it belongs to:

1. Read `[[direction.restructure.legacy_zones]]` paths
2. Check if the file path falls under any legacy zone
3. Apply the appropriate policy:

**Legacy zone (minimal-change):**
- Only change what the task explicitly requires
- Do NOT learn patterns from this code — it represents the old architecture
- Do NOT refactor or improve legacy code
- Do NOT add new functionality to legacy zones — create new code in non-legacy locations
- If the task requires changes here, make the smallest possible change

**Non-legacy zone (active):**
- Follow target state conventions strictly
- New code must align with `target_state` description
- Do not copy patterns from legacy zones into new code
- Apply migration strategy patterns where applicable

**No legacy zones defined (full restructure):**
- The entire codebase needs restructuring toward target state
- Follow target state conventions everywhere
- Improve code toward target state as you touch it
- No files are protected — all are fair game for restructuring

### Migration Strategies

Read `migration_strategy` to inform approach:
- **strangler-fig**: Build new alongside old, gradually redirect. Never modify old code to match new patterns — replace it.
- **big-bang**: Coordinated rewrite. Follow target state in all new code. Flag legacy code that blocks progress.
- **incremental**: Module-by-module migration. Each touched module should be fully migrated before moving on.

## Reporting

In SUMMARY.md, note:
- Which direction mode was active
- If restructure: which zone(s) were touched and what policy applied
- Any conflicts between task requirements and direction policy (flag as governance decision)
```

**Step 2: Commit**

```bash
git add skills/orchestrate/references/direction-protocol.md
git commit -m "feat(skills): add direction protocol reference for runtime zone checking"
```

---

### Task 9: Zone Check CLI Command

Add `zone check` command to cli-spec.toml.

**Files:**
- Modify: `templates/cli-spec.toml`

**Step 1: Add zone check command**

Add after the `auto decisions` command section (end of file, before `[output]`):

```toml
# === Direction ===

[[commands]]
name = "zone check"
description = "Check direction zone for a file path"
args = [
    { name = "path", description = "File or directory path to check", required = true },
]
reads = [".dominion/dominion.toml"]
behavior = """
Read dominion.toml [direction] section.

If [direction] does not exist or mode != "restructure":
  Output: "No direction constraints. Mode: {mode or 'not configured'}"
  Exit.

If mode = "restructure":
  Read [[direction.restructure.legacy_zones]].

  If no legacy zones defined:
    Output: "Full restructure. Follow target state: {target_state}"
    Exit.

  Check if {path} falls under any legacy zone path:
  If yes:
    Output: "Legacy zone: {zone_path}. Policy: {policy}. Minimal changes only."
  If no:
    Output: "Active zone. Follow target state: {target_state}. Strategy: {migration_strategy}"
"""
```

**Step 2: Update minimum_commands**

Add `"zone check"` to the `minimum_commands` array at the top of the file.

**Step 3: Validate TOML**

Run: `python3 -c "import tomllib; tomllib.load(open('templates/cli-spec.toml','rb')); print('OK')"`
Expected: `OK`

**Step 4: Commit**

```bash
git add templates/cli-spec.toml
git commit -m "feat(cli): add zone check command for direction system"
```

---

### Task 10: Init Wizard — Direction Naming + Specialized Roles Section

Update the init wizard with new direction naming and add specialized roles section.

**Files:**
- Modify: `skills/init/references/wizard-full.md`

**Step 1: Update Section 2 direction naming**

In Section 2: Direction, change:
- `**Evolve**` → `**Improve**`
- `**Transform**` → `**Restructure**`
- All references to `transform` → `restructure` (target_state, legacy_zones paths)
- `[direction.transform.target_state]` → `[direction.restructure.target_state]`
- `[direction.transform.legacy_zones]` → `[direction.restructure.legacy_zones]`
- `minimal-touch` → `minimal-change`

**Step 2: Add Section 5: Specialized Roles**

Insert a new section after Section 4 (Git Workflow) and before current Section 5 (Tools & MCPs). Renumber current Sections 5-9 to 6-10.

New Section 5:

```markdown
## Section 5: Specialized Roles

Read `@data/detection/roles.toml` for role triggers. Cross-reference against discovery results.

Present detected roles:
```
Detected specialized roles:
  1. DevOps — CI/CD and Docker configs found
  2. Database Engineer — PostgreSQL detected via sqlalchemy

Add or remove? [confirm / add <role> / remove <number>]
```

- **confirm**: activate detected roles
- **add <role>**: show available roles from roles.toml, let user pick
- **remove <number>**: deactivate a detected role

For each activated role:
- Read the agent template from `@templates/agents/{role}.toml`
- The Attendant will generate the agent config during the generation phase

If no roles detected:
```
No specialized roles detected. You can add them later with /dominion:educate --agent.
```
```

**Step 3: Renumber remaining sections**

- Current Section 5 (Tools & MCPs) → Section 6
- Current Section 6 (Knowledge Sources) → Section 7
- Current Section 7 (Taste) → Section 8
- Current Section 8 (Autonomy) → Section 9
- Current Section 9 (Roadmap) → Section 10

**Step 4: Commit**

```bash
git add skills/init/references/wizard-full.md
git commit -m "feat(skills): update wizard direction naming and add specialized roles section"
```

---

### Task 11: Domain Taxonomy Data

Create comprehensive domain taxonomy question tree.

**Files:**
- Create: `data/taxonomy/domains.toml`

**Step 1: Create directory and file**

Run: `ls data/` to verify the parent exists, then create `data/taxonomy/`.

Create `data/taxonomy/domains.toml` with comprehensive multi-level taxonomy. Include at minimum these top-level domains with subdomains and follow-up questions:

```toml
[meta]
schema_version = 1
# Domain taxonomy for /dominion:educate DKCP Phase 1
# Question tree structure — enough to ask smart follow-ups

# === Healthcare ===

[[domains]]
name = "healthcare"
subdomains = ["clinical", "pharma", "medical-devices", "health-it", "telehealth"]
follow_ups = [
    "Clinical trials or patient care systems?",
    "Subject to HIPAA compliance?",
    "FDA-regulated software?",
    "EHR/EMR integration needed?",
]

[[domains.subdomains]]
parent = "healthcare"
name = "pharma"
follow_ups = [
    "Drug discovery or manufacturing?",
    "Target identification or lead optimization?",
    "GxP compliance requirements?",
]

[[domains.subdomains]]
parent = "healthcare"
name = "clinical"
follow_ups = [
    "Patient-facing or provider-facing?",
    "Clinical decision support?",
    "HL7/FHIR interoperability?",
]

# === Finance ===

[[domains]]
name = "finance"
subdomains = ["banking", "trading", "insurance", "payments", "crypto", "lending"]
follow_ups = [
    "Retail banking or institutional?",
    "Real-time transaction processing?",
    "PCI-DSS or SOX compliance?",
    "Multi-currency support?",
]

[[domains.subdomains]]
parent = "finance"
name = "trading"
follow_ups = [
    "High-frequency or standard execution?",
    "Market data feeds — which providers?",
    "Risk management requirements?",
]

[[domains.subdomains]]
parent = "finance"
name = "payments"
follow_ups = [
    "Payment gateway or processor?",
    "PCI-DSS compliance level?",
    "Cross-border payments?",
]

# === E-commerce ===

[[domains]]
name = "e-commerce"
subdomains = ["marketplace", "direct-to-consumer", "b2b", "subscription"]
follow_ups = [
    "Physical goods, digital, or services?",
    "Marketplace or single-vendor?",
    "Inventory management complexity?",
    "Tax jurisdiction handling?",
]

# === Education ===

[[domains]]
name = "education"
subdomains = ["k12", "higher-ed", "corporate-training", "edtech", "lms"]
follow_ups = [
    "Student-facing or educator-facing?",
    "FERPA or COPPA compliance?",
    "Assessment and grading?",
    "Content delivery or creation?",
]

# === Media & Entertainment ===

[[domains]]
name = "media"
subdomains = ["streaming", "publishing", "gaming", "social", "advertising"]
follow_ups = [
    "Content creation or distribution?",
    "User-generated content moderation?",
    "Rights management / DRM?",
    "Real-time or on-demand?",
]

# === Logistics & Supply Chain ===

[[domains]]
name = "logistics"
subdomains = ["shipping", "warehousing", "fleet-management", "last-mile", "procurement"]
follow_ups = [
    "B2B or B2C fulfillment?",
    "Real-time tracking requirements?",
    "Multi-carrier integration?",
    "Cross-border customs handling?",
]

# === Real Estate ===

[[domains]]
name = "real-estate"
subdomains = ["property-management", "listings", "construction", "proptech"]
follow_ups = [
    "Residential or commercial?",
    "Property management or transactions?",
    "MLS integration?",
]

# === Government & Public Sector ===

[[domains]]
name = "government"
subdomains = ["civic-tech", "defense", "public-health", "taxation", "justice"]
follow_ups = [
    "Federal, state, or local?",
    "FedRAMP or IL requirements?",
    "Citizen-facing or internal?",
    "Accessibility standards (Section 508)?",
]

# === Manufacturing & IoT ===

[[domains]]
name = "manufacturing"
subdomains = ["industrial-iot", "quality-control", "supply-chain", "mes", "scada"]
follow_ups = [
    "Discrete or process manufacturing?",
    "Real-time equipment monitoring?",
    "OT/IT convergence?",
    "Industrial protocol support (OPC-UA, MQTT)?",
]

# === Agriculture ===

[[domains]]
name = "agriculture"
subdomains = ["precision-farming", "livestock", "supply-chain", "agritech"]
follow_ups = [
    "Crop management or livestock?",
    "Sensor/IoT integration?",
    "Supply chain traceability?",
]

# === Energy & Utilities ===

[[domains]]
name = "energy"
subdomains = ["renewable", "oil-gas", "grid-management", "smart-metering"]
follow_ups = [
    "Generation, transmission, or distribution?",
    "Renewable energy forecasting?",
    "NERC CIP compliance?",
    "Smart grid / AMI integration?",
]

# === Legal ===

[[domains]]
name = "legal"
subdomains = ["contract-management", "ediscovery", "compliance", "legaltech"]
follow_ups = [
    "Law firm or in-house legal?",
    "Contract lifecycle management?",
    "Regulatory compliance tracking?",
    "Privilege and confidentiality handling?",
]

# === Travel & Hospitality ===

[[domains]]
name = "travel"
subdomains = ["booking", "hospitality", "airlines", "car-rental", "experiences"]
follow_ups = [
    "B2C booking or B2B distribution?",
    "GDS/channel manager integration?",
    "Dynamic pricing?",
    "Multi-language / multi-currency?",
]

# === Telecommunications ===

[[domains]]
name = "telecom"
subdomains = ["network-management", "billing", "customer-care", "5g"]
follow_ups = [
    "Network operations or customer-facing?",
    "BSS or OSS systems?",
    "5G / edge computing?",
    "Regulatory compliance (FCC)?",
]

# === Cybersecurity ===

[[domains]]
name = "cybersecurity"
subdomains = ["siem", "endpoint-protection", "identity", "threat-intelligence", "compliance"]
follow_ups = [
    "Detection and response or prevention?",
    "SOC operations?",
    "Compliance framework (SOC 2, ISO 27001)?",
    "Zero trust architecture?",
]

# === AI / ML ===

[[domains]]
name = "ai-ml"
subdomains = ["nlp", "computer-vision", "recommender-systems", "mlops", "generative-ai"]
follow_ups = [
    "Training infrastructure or inference serving?",
    "MLOps / model lifecycle management?",
    "Data labeling and annotation?",
    "Model governance and bias auditing?",
]

# === Automotive ===

[[domains]]
name = "automotive"
subdomains = ["connected-car", "autonomous-driving", "ev-charging", "fleet", "aftermarket"]
follow_ups = [
    "Vehicle software or infrastructure?",
    "AUTOSAR or ASPICE compliance?",
    "V2X communication?",
    "Over-the-air updates?",
]

# === Biotech & Life Sciences ===

[[domains]]
name = "biotech"
subdomains = ["genomics", "bioinformatics", "lab-automation", "clinical-research"]
follow_ups = [
    "Wet lab or dry lab (computational)?",
    "Genomic data processing pipelines?",
    "21 CFR Part 11 compliance?",
    "LIMS integration?",
]

# === Developer Tools ===

[[domains]]
name = "developer-tools"
subdomains = ["ide", "ci-cd", "testing", "monitoring", "package-management", "documentation"]
follow_ups = [
    "For individual developers or teams?",
    "Cloud-hosted or self-hosted?",
    "Language/framework specific or polyglot?",
    "Enterprise or open-source model?",
]

# === SaaS / Platform ===

[[domains]]
name = "saas"
subdomains = ["multi-tenant", "marketplace", "analytics", "crm", "erp", "hr"]
follow_ups = [
    "Multi-tenant architecture?",
    "Self-serve or sales-led?",
    "API-first or UI-first?",
    "Enterprise SSO / SCIM requirements?",
]
```

**Step 2: Validate TOML**

Run: `python3 -c "import tomllib; tomllib.load(open('data/taxonomy/domains.toml','rb')); print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add data/taxonomy/domains.toml
git commit -m "feat(data): add comprehensive domain taxonomy question tree for educate"
```

---

### Task 12: Educate Skill — SKILL.md + DKCP Protocol Reference

Create the `/dominion:educate` skill definition and DKCP protocol reference.

**Files:**
- Create: `skills/educate/SKILL.md`
- Create: `skills/educate/references/dkcp-protocol.md`

**Step 1: Create skills/educate/ directory**

Run: `mkdir -p skills/educate/references`

**Step 2: Create SKILL.md**

```markdown
---
name: educate
description: Capture domain knowledge through structured interview or external sources. Produces knowledge files, skills, or agent configs.
---

# /dominion:educate

Teach Dominion domain knowledge from humans, documentation, or external sources.

## Flag Parsing

- `--from <source>`: Pull from external source (notion, confluence, obsidian, url, file path)
- `--agent`: Force output as agent config (skip output routing)
- `--skill`: Force output as skill file (skip output routing)
- No flags: interactive DKCP interview

## Pre-check

1. Read `.dominion/dominion.toml` — verify project is initialized
2. If `--from` provided: verify source is accessible (file exists, URL reachable, API token configured)
3. Create `.dominion/knowledge/` directory if it doesn't exist

## With `--from` Source

Follow `@references/source-integration.md` to extract knowledge from the external source.
Then skip to Phase 5 (Artifact Grounding) of the DKCP protocol.

## Without `--from` (Interactive Interview)

Follow `@references/dkcp-protocol.md` — the full 7-phase Domain Knowledge Capture Protocol.

## Output Routing

If `--agent` or `--skill` flag provided, use that output format directly.
Otherwise, follow `@references/output-routing.md` to determine the best output format.

## Post-capture

1. If output is a knowledge file: write to `.dominion/knowledge/{topic}.md`, update `.dominion/knowledge/index.toml`
2. If output is a skill: write to `.dominion/skills/{name}.md`
3. If output is an agent: write TOML to `.dominion/agents/{role}.toml`, generate `.claude/agents/{role}.md` via Attendant
4. Run `dominion-cli knowledge sync` to update MEMORY.md with new knowledge
5. Commit all new files
```

**Step 3: Create dkcp-protocol.md**

```markdown
# Domain Knowledge Capture Protocol (DKCP)

7-phase adaptive interview for capturing domain knowledge.

## Phase 1: Domain Mapping

**Agent:** Researcher
**Thinking:** Normal

1. Read `@data/taxonomy/domains.toml`
2. Ask: "What domain does this project operate in?"
3. Match the answer against the taxonomy
4. If match found: use the domain's `follow_ups` to ask targeted questions about subdomains
5. If no match: use Context7 or WebSearch to research the domain, then ask clarifying questions
6. Record: domain name, subdomains involved, key terminology

Output: domain map with terms and subdomain scope.

## Phase 2: Stakeholder Mapping

**Agent:** Researcher
**Thinking:** Normal

Ask one at a time:
1. "Who are the primary users of this system?"
2. "Who are the secondary stakeholders (ops, compliance, support)?"
3. "Are there regulatory bodies that oversee this domain?"
4. "What breaks if this system fails? Who gets hurt?"

Record: stakeholder list with roles and impact levels.

## Phase 3: Regulatory Scan

**Agent:** Researcher
**Thinking:** High effort

Based on domain and stakeholders identified in Phases 1-2:
1. Check taxonomy for regulatory follow-ups (HIPAA, PCI-DSS, GDPR, etc.)
2. Ask: "Are any of these regulations applicable?" (present as checklist)
3. For each applicable regulation: ask about compliance level, current status, and specific requirements
4. Use WebSearch to verify current regulatory requirements if needed

Record: applicable regulations, compliance requirements, certification needs.

## Phase 4: Deep Probe

**Agent:** Advisor
**Thinking:** Ultrathink

Review all knowledge captured in Phases 1-3. Identify:
- Areas where captured knowledge is thin (few details, vague answers)
- Contradictions between stakeholder needs and regulatory requirements
- Domain-specific edge cases that weren't covered

For each gap, ask one targeted follow-up question. Continue until:
- All major gaps are filled, OR
- User indicates they've shared everything they know

## Phase 5: Artifact Grounding

**Agent:** Researcher
**Thinking:** Normal

Anchor domain concepts to actual codebase:
1. Use Serena to search for domain terms in the codebase (class names, function names, comments)
2. For each domain concept: find the corresponding code symbols
3. If a concept has no code representation: note it as "not yet implemented" or "implicit"
4. If code uses different terminology than the domain: note the mapping

Output: concept-to-code mapping table.

## Phase 6: Knowledge Structuring

**Agent:** Advisor
**Thinking:** High effort

Organize captured knowledge into structured files:
1. **Glossary** — domain terms with definitions and code mappings
2. **Constraints** — regulatory requirements, compliance rules, business rules
3. **Stakeholder map** — who cares about what, impact levels
4. **Domain patterns** — common patterns in this domain (e.g., "all financial calculations use decimal, never float")

Write each as a `.md` file in `.dominion/knowledge/`.
Update `.dominion/knowledge/index.toml` with entries for each new file.

## Phase 7: Calibration

**Agent:** Advisor
**Thinking:** Normal

Present the structured knowledge back to the user:
1. Show glossary — "Are these definitions accurate?"
2. Show constraints — "Did I capture all the important rules?"
3. Show stakeholder map — "Is this complete?"
4. Show domain patterns — "Are these patterns correct?"

For each correction:
- Update the relevant knowledge file
- Note what was corrected (helps improve future interviews)

After calibration, proceed to output routing.
```

**Step 4: Commit**

```bash
git add skills/educate/SKILL.md skills/educate/references/dkcp-protocol.md
git commit -m "feat(skills): add educate skill with DKCP protocol reference"
```

---

### Task 13: Educate Skill — Source Integration + Output Routing References

Create the remaining educate reference files.

**Files:**
- Create: `skills/educate/references/source-integration.md`
- Create: `skills/educate/references/output-routing.md`

**Step 1: Create source-integration.md**

```markdown
# Source Integration

Extract domain knowledge from external sources for `/dominion:educate --from`.

## Source Types

### Notion (`--from notion`)
1. Verify Notion MCP is available (check state.toml `[[mcp_status]]`)
2. If unavailable: "Notion MCP not available. Provide a Notion API token or use --from url with exported pages."
3. If available: ask for the database or page URL
4. Extract: page content, database entries, comments
5. Structure into domain knowledge format

### Confluence (`--from confluence`)
1. Ask for Confluence URL and space key
2. Use WebFetch to retrieve pages via REST API
3. Extract: page content, labels, child pages
4. Structure into domain knowledge format

### Obsidian (`--from obsidian:<vault-path>`)
1. Verify the vault path exists on the local filesystem
2. Read the vault's `.obsidian/` directory to understand structure
3. Use Glob to find `.md` files
4. Read files, following `[[wikilinks]]` to build a knowledge graph
5. Structure into domain knowledge format

### URL (`--from url:<url>`)
1. Use WebFetch to retrieve the page
2. Extract meaningful content (skip navigation, ads, boilerplate)
3. If the page links to sub-pages: ask if those should be included
4. Structure into domain knowledge format

### Local File (`--from file:<path>`)
1. Verify the file exists (must be within the project directory)
2. Read the file content
3. If it's a directory: read all `.md`, `.txt`, `.pdf` files within
4. Structure into domain knowledge format

## Post-extraction

After extracting from any source:
1. Cross-reference extracted terms against the codebase (using Serena)
2. Identify conflicts between source knowledge and existing `.dominion/knowledge/` files
3. Present a summary: "Extracted {N} concepts, {N} constraints, {N} patterns from {source}"
4. Proceed to DKCP Phase 5 (Artifact Grounding) to anchor in code
```

**Step 2: Create output-routing.md**

```markdown
# Output Routing

Determine the best output format for captured domain knowledge.

## Decision Logic

After knowledge is captured and structured, the Advisor evaluates scope:

### Knowledge Files (default)
Use when the captured knowledge is:
- Domain facts, terminology, glossaries
- Business rules and constraints
- Regulatory requirements
- Stakeholder maps
- Reference information agents need occasionally

Output: `.dominion/knowledge/{topic}.md` files + index.toml entries

### Skill
Use when the captured knowledge describes:
- A repeatable procedure or workflow
- A decision tree that agents should follow
- A domain-specific process (e.g., "how to handle PCI-DSS audit prep")
- Something that should fire as a `/dominion:*` command

Output: `.dominion/skills/{name}.md` with frontmatter

### Agent
Use when the captured knowledge requires:
- Ongoing specialized behavior (not a one-time procedure)
- Specific tool access or governance rules
- File ownership over domain-specific files
- A role that should appear in the agent roster

Output: `.dominion/agents/{role}.toml` + `.claude/agents/{role}.md`

## Presenting the Recommendation

```
Based on the captured scope, I recommend:
  Format: {knowledge files | skill | agent}
  Reason: {why this format fits}

  {If knowledge}: {N} files covering {topics}
  {If skill}: Skill name: {name}, triggers on: {description}
  {If agent}: Agent role: {role}, purpose: {purpose}

Proceed with this format? [Y / change to skill / change to agent / change to knowledge]
```

If the user overrides, use their chosen format. The `--agent` and `--skill` flags skip this routing entirely.
```

**Step 3: Commit**

```bash
git add skills/educate/references/source-integration.md skills/educate/references/output-routing.md
git commit -m "feat(skills): add source integration and output routing references for educate"
```

---

### Task 14: Study Skill — SKILL.md + References

Create the `/dominion:study` skill with all three reference files.

**Files:**
- Create: `skills/study/SKILL.md`
- Create: `skills/study/references/inventory-assessment.md`
- Create: `skills/study/references/kill-gate.md`
- Create: `skills/study/references/recreation.md`

**Step 1: Create skills/study/ directory**

Run: `mkdir -p skills/study/references`

**Step 2: Create SKILL.md**

```markdown
---
name: study
description: Evaluate an existing plugin's skills/agents, security-review them, and produce Dominion-native artifacts refined beyond the originals.
---

# /dominion:study

Internalize external plugins into Dominion-native artifacts.

## Flag Parsing

- `<plugin>`: Required. The plugin name or path to study.
- `--skill <name>`: Study one specific skill from the plugin
- `--agent <name>`: Study one specific agent from the plugin
- No skill/agent flag: study the entire plugin

## Pre-check

1. Read `.dominion/dominion.toml` — verify project is initialized
2. Locate the plugin: check installed plugins list, resolve path
3. If plugin not found: "Plugin '{name}' not found. Is it installed?"

## Step 1: Read & Assess

Follow `@references/inventory-assessment.md`

Produces: inventory of skills/agents/hooks, security findings, benefit assessment per item.

## Step 2: Kill Gate

Follow `@references/kill-gate.md`

For each assessed item: pass or kill. Items that don't pass are dropped — no further processing.

## Step 3: Recreate

Follow `@references/recreation.md`

For each item that passed the kill gate: create Dominion-native version.

## Post-study

1. Present summary: "{N} items studied, {passed} passed kill gate, {created} artifacts created"
2. List created artifacts with paths
3. Run `dominion-cli agents generate` if any agents were created
4. Commit all new files
5. Inform user: "The studied plugin can now be uninstalled if desired."
```

**Step 3: Create inventory-assessment.md**

```markdown
# Inventory & Assessment

Step 1 of the study pipeline.

## Agents: Researcher + Security Auditor

### Inventory

1. Locate the plugin's directory (installed plugins path)
2. Read the plugin manifest (plugin.json or equivalent)
3. List all skills: read each skill file, note name, description, trigger conditions
4. List all agents: read each agent config, note role, model, tools
5. List all hooks: read hook definitions, note event triggers and commands
6. List all settings: note configuration options

Present inventory:
```
Plugin: {name} v{version}
  Skills: {count}
    - {name}: {description}
  Agents: {count}
    - {role}: {purpose}
  Hooks: {count}
    - {event}: {command}
```

### Security Review

For each skill and agent, the Security Auditor checks:
1. **Prompt injection**: Does the skill accept external input that could manipulate agent behavior?
2. **Data exfiltration**: Does the skill send data to external services without user knowledge?
3. **Permission escalation**: Does the skill request permissions beyond what it needs?
4. **Unsafe operations**: Does the skill run destructive commands, modify system files, or access credentials?

Security findings are rated: safe / caution / dangerous.
- **dangerous**: item is immediately killed, does not proceed to kill gate
- **caution**: noted, proceeds to kill gate with warning
- **safe**: proceeds normally

### Benefit Assessment

For each item (excluding dangerous ones), the Researcher evaluates:
1. What does this item do?
2. Does the project currently have this capability?
3. If not: would having it concretely improve development on *this project*?
4. If yes: what specific scenarios would trigger it?

Record assessment for each item: purpose, current_coverage, benefit_scenarios.
```

**Step 4: Create kill-gate.md**

```markdown
# Kill Gate

Step 2 of the study pipeline. The Advisor decides which items proceed to recreation.

## Gate Criteria

For each item that passed security review, the Advisor must answer:

1. **Concrete scenarios**: Name at least 2 specific situations in this project where this item would fire.
   - "When the developer edits API endpoints" — concrete
   - "It might help with code quality" — too vague, KILL

2. **Outcome improvement**: What measurably improves when this item is used?
   - "Catches OpenAPI spec drift before it reaches production" — measurable
   - "Generally makes things better" — not measurable, KILL

3. **Existing coverage**: Does a Dominion agent or skill already cover this?
   - If fully covered: KILL (avoid duplication)
   - If partially covered: note what's additive, proceed if substantial

## Presentation

```
Kill Gate Results:
  PASS: {name} — {reason}
    Scenarios: {scenario_1}, {scenario_2}
    Improves: {outcome}

  KILL: {name} — {reason}
    Why: {explanation}
```

## Strictness

This gate is intentionally strict. The cost of recreating a useless skill is wasted tokens and artifact bloat. The cost of killing a marginally useful skill is zero — the original plugin remains available.

If zero items pass: "No items from {plugin} passed the benefit threshold for this project. The plugin's capabilities are either already covered by Dominion agents or not concretely applicable."
```

**Step 5: Create recreation.md**

```markdown
# Recreation

Step 3 of the study pipeline. Create Dominion-native artifacts that improve on the originals.

## Agents: Researcher + Reviewer

## Process

For each item that passed the kill gate:

### 1. Critical Analysis

Read the original skill/agent carefully. Identify:
- **Strengths**: What does it do well? What patterns are worth preserving?
- **Weaknesses**: What's poorly structured, overly complex, or fragile?
- **Assumptions**: What does it assume about the project? Do those assumptions hold here?
- **Missed opportunities**: What could it do better with project-specific knowledge?

### 2. Design

Design the Dominion-native version:
- If recreating as a **skill**: follow Dominion skill conventions (directive prose, `@references/` for sub-steps, valid YAML frontmatter)
- If recreating as an **agent**: create TOML config following existing agent template patterns, with appropriate model, tools, governance, and file ownership
- If recreating as **knowledge**: structure as `.dominion/knowledge/` files with index entries

The recreation must:
- Integrate with the existing agent model (respect governance, file ownership, hard stops)
- Use project-specific knowledge (conventions from style.toml, direction from dominion.toml)
- Follow Dominion conventions (CLI commands, signal protocol, SUMMARY.md format)

### 3. Write

Write the Dominion-native artifact:
- Skills: write to `.dominion/skills/{name}.md`
- Agents: write TOML to `.dominion/agents/{role}.toml`, Attendant generates `.claude/agents/{role}.md`
- Knowledge: write to `.dominion/knowledge/{topic}.md`, update index.toml

### 4. Verify

The Reviewer checks the recreated artifact:
- Does it follow Dominion conventions?
- Is it actually better than the original? (not just a copy with different formatting)
- Does it integrate properly with existing agents?
- Are there any governance conflicts?

If verification fails: iterate on the design. Do not commit a recreation that's worse than the original.
```

**Step 6: Commit**

```bash
git add skills/study/SKILL.md skills/study/references/inventory-assessment.md skills/study/references/kill-gate.md skills/study/references/recreation.md
git commit -m "feat(skills): add study skill with inventory, kill-gate, and recreation references"
```

---

### Task 15: Explore Step — Role Trigger Detection

Add role trigger detection to the explore step so new roles can be suggested during improve.

**Files:**
- Modify: `skills/explore/SKILL.md`

**Step 1: Add role trigger detection**

After Step 3 (Assumption Verification) and before Step 4 (Write Research), add a new step:

```markdown
## Step 3.5: Role Trigger Detection

Check for new specialized role opportunities:
1. Read `@data/detection/roles.toml` for all role triggers
2. Read `.dominion/agents/` to get currently active roles
3. Cross-reference: are there triggers firing for roles not yet activated?
4. For each new trigger found: record as a role proposal in research.toml `[[role_proposals]]`

```toml
[[role_proposals]]
role = ""                           # role name from roles.toml
trigger = ""                        # what triggered the detection
confidence = ""                     # high | medium | low
```

If no new triggers found: skip. This step is silent unless new roles are detected.
```

**Step 2: Commit**

```bash
git add skills/explore/SKILL.md
git commit -m "feat(skills): add role trigger detection to explore step"
```

---

### Task 16: Improve Step — Role Suggestions

Add role suggestion presentation to the retrospective.

**Files:**
- Modify: `skills/improve/references/retrospective.md`

**Step 1: Add role suggestion section**

After the "Autonomous Decision Review" section and before "Present Retrospective", add:

```markdown
## Role Suggestions

Check the most recent research.toml for `[[role_proposals]]` entries.

If none exist, skip this section.

If proposals exist, present them:

```
New specialized roles detected:

  {role}: {trigger}
  Confidence: {confidence}
  Purpose: {description from roles.toml}

  Activate this agent? [Y/n]
```

For each accepted role:
- Read the agent template from `@templates/agents/{role}.toml`
- Attendant generates the agent config: `.dominion/agents/{role}.toml` + `.claude/agents/{role}.md`
- Run `dominion-cli agents generate` to update AGENTS.md

For rejected roles:
- Note in improvements.toml as a rejected proposal (so it's not suggested again next phase)
```

**Step 2: Commit**

```bash
git add skills/improve/references/retrospective.md
git commit -m "feat(skills): add role suggestion section to retrospective"
```

---

### Task 17: Validate Checks 22-25

Add new validation checks for v0.6 features.

**Files:**
- Modify: `skills/validate/references/checks.md`

**Step 1: Add checks 22-25**

Append after Check 21:

```markdown
## Check 22: Direction Configuration

- If `.dominion/dominion.toml` has a `[direction]` section:
  - Verify `mode` is one of: maintain, improve, restructure
  - If mode = "restructure": verify `[direction.restructure]` exists
  - Verify `target_state` is non-empty when mode is restructure
  - Verify `migration_strategy` is one of: strangler-fig, big-bang, incremental

Pass: direction config valid
Warn: no [direction] section (default maintain behavior)
Fail: invalid mode or missing restructure config

## Check 23: Restructure Legacy Zones

- If `[direction]` mode = "restructure" and `[[direction.restructure.legacy_zones]]` entries exist:
  - For each legacy zone: verify `path` is non-empty
  - Verify `policy` is "minimal-change"
  - Verify the path exists in the project (warn if it doesn't — may be planned)

Pass: all legacy zones have valid paths and policies
Warn: legacy zone path does not exist in project (may be planned)
Fail: missing path or invalid policy value

## Check 24: Specialized Role Agent Files

- For each `.dominion/agents/*.toml` file:
  - If the role matches a name in `@data/detection/roles.toml`:
    - Verify the agent template exists in `@templates/agents/{role}.toml`
    - Verify the agent has a matching `.claude/agents/{role}.md`

Pass: all specialized role agents reference valid templates and have .md files
Warn: no specialized roles activated (acceptable)
Fail: agent references non-existent template or missing .md file

## Check 25: Domain Taxonomy Integrity

- Verify `@data/taxonomy/domains.toml` parses as valid TOML
- Verify each `[[domains]]` entry has: name, subdomains (array), follow_ups (array)
- Verify each `[[domains.subdomains]]` entry has: parent, name, follow_ups (array)
- Verify subdomain `parent` values reference existing domain names

Pass: taxonomy valid and consistent
Fail: parse error, missing required fields, or orphaned subdomains
```

**Step 2: Commit**

```bash
git add skills/validate/references/checks.md
git commit -m "feat(skills): add validate checks 22-25 for direction, roles, taxonomy"
```

---

### Task 18: CLI Spec Version Bump

Update cli-spec.toml spec_version and minimum_commands.

**Files:**
- Modify: `templates/cli-spec.toml`

**Step 1: Update spec_version**

Change: `spec_version = "0.5"` → `spec_version = "0.6"`

**Step 2: Add zone check to minimum_commands**

Add `"zone check"` to the `minimum_commands` array.

**Step 3: Validate TOML**

Run: `python3 -c "import tomllib; tomllib.load(open('templates/cli-spec.toml','rb')); print('OK')"`
Expected: `OK`

**Step 4: Commit**

```bash
git add templates/cli-spec.toml
git commit -m "chore(cli): bump spec_version to 0.6, add zone check to minimum_commands"
```

---

### Task 19: Version Bump

Bump plugin and marketplace manifests to 0.6.0.

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Step 1: Update versions**

In both files, change `"version": "0.5.0"` → `"version": "0.6.0"`.

**Step 2: Commit**

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore: bump version to 0.6.0"
```

---

### Task 20: Research Schema — Role Proposals

Add `[[role_proposals]]` to the research.toml schema template.

**Files:**
- Modify: `templates/schemas/research.toml`

**Step 1: Add role_proposals section**

Append to the end of `templates/schemas/research.toml`:

```toml
# Role proposals (detected during explore, suggested during improve)
[[role_proposals]]
role = ""                           # role name from roles.toml
trigger = ""                        # what triggered the detection
confidence = ""                     # high | medium | low
```

**Step 2: Validate TOML**

Run: `python3 -c "import tomllib; tomllib.load(open('templates/schemas/research.toml','rb')); print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add templates/schemas/research.toml
git commit -m "feat(schemas): add role_proposals to research.toml schema"
```

---

### Task 21: Integration Validation

Verify all changes work together — TOML files parse, file references resolve, no broken cross-references.

**Files:**
- Read: All modified and created files

**Step 1: Validate all TOML files**

Run:
```bash
for f in data/detection/roles.toml data/detection/languages.toml data/taxonomy/domains.toml templates/schemas/dominion.toml templates/schemas/research.toml templates/cli-spec.toml templates/agents/devops.toml templates/agents/frontend-engineer.toml templates/agents/database-engineer.toml templates/agents/cloud-engineer.toml templates/agents/observability-engineer.toml templates/agents/api-designer.toml templates/agents/analyst.toml templates/agents/technical-writer.toml templates/agents/release-manager.toml; do echo -n "$f: "; python3 -c "import tomllib; tomllib.load(open('$f','rb')); print('OK')"; done
```

Expected: all OK

**Step 2: Verify file references in skills**

Check that all `@references/` paths in skill files point to files that exist:
- `skills/educate/SKILL.md` references: `@references/dkcp-protocol.md`, `@references/source-integration.md`, `@references/output-routing.md`
- `skills/study/SKILL.md` references: `@references/inventory-assessment.md`, `@references/kill-gate.md`, `@references/recreation.md`
- `skills/orchestrate/references/direction-protocol.md` — standalone, no outgoing references
- `skills/explore/SKILL.md` references: `@data/detection/roles.toml`

Verify each referenced file exists.

**Step 3: Verify cross-references**

- `data/detection/roles.toml` `agent_template` values match files in `templates/agents/`
- `templates/cli-spec.toml` includes `zone check` in minimum_commands
- `skills/validate/references/checks.md` checks 22-25 reference correct schemas

**Step 4: Final commit if fixes needed**

If any fixes were required:
```bash
git add -A
git commit -m "fix: resolve integration issues from v0.6 cross-references"
```
