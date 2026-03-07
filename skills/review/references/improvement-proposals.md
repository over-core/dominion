# Improvement Proposals

Generate actionable improvement proposals from phase evidence.

## Inputs

Read:
1. All SUMMARY.md files for the current phase: `.dominion/phases/{N}/summaries/task-*.md`
   - Focus on "Friction Encountered" and "Decisions Made" sections
2. Findings from Steps 1-3 (already in conversation context)
3. `.dominion/improvements.toml` — previously rejected proposals (do not re-propose)

## Pattern Detection

Scan for recurring themes:

- **Repeated lookups**: multiple agents performing the same information retrieval → propose CLI command or knowledge file
- **Convention violations**: same style issue flagged in multiple tasks → propose style.toml addition or hookify rule
- **Missing tooling**: agents using multi-step workarounds for a common operation → propose CLI command
- **Instruction gaps**: agents repeatedly encountering the same surprise → propose agent instruction refinement
- **Documentation gaps**: agents struggling to find the right approach → propose knowledge file or doc chain update

## Filtering

Before proposing:
1. Read `.dominion/improvements.toml`
2. Check each candidate against previously rejected proposals (match by title similarity and type)
3. Do not re-propose rejected items unless new evidence significantly changes the case
4. Check accepted proposals — don't propose something already implemented

## Proposal Formulation

For each identified improvement:

1. **Categorize**: tooling (new CLI command, new hook), governance (new rule, modified hard stop), convention (style change, instruction update)
2. **Evidence**: list specific file references (summaries, review findings, test reports)
3. **Reason**: explain why this matters — quantify if possible ("4 agents wasted ~12k tokens each on this lookup")
4. **Actionable**: the proposal must describe what to change, not just what's wrong

## Output

Produce `[[proposals]]` entries with:
- id: P{N} (sequential, unique within this phase's review)
- type: tooling | governance | convention
- title: concise description of the change
- evidence: list of file paths
- reason: why this improvement matters
- status: "pending"

## Guard Rail

Never propose removing a governance hard stop. Flag it as a finding with category "governance" and severity "info" instead.
