# Detection

Scan the project to detect languages, frameworks, infrastructure, existing setup, and git workflow.

## Step 1: Root Scan

List the project root directory. Read key files:
- README.md (if exists) — project description
- Any top-level config files (Cargo.toml, pyproject.toml, package.json, go.mod, etc.)

## Step 2: Language Detection

Reference: [languages.toml](../data/languages.toml)

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

### Dev Profile Matching

For each detected package manager, find the matching `[[package_manager_profiles]]` entry in [languages.toml](../data/languages.toml):

1. Match by `lock_file` field against detected lock files from Step 2
2. Extract the full profile: `name`, `install`, `add`, `run`, `prohibited`, `venv_required`, `venv_path`, `hook_prefix`
3. If no profile matches, construct a minimal profile from the detected package manager name and install command

Record `dev_profiles` — one per detected package manager — containing:
- `name` — package manager name (e.g., "uv", "pnpm", "cargo")
- `language` — associated language
- `install` — canonical install command
- `add` — add dependency command
- `run` — run command prefix
- `prohibited` — list of prohibited commands (auto-derived safety rules)
- `venv_required` — whether a virtual environment is required
- `venv_path` — expected venv location
- `hook_prefix` — command prefix for hook scripts

These profiles drive auto-generated safety rules in the interview (Phase 2: Present & Confirm) and generation (CLAUDE.md, settings.local.json, agent hard_stops) — no user input needed.

## Step 3: Framework Detection

Reference: [frameworks.toml](../data/frameworks.toml)

For each framework entry matching detected languages:
- Check `detection.cargo_dep` / `detection.pyproject_dep` / `detection.npm_dep` / `detection.go_dep` in the relevant manifest file
- Check `detection.files` if specified
- Record detected frameworks with their `category` and `conventions`

## Step 4: MCP Detection (v0.3.0)

Read the project's `.mcp.json` file (if exists). Match known server names against configured entries:
- `serena` → code navigation
- `exa` → web search
- `context7` → library docs
- `echovault` → cross-session memory
- `sequential-thinking` → reasoning chains

Store in config.toml `[tools].available`. Tool directives and hooks are ONLY generated for detected MCPs.

## Step 5: Git Platform Detection (v0.3.0)

Read `git remote -v` and detect platform from remote URL:
- `github.com` → `git_platform = "github"` (uses `gh` CLI)
- `gitlab.com` or self-hosted GitLab → `git_platform = "gitlab"` (uses `glab` CLI)
- `bitbucket.org` → `git_platform = "bitbucket"`
- Other → `git_platform = "other"`

Store in config.toml `[project].git_platform`. Used by ship skill for PR creation.

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
- `dev_profiles`: list of matched package manager profiles (install, add, run, prohibited, venv, hook_prefix)
- `git_workflow`: branching, commit_format, merge_strategy, pre_commit_tooling, pr_templates
- `existing_setup`: what Claude Code artifacts already exist (brownfield indicators)
- `style_observations`: per-language convention observations
- `project_shape`: monorepo/workspace/single-project, primary language
- `recommended_mcps`: from registry cross-reference
- `recommended_roles`: specialized roles to activate (from infrastructure detection)
