# Project Instructions

## Project
Dominion is a Claude Code plugin that analyzes projects and generates complete AI development methodologies — agents, tools, governance, conventions, CLI toolkit — committed to git.

The plugin is the author. The artifacts are the runtime. Dominion is needed to create and evolve the setup; a cloned repo works without it.

## What This Is NOT
This is not a traditional codebase. There is almost no application code. The product is:
- **Skill files** (markdown) — instructions Claude follows during /dominion:* commands
- **TOML data** — detection tables, agent templates, schemas, registry
- **Reference files** (markdown) — reusable sub-step instructions referenced by skills

## Structure
```
skills/           User-facing skills (/dominion:init, /dominion:validate)
  init/references/  Sub-step instructions (discovery, wizard, generation)
templates/        Agent TOML templates, TOML schemas, CLI spec
data/detection/   Language, framework, infrastructure detection tables
registry/         Curated MCP/plugin/LSP evaluations
docs/plans/       Design docs and implementation plans (not committed)
```

## Mandatory Rules
- Never add traditional application code — this is a prompt engineering project
- Every TOML file must parse cleanly. Validate after writing: `python3 -c "import tomllib; tomllib.load(open('file.toml','rb'))"`
- Skill files must have valid YAML frontmatter between `---` delimiters
- Reference files use `@path/to/file` syntax to point to other plugin files
- Detection data is structured TOML, not hardcoded in skill prose
- Do not add commands, agents, or features scoped for versions beyond what's being built
- Design doc (DOMINION.md) is the source of truth for intended behavior

## Writing Skills
Skill prose is directive, not explanatory. Write instructions the LLM follows, not documentation a human reads. Be specific:
- Bad: "Analyze the project structure"
- Good: "Use Glob to find Cargo.toml, pyproject.toml, package.json, go.mod. Read each found file. Record languages, package managers, and dependencies."

Reference files with `@references/filename.md` — the skill system resolves these.

## Writing TOML Templates
Agent TOML templates use `{{placeholder}}` for values filled at init time. Schema templates show the full structure with comments explaining each field. Keep comments terse.

## Git Conventions
- Commit format: conventional commits (feat:, fix:, docs:, refactor:)
- Commit messages: one line, lowercase after prefix, no period
- No Co-Authored-By trailers
- Commit granularity: one logical change per commit

## Quality Gates
- TOML files parse: `python3 -c "import tomllib; tomllib.load(open('file.toml','rb'))"`
- Skill frontmatter is valid YAML
- No broken `@references/` paths in skill files
- /dominion:validate passes after any structural change

## Decision Framework
- **Decide autonomously:** TOML formatting, file organization within established structure, comment wording
- **Flag and continue:** detection data additions (new languages/frameworks), registry rating adjustments
- **STOP and ask:** new skills, new agent roles, changes to init flow order, anything that changes the design doc's intended behavior
