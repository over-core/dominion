---
name: discuss
description: Capture user intent — goals, scope, constraints, priorities
---

# /dominion:discuss

## Intent Capture

1. Ask the user to describe what they want to accomplish
2. Assess complexity from the intent description:
   - Use `mcp__dominion__pipeline_next(complexity_level: "<assessed_level>")` to record the assessment
   - **trivial**: single-file fix, typo, rename → pipeline skips directly to execute
   - **moderate**: feature addition, refactoring → standard pipeline
   - **complex**: multi-component work, redesign → full pipeline with structured requirements
   - **major**: architecture-level change → full pipeline with panel debate

## Dispatch

1. Call `mcp__dominion__step_dispatch(step: "discuss")`
2. Read the response. If it indicates prerequisites are missing, show them to the user and stop
3. Based on the response `mode`:
   - **inline**: Handle the discuss step directly — capture intent conversationally
   - **panel**: Call `mcp__dominion__agent_start(role: "architect", mode: "panel", panel_topic: "<user intent>")`. Present panel participants and facilitate multi-perspective debate. Capture the panel recommendation as the discuss output.
   - **subagent**: Spawn `Agent(prompt: response.context, description: "discuss — agent")` with model `response.model`
   - **multi_subagent**: Spawn multiple agents from `response.agents` list
   - **worktree**: Spawn `Agent(isolation: "worktree", prompt: response.context, description: "discuss — agent")` with model `response.model`

## Adaptive Requirements (complexity = complex | major)

When complexity is **complex** or **major**, use the structured requirements framework:

1. Follow adaptive-requirements.md
2. Walk the user through Jobs-to-be-Done, user stories, acceptance criteria
3. Capture success metrics and risk assessment
4. Write the structured intent to phase directory via `mcp__dominion__agent_submit`

For **trivial** or **moderate** complexity, capture intent conversationally without the structured framework.

## Completion

1. Call `mcp__dominion__phase_status()` to verify completion
2. Show results summary to the user
