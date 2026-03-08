# Output Routing

Determine the best output format for captured domain knowledge.

## Decision Logic

After knowledge is captured and structured, the Advisor evaluates scope:

### Knowledge Files (default)
Use when the captured knowledge is:
- Domain facts, terminology, glossaries
- Business rules and constraints
- Regulatory requirements
- Stakeholder maps
- Reference information agents need occasionally

Output: `.dominion/knowledge/{topic}.md` files + index.toml entries

### Skill
Use when the captured knowledge describes:
- A repeatable procedure or workflow
- A decision tree that agents should follow
- A domain-specific process (e.g., "how to handle PCI-DSS audit prep")
- Something that should fire as a `/dominion:*` command

Output: `.dominion/skills/{name}.md` with frontmatter

### Agent
Use when the captured knowledge requires:
- Ongoing specialized behavior (not a one-time procedure)
- Specific tool access or governance rules
- File ownership over domain-specific files
- A role that should appear in the agent roster

Output: `.dominion/agents/{role}.toml` + `.claude/agents/{role}.md`

## Presenting the Recommendation

```
Based on the captured scope, I recommend:
  Format: {knowledge files | skill | agent}
  Reason: {why this format fits}

  {If knowledge}: {N} files covering {topics}
  {If skill}: Skill name: {name}, triggers on: {description}
  {If agent}: Agent role: {role}, purpose: {purpose}

Proceed with this format? [Y / change to skill / change to agent / change to knowledge]
```

If the user overrides, use their chosen format. The `--agent` and `--skill` flags skip this routing entirely.
