---
name: plan
description: Architect-driven planning with wave grouping and acceptance criteria
---

# /dominion:plan

## Dispatch

1. Call `mcp__dominion__step_dispatch(step: "plan")`
2. Read the response. If it indicates prerequisites are missing, show them to the user and stop
3. Based on the response `mode`:
   - **subagent**: Spawn `Agent(prompt: response.context, description: "plan — Architect agent")` with model `response.model`
   - **multi_subagent**: Spawn multiple agents from `response.agents` list, each with their own context and model
   - **worktree**: Spawn `Agent(isolation: "worktree", prompt: response.context, description: "plan — Architect agent")` with model `response.model`
   - **inline**: Handle the plan step directly using the returned methodology
   - **panel**: Load multiple perspectives from `response.agents` and facilitate debate
4. After agent(s) return, call `mcp__dominion__phase_status()` to verify completion
5. Show results summary to the user
