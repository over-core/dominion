# Phase Retrospective

Advisor-driven structured reflection on the completed phase.

## Inputs

Read:
1. `.dominion/phases/{N}/metrics.toml` — quality and process numbers
2. `.dominion/metrics-history.toml` — trends vs previous phases
3. All SUMMARY.md files: `.dominion/phases/{N}/summaries/task-*.md`
4. `.dominion/phases/{N}/test-report.toml` — test results and gaps
5. `.dominion/phases/{N}/review.toml` — findings
6. `.dominion/phases/{N}/progress.toml` — wave/task execution data

## Present Retrospective

Structure the reflection in three sections:

### What Went Well
- Tasks that completed smoothly (no friction, no blockers)
- Quality improvements over previous phase (from metrics trends)
- Effective patterns that emerged

### What Caused Friction
- Aggregate friction from all summaries — group by theme, not by task
- Blockers encountered and how they were resolved
- Tasks that failed or required replanning
- Quantify where possible ("3 of 9 tasks reported the same lookup issue")

### Patterns & Observations
- Recurring decisions across tasks (from summary Decisions Made sections)
- Convention drift (new patterns emerging that aren't in style.toml yet)
- Tool effectiveness (which MCPs/tools were useful, which were missing)
- Cross-phase trends (improving? degrading? stable?)

## User Input

After presenting, ask:
"Any additional observations or things you noticed during this phase? [free text / skip]"

Record user observations — they feed into proposal context in Step 2.

## Output

The retrospective is conversational — no artifact is written. Its purpose is to:
1. Orient the user on what happened
2. Surface themes that inform proposal review in Step 2
3. Capture any user observations the Reviewer may have missed
