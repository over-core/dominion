# Overlap Check

Detect overlap between a proposed new artifact and existing Dominion entities.

## Agent Overlap

When proposing a new agent:

1. Read all `.dominion/agents/*.toml`
2. For each existing agent, compare:
   - **Purpose**: does the proposed purpose overlap with an existing agent's `purpose` field?
   - **File ownership**: does the proposed agent want to own files already owned by another agent?
   - **Tool overlap**: does the proposed agent use the same specialized tools/MCPs?
   - **Methodology alignment**: does the proposed agent's `[methodology.methods]` overlap with an existing agent's methods? If >50% of methods are shared, the agents are too similar — recommend extending the existing agent instead. Also check for cross-dependency conflicts with the specialist interaction model (e.g., two agents claiming the same Reviewer query domain).
3. Score overlap: none / partial / significant

### Partial Overlap
The proposed agent shares some capabilities but has a distinct primary purpose.
Recommendation: proceed with creation, but note the overlap in the agent's TOML as a `[coordination]` section.

### Significant Overlap
The proposed agent largely duplicates an existing agent.
Recommendation: extend the existing agent with new skills/capabilities instead.

## Skill Overlap

When proposing a new skill:

1. Read all `.dominion/skills/*.md` (check frontmatter `name` and `description`)
2. Compare the proposed skill's trigger and purpose against existing skills
3. Check if the proposed workflow is a subset of an existing skill's workflow

Recommendation if overlap: add as a flag or sub-step to the existing skill.

## Knowledge Overlap

When proposing new knowledge files:

1. Read `.dominion/knowledge/index.toml`
2. Check if the proposed topic overlaps with existing entries
3. If the topic is a subtopic of existing knowledge: recommend extending the existing file

## CLI Command Overlap

When proposing a new CLI command:

1. Read `.dominion/specs/cli-spec.toml`
2. Check if a similar command already exists (by name or by behavior)
3. If similar: recommend extending the existing command with new args/flags
4. If the proposed command is simple data access (read/write a TOML file): note that `dominion-cli data get/set` already provides generic access — a dedicated command may not be needed

## Output

For any overlap check, return:
```
Overlap assessment:
  Type: {none | partial | significant}
  With: {existing artifact name}
  Details: {what overlaps}
  Recommendation: {proceed | extend existing | merge}
```
