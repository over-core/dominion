# Assumption Verification

After producing findings, opportunities, and assumptions, run a verification pass on all assumptions.

## Verification Protocol

For each `[[assumptions]]` entry in research.toml:

### Step 1: Classify Risk

Assess the assumption's risk level:
- **high** — if false, phase goals are unachievable or plan must fundamentally change
- **medium** — if false, specific tasks need replanning but phase goals are still achievable
- **low** — if false, minor adjustments needed with no structural impact

Set `risk` field accordingly.

### Step 2: Attempt Verification

Use available tools to verify each assumption:

1. **Code-verifiable** — read files, check imports, inspect APIs, run non-destructive commands
   - Example: "Library X supports feature Y" → check dependency version, read docs via context7
   - Set `status = "verified"`, `verified_by = "{method used}"`, `verified_at = "{ISO 8601}"`

2. **Docs-verifiable** — check documentation, changelogs, README files
   - Use context7 `query-docs` or read local docs
   - Set `status = "verified"`, `verified_by = "docs: {source}"`, `verified_at = "{ISO 8601}"`

3. **Cannot verify now** — requires runtime execution, external API calls, or human judgment
   - Set `status = "unverified"`, leave `verified_by` and `verified_at` empty
   - The Architect treats these as risks during planning

4. **Contradicted by evidence** — evidence found that disproves the assumption
   - Set `status = "false"`, `verified_by = "contradicted: {evidence}"`
   - Flag prominently in the research output

## False Assumption Handling

If any assumption is marked `false`:
- Present to the user immediately: "Assumption {id} is false: {text}. Evidence: {verified_by}"
- The Architect must account for this during planning — the false assumption constrains the design
- Do NOT silently continue — false assumptions change the scope of the phase

## Output

The verification pass modifies the existing `[[assumptions]]` entries in research.toml. No new artifact is produced.
