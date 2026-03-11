# Skill Quality Guide

Use this guide when designing a new skill. Part 1 guides the Advisor during Step 3 (design proposal). Part 2 provides the Reviewer with acceptance criteria for Step 4 (criticism).

---

## Part 1: Design Guidance

### 1.1 Structural Patterns

**YAML Frontmatter** — every SKILL.md starts with:

```yaml
---
name: kebab-case-name
description: One sentence optimized for trigger accuracy
---
```

- `name`: kebab-case, matches the `/dominion:{name}` command. Must be unique across all existing skills.
- `description`: one sentence that the LLM matches against when deciding whether to invoke this skill. Optimize for trigger accuracy — too broad catches false positives, too narrow misses legitimate invocations.

**Body structure:**

```markdown
# /dominion:{name}

One-line summary of what this skill does.

<IMPORTANT>
Pre-checks and warnings (if any).
</IMPORTANT>

## Flag Parsing
(if skill accepts flags — parse BEFORE any logic)

## Pre-check
(verify required state exists)

## Step 1: {Action}
Follow [reference.md](references/reference.md)
— or inline instructions if short —

## Step 2: {Action}
...

## Completion
{Final output format}
```

**Line budget:** SKILL.md under 500 lines. If exceeding, delegate detail to reference files via markdown links: `[filename.md](references/filename.md)`.

**Reference file organization:**
- Skill-local references go in `skills/{name}/references/` — for procedures specific to this skill
- Shared references go in `templates/references/` — for procedures reused across multiple skills
- Never duplicate shared content into skill-local references

### 1.2 Prose Style

Write instructions the LLM follows, not documentation a human reads.

**Directive, not explanatory:**

| Bad | Good |
|-----|------|
| "Analyze the project structure to understand the architecture" | "Use Glob to find Cargo.toml, pyproject.toml, package.json, go.mod. Read each found file. Record languages, package managers, and dependencies." |
| "Consider the implications of the changes" | "Read review.toml findings. For each Critical finding: check if the proposed change resolves it. Record unresolved findings." |
| "The system should validate inputs" | "Run `dominion-cli validate`. If errors: list them and STOP." |

**Rules:**
- Specify tools by name: "Read file X" not "check file X." "Run `dominion-cli state update`" not "update the state."
- Specify outputs with templates: show the exact output format in a code block, not "present a summary."
- Every step produces an observable artifact: file written, state updated, output shown to user. No steps that "think about" something without producing output.
- Use imperative mood: "Read", "Write", "Run", "Present" — not "You should read" or "It would be good to."

### 1.3 Pre-checks and Error Handling

Every skill starts with pre-checks before any main logic:

**Required state:**
```markdown
1. Read `.dominion/dominion.toml` — verify project is initialized
2. Check for `.dominion/{required_file}.toml`
   - If missing: STOP. "{file} not found. Run /dominion:{prerequisite} first."
```

**Required plugins:**
```markdown
Check if `{plugin}` is installed (look for `/{plugin}` in available skills).
If not installed: STOP. "{plugin} plugin is required. Install: /plugin marketplace install {plugin}"
```

**Required MCPs:**
```markdown
Check if `{mcp}` is available.
If not available: STOP. "{mcp} MCP is required for this skill."
```

**Principle:** halt early with a clear message. Never proceed with degraded functionality — partial execution creates confusing state.

### 1.4 State Management

Skills that participate in the pipeline must manage state:

**On start:**
```markdown
Run `dominion-cli state update --step {step} --status in_progress`
```

**On completion:**
```markdown
Run `dominion-cli state update --step {step} --status complete`
Run `dominion-cli state checkpoint`
```

**Resume detection** (for interruptible skills):
```markdown
Read `.dominion/state.toml` — if `position.step = "{step}"` and `status = "in_progress"`:
  "Previous {step} was interrupted. Resume from where it stopped? [resume / restart]"
```

Standalone skills (not part of the pipeline) skip state management.

### 1.5 User-Facing Output

**Structured output** — use code blocks for proposals, summaries, status:

```markdown
Present to user:
```
Phase {N} complete.
  Tasks: {completed}/{total}
  Blockers: {count}
  Next: /dominion:{next_step}
```
```

**Action prompts** — always end with clear options:
```
[Y / modify / cancel]
[approve / edit / cancel]
[1 / 2 / 3]
```

**Progressive disclosure** — summary first, details on request. Match the user's experience level if `user-profile.toml` is available:
- Beginner: explain what happened and why
- Intermediate: brief rationale for non-obvious outcomes
- Advanced: terse output, details only on request

**"What's next" guidance** — every skill ends with what the user should do next:
```
Next: /dominion:validate to verify integrity.
```

### 1.6 Token Budget Awareness

- Delegate to reference files to keep SKILL.md lean — the LLM loads referenced files on demand, not all upfront
- Avoid embedding large TOML templates inline — reference schema files instead: `[schema.toml](../../templates/schemas/schema.toml)`
- If the skill orchestrates multiple agents, note which agents are spawned and the approximate context cost
- Prefer reading specific fields from TOML files over loading entire files when only a few values are needed

### 1.7 Testing Strategy

The skill-creator plugin handles eval loops, but the design proposal should provide test material:

**Provide 3-5 positive trigger examples** — invocations that SHOULD trigger this skill:
```
- "/dominion:{name}"
- "/dominion:{name} --flag"
- "I want to {action that maps to this skill}"
```

**Provide 3-5 negative trigger examples** — invocations that should NOT trigger this skill:
```
- "/dominion:{similar_skill}" (distinguish from adjacent skills)
- "I want to {action that maps to a different skill}"
- "{ambiguous request that could be this or another skill}"
```

These become test cases for skill-creator's eval loop: draft skill, spawn with/without-skill runs, grade trigger accuracy, iterate.

**Description optimization:** the `description` field is the primary trigger. After eval, the description may need revision to improve accuracy. Common fixes:
- Too broad → add qualifying words that narrow scope
- Too narrow → remove overly specific terms that block legitimate triggers
- Ambiguous → add "not X" clarifications

---

## Part 2: Acceptance Criteria

The Reviewer applies these checklists during Step 4 (criticism).

### Structural Checklist

- [ ] YAML frontmatter present with `name` and `description` fields
- [ ] `name` is kebab-case and unique across existing skills (check `.dominion/skills/*.md`)
- [ ] `description` is one sentence, specific to this skill's purpose
- [ ] Title matches `/dominion:{name}` format
- [ ] Steps are numbered and sequential
- [ ] Each step has a clear output (artifact produced, state updated, or user output)
- [ ] SKILL.md under 500 lines
- [ ] All markdown link references point to existing files (no broken `[ref](references/ref.md)` paths)
- [ ] Reference files in `references/` directory are used for detail (not everything inline)

### Prose Quality Checklist

- [ ] Prose is directive — instructions the LLM follows, not documentation
- [ ] Tool usage is specific — named tools ("Read", "Run `dominion-cli`"), not vague ("analyze", "check")
- [ ] Output formats are templated — exact format shown in code blocks
- [ ] No steps without observable output — every step produces something
- [ ] Imperative mood used throughout — "Read", "Write", "Present"

### Robustness Checklist

- [ ] Pre-checks verify required state before proceeding
- [ ] Pre-checks verify required plugins/MCPs before proceeding
- [ ] Error paths STOP with clear messages — no degraded fallback
- [ ] State management via `dominion-cli` CLI — not direct TOML edits
- [ ] Flag parsing happens before any logic (if flags exist)
- [ ] Resume detection for interruptible skills (if applicable)

### Trigger Quality Checklist

- [ ] `description` distinguishes this skill from ALL existing skills
- [ ] 3-5 positive trigger examples provided
- [ ] 3-5 negative trigger examples provided
- [ ] No overlap with existing skill triggers (cross-reference existing descriptions)
- [ ] Description optimized for the skill-creator eval loop
