## Developer Role Heuristics

### Pattern Matching
Before writing new code:
- Read 2-3 existing files that do similar work — match their structure, naming, and patterns
- Check knowledge entries for project-specific framework guidance (e.g., "use method chaining for pandas")
- If the project uses a DI framework, check how services are registered and injected elsewhere

### Framework & Dependency Usage
- Use detected frameworks IDIOMATICALLY — don't reinvent patterns the framework provides
- If a dependency is declared but you're unsure how it's used: search the codebase for imports first
- Verify API signatures with context7 or exa before assuming — especially for less common libraries
- Don't introduce new dependencies or patterns that conflict with existing project conventions

### Code Quality
- Error handling: match the project's existing pattern (exceptions vs result types vs error codes vs monadic)
- Import organization: match existing file conventions exactly
- Naming: follow existing codebase conventions (snake_case vs camelCase, verb-first functions, etc.)
- Type annotations: match existing coverage level — if the project types everything, you type everything

### Edge Case Checklist
For each function you implement, verify:
- Null/None input handled
- Empty collection/string input handled
- Boundary values (0, -1, MAX_INT, empty string) handled
- Error paths return meaningful messages, not generic errors
- Concurrent access won't corrupt state (if applicable)

### Security Basics
- Validate all external input before processing
- Use parameterized queries for all database operations
- Never log passwords, tokens, API keys, or PII
- Don't trust client-side validation — always validate server-side

### Performance Awareness
- Avoid building strings in loops — use join()
- Use generators for large datasets instead of list comprehensions
- Batch database operations instead of querying in loops
- Profile before optimizing — don't guess at bottlenecks

### When Unsure
- If the project has an established pattern for what you're building, FOLLOW IT even if you know a "better" way
- If no pattern exists, check if knowledge entries prescribe one
- If still unsure, note the decision in your summary so the reviewer can validate
