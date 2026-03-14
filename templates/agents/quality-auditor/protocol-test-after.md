# Test-After Protocol (Standard Mode)

When `testing_style` includes `test-after`, write comprehensive tests for completed implementation.

## Test Strategy

1. **Read risk context** — HRBT risk matrix from research.toml, critical_path flags from plan.toml.
2. **Layer by test pyramid** — many unit tests (base), some integration (boundaries), few e2e (full stack).
3. **Modulate depth by risk** — high-risk components get all layers + property-based + adversarial. Low-risk get unit only.

## Test Design

Apply techniques based on code characteristics:
- **Equivalence Partitioning** for input spaces
- **Boundary Value Analysis** at partition edges
- **State Transition Testing** for stateful components
- **Decision Table Testing** for complex conditionals

## Test Implementation

- Follow AAA structure (Arrange-Act-Assert) — no logic in tests.
- Mock at system boundaries only, not internal modules.
- Use data-driven/parameterized tests for equivalence classes.
- Run after each batch to catch failures early.

## Output

Write `test-report.toml` with criteria results, coverage analysis, and gap inventory.
