# Audit Synthesis Protocol

Before issuing your verdict, synthesize all audit findings from the multi-agent audit step.

1. **Read test-report.toml** — Quality Auditor's testing findings, coverage gaps, fragility assessment
2. **Read security-findings.toml** — Security Auditor's vulnerability findings (if present)
3. **Read performance-report.toml** — Analyst's performance findings (if present)

## Cross-referencing

- If Security Auditor found vulnerabilities that Quality Auditor's tests don't cover → severity upgrade
- If Analyst found performance regressions in code that passed all tests → flag test gap
- If multiple auditors flagged the same area → systematic issue, not isolated bug

## Verdict Synthesis

Your verdict must account for ALL audit findings, not just your own code review:
- Any high-severity security finding → automatic no-go
- Multiple medium-severity findings in the same area → consider no-go
- Test coverage gaps in critical paths → go-with-warnings at minimum
