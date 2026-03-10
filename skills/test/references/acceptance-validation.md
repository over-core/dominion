# Acceptance Validation

Tester-driven verification of plan acceptance criteria.

## HRBT Risk Context

Before running validations, load risk context:
1. Read `.dominion/phases/{N}/research.toml` — find HRBT risk matrix entries
2. Map each task's affected components to risk levels (high/medium/low)
3. Critical-path tasks (plan.toml `critical_path = true`) get stricter validation — all criteria must pass with explicit evidence

## Smoke Testing

Run smoke tests FIRST before detailed validation:
1. Identify core user paths from plan.toml tasks (high-priority, critical-path)
2. Run a quick smoke: build succeeds, main entry point starts, core API responds
3. If smoke fails → halt validation, report blocker via `dominion-tools signal blocker`
4. Only proceed to detailed validation after smoke passes

## Input

Read and internalize:
1. `.dominion/phases/{N}/plan.toml` — tasks with acceptance criteria and verify_commands
2. `.dominion/phases/{N}/progress.toml` — task statuses (only validate complete tasks)
3. `.dominion/phases/{N}/summaries/task-{id}.md` — developer-reported criteria status

## Validation Protocol

For each completed task in plan.toml:

### 1. Run verify_command
If the task has a `verify_command` (not empty string):
- Run the command from the project root
- Record stdout/stderr as evidence
- Pass if exit code 0, fail otherwise

### 2. Check Each Criterion
For each criterion in the task's acceptance criteria:

- **Code existence**: Use Grep/Glob to verify the described code/feature exists
- **Behavior**: Run relevant tests (language-specific: `cargo test`, `pytest`, `npm test`, `go test`)
- **Convention compliance**: Check against `.dominion/style.toml` rules if the criterion mentions style/conventions

Record status as "passed" or "failed" with specific evidence.

### 3. Run Project Test Suite
Run the project's full test suite (detect from project structure):
- Rust: `cargo test`
- Python: `pytest`
- Node.js: `npm test`
- Go: `go test ./...`

Record total tests run, passed, failed.

## Output

For each task, for each criterion:
- `task`: task id
- `criterion`: exact criterion text from plan.toml
- `status`: "passed" or "failed"
- `evidence`: test output, file reference, or command output

Summary counts:
- `total_criteria`, `criteria_passed`, `criteria_failed`
- `tests_run`, `tests_passed`, `tests_failed`
- `coverage_delta`: compare test count before and after phase (use git to check)
