# Test Audit Protocol (TDD Mode)

When `testing_style` includes `tdd`, the Developer has already written tests for each task. Your role shifts from writing tests to AUDITING the Developer's tests.

## Audit Checklist

1. **Assertion coverage** — Does every acceptance criterion have at least one test? Map criteria to test functions.
2. **Edge case coverage** — Apply Boundary Value Analysis to each tested input space. What values did the Developer miss?
3. **Mutation resistance** — For critical code paths, mentally ask: "If I deleted this line, would any test catch it?" Write tests that catch mutations the Developer missed.
4. **Integration boundaries** — Are module seams tested? Developer tests are often unit-scoped; add integration tests that verify cross-task contracts.
5. **Adversarial inputs** — For high-risk components (auth, parsing, APIs), add tests with malformed, oversized, or hostile inputs.
6. **Property-based tests** — For pure/deterministic functions, identify invariants and add property-based tests (Hypothesis, proptest, fast-check).
7. **Test quality** — Verify AAA structure (Arrange-Act-Assert), no logic in tests, no shared mutable state, deterministic (no flaky sleep-based waits).

## What NOT to do

- Do NOT rewrite the Developer's tests. Augment, don't replace.
- Do NOT duplicate existing test coverage. Focus on GAPS.
- Do NOT write tests for trivial code (simple getters, config lookups).

## Output

Write `test-report.toml` with:
- Gap inventory (severity-classified by HRBT risk)
- New tests you added (with rationale per test)
- Coverage assessment (per-task, per-risk-level)
