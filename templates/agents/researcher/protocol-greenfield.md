# Greenfield Research Protocol

For new features and greenfield projects:

1. **Ecosystem survey** — identify libraries, frameworks, and patterns relevant to the feature
   - Use context7 for indexed library docs
   - Use Exa `get_code_context_exa` for real-world code examples (if available)
   - Use Exa `web_search_exa` for best practices and architecture patterns
2. **Architectural analysis** — analyze how the feature fits into existing architecture
   - Use serena for codebase structure mapping
   - Identify integration points and boundaries
   - Map module dependencies with Bohner-Arnold impact analysis
3. **Risk assessment** — identify risks with evidence-based severity:
   - **high**: breaking changes, security implications, architectural violations
   - **medium**: performance concerns, complexity, integration challenges
   - **low**: style issues, minor refactoring opportunities
4. **Specialist referrals** — if findings touch security, database, API design, or infrastructure, add `specialist_referral` field pointing to the relevant specialist agent
5. **Write research.toml** — findings (severity-sorted), assumptions (confidence-graded), opportunities, specialist referrals
