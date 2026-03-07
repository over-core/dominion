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
7. `.dominion/state.toml` — `[[autonomous_decisions]]` for auto mode review

## SBAR Framing

For complex phase outcomes, structure the retrospective using SBAR:
- **Situation**: current phase status (completed, partial, blocked)
- **Background**: what was planned, what context existed at phase start
- **Assessment**: what actually happened — metrics, friction themes, quality delta
- **Recommendation**: key takeaways and recommended next actions

Use SBAR when the phase had significant friction, unexpected outcomes, or multiple competing concerns. For straightforward phases, the standard What Went Well / Friction / Patterns structure is sufficient.

## Progressive Disclosure

Adapt retrospective depth to user experience level (from user-profile.toml):
- **Beginner**: full explanations of metrics, what they mean, why they matter. Walk through each section with context.
- **Intermediate**: standard retrospective with brief context. Highlight significant changes.
- **Advanced**: metrics summary, friction themes only if actionable. Skip explanations.

## CBAM-lite Consumption

When presenting proposals during the improve step:
1. Read Researcher's CBAM cost-benefit analysis from research.toml (if available)
2. For each proposal, cross-reference with CBAM data to estimate ROI
3. Present proposals ordered by impact-to-effort ratio
4. Use CBAM data to support recommendations: "This proposal addresses a high-cost area identified in research"

## Autonomous Decision Review

Check state.toml for `[[autonomous_decisions]]` where `reviewed = false`.

If none exist, skip this section.

If unreviewed decisions exist, present them BEFORE the standard retrospective:

```
{N} autonomous decisions from auto mode:

  {id}. [{type}] {description}
     Task: {task} | Reason: {reason}
     Session: {session_id} | Time: {timestamp}

     [Accept / Roll back]
```

For each decision:
- **Accept**: set `reviewed = true`, `outcome = "accepted"` in state.toml
- **Roll back**: set `reviewed = true`, `outcome = "rolled-back"` — follow [rollback-protocol.md](../../../templates/references/rollback-protocol.md) to revert the relevant commits. Present the rollback result before continuing.

After all decisions are reviewed, proceed to regular decisions review.

### Regular Decisions Review

Run `dominion-cli state decisions --phase {N}` to get decisions recorded during this phase.

If decisions exist, present a summary:
```
{count} decisions recorded during Phase {N}:

{For each decision:}
  D{id} ({task}): {text} [tags: {tags}]
```

These are informational — no accept/reject needed. They provide context for the retrospective analysis below. Flag any decisions that suggest process improvements (e.g., recurring trade-offs, blocked-then-unblocked patterns).

## Role Suggestions

Check the most recent research.toml for `[[role_proposals]]` entries.

If none exist, skip this section.

If proposals exist, present them:

```
New specialized roles detected:

  {role}: {trigger}
  Confidence: {confidence}
  Purpose: {description from roles.toml}

  Activate this agent? [Y/n]
```

For each accepted role:
- Read the agent template from [agents/{role}.toml](../../../templates/agents/{role}.toml)
- Secretary generates the agent config: `.dominion/agents/{role}.toml` + `.claude/agents/{role}.md`
- Run `dominion-cli agents generate` to update AGENTS.md

For rejected roles:
- Note in improvements.toml as a rejected proposal (so it's not suggested again next phase)

## Preference Promotion

Check if any project-specific preferences from `.dominion/style.toml` or `.dominion/dominion.toml` match across this and previous projects (if the user has worked on multiple Dominion projects).

If the user explicitly states "I always want this" for any preference during the retrospective, promote it:

```
Promote "{preference}" to global preferences?
This will apply to all future Dominion projects. [Y/n]
```

If accepted:
- Read or create `~/.claude/.dominion/global-preferences.toml`
- Add the preference under the appropriate section
- Confirm: "Added to global preferences."

<IMPORTANT>
Only write to `~/.claude/.dominion/` when the user explicitly approves a promotion.
Never infer preferences to promote — only act on explicit user statements.
</IMPORTANT>

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
