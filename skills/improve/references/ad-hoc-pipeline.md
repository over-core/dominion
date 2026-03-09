# Ad-Hoc Improvement Pipeline

6-step pipeline for ad-hoc requests (no phase context). Handles agent creation, skill creation, knowledge capture, CLI commands, hooks, and config extensions.

## Step 1: Capture Intent (Advisor)

If `--agent` flag: intent is "create a new agent." Skip to Step 2 with agent output type pre-selected.
If `--skill` flag: intent is "create a new skill." Skip to Step 2 with skill output type pre-selected.
If `--from <source>` flag: follow `@references/source-integration.md` to extract knowledge, then continue from Step 2.

If no flags:
1. Ask: "What do you want to improve or create?"
2. Listen to user's plain language description
3. Read `@templates/references/structural-awareness.md` — understand available building blocks
4. Classify the request: is this an agent, skill, knowledge, CLI command, hook, or config change?

## Step 2: Investigate (Researcher)

1. Read `@templates/references/structural-awareness.md`
2. Read existing artifacts that might overlap:
   - For agent requests: read all `.dominion/agents/*.toml` — check for role overlap
   - For skill requests: check existing `.dominion/skills/` — check for procedure overlap
   - For knowledge: check `.dominion/knowledge/index.toml` — check for topic overlap
   - For CLI commands: read `.dominion/specs/cli-spec.toml` — check for command overlap
   - For hooks: check `.claude/hooks/` — check for rule overlap
3. Follow `@references/overlap-check.md` for overlap detection logic

If significant overlap found:
```
This overlaps with existing {type}: {name}
  Overlap: {description of overlap}

Options:
  1. Extend existing {name} instead
  2. Create new {type} alongside it
  3. Cancel

[1 / 2 / 3]
```

If `--agent` or `--skill` flag was used but Researcher recommends against it:
```
You requested a new {agent/skill}, but this might work better as {alternative}.
  Reason: {reason}

Proceed with {agent/skill} anyway? [Y / switch to {alternative}]
```

## Step 3: Design Proposal (Advisor)

If interactive interview needed (no `--from` source and creating an agent or skill):
1. Follow `@references/dkcp-protocol.md` — the 7-phase domain knowledge capture
2. Structure captured knowledge into the proposed artifact

If request is straightforward (CLI command, hook, config):
1. Draft the proposed artifact directly from user description

Present the proposal:
```
Proposed {type}: {name}
  Purpose: {description}
  Files to create: {list}
  Wiring needed: {AGENTS.md, settings.json, etc.}

{Show draft content for review}
```

## Step 4: Criticism (Reviewer)

Reviewer evaluates the proposal against:
1. **Scope** — is this too broad? Too narrow? Should it be split or merged?
2. **Overlap** — does this duplicate existing capabilities? (cross-reference Researcher's findings)
3. **Naming** — is the name clear, consistent with existing conventions?
4. **Governance** — does this need file ownership, hard stops, escalation rules?
5. **Completeness** — are all wiring steps accounted for?

Reviewer produces a brief assessment:
```
Review: {APPROVE | SUGGEST CHANGES}
  {If changes}: {list of suggested changes with reasons}
```

## Step 5: Present Final Proposal (Advisor)

Incorporate Reviewer feedback. Present to user:

```
Final proposal {with Reviewer adjustments}:
  {type}: {name}
  Purpose: {purpose}
  {If reviewer suggested changes}: Reviewer suggested: {changes}

  Files:
    Create: {list}
    Modify: {list}

Approve? [Y / modify / cancel]
```

- **Y**: proceed to creation
- **modify**: user adjusts, re-present
- **cancel**: exit

## Step 6: Create Artifacts (Attendant)

For each output type, follow the creation steps from `@templates/references/structural-awareness.md`:

### Agent
1. Write `.dominion/agents/{role}.toml`
2. Run `dominion-tools agents generate`
3. Update `.claude/settings.json` with required permissions
4. Run `dominion-tools doc generate` to regenerate DOMINION.md

### Skill
1. Write `.dominion/skills/{name}.md` with frontmatter
2. Write reference files if needed
3. Run `dominion-tools doc generate` to regenerate DOMINION.md

### Knowledge
1. Write `.dominion/knowledge/{topic}.md`
2. Update `.dominion/knowledge/index.toml`
3. Run `dominion-tools knowledge sync`

### CLI Command
1. Add `[[commands]]` entry to `.dominion/specs/cli-spec.toml`
2. Developer agent implements the command
3. Validate: `dominion-tools {command} --help`

### Hook Rule
1. Write hookify rule to `.claude/hooks/`
2. Test the rule

### Config Section
1. Add section to `.dominion/dominion.toml`
2. Validate TOML parses

After all artifacts created:
- Commit all new files: `git commit -m "improve: add {type} {name}"`
- Record in `.dominion/improvements.toml` as accepted proposal with `applied_by = "ad-hoc"`

```
Created {type}: {name}
  Files: {list of created/modified files}
  Wiring: {what was updated}

Run /dominion:validate to verify integrity.
```
