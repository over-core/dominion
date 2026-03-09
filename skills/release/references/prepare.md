# Release Prepare

Generate changelog and PR synopsis from commit history.

## Changelog Generation

**Agent:** Release Manager

1. Read `.dominion/specs/release-spec.toml` — get `[changelog]` config
2. Determine last release point:
   - If git tags exist matching `v*`: use the most recent tag
   - If no tags: use initial commit
3. Get commit log since last release: `git log {last_tag}..HEAD --oneline`
4. Parse commits by format:
   - If `changelog.format = "conventional"`: group by type prefix (feat, fix, refactor, etc.)
   - If `changelog.format = "keep-a-changelog"`: group into Added, Changed, Deprecated, Removed, Fixed, Security
   - If `changelog.format = "custom"`: list chronologically
5. Read `.dominion/dominion.toml [workflow]` — check `ai_co_author`
   - If `false`: strip any Co-Authored-By trailers from commit messages in changelog

### Output

Write to `.dominion/release/changelog-draft.md`:

```markdown
## [{next_version}] - {date}

### Added
- {feat commits}

### Fixed
- {fix commits}

### Changed
- {refactor/chore commits}
```

## Version Suggestion

Based on commit types since last release:
- Any `feat` commits → suggest minor bump
- Only `fix` commits → suggest patch bump
- Any commit with `BREAKING CHANGE` or `!` → suggest major bump

Present: "Suggested version: {current} → {suggested} ({reason})"

## PR Synopsis

**Agent:** Advisor

1. Read the changelog draft
2. Read `.dominion/phases/` — find the most recent completed phase(s) since last release
3. Synthesize a human-readable summary:
   - What was built (high-level, not commit-level)
   - Why it matters (from phase intent.md if available)
   - What to test (from test-report.toml if available)

### Output

Write to `.dominion/release/synopsis-draft.md`:

```markdown
## Summary

{2-4 bullet points of what changed and why}

## Changes

{Grouped by area/feature, not by commit}

## Testing

{What was tested, any known limitations}
```

## Completion

```
Release drafts ready:
  Changelog: .dominion/release/changelog-draft.md ({N} entries)
  Synopsis:  .dominion/release/synopsis-draft.md
  Suggested: {current} → {suggested}
```
