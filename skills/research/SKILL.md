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
   - Call `mcp__dominion__assess_complexity_tool(intent)` → present, allow override
   - Call `mcp__dominion__start_phase(intent, complexity)`
3. Call `mcp__dominion__prepare_step(phase, "research")` → get path + dispatch
4. Read CLAUDE.md from returned path
5. Dispatch by thread type:
   - B-Thread (moderate): spawn single Researcher agent
   - P-Thread (complex/major): for each agent, call `prepare_step(phase, "research", role=role)`, Read each CLAUDE.md, spawn all in parallel
6. After all agents return: call `mcp__dominion__advance_step(phase, "research")`
7. Report: "Research complete. Run /dominion:plan to continue."
