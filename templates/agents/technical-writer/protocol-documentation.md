# Documentation Protocol

## Content Audit

Before writing:
1. Inventory existing docs — what exists, what's stale, what's missing?
2. Check Diataxis type needed: tutorial (learning), how-to (goal), reference (information), explanation (understanding)
3. Identify the audience — developer? operator? end user? New contributor?

## Source Analysis

Extract knowledge from code using serena:
1. `get_symbols_overview` — map public API surface
2. `find_symbol` with `include_body=True` — read implementations to document
3. Trace type definitions and function signatures for reference docs
4. Read existing docstrings and inline comments

Do NOT read entire files — use symbol-level navigation for efficiency.

## Writing Standards

1. **Plain language** — short sentences, active voice, concrete examples. No jargon without definition.
2. **Progressive disclosure** — lead with what the reader needs most. Details in subsequent sections.
3. **Code examples are mandatory** — every API reference entry needs a working example. No "see the source code" copouts.
4. **Docs as Code** — documentation lives in the repo, version-controlled alongside code, reviewed in PRs.

## Diagramming

Use Mermaid or D2 for diagrams:
- **Architecture diagrams** — C4 model (context → container → component)
- **Sequence diagrams** — for multi-step flows (API calls, pipeline steps)
- **State diagrams** — for lifecycle management (pipeline states, deployment stages)
- Keep diagrams simple — 5-10 nodes maximum. Split complex diagrams.

## ADRs (Architecture Decision Records)

When assigned ADR tasks:
1. Follow Michael Nygard format: Title, Status, Context, Decision, Consequences
2. Context must explain WHY, not just WHAT
3. Consequences must list both positive and negative
4. Link to related ADRs when decisions supersede or depend on others

## Verification

1. All links resolve (no broken references)
2. Code examples compile/run
3. Diagrams render correctly
4. Content matches current code (check against serena symbols)
