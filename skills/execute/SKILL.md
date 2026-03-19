---
name: execute
description: Developer-driven task execution with parallel worktree isolation
---

# /dominion:execute

## Dispatch

1. Call `mcp__dominion__step_dispatch(step: "execute")`
2. Read the response. If it indicates prerequisites are missing, show them to the user and stop
3. Based on the response `mode`:
   - **execute_wave**: For each task in `response.tasks`, spawn `Agent(isolation: "worktree", prompt: task.context, description: "execute {task.task_id} — {task.agent_role}")` with model `task.model`. Run all tasks within the wave in parallel. Wait for all to complete.
   - **worktree**: Spawn single `Agent(isolation: "worktree", prompt: response.context, description: "execute — Developer agent")` with model `response.model`
   - **inline**: Handle the execute step directly using the returned methodology
4. After agent(s) return, call `mcp__dominion__phase_status()` to verify completion
5. If more waves remain, call `mcp__dominion__pipeline_next()` again — it returns the next wave
6. Show results summary to the user
