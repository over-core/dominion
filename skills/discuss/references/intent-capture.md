# Intent Capture

Advisor-driven conversation to establish phase goals and boundaries.

## Context Loading

Before asking questions, read and internalize:
1. `.dominion/dominion.toml` `[project]` section — project name, vision, mode, team size
2. `.dominion/roadmap.toml` — current phase description, milestone context
3. Previous phase's `review.toml` `[[findings]]` with severity "high" (if exists)
4. `.dominion/backlog.toml` items with priority "high" (if exists)

## Socratic Questioning

When user goals are vague or ambiguous, use Socratic questioning to draw out specifics:
- "What would success look like for this phase?"
- "If you had to cut one feature, which goes first?"
- "What's the worst outcome you want to avoid?"
- "Who will use this, and what will they do with it?"

Never accept ambiguous intent like "just make it better" or "fix everything." Drill down to concrete, testable goals.

## Decision Support

When the user faces scope trade-offs during intent capture:
1. Present options with trade-offs using evidence from research (CBAM-lite analysis if available)
2. Articulate consequences of each option
3. Recommend based on effort-vs-value ratio
4. Present a clear default: "Here's what I'd recommend and why"
5. Never decide for the user — present options, let them choose

## Active Listening

After each substantive user response, confirm understanding before moving on:
- "So you want X but not Y — correct?"
- "Let me make sure I understand: the priority is A, then B, and C is out of scope?"
- Never assume implicit agreement — explicit confirmation required

## Required Questions

Ask these in order, presenting relevant context with each:

1. **Goal**: "What should this phase accomplish? The roadmap says: '{phase description from roadmap}'. Is that still accurate, or has the goal shifted?"

2. **Scope boundary**: "What is explicitly OUT of scope for this phase? Name specific features, files, or areas that should not be touched."

3. **Constraints**: "Any constraints I should know? Timeline pressure, compatibility requirements, performance targets, external dependencies?"

4. **Priority order**: "If we can't finish everything, what gets cut first? Rank the sub-goals."

## Conditional Questions

Ask these only when relevant context exists:

- **If backlog has high-priority items**: "These backlog items are marked high priority: {list}. Include any in this phase?"
- **If previous review had high findings**: "Last review flagged these issues: {list}. Address any of them this phase?"
- **If project has multiple components**: "Which components are in play this phase? {list from dominion.toml}"

## Output

After the conversation, summarize the captured intent and confirm with the user:

```
Phase {N} Intent:
  Goal: {goal}
  Success criteria: {list}
  Scope boundary: {exclusions}
  Constraints: {list}
  Priority order: {ranked list}
  Backlog inclusions: {list or "none"}
  Components: {list or "all"}
```

Ask: "Does this capture your intent? [Y / edit]"

Store the confirmed intent in `.dominion/phases/{N}/intent.md` as markdown for downstream skills to reference.
