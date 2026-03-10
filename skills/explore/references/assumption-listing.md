# Assumption Listing

Identify and classify assumptions that the phase plan will depend on.

## Historical Awareness

Before listing new assumptions, search EchoVault for prior assumptions from previous phases:

1. Run `memory_search` with query "assumptions" scoped to the current project
2. Run `memory_search` with query "verified assumptions" for known-true facts
3. Review results — if a prior assumption was already verified or falsified, do NOT re-list it as new. Instead:
   - If **verified**: reference it as established fact, not assumption
   - If **false**: note the contradiction and adjust current assumptions accordingly
   - If **unverified from prior phase**: carry it forward with its existing status and add any new evidence

This prevents redundant verification work and ensures cross-phase learning.

## Sources of Assumptions

### From Research Findings
For each finding, ask: "What must be true for the recommendation to work?"
- Architecture assumptions: "Module X can be extended without breaking Y"
- Dependency assumptions: "Library Z supports feature W in current version"
- Quality assumptions: "Existing tests cover the contract we need to preserve"

### From Phase Goals
For each goal in intent.md, ask: "What must be true for this to be achievable?"
- Scope assumptions: "Feature X can be implemented without touching module Y"
- Effort assumptions: "This change is atomic enough for a single task"
- Integration assumptions: "Components A and B can be modified independently"

### From Dependencies
For each relevant dependency:
- Compatibility: "Version X.Y is compatible with our stack"
- Feature availability: "The API we need exists and is stable"
- License: "License permits our usage pattern"

## Verification Protocol

For each assumption, attempt immediate verification:

- **Can verify now** (read a file, check a version, test an import): verify it, set status = "verified", record verified_by
- **Can only verify by running** (needs test execution, API call, build): set status = "unverified", note what would verify it
- **Clearly false** (contradicted by evidence found during analysis): set status = "false", record the contradicting evidence

## Output Format

Each assumption must have:
- `id`: A1, A2, ... (sequential)
- `text`: clear statement of what is assumed
- `status`: unverified | verified | false
- `evidence_grade`: confirmed | supported | inferred | speculative
- `verified_by`: evidence or method used to verify (empty if unverified)

Evidence grade definitions:
- **confirmed** — Multiple independent sources (code + tests + docs). Highest confidence.
- **supported** — Single strong source (direct code inspection). High confidence.
- **inferred** — Logical deduction from observed patterns. Medium confidence. Flag for verification.
- **speculative** — Hypothesis without direct evidence. Low confidence.

Note: `status` and `evidence_grade` are independent. An assumption can be `status = "verified"` with `evidence_grade = "supported"` (verified by one strong source) or `status = "unverified"` with `evidence_grade = "inferred"` (logically reasonable but not yet checked).

Flag any "false" assumptions immediately — these may invalidate phase goals.
