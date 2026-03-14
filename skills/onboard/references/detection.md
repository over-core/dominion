# Detection

Scan the project to detect languages, frameworks, infrastructure, existing setup, and git workflow.

## Step 1: Root Scan

List the project root directory. Read key files:
- README.md (if exists) — project description
- Any top-level config files (Cargo.toml, pyproject.toml, package.json, go.mod, etc.)

## Step 2: Language Detection

Reference: [languages.toml](../../../data/detection/languages.toml)

For each language entry, check if any `indicators` files exist using Glob.
For detected languages, also check:
- Which `file_extensions` are present and approximate file count
- Which `package_managers` lock files exist
- Which `formatters` config files exist
- Which `linters` config files exist
- Which `test_runners` config files exist
- Which `build_files` exist

Record the primary language (most files or explicit build system).

### Package Manager Detection

Determine the active package manager from lock files:
- `uv.lock` → uv (install: `uv sync`)
- `poetry.lock` → poetry (install: `poetry install`)
- `Pipfile.lock` → pipenv (install: `pipenv install`)
- `requirements.txt` (no lock file) → pip (install: `pip install -r requirements.txt`)
- `package-lock.json` → npm (install: `npm install`)
- `yarn.lock` → yarn (install: `yarn install`)
- `pnpm-lock.yaml` → pnpm (install: `pnpm install`)
- `Cargo.lock` → cargo (install: `cargo build`)
- `go.sum` → go (install: `go mod download`)

Record: `package_manager`, `install_command`, and `venv_path` (`.venv` for Python, `node_modules` for JS, empty for Rust/Go).

## Step 3: Framework Detection

Reference: [frameworks.toml](../../../data/detection/frameworks.toml)

For each framework entry matching detected languages:
- Check `detection.cargo_dep` / `detection.pyproject_dep` / `detection.npm_dep` / `detection.go_dep` in the relevant manifest file
- Check `detection.files` if specified
- Record detected frameworks with their `category` and `conventions`

## Step 4: Infrastructure Detection

Reference: [infrastructure.toml](../../../data/detection/infrastructure.toml)

For each infrastructure entry:
- Check `detection.files` and `detection.directories` using Glob
- Check `detection.file_extensions` if specified
- For pattern-based detection (`detection.patterns`), use Grep on relevant config files
- Record `activates_role` for specialized role recommendations

## Step 5: MCP & Tool Inventory

Detect currently available MCPs by checking which `mcp__*` tools are loaded in the session.
Cross-reference against [registry.toml](../../../registry/registry.toml):
- Categorize each detected MCP (required / recommended / optional)
- Identify missing required MCPs
- Identify recommended MCPs that match the detected stack
- Note any unknown/custom MCPs (preserve, do not recommend removing)

Check for LSP plugins relevant to detected languages (from registry lsps section).

## Step 6: Git Workflow Detection

### 6a: Remote & CI

- Check `.git/config` for remote URL (determines github vs gitlab MCP recommendation)
- Check for `.github/` or `.gitlab-ci.yml` for CI detection

### 6b: Branch Strategy

Run `git branch -r` to list remote branches. Analyze patterns:
- `feature/*`, `fix/*`, `hotfix/*` → GitHub Flow or GitFlow
- Only `main` + short-lived branches → trunk-based
- `develop` + `release/*` branches → GitFlow
- Record detected pattern and example branches

### 6c: Commit Conventions

Run `git log --oneline -20` to read recent commit messages. Analyze:
- Matches `type(scope): message` or `type: message` → conventional commits
- Matches `PROJ-123 message` or `[PROJ-123]` → ticket-prefixed
- No consistent pattern → free-form
- Record detected format and 2-3 example messages

### 6d: Merge Strategy

Run `git log --merges -5 --oneline` and `git log --no-merges -10 --oneline`:
- Many merge commits with `Merge pull request` or `Merge branch` → merge commits
- Few/no merge commits, linear history → squash or rebase
- Record detected strategy

### 6e: Pre-commit Tooling

Check for existing pre-commit infrastructure:
- `.pre-commit-config.yaml` → pre-commit framework
- `.husky/` → husky (JS)
- `lefthook.yml` → lefthook
- `.githooks/` → custom git hooks
- `lint-staged` in package.json → lint-staged
- Record what exists, do not recommend replacing

### 6f: PR Templates

Check for existing PR/MR templates:
- `.github/pull_request_template.md`
- `.github/PULL_REQUEST_TEMPLATE/` directory
- `.gitlab/merge_request_templates/`
- Record existence and rough structure

## Step 7: Existing Claude Code Setup

- Check for `CLAUDE.md` — record existence, rough size, section headings
- Check for `.claude/` directory — agents/, settings.local.json, hooks/
- Check for `AGENTS.md`
- Check for `.mcp.json` — record existing MCP server entries
- If existing setup found: note brownfield mode for interview phase

## Step 8: Style Sampling

For each full-level detected language, read 3-5 representative source files:
- Pick files from different directories (avoid test files for convention detection)
- Note: naming conventions (snake_case, camelCase), indentation, line length
- Note: error handling patterns, import organization, comment style
- Note: architectural patterns (MVC, hexagonal, modules, etc.)

Use this to pre-fill style.toml convention choices for the interview.

## Output Structure

Organize detection results as structured data in the conversation context:

- `detected_languages`: list with tier, tools, conventions
- `detected_frameworks`: list with category, conventions
- `detected_infrastructure`: list with category, activates_role
- `detected_mcps`: list with tier, status (installed/missing)
- `git_workflow`: branching, commit_format, merge_strategy, pre_commit_tooling, pr_templates
- `existing_setup`: what Claude Code artifacts already exist (brownfield indicators)
- `style_observations`: per-language convention observations
- `project_shape`: monorepo/workspace/single-project, primary language
- `recommended_mcps`: from registry cross-reference
- `recommended_roles`: specialized roles to activate (from infrastructure detection)
