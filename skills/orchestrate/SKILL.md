---
name: orchestrate
description: Drive the full pipeline — assess complexity, dispatch agents by thread type, manage retries
---

# /dominion:orchestrate

Drive the Dominion pipeline from intent to completion. Manages state recovery, agent dispatch, wave execution, review retry, and circuit breaker.

Usage: `/dominion:orchestrate "Add rate limiting to the API endpoints"`
Auto mode: `/dominion:orchestrate --auto "Add rate limiting"`

## Section 1: State Recovery

1. Call `mcp__dominion__get_progress()`
2. If circuit_breaker == "open":
   - Inform user: "Pipeline halted by circuit breaker. Make manual fixes, then re-run."
   - Reset circuit breaker to HALF_OPEN (user acknowledges by re-running)
   - Re-enter execute step
3. If phase complete (step == "idle", status == "complete"):
   - Read review output for knowledge_updates in retrospective
   - Call `mcp__dominion__save_knowledge()` for each entry with content, tags, summary
   - Report completion
   - Output `<promise>pipeline complete</promise>` for ralph-loop
4. If completed steps exist: skip them, continue from current position

## Section 2: Phase Initialization (if no active phase)

1. Parse `--auto` flag from invocation
2. Call `mcp__dominion__assess_complexity_tool(intent)` → get suggested complexity
3. Present assessment to user: "{complexity}: {reasoning}. Override? [Y/change/n]"
   - In `--auto` mode: use suggestion, MODERATE floor (never below moderate)
4. Call `mcp__dominion__start_phase(intent, complexity)` → creates phase + step dirs

## Section 3: Step Loop

For each step in pipeline profile (skipping completed):

a. Call `mcp__dominion__prepare_step(phase, step)` → returns path + thread_type + agents
b. Read CLAUDE.md from returned path via Read tool
c. Branch on thread type:

   **B-Thread** (single agent):
   - Spawn single `Agent(prompt=claude_md_content, subagent_type=agents[0].role)`

   **P-Thread** (parallel agents):
   - For each agent: call `prepare_step(phase, step, role=agent.role)`, Read its CLAUDE.md
   - Spawn ALL agents in parallel with their respective content

   **F-Thread** (panel — discuss step):
   - For each panel agent: call `prepare_step(phase, step, role=agent.role)`, Read CLAUDE.md
   - Spawn in parallel → collect outputs
   - Orchestrator synthesizes inline: read all summaries, produce recommendation + dissents + trade_offs
   - Submit synthesis: `submit_work(phase, "discuss", "orchestrator", synthesis, summary)`

   **Z-Thread** (trivial — execute only):
   - Call `prepare_task(phase, "01", task_info={"title": intent, "description": intent, "files": [], "wave": 1, "dependencies": [], "agent_role": "developer"})`
   - Read CLAUDE.md, spawn developer

d. **Execute step — wave loop:**
   - Read `plan/output/tasks.toml` → group tasks by wave
   - For each wave (ascending):
     - For each task: call `prepare_task(phase, task_id)`, Read CLAUDE.md
     - Spawn `Agent(isolation='worktree', prompt=content, subagent_type=task.agent_role)`
     - After ALL agents return: **Worktree Merge Protocol**
       1. Merge each branch: `git merge --no-ff {branch} -m "feat: {task_title}"`
       2. On conflict → C-Thread halt: "Merge conflict in {files}. Resolve manually, re-run."
       3. On success → `git branch -d {branch}` cleanup
       4. After ALL wave N branches merged → wave N+1 from updated HEAD
   - After all waves complete

e. After all agents for step return: call `mcp__dominion__advance_step(phase, step)`

f. **Review step — two-phase protocol (complex/major):**
   1. Call `prepare_step(phase, "review", role="security-auditor")` + `prepare_step(phase, "review", role="analyst")`
   2. Spawn specialists in parallel
   3. After specialists submit: call `prepare_step(phase, "review")` (regenerates with specialist summaries)
   4. Spawn Reviewer with enriched brief
   5. After Reviewer submits: call `advance_step(phase, "review")`
   - Then: call `mcp__dominion__quality_gate(phase)` → verdict → proceed/retry/halt
   - If not `--auto`: present verdict to user (C-Thread checkpoint)

## Section 4: L-Thread Retry (--auto only)

When quality_gate returns action="retry":
1. Read blocking_findings from quality_gate response
2. For each finding, construct task_info: `{"title": "Fix: {desc}", "description": "Address {category} at {file}. Finding: {desc}", "files": ["{file}"], "wave": 1, "dependencies": [], "agent_role": "developer"}`
3. Call `prepare_task(phase, "fix-01", task_info=...)` for each fix task
4. Read each fix CLAUDE.md, spawn `Agent(isolation='worktree', prompt=content)` for each
5. Merge fix worktrees
6. Call `prepare_step(phase, "review")` → resets "complete" → "active", regenerates with fix summaries
7. Spawn review agent(s) (follow two-phase protocol if complex/major)
8. After review: call `advance_step(phase, "review")`
9. Circuit breaker checks (quality_gate updates state.toml):
   - Same-finding hash comparison
   - Retry count against max_retries
10. On circuit breaker trigger → C-Thread halt even in --auto mode

## Section 5: Completion

After review go/go-with-warnings:
1. Read review output for retrospective.knowledge_updates
2. Call `save_knowledge()` for each entry with content, tags, summary
3. If --auto: intent self-assessment
   - Read phase CLAUDE.md intent
   - Compare to execute + review summaries
   - Flag gaps as warnings
4. Output completion message
5. Include `<promise>pipeline complete</promise>` for ralph-loop compatibility
