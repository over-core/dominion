---
name: research
description: Run the research step — codebase analysis producing structured findings
---

# /dominion:research

Run the research step standalone. Auto-creates a phase if none is active.

## Steps

1. Call `mcp__dominion__get_progress()`
2. If no active phase:
   - Ask user for intent (or use argument if provided)
   - Call `mcp__dominion__suggest_pipeline_tool(intent)` → present, allow override
   - Call `mcp__dominion__start_phase(intent, pipeline=[...])`
3. Call `mcp__dominion__prepare_step(phase, "research")` → get path + dispatch
4. Read CLAUDE.md from returned path
5. Dispatch by agent count:
   - Single agent: spawn single Researcher agent
   - Multiple agents in parallel: for each agent, call `prepare_step(phase, "research", role=role)`, Read each CLAUDE.md, spawn all in parallel
6. After all agents return: call `mcp__dominion__advance_step(phase, "research")`
7. Report: "Research complete. Run /dominion:plan to continue."
