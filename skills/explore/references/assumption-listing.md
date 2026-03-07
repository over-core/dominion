# Assumption Listing

Identify and classify assumptions that the phase plan will depend on.

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
- `verified_by`: evidence or method used to verify (empty if unverified)

Flag any "false" assumptions immediately — these may invalidate phase goals.
