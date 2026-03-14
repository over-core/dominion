---
name: release
description: Generate changelog, PR synopsis, and release notes. Optionally publish with full git ceremony. Spec-driven, language-agnostic.
---

# /dominion:release

Prepare and optionally publish a release using the project's release spec.

<IMPORTANT>
This skill requires the Release Manager specialized role.
If `.dominion/agents/release-manager.toml` does not exist:
  "Release Manager role is not activated. Activate it first with /dominion:improve --agent, or proceed with Advisor-only mode (simpler synopsis, no structured changelog)? [activate / advisor-only]"
</IMPORTANT>

## Flag Parsing

- `--publish`: After preparing, execute the full publish ceremony (PR, tag, release)
- No flags: prepare only — generate drafts for review

## Pre-check

1. Call `mcp__dominion__get_config(section: "project")` — verify project is initialized
2. Call `mcp__dominion__get_config(section: "release")` — check for release spec
   - If missing or empty: follow [bootstrap.md](references/bootstrap.md) to generate it
   - If present: read and validate spec
3. Call `mcp__dominion__get_roadmap()` — get current milestone context
4. Create `.dominion/release/` directory if it doesn't exist

## Step 1: Prepare Release

Follow [prepare.md](references/prepare.md):
1. Release Manager reads commit history since last tag
2. Release Manager generates changelog draft
3. Advisor writes PR synopsis
4. Save drafts to `.dominion/release/`

## Step 2: Review Drafts

Present drafts to user:
```
Release drafts ready:
  Changelog: .dominion/release/changelog-draft.md
  Synopsis:  .dominion/release/synopsis-draft.md
  Version:   {current} → {suggested next version}

Review and edit? [approve / edit / cancel]
```

- **approve**: proceed (to publish if `--publish`, otherwise done)
- **edit**: user edits, then re-present
- **cancel**: clean up `.dominion/release/`, exit

## Step 3: Publish (only with `--publish`)

Follow [publish.md](references/publish.md):
1. Bump version per release-spec
2. Build artifacts
3. Publish to registries
4. Create PR and/or GitHub release
5. Commit version bump + changelog
6. Clean up `.dominion/release/`

## Completion

```
Release {version} {prepared | published}.
  Changelog: {output path}
  {If published}: PR: {url}, Release: {url}
```
