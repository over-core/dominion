---
name: discuss
description: Run the discuss step — capture intent, F-Thread panel debate at complex/major, spec assessment
---

# /dominion:discuss

Run the discuss step standalone. Auto-creates a phase if none is active.

## Steps

1. Call `mcp__dominion__get_progress()`
2. If no active phase: auto-create (assess_complexity + start_phase)
3. Call `mcp__dominion__prepare_step(phase, "discuss")` → get dispatch
4. Dispatch by thread type:

   **F-Thread (complex/major — panel debate):**
   - Round 1: For each panel agent, call `prepare_step(phase, "discuss", role=role)`, Read CLAUDE.md, spawn in parallel
     - IMPORTANT: Use Dominion agents (subagent_type=role resolves to `.claude/agents/{role}.md`). Do NOT use plugin agents.
   - Round 2: Read all summaries from `discuss/output/summary.md`
   - Orchestrator synthesizes: "Here are N perspectives: {summaries}. Identify agreement, disagreement, trade-offs."
   - Check for complexity_override recommendations in panel outputs
   - Submit synthesis: `submit_work(phase, "discuss", "orchestrator", synthesis, summary)`

   **B-Thread (moderate — no panel):**
   - Discuss step is not in moderate pipeline. If called standalone at moderate, capture intent directly from conversation.

5. After synthesis: call `mcp__dominion__advance_step(phase, "discuss")`
6. If panel recommended complexity_override:
   - Report: "Panel recommends '{override}' complexity. Adjusting pipeline."
7. Report: "Discuss complete. Panel recommendation: {summary}. Run /dominion:research to continue."
