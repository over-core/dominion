---
name: execute
description: Developer-driven task execution with worktree isolation
---

# /dominion:execute

## Dispatch

1. Call `mcp__dominion__step_dispatch(step: "execute")`
2. Read the response. If it indicates prerequisites are missing, show them to the user and stop
3. Based on the response `mode`:
   - **subagent**: Spawn `Agent(prompt: response.context, description: "execute — Developer agent")` with model `response.model`
   - **multi_subagent**: For each agent in `response.agents`, spawn `Agent(isolation: "worktree", prompt: agent.context, description: "execute task {agent.task_id} — {agent.role}")` with model `agent.model`. Run agents within the same wave in parallel. Wait for all to complete before proceeding to the next wave.
   - **worktree**: Spawn `Agent(isolation: "worktree", prompt: response.context, description: "execute — Developer agent")` with model `response.model`
   - **inline**: Handle the execute step directly using the returned methodology
   - **panel**: Load multiple perspectives from `response.agents` and facilitate debate
4. After agent(s) return, call `mcp__dominion__phase_status()` to verify completion
5. If `response.next_wave` is present, repeat from step 1 (next wave dispatch)
6. Show results summary to the user
