---
name: discuss
description: Run the discuss step — capture intent, panel debate for multi-perspective analysis, spec assessment
---

# /dominion:discuss

Run the discuss step standalone. Auto-creates a phase if none is active.

## Steps

1. Call `mcp__dominion__get_progress()`
2. If no active phase: auto-create (suggest_pipeline_tool + start_phase(intent, pipeline=[...]))
3. Call `mcp__dominion__prepare_step(phase, "discuss")` → get dispatch
4. Dispatch by thread type:

   **Panel debate (multiple agents):**
   - Round 1: For each panel agent, call `prepare_step(phase, "discuss", role=role)`, Read CLAUDE.md, spawn in parallel
     - IMPORTANT: Use Dominion agents (subagent_type=role resolves to `.claude/agents/{role}.md`). Do NOT use plugin agents.
   - Round 2: Read all summaries from `discuss/output/summary.md`
   - Orchestrator synthesizes: "Here are N perspectives: {summaries}. Identify agreement, disagreement, trade-offs."
   - Check for pipeline_adjustment and specialist_additions recommendations in panel outputs
   - Submit synthesis: `submit_work(phase, "discuss", "orchestrator", synthesis, summary)`

   **Single agent:**
   - Spawn architect, capture scope. If called standalone without panel, capture intent directly from conversation.

5. After synthesis: call `mcp__dominion__advance_step(phase, "discuss")`
6. If panel recommended pipeline_adjustment:
   - Report: "Panel recommends adjusting pipeline. Applying specialist_additions."
7. Report: "Discuss complete. Panel recommendation: {summary}. Run /dominion:research to continue."
