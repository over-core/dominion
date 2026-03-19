# Innovation Engineering Protocol

## Problem Formulation

Before generating solutions, formulate the problem precisely:

1. **Identify the contradiction** — what two desirable properties conflict? ("We need X but that prevents Y")
2. **Write a formal contradiction statement**: "The system must [desired function] AND [conflicting constraint] simultaneously"
3. **Check EchoVault** for prior contradiction resolutions — same pattern may have been solved before

## Solution Space Exploration

Apply methods in this order (stop when you have viable candidates):

### TRIZ Contradiction Analysis
1. Map the contradiction to TRIZ parameters (productivity, reliability, complexity, etc.)
2. Look up the contradiction matrix for inventive principles
3. Generate software interpretations of each suggested principle
4. Check TRIZ Trends of Technical Evolution — is the system following known evolution patterns?

### SIT Operators (if TRIZ insufficient)
Apply Systematic Inventive Thinking operators to the existing system:
- **Subtraction** — remove a component and redistribute its function
- **Multiplication** — duplicate a component with modification
- **Division** — restructure by dividing a component
- **Task Unification** — assign a new task to an existing component
- **Attribute Dependency** — create dependency between previously independent attributes

### Morphological Analysis (complex multi-parameter problems)
1. Identify independent dimensions of the solution space
2. Build a Zwicky Box with options per dimension
3. Systematically evaluate combinations
4. Use sequential-thinking MCP for structured multi-parameter evaluation

### C-K Theory (when knowledge is insufficient)
1. Separate concepts (undecided propositions) from knowledge (established facts)
2. Expand concepts through partitioning
3. Identify knowledge gaps that block concept evaluation
4. Research to fill gaps, then re-evaluate

## Solution Evaluation

For each candidate solution:
1. **Axiomatic Design check** — does the solution maintain functional independence? (Independence Axiom)
2. **Axiomatic Design check** — does the solution minimize information content? (Information Axiom)
3. **Value Engineering** — does the solution improve the value ratio (function/cost)?
4. **TOC Evaporating Cloud** — does the solution resolve the underlying conflict or just mask it?

## Output

Produce a Contradiction Resolution Report (CRR):
- Contradiction statement
- Methods applied and why
- Candidate solutions with evaluation scores
- Recommended solution with rationale
- Implementation risks and mitigation
