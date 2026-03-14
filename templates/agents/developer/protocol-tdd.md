# TDD Protocol

For each task assigned in plan.toml:

1. **Read acceptance criteria** from the task's `acceptance_criteria` field and `verify_command`.
2. **Write failing tests** that capture each criterion as an executable assertion.
   - One test function per criterion. Use descriptive names: `test_<criterion_behavior>`.
   - Tests MUST fail for the RIGHT reason (missing implementation, not import errors).
3. **Run tests** — verify they fail. If they pass, the criterion was already met or the test is wrong.
4. **Implement minimum code** to make each failing test pass. No speculative features.
   - Follow existing codebase patterns from style.toml conventions.
   - Stay within `file_ownership` boundaries.
5. **Run tests again** — verify they pass. If they don't, iterate implementation.
6. **Refactor** while keeping tests green.
   - Apply refactoring only if code smells are present (Fowler catalog).
   - Run tests after each refactoring step.
7. **Run full test suite** for regressions before marking task complete.
8. **One atomic commit** per Red-Green-Refactor cycle.

Do NOT write tests-after. If a criterion can't be tested first, flag it via `agent_signal(signal_type: "need-help")`.
