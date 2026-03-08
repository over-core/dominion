# Quick Workflow

Lightweight execution with governance guardrails.

## Governance Check

Before making changes:
1. Read `.dominion/dominion.toml` `[governance.hard_rules]` — these apply to all changes
2. Read `.dominion/style.toml` — follow code conventions
3. Check if the files being modified are in `governance.file_ownership` — if so, warn the user that this is a governance-sensitive area

## Execution

1. Implement the change following CLAUDE.md conventions and style.toml rules
2. Run the project test suite (detect from project structure):
   - Rust: `cargo test`
   - Python: `pytest`
   - Node.js: `npm test`
   - Go: `go test ./...`
3. If tests fail: fix and retry (max 2 retries). If still failing after retries, present the failure to the user.

## Minimal Summary

Write a summary to `.dominion/quick-summaries/quick-{timestamp}.md`:

```markdown
# Quick: {title}

## What Was Done
{description}

## Files Changed
- `path/to/file` — {what changed}

## Tests
{pass/fail with details}
```

Create the `quick-summaries/` directory if it does not exist.

## Commit

Commit using conventional commit format:
```bash
git add {specific files}
git commit -m "{type}({scope}): {description}"
```

## Reviewer Escalation

If any governance-sensitive files were modified (files listed in `governance.file_ownership` with restricted roles):
- Run a lightweight review: check the diff against hard_rules and style.toml
- Flag any violations to the user before committing
