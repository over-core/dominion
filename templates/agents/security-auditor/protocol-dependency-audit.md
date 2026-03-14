# Dependency Audit Protocol

Review dependency changes for security implications:

1. **New dependencies** — for each new package:
   - Check known vulnerabilities (CVE databases via Exa or WebSearch)
   - Assess maintenance status (last release, open issues, bus factor)
   - Evaluate transitive dependency tree size
   - Check license compatibility
2. **Updated dependencies** — for each version change:
   - Review changelog for security fixes
   - Check for breaking changes that might bypass security controls
   - Verify compatibility with existing security measures
3. **Removed dependencies** — verify no security features depended on removed packages

## Dependency Findings

Include in security-findings.toml:
- `category`: "dependency"
- `package`: package name and version
- `vulnerability`: CVE ID if applicable
- `remediation`: upgrade path or alternative package
