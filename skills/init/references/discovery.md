# Project Discovery Protocol

Instructions for analyzing a target project during `/dominion:init`.

## Phase 1: Root Scan

List the project root directory. Read key files:
- README.md (if exists) — project description
- Any top-level config files (Cargo.toml, pyproject.toml, package.json, go.mod, etc.)

## Phase 2: Language Detection

Reference: `@data/detection/languages.toml`

For each language entry, check if any `indicators` files exist using Glob.
For detected languages, also check:
- Which `file_extensions` are present and approximate file count
- Which `package_managers` lock files exist
- Which `formatters` config files exist
- Which `linters` config files exist
- Which `test_runners` config files exist
- Which `build_files` exist

Record the primary language (most files or explicit build system).

## Phase 3: Framework Detection

Reference: `@data/detection/frameworks.toml`

For each framework entry matching detected languages:
- Check `detection.cargo_dep` / `detection.pyproject_dep` / `detection.npm_dep` / `detection.go_dep` in the relevant manifest file
- Check `detection.files` if specified
- Record detected frameworks with their `category` and `conventions`

## Phase 4: Infrastructure Detection

Reference: `@data/detection/infrastructure.toml`

For each infrastructure entry:
- Check `detection.files` and `detection.directories` using Glob
- Check `detection.file_extensions` if specified
- For pattern-based detection (`detection.patterns`), use Grep on relevant config files
- Record `activates_role` for specialized role recommendations

## Phase 5: MCP & Tool Inventory

Detect currently available MCPs by checking which `mcp__*` tools are loaded in the session.
Cross-reference against `@registry/registry.toml`:
- Categorize each detected MCP (required / recommended / optional)
- Identify missing required MCPs
- Identify recommended MCPs that match the detected stack
- Note any unknown/custom MCPs (preserve, don't recommend removing)

Check for LSP plugins relevant to detected languages (from registry lsps section).

## Phase 6: Git Workflow Detection

- Check `.git/config` for remote URL (determines github vs gitlab MCP recommendation)
- Check recent commit messages for patterns (conventional commits, ticket prefixes, etc.)
- Check for existing branch naming patterns
- Check for `.github/` or `.gitlab-ci.yml` for CI detection
- Check for existing `.githooks/` or pre-commit config

## Phase 7: Existing Claude Code Setup

- Check for `CLAUDE.md` — record existence, rough size, section headings
- Check for `.claude/` directory — agents/, settings.json, hooks/
- Check for `AGENTS.md`
- If existing setup found: warn user that v0.1 creates fresh (merge is v0.7 `dominion claim`)

## Phase 8: Style Sampling

For each Tier 1 detected language, read 3-5 representative source files:
- Pick files from different directories (avoid test files for convention detection)
- Note: naming conventions (snake_case, camelCase), indentation, line length
- Note: error handling patterns, import organization, comment style
- Note: architectural patterns (MVC, hexagonal, modules, etc.)

Use this to pre-fill style.toml convention choices for the wizard.

## Output Structure

Organize discovery results as structured data in the conversation context:

- `detected_languages`: list with tier, tools, conventions
- `detected_frameworks`: list with category, conventions
- `detected_infrastructure`: list with category, activates_role
- `detected_mcps`: list with tier, status (installed/missing)
- `git_workflow`: branch patterns, commit style, CI
- `existing_setup`: what Claude Code artifacts already exist
- `style_observations`: per-language convention observations
- `project_shape`: monorepo/workspace/single-project, primary language
- `recommended_mcps`: from registry cross-reference
- `recommended_roles`: specialized roles to activate (from infrastructure detection)
