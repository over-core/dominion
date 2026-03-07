# Codebase Analysis

Researcher-driven analysis scoped to the current phase goals.

## Methodology Phases

Research follows a 5-phase pipeline. Execute in order:

1. **Context Loading** — Never start from scratch. Read prior phase research (`dominion-cli research findings`), backlog items, EchoVault search results (`memory_search` + `memory_context`), `intent.md`, and `roadmap.toml`. Understand what is already known before exploring.

2. **Architecture Mapping** — Top-down systematic exploration. Trace entry points → module boundaries → dependency graph → data flow → control flow. Primary tool: serena (`get_symbols_overview`, `find_referencing_symbols`). Record findings with category "architecture".

3. **Deep Analysis** — Bottom-up targeted analysis. Check error handling, test coverage, technical debt, documentation state, complexity, and pattern consistency against `style.toml`. Record findings with appropriate categories.

4. **Cross-Cutting** — Specialist-aware expansion. Check `.dominion/agents/` for active specialist roles. Read their `[research_lens]` checklists. Apply matching specialist-activated methods (e.g., if security-auditor exists, apply STRIDE threat modeling; if database-engineer exists, trace data lineage).

5. **Synthesis** — Prioritize and flag. Score findings by severity x confidence x goal alignment. Assess opportunities. Map assumptions. Generate specialist referrals. Save discoveries to EchoVault via `memory_save`.

## Evidence Grading

Every finding and assumption requires an evidence grade:

- **confirmed** — Multiple independent sources (code + tests + docs). Highest confidence. Use for findings backed by direct code inspection AND corroborating evidence.
- **supported** — Single strong source (direct code inspection). High confidence. Most common grade for code-verified findings.
- **inferred** — Logical deduction from observed patterns. Medium confidence. Flag for verification during planning. Must explain reasoning chain.
- **speculative** — Hypothesis without direct evidence. Low confidence. List as assumption, NEVER as finding. Always explain what evidence would confirm or deny.

## Specialist-Aware Cross-Cutting

When specialist agents are active (check `.dominion/agents/` for non-core agent files):

- **security-auditor**: Apply STRIDE per component. Produce threat categories, attack surface inventory.
- **database-engineer**: Trace data flow paths, integrity constraints, migration risk.
- **api-designer**: Surface inventory, versioning state, consumer dependency map, breaking change risk.
- **frontend-engineer**: State flow, render dependency chains, accessibility gap inventory.
- **devops**: Pipeline effects, infrastructure dependency changes, rollback surface.
- **observability-engineer**: Instrumentation coverage, logging gaps, SLO-relevant paths.
- **cloud-engineer**: Service dependency changes, IAM scope, cost/quota implications.
- **release-manager**: Changelog candidates, semver implications, migration guide needs.
- **technical-writer**: Stale docs, missing API docs, ADR candidates.

If a specialist role is NOT active, skip its cross-cutting checklist entirely.

## Scope Determination

1. Read `.dominion/phases/{N}/intent.md` for phase goals and scope boundary
2. Read `.dominion/roadmap.toml` for phase description
3. Identify relevant source directories, modules, and files based on goals
4. Explicitly note what is OUT of scope per the intent

## Architecture Scan

For each relevant area:
1. Use Glob to find source files in the area
2. Read key files — entry points, interfaces, configuration
3. Identify patterns: design patterns in use, layering, module boundaries
4. Note coupling: which modules depend on each other, shared state, cross-cutting concerns
5. Map public APIs and interfaces that the phase may need to modify or extend

Record findings with category "architecture".

## Dependency Analysis

1. Read package manifests (Cargo.toml, pyproject.toml, package.json, go.mod, etc.)
2. Check dependency versions — are any deprecated, outdated, or known-vulnerable?
3. Cross-reference with `.dominion/dominion.toml` `[governance.hard_rules]` for dependency constraints
4. Note any dependency changes the phase goals may require

Record findings with category "dependency".

## Code Quality Scan

1. Use Grep to find error handling patterns — bare excepts, unwraps, unchecked returns
2. Check test coverage — do areas the phase will modify have tests?
3. Look for documentation gaps in public APIs the phase will extend
4. Check for TODO/FIXME/HACK comments in relevant areas

Record findings with category "testing", "performance", or "security" as appropriate.

## Risk Identification

For each area the phase will modify:
1. What could go wrong? (breaking changes, data loss, security gaps)
2. What is the blast radius? (how many other modules are affected)
3. What existing test coverage exists?
4. Are there governance-sensitive files (from dominion.toml)?

Record high-risk findings with severity "high".

## Opportunity Identification

While analyzing the codebase, note improvement opportunities that are outside the current phase scope but valuable:

1. **Simplification**: complex patterns that could be simplified, redundant abstractions
2. **Reuse**: shared logic duplicated across modules that could be extracted
3. **Performance**: obvious performance gains (missing indexes, unnecessary allocations, N+1 queries)
4. **Developer experience**: friction in build, test, or development workflows

Each opportunity must have:
- `id`: O1, O2, ... (sequential)
- `title`: one-line summary
- `benefit`: what improves if addressed
- `effort`: low | medium | high

## Output Format

Each finding must have:
- `id`: F1, F2, ... (sequential)
- `severity`: high | medium | low
- `category`: architecture | dependency | performance | security | testing
- `title`: one-line summary
- `description`: detailed explanation
- `evidence`: list of file:line references
- `recommendation`: actionable next step
