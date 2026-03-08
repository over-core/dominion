# Summary Writing

Instructions for Developer agents writing task summaries.

## File Location

Write the summary to: `.dominion/phases/{N}/summaries/task-{id}.md`

Create the `summaries/` directory if it does not exist.

## Required Sections

```markdown
# Task {id}: {title}

## What Was Done
{Specific description of changes made. Not "updated the module" but "Added JWT validation middleware in src/auth/middleware.rs that checks token expiry and role claims."}

## Files Changed
- `path/to/file1` — {what changed}
- `path/to/file2` — {what changed}

## Acceptance Criteria
- [x] {criterion 1 — checked if passing}
- [x] {criterion 2 — checked if passing}
- [ ] {criterion 3 — unchecked if failing, with note}

## Friction Encountered
{What was harder than expected, what required workarounds, what assumptions were wrong. This is the most valuable section — be honest and specific. "None" is acceptable but rare.}

## Decisions Made
{Any design decisions or trade-offs made during implementation. Include rationale. Reference relevant standards or patterns.}

## Handoff Notes
{Information downstream tasks need to know. API changes, new types introduced, configuration changes, gotchas. "None" if no downstream tasks depend on this.}
```

## Rules

1. **Be specific, not vague.** "Changed the handler" is useless. "Added error handling for expired tokens in `handle_auth()`, returning 401 with error body" is useful.
2. **Every file changed must be listed.** No exceptions. Include the type of change (added, modified, deleted).
3. **Friction and Decisions are the most valuable sections.** These feed into inter-wave knowledge transfer and review. Invest time here.
4. **Acceptance criteria checkboxes must match the plan.** Use the exact criterion text from plan.toml. Check or uncheck honestly.
5. **Handoff notes are for downstream tasks, not humans.** Write them so another Developer agent can act on them without asking questions.
