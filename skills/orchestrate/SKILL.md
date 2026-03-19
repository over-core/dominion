---
name: orchestrate
description: Drive the full phase pipeline with user control points
---

# /dominion:orchestrate

## Pipeline Loop

1. Call `mcp__dominion__pipeline_next()`
2. Follow the returned instruction:
   - **spawn_agent**: Spawn `Agent(prompt: response.context, description: "{response.step} — {response.agent_role}")` with model `response.model`. If `response.isolation` is `"worktree"`, use `Agent(isolation: "worktree", ...)`.
   - **execute_wave**: For each task in `response.tasks`, spawn `Agent(isolation: "worktree", prompt: task.context, description: "execute {task.task_id} — {task.agent_role}")` with model `task.model`. Run ALL tasks in parallel. Wait for all to complete.
   - **multi_subagent**: For each agent in `response.agents`, spawn in parallel. Wait for all to complete.
   - **panel**: Load perspectives from `response.agents`, facilitate multi-perspective debate
   - **user_checkpoint**: Present `response.message` to the user and wait for their input
   - **complete**: Show `response.summary` and stop
   - **inline**: Handle the step directly using the returned methodology
   - **error**: Show `response.message` and stop
3. Repeat from step 1 until `complete` or `error`
