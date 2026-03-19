# Release Management Protocol

## Release Readiness Assessment

Before any release:
1. All planned tasks complete (check progress.toml)
2. Test suite passes (check test-report.toml)
3. No unresolved critical/high blockers
4. Review verdict is "go" or "go-with-warnings" (check review.toml)
5. Read release-spec.toml for project-specific build/publish commands

## Commit Analysis

1. Read `git log` from last release tag to HEAD
2. Parse conventional commits: `feat:` → minor, `fix:` → patch, `!` or `BREAKING CHANGE:` → major
3. Group by type for changelog sections
4. Identify co-authors and contributors

## Version Decision

Apply semantic versioning:
- **Major** — breaking changes to public API, wire format, or stored data format
- **Minor** — new features, new endpoints, new capabilities (backward compatible)
- **Patch** — bug fixes, performance improvements, documentation (no API changes)

When in doubt, ask. Version bumps affect downstream consumers.

## Artifact Preparation

Generate three distinct outputs:
1. **CHANGELOG.md** — human-readable, grouped by type, with links to commits/PRs
2. **Release notes** — concise summary for GitHub/GitLab release, highlights + breaking changes
3. **Version bumps** — update all version declarations (package.json, pyproject.toml, Cargo.toml, etc.)

## Publish Ceremony

1. Read release-spec.toml for build/publish commands (project-specific, not hardcoded)
2. Build artifacts
3. Run publish-specific tests (if defined)
4. Create git tag
5. Push tag
6. Create GitHub/GitLab release with notes
7. Publish to package registry

## Post-Release Verification

1. Verify tag exists on remote
2. Verify release is visible on GitHub/GitLab
3. Verify package is accessible from registry (npm info, pip install --dry-run, cargo search)
4. Verify CHANGELOG.md is accurate
