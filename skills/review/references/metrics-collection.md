# Metrics Collection

Compute phase-level quality and process metrics after review.

## Data Sources

Read:
1. `.dominion/phases/{N}/test-report.toml` → quality metrics
2. `.dominion/phases/{N}/review.toml` → finding counts (from Steps 1-3, already written)
3. `.dominion/phases/{N}/progress.toml` → process metrics
4. `.dominion/phases/{N}/summaries/task-*.md` → token estimates, friction counts
5. `.dominion/phases/{N}/plan.toml` → total acceptance criteria count

## Quality Metrics

- `tests_added`: from test-report.toml `summary.tests_run`
- `tests_passing`: from test-report.toml `summary.tests_passed`
- `linter_warnings`: run the project's linter if configured in style.toml, count warnings. If no linter configured, set to 0
- `coverage_delta`: from test-report.toml `summary.coverage_delta`
- `review_findings_high/medium/low`: count findings by severity from review.toml
- `acceptance_criteria_passed/failed`: from test-report.toml `summary.criteria_passed` and `summary.criteria_failed`

## Process Metrics

- `tasks_completed`: count tasks with status "complete" in progress.toml
- `tasks_failed`: count tasks with status "failed" in progress.toml
- `tasks_replanned`: count tasks with status "replanned" or tasks that appear in multiple waves (wave reassignment)
- `waves_count`: count waves in progress.toml
- `blockers_encountered`: count blocker signal files that were created during this phase (check `.dominion/signals/` for files referencing this phase's tasks, including resolved ones)
- `rollbacks_performed`: count rollback commits in git log for this phase (match "revert: rollback task" messages)
- `average_tokens_per_task`: estimate from summary file sizes (rough proxy — each summary character ≈ 1 token for the work that produced it). If not estimable, set to 0
- `improvement_proposals`: count proposals in review.toml
- `iso_25010_delta`: score each ISO 25010 dimension (functional suitability, performance efficiency, compatibility, usability, reliability, security, maintainability, portability) using the shared rubric from [iso-25010-rubric.md](../../../templates/references/iso-25010-rubric.md). Compare against Researcher's pre-phase baseline from research.toml. Record delta per dimension (positive = improved).
- `sqale_debt_delta`: assess current technical debt by category (design, implementation, test). Compare against Researcher's pre-phase SQALE inventory. Record delta (negative = debt reduced).

## Write Metrics

Write `.dominion/phases/{N}/metrics.toml` using [metrics.toml](../../../templates/schemas/metrics.toml) as the schema.

## Update History

Read `.dominion/metrics-history.toml` (create from [metrics-history.toml](../../../templates/schemas/metrics-history.toml) if not exists).
Append a new `[[phases]]` entry with summarized metrics:
- `number`: phase number
- `tests_added`: from quality metrics
- `blocker_rate`: blockers_encountered / tasks_completed (0 if no tasks)
- `tokens_per_task`: average_tokens_per_task
- `findings_high`: review_findings_high
- `findings_medium`: review_findings_medium
- `acceptance_pass_rate`: criteria_passed / (criteria_passed + criteria_failed) (0 if no criteria)
- `improvement_proposals`: count

## Validate

Run: `python3 -c "import tomllib; tomllib.load(open('.dominion/phases/{N}/metrics.toml','rb'))"` — must parse.
