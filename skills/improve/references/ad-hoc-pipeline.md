# Ad-Hoc Improvement Pipeline

6-step pipeline for ad-hoc requests (no phase context). Handles agent creation, skill creation, knowledge capture, CLI commands, hooks, and config extensions.

## Step 1: Capture Intent (Advisor)

If `--agent` flag: intent is "create a new agent." Skip to Step 2 with agent output type pre-selected.
If `--skill` flag: intent is "create a new skill." Skip to Step 2 with skill output type pre-selected.
If `--from <source>` flag: follow [source-integration.md](source-integration.md) to extract knowledge, then continue from Step 2.

If no flags:
1. Ask: "What do you want to improve or create?"
2. Listen to user's plain language description
3. Read [structural-awareness.md](../../../templates/references/structural-awareness.md) — understand available building blocks
4. Classify the request: is this an agent, skill, knowledge, CLI command, hook, or config change?

## Step 2: Investigate (Researcher)

1. Read [structural-awareness.md](../../../templates/references/structural-awareness.md)
2. Read existing artifacts that might overlap:
   - For agent requests: read all `.dominion/agents/*.toml` — check for role overlap
   - For skill requests: check existing `.dominion/skills/` — check for procedure overlap
   - For knowledge: check `.dominion/knowledge/index.toml` — check for topic overlap
   - For CLI commands: read `.dominion/specs/cli-spec.toml` — check for command overlap
   - For hooks: check for existing hookify rules (`.claude/hookify.*.local.md`) and native hooks in `.claude/settings.json` `"hooks"` config — check for event/pattern overlap
3. Follow [overlap-check.md](overlap-check.md) for overlap detection logic

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
1. Follow [dkcp-protocol.md](dkcp-protocol.md) — the 7-phase domain knowledge capture
2. If output type is **agent**: follow [agent-methodology-design.md](../../../templates/references/agent-methodology-design.md) — design the `[methodology]` section from DKCP output (phases, methods, tool routing, research lens, cross-dependencies, self-critique)
3. If output type is **skill**: follow [skill-quality-guide.md](../../../templates/references/skill-quality-guide.md) Part 1 — apply design guidance (structural patterns, prose style, pre-checks, state management, testing strategy)
4. Structure captured knowledge into the proposed artifact

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
6. **Methodology quality** — for agents: apply self-critique checklist from [agent-methodology-design.md](../../../templates/references/agent-methodology-design.md) Step 7. For skills: apply acceptance criteria from [skill-quality-guide.md](../../../templates/references/skill-quality-guide.md) Part 2.

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

## Step 6: Create Artifacts (Secretary)

For each output type, follow the creation steps from [structural-awareness.md](../../../templates/references/structural-awareness.md):

### Agent
1. Write `.dominion/agents/{role}.toml`
2. Run `dominion-tools agents generate`
3. Update `.claude/settings.json` with required permissions
4. Run `dominion-tools doc generate` to regenerate DOMINION.md

### Skill

Check if the `skill-creator` plugin is installed (look for `/skill-creator` in available skills).

**If skill-creator is installed (preferred):**

Hand off to skill-creator with the architecture context from Steps 1-5:

```
The Dominion improve pipeline has approved a new skill:
- Name: {name}
- Purpose: {purpose}
- Governance: {any hard stops or file ownership from Reviewer}
- Reference files needed: {list from design proposal}
- Wiring: skill will be placed at `.dominion/skills/{name}.md`

Use this context to write the SKILL.md. Follow quality criteria from skill-quality-guide.md:
- Directive prose (instructions the LLM follows, not documentation)
- Specify tools by name, specify outputs with templates, every step produces observable artifact
- Use markdown links for sub-steps: `[filename.md](references/filename.md)`
- Keep SKILL.md under 500 lines; use references/ for detail
- Pre-checks verify required state/plugins/MCPs before any logic
- Flag parsing before context detection before main steps
- Trigger examples: {positive examples from design proposal} should match, {negative examples} should not

After writing, run the eval loop: create test cases (use positive/negative trigger examples from above), spawn with/without-skill runs, grade, iterate with user feedback, then optimize the description for triggering accuracy.
```

After skill-creator completes, the Secretary places the validated files:
1. Move skill files to `.dominion/skills/{name}.md` (and `references/` if created)
2. Run `dominion-tools doc generate` to regenerate DOMINION.md
3. Update `.claude/settings.json` if the skill needs permissions

**If skill-creator is NOT installed:**

STOP. Tell the user:
```
Skill-creator plugin is required for skill creation.
Install: /plugin marketplace install skill-creator
Then re-run /dominion:improve --skill to create the skill with proper quality validation.
```

Do not attempt to write skills manually without skill-creator's eval loop — untested skills with unoptimized descriptions will not trigger correctly.

### Knowledge
1. Write `.dominion/knowledge/{topic}.md`
2. Update `.dominion/knowledge/index.toml`
3. Run `dominion-tools knowledge sync`

### CLI Command
1. Add `[[commands]]` entry to `.dominion/specs/cli-spec.toml`
2. Developer agent implements the command
3. Validate: `dominion-tools {command} --help`

### Hook Rule

Check if the `hookify` plugin is installed (look for `/hookify` in available skills).

**If hookify is installed (preferred):**

Hand off to hookify with the architecture context from Steps 1-5:

```
The Dominion improve pipeline has approved a new hook rule:
- Purpose: {purpose}
- Trigger: {what should fire this rule — tool calls, file edits, session events}
- Action: {warn or block}
- Pattern: {what to match}

Use /hookify:writing-rules to create a properly formatted hookify rule file.
```

After hookify creates the rule, verify it fires correctly by testing the trigger condition.

**If hookify is NOT installed:**

STOP. Tell the user:
```
Hookify plugin is required for hook creation.
Install: /plugin marketplace install hookify
```

Do not attempt to write hooks manually without hookify's authoring documentation.

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
