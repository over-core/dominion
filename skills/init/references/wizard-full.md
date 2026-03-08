# Full Setup Wizard

Each section is independent. In customize mode, only selected sections run.
Skipped sections use detected defaults from discovery.

## Section 1: Project Identity

Ask:
1. "What's this project? One sentence." → dominion.toml [project.vision]
2. "Who uses it?" → dominion.toml [project.target_users]
3. "Team size?" → options: solo + AI / small team (2-5) / larger team
4. "Any hard constraints?" → free text → dominion.toml [project.constraints.hard_rules]

## Section 2: Direction

Ask:
1. "What's the project's current state?"
   - **Maintain** — codebase is good, preserve existing patterns
   - **Evolve** — mostly good, improve incrementally (boy scout rule)
   - **Transform** — significant restructuring planned

If transform:
2. "Describe the target state" → dominion.toml [direction.transform.target_state]
3. "Migration strategy?" → strangler-fig / big-bang / incremental
4. "Any legacy zones to protect?" → paths → dominion.toml [direction.transform.legacy_zones]

## Section 3: Code Style (per detected language)

For each Tier 1 language, present detected conventions and ask to confirm or change.
For each Tier 2 language, present detected tooling and ask for any convention preferences.

Example for Rust:
1. "Error handling: thiserror+anyhow / custom / other?" (pre-select if detected)
2. "Async runtime: tokio / async-std / smol / none?" (pre-select if detected)
3. "Unwrap policy: never / test-only / justified?"
4. "Doc comments: all-public / non-trivial / none?"
5. "Tracing: async-io / all-public / none?"
6. "Max function lines?" (default: 50)
7. "Max file lines?" (default: 500)

Example for Python:
1. "Type hints: all-signatures / public-only / none?"
2. "String formatting: f-strings / format / percent?"
3. "CLI framework: click+rich / typer / argparse?"
4. "Docstring style: google / numpy / sphinx?"

## Section 4: Git Workflow

Ask (present detected values as defaults):
1. "Branching strategy?" → trunk-based / github-flow / gitflow / custom (default: detected or github-flow)
2. "Commit format?" → conventional commits / ticket-prefixed / free-form (default: detected or conventional)
3. "Merge strategy?" → squash / rebase / merge commits (default: detected or squash)
4. "Code review?" → all changes / major only / agents review (solo devs) (default: agents review for solo, all changes otherwise)
5. "Release workflow?" → semver / calver / custom / none yet
6. "Any git pet peeves?" → free text → style.toml [taste] or CLAUDE.md

Store answers in dominion.toml:
```toml
[workflow]
branching = "{answer}"
commit_format = "{answer}"
merge_strategy = "{answer}"
review_process = "{answer}"
release_workflow = "{answer}"
```

### Generated Git Artifacts

After wizard completion, generate these artifacts:

#### `.githooks/pre-commit`

Generate a shell script that:
- Runs formatters for each detected language (from style.toml [language.{lang}.formatter])
- Runs linters for each detected language (from style.toml [language.{lang}.linter])
- Runs fast test validation if configured (style.toml [language.{lang}.test_command])
- Validates commit message format if commit_format != "free-form"
- Exits non-zero on any failure

If existing pre-commit tooling was detected (Phase 6e), do NOT generate — warn user and skip.

Make executable: `chmod +x .githooks/pre-commit`
Configure git: `git config core.hooksPath .githooks`

#### `.githooks/commit-msg`

Generate a shell script that validates commit messages:
- If conventional commits: check `^(feat|fix|docs|refactor|chore|test|perf|ci|build|style|revert)(\(.+\))?: .+$`
- If ticket-prefixed: check for ticket pattern at start (ask user for pattern, e.g., `[A-Z]+-[0-9]+`)
- If free-form: skip generation

Make executable: `chmod +x .githooks/commit-msg`

#### `.dominion/templates/pull-request.md`

Generate a PR template:

```markdown
## Summary

<!-- Brief description of changes -->

## Changes

<!-- List of changes -->

## Testing

<!-- How were changes tested? -->

## Checklist

- [ ] Tests pass
- [ ] Code follows project conventions
- [ ] Documentation updated (if applicable)
```

If existing PR template detected (Phase 6f), do NOT generate — preserve existing.
If `.github/` exists, also copy to `.github/pull_request_template.md`.

## Section 5: Tools & MCPs

For each recommended MCP (from registry cross-reference):
- "[name] — [purpose]. Include? [Y/n]"

For missing required MCPs:
- Show install command, ask if they want to install now or skip

For detected custom/unknown MCPs:
- "Found [name]. Keep in agent configs? [Y/n]"

## Section 6: Knowledge Sources

Ask:
1. "Any external knowledge bases?"
   - Notion (needs API token)
   - Confluence (needs URL + credentials)
   - Obsidian (local vault path)
   - URLs (list of documentation URLs)
   - Other (describe)
   - None

Store for v0.6 `/dominion:educate`. In v0.1, just record the answer in dominion.toml.

## Section 7: Taste

Free-form section:
1. "Things you want agents to ALWAYS do?" → style.toml [taste.dos]
2. "Things you want agents to NEVER do?" → style.toml [taste.donts]
3. "Any other preferences?" → captured in CLAUDE.md or style.toml as appropriate

## Section 8: Autonomy

Ask:
1. "Enable auto mode for unattended pipeline runs? [Y/n]" (default: Y)

If yes, generate `[autonomy]` section in dominion.toml with defaults:
```toml
[autonomy]
mode = "interactive"

[autonomy.circuit_breakers]
max_tokens_per_task = 50000
max_retry_attempts = 3
max_cascade_replans = 2
max_failed_tasks_per_wave = 0
session_time_limit_hours = 8

[autonomy.replan_constraints]
can_split_tasks = true
can_reorder_within_wave = true
can_add_dependencies = true
cannot_change_wave_count = true
cannot_modify_completed_tasks = true
cannot_alter_governance_rules = true
```

If no: skip section. Auto mode will not be available until the user adds the section manually.

Optional follow-up (only if user says yes):
2. "Max tokens per task? [50000]" → override default
3. "Session time limit (hours)? [8]" → override default

## Section 9: Roadmap

Ask:
1. "What's the first milestone for this project?" → roadmap.toml
2. "Can you list the rough phases to get there?" → roadmap.toml phases
3. "Any success criteria for the milestone?" → dominion.toml [project.success_criteria]
