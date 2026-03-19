---
name: review
description: Run the review step — cross-cutting code review with specialist support
---

# /dominion:review

Run the review step standalone. Auto-creates a phase if none is active.

## Steps

1. Call `mcp__dominion__get_progress()`
2. If no active phase: auto-create (assess_complexity + start_phase)
3. Determine review protocol from complexity:

   **Moderate (B-Thread):**
   - Call `prepare_step(phase, "review")` → single Reviewer
   - Read CLAUDE.md, spawn Reviewer

   **Complex/Major (two-phase P-Thread):**
   - Phase 1: call `prepare_step(phase, "review", role="security-auditor")` + `prepare_step(phase, "review", role="analyst")`
   - Read each CLAUDE.md, spawn specialists in parallel
   - Phase 2: call `prepare_step(phase, "review")` (regenerates with specialist summaries)
   - Read CLAUDE.md, spawn Reviewer with enriched brief

4. After Reviewer submits: call `mcp__dominion__advance_step(phase, "review")`
5. Call `mcp__dominion__quality_gate(phase)` → present verdict
6. Report: "{verdict}. {blocking_count} blocking, {warning_count} warnings."
