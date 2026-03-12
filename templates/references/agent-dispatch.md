# Agent Dispatch Protocol

How the orchestrator dispatches pipeline steps to their assigned agents.

## Dispatch Modes

### Inline Dispatch

Used when the step requires user interaction (discuss, improve).

1. Read `.claude/agents/{role}.md` for the assigned agent
2. Adopt the agent's startup sequence:
   - Load required MCPs via ToolSearch
   - Read current state: `dominion-cli state position --json`
   - Load prior context from EchoVault (if available): call `memory_context`
   - Search task-relevant memory (if available): call `memory_search` with phase topic
3. Follow the agent's methodology phases as described in the .md file
4. On completion, run the agent's memory protocol (save discoveries to EchoVault)
5. Return control to the orchestrator with the step's output artifact

The orchestrator IS the agent for inline steps. It reads the agent instructions and follows them directly.

### Subagent Dispatch

Used for analytical steps that produce artifacts without user interaction (explore, plan, test, review).

1. Read `.claude/agents/{role}.md` to get behavioral instructions
2. Spawn the agent via the Agent tool:
   ```
   Agent(
     prompt: "<behavioral instructions from .md>\n\n<phase context>\n\n<specific task details>",
     description: "{step} — {role} agent"
   )
   ```
3. Include in the prompt:
   - The full content of `.claude/agents/{role}.md` (behavioral instructions)
   - Phase number, active specialist list, direction mode
   - Input artifacts (e.g., intent.md for explore, research.toml for plan)
   - Output expectations (what artifact to produce and where)
4. Collect the output artifact when the agent completes
5. Verify the artifact exists and is well-formed

Do NOT substitute Claude Code built-in subagent types (Explore, Plan) for Dominion agents. Dominion agents carry project-specific methodology, tool routing, and governance that built-in types lack.

### Worktree Dispatch

Used for execute-step tasks that modify code in parallel.

1. Read `.claude/agents/{role}.md` for the assigned agent (Developer or specialist)
2. Spawn via Agent tool with worktree isolation:
   ```
   Agent(
     isolation: "worktree",
     prompt: "<behavioral instructions from .md>\n\n<task details from plan.toml>",
     description: "execute task {id} — {role}"
   )
   ```
3. Include in the prompt:
   - The full content of `.claude/agents/{role}.md`
   - Task details: id, title, description, file_ownership, acceptance criteria, verify_command
   - Upstream handoff notes from completed tasks
   - Knowledge refs from plan.toml
4. SDK manages worktree lifecycle (creation in `.claude/worktrees/`, permissions, cleanup)
5. On completion: SDK returns branch name — orchestrator merges
6. Worktree auto-cleaned if agent made no changes

## Fallback Rules

- If a subagent dispatch fails (spawn error, timeout): retry once, then fall back to inline dispatch
- If worktree dispatch fails 2+ times: switch to serial inline execution (see execute skill)
- If the agent .md file is missing: HALT — agent generation is incomplete, run `/dominion:validate`
