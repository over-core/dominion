# Security-Aware Protocol

When Security Auditor is active in the project, apply security considerations to your work.

## For Researcher

- Include threat surface analysis in findings
- Flag authentication, authorization, crypto, and injection patterns
- Add `specialist_referral: "security-auditor"` to security-related findings

## For Architect

- Route security-related tasks to Security Auditor
- Include security constraints in task acceptance criteria
- Flag public API changes, auth flows, and data access patterns

## For Developer

- Follow OWASP Top 10 awareness: input validation, output encoding, auth checks
- Never hardcode secrets, tokens, or credentials
- Use parameterized queries, not string concatenation for data access
- Report security-adjacent patterns via `agent_signal` if uncertain

## For Reviewer

- Check for security anti-patterns in code changes
- Verify auth boundaries are maintained
- Flag unvalidated input handling
