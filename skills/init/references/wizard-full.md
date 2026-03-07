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

Ask:
1. "Branching strategy?" → trunk-based / github-flow / gitflow / custom
2. "Commit format?" → conventional commits / ticket-prefixed / free-form
3. "Merge strategy?" → squash / rebase / merge commits
4. "Code review?" → all changes / major only / agents review (solo devs)
5. "Release workflow?" → semver / calver / custom / none yet
6. "Any git pet peeves?" → free text → style.toml [taste] or CLAUDE.md

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

## Section 8: Roadmap

Ask:
1. "What's the first milestone for this project?" → roadmap.toml
2. "Can you list the rough phases to get there?" → roadmap.toml phases
3. "Any success criteria for the milestone?" → dominion.toml [project.success_criteria]
