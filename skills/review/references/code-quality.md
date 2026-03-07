# Code Quality Review

Reviewer-driven code quality assessment.

## Input

Read and internalize:
1. Git diff: all changes in this phase (diff from phase start commit to current HEAD)
2. `.dominion/phases/{N}/test-report.toml` — test results and gaps
3. `.dominion/style.toml` — project code conventions
4. Run `dominion-cli style check` to get automated convention violations

## Review Dimensions

The code quality review is one part of a 9-dimension assessment. This reference covers the dimensions evaluated during code review. Each finding gets a severity from the unified severity framework:

- **Critical**: correctness bugs, security vulnerabilities, data loss risk, governance violations, PII exposure
- **Major**: performance degradation, high-risk untested code, missing error recovery, breaking changes without migration
- **Minor**: style violations, naming issues, documentation gaps, sub-optimal patterns
- **Info**: suggestions, alternative approaches, observations

## Security Dimension (OWASP Top 10)

Check for common vulnerability classes in changed code:
- **Injection**: SQL, command, XSS — any unsanitized input reaching execution contexts
- **Broken Authentication**: weak password policies, missing MFA, session fixation
- **Sensitive Data Exposure**: secrets in code, PII in logs, unencrypted sensitive data at rest
- **Broken Access Control**: IDOR/BOLA, missing authorization checks, privilege escalation
- **Security Misconfiguration**: debug mode in production, default credentials, open CORS
- **Input validation**: missing boundary validation at system entry points

## Compliance Baseline

Check for regulatory red flags (not a full compliance audit — flag for Security Auditor):
- PII in logs or error messages
- Hardcoded secrets or credentials
- Unencrypted sensitive data at rest
- Data retention patterns (storing data without expiry)
- Missing input sanitization for stored data

## Resource Management

Check for proper resource cleanup:
- Language-specific patterns: RAII (Rust/C++), context managers (Python), try-with-resources (Java), defer (Go)
- Missing cleanup in error paths
- Resource leaks in hot paths (connections, file handles, locks)

## Error Recovery

Check error handling goes beyond catching:
- Does the system recover after errors, not just catch them?
- Missing timeouts on external calls
- Retry without backoff
- Cascading failure potential
- Missing circuit breakers on external dependencies

## Checklist

### Style Compliance
- **Naming**: do new identifiers follow the project's naming conventions (from style.toml)?
- **Formatting**: consistent indentation, line length, import ordering?
- **Imports**: no unused imports, proper grouping?
- Run project linter if configured (detect from project structure)

### Error Handling
- Are errors handled explicitly, not silently swallowed?
- Do error messages provide context (what failed, why, what to do)?
- Are error types appropriate (not generic catch-all)?

### Complexity
- Flag functions/methods over 50 lines
- Flag nesting deeper than 3 levels
- Flag functions with more than 5 parameters
- Suggest extraction or simplification for flagged items

### Documentation
- Do new public APIs have documentation?
- Are complex algorithms commented?
- Are configuration options documented?

### Style Check Results
- **Style check results**: include any violations from `dominion-cli style check` as findings with category "convention"

## Output

For each finding:
- `id`: R1, R2, ... (sequential, continuing from other review steps)
- `category`: "code-quality"
- `severity`: high (bugs, security) | medium (maintainability) | low (style) | info (suggestions)
- `title`: one-line summary
- `description`: detailed explanation
- `file`: file path where the issue was found
- `suggestion`: actionable fix
