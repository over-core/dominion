# Acceptance Criteria

Define verifiable done conditions for each task.

## Rules

1. **Minimum 2 criteria per task.** Every task must have at least two acceptance criteria.
2. **Observable.** Each criterion must be verifiable by reading code, running a command, or checking output — not by subjective judgment.
3. **Specific.** "Tests pass" is too vague. "All tests in tests/auth/ pass" is specific.
4. **Independent.** Each criterion should be checkable independently of other criteria.

## Categories

- **Functional**: the feature/change works as intended (e.g., "Endpoint returns 200 with valid token")
- **Quality**: code meets standards (e.g., "No new clippy warnings introduced")
- **Integration**: the change works with surrounding code (e.g., "Existing auth tests still pass")

Each task should have at least one functional criterion.

## Verify Command

For each task, define a `verify_command` if the criteria can be checked by running a shell command:
- Test commands: `cargo test --test auth`, `pytest tests/auth/`, `npm test -- --grep auth`
- Lint commands: `cargo clippy`, `ruff check src/auth/`
- Build commands: `cargo build`, `npm run build`

Set to `""` if no automated verification is possible (e.g., documentation-only tasks).

## Assumption References

Link each task to relevant assumptions from research.toml:
- If a task depends on assumption A3 being true, add `ref = "A3"` to `[[tasks.assumptions]]`
- This enables the execute step to verify assumptions before starting work

## Output

For each task, produce:
- `criteria`: list of verifiable done conditions
- `verify_command`: shell command or `""`
- `assumptions`: list of assumption refs
