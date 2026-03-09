# Release Publish

Execute the full release ceremony after drafts are approved.

**Agent:** Secretary

## Pre-publish Checks

1. Verify drafts exist: `.dominion/release/changelog-draft.md` and `.dominion/release/synopsis-draft.md`
2. Read `.dominion/specs/release-spec.toml`
3. Read `.dominion/dominion.toml [workflow]` — get branching, merge_strategy, ai_co_author
4. For each `[[publish.steps]]`: run `auth_check` command
   - If any fail: report which and ask user to authenticate before continuing

## Step 1: Version Bump

1. Read `versioning.bump_command` from release-spec
2. Replace `{{level}}` with user-chosen level (major/minor/patch)
3. Replace `{{version}}` with the calculated next version
4. Run the bump command
5. Verify: run `versioning.read_command`, confirm version matches expected

## Step 2: Update Changelog

1. Read `changelog.output` from release-spec (e.g., `CHANGELOG.md`)
2. If file exists: prepend the new changelog section from draft
3. If file doesn't exist: create it with the draft content
4. Add a header: `# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n`

## Step 3: Build

If `build.command` is non-empty:
1. Run each command in `build.pre_build` sequentially
2. Run `build.command`
3. Run each command in `build.post_build` sequentially
4. Verify `build.artifacts` exist

If `build.command` is empty: skip this step.

## Step 4: Commit

1. Stage: version source file, changelog file
2. Commit message: `chore(release): v{version}`
3. Respect `ai_co_author` setting for trailer

## Step 5: Publish to Registries

For each `[[publish.steps]]` in release-spec:
1. Check `skip_if` condition — if met, skip with message
2. Run `command` with `{{version}}` and `{{image}}` placeholders replaced
3. Report success or failure per step

## Step 6: Create PR (if applicable)

Based on `workflow.branching`:
- **github-flow** or **gitflow**: create PR to main/develop with synopsis as body
  ```
  gh pr create --title "Release v{version}" --body-file .dominion/release/synopsis-draft.md
  ```
- **trunk-based**: skip PR, push directly (after user confirmation)

## Step 7: Tag and GitHub Release

After PR is merged (or directly for trunk-based):
1. Tag: `git tag -a v{version} -m "Release v{version}"`
2. Push tag: `git push origin v{version}`
3. Create GitHub release:
   ```
   gh release create v{version} --title "v{version}" --notes-file .dominion/release/changelog-draft.md {artifacts}
   ```
   Where `{artifacts}` are paths from `build.artifacts`

## Step 8: Cleanup

1. Remove `.dominion/release/` directory
2. Report completion

```
Release v{version} published.
  Changelog: {changelog.output}
  PR: {url} (if created)
  Release: {github release url}
  Registries: {list of successful publishes}
```

## Error Handling

- If any publish step fails: report the error, continue with remaining steps, summarize at end
- If build fails: halt immediately, do not publish. Report error.
- If version bump fails: halt immediately. Report error.
- Never roll back a partially published release — report what succeeded and what failed, let user decide.
