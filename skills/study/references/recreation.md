# Recreation

Step 3 of the study pipeline. Create Dominion-native artifacts that improve on the originals.

## Agents: Researcher + Reviewer

## Process

For each item that passed the kill gate:

### 1. Critical Analysis

Read the original skill/agent carefully. Identify:
- **Strengths**: What does it do well? What patterns are worth preserving?
- **Weaknesses**: What's poorly structured, overly complex, or fragile?
- **Assumptions**: What does it assume about the project? Do those assumptions hold here?
- **Missed opportunities**: What could it do better with project-specific knowledge?

### 2. Design

Design the Dominion-native version:
- If recreating as a **skill**: follow Dominion skill conventions (directive prose, markdown links for sub-steps, valid YAML frontmatter)
- If recreating as an **agent**: create TOML config following existing agent template patterns, with appropriate model, tools, governance, and file ownership
- If recreating as **knowledge**: structure as `.dominion/knowledge/` files with index entries

The recreation must:
- Integrate with the existing agent model (respect governance, file ownership, hard stops)
- Use project-specific knowledge (conventions from style.toml, direction from dominion.toml)
- Follow Dominion conventions (CLI commands, signal protocol, SUMMARY.md format)

### 3. Write

Write the Dominion-native artifact:
- Skills: write to `.dominion/skills/{name}.md`
- Agents: write TOML to `.dominion/agents/{role}.toml`, Attendant generates `.claude/agents/{role}.md`
- Knowledge: write to `.dominion/knowledge/{topic}.md`, update index.toml

### 4. Verify

The Reviewer checks the recreated artifact:
- Does it follow Dominion conventions?
- Is it actually better than the original? (not just a copy with different formatting)
- Does it integrate properly with existing agents?
- Are there any governance conflicts?

If verification fails: iterate on the design. Do not commit a recreation that's worse than the original.
