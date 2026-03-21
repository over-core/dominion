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
2. Determine if intent references a design doc (check for doc/spec/design file mentions)
3. Call `mcp__dominion__assess_complexity_tool(intent, has_design_doc=True/False)` → get suggested complexity
4. Present assessment to user: "{complexity}: {reasoning}. Override? [Y/change/n]"
   - In `--auto` mode: use suggestion, MODERATE floor (never below moderate)
5. Call `mcp__dominion__start_phase(intent, complexity)` → creates phase + step dirs

## Section 3: Step Loop

For each step in pipeline profile (skipping completed):

a. Call `mcp__dominion__prepare_step(phase, step)` → returns path + thread_type + agents
b. Read CLAUDE.md from returned path via Read tool
c. Branch on thread type:

   **B-Thread** (single agent):
   - Spawn single `Agent(prompt=claude_md_content, subagent_type=agents[0].role)`
   - IMPORTANT: agents[0].role resolves to `.claude/agents/{role}.md` — a Dominion agent.
     Do NOT use plugin agents from your system prompt (e.g., python-development:python-pro).
     Dominion agents are purpose-built for this pipeline with correct model assignment and hard stops.

   **P-Thread** (parallel agents):
   - For each agent: call `prepare_step(phase, step, role=agent.role)`, Read its CLAUDE.md
   - Spawn ALL agents in parallel with their respective content, using `subagent_type=agent.role`
   - Same rule: use Dominion agents, NOT plugin agents

   **F-Thread** (panel — discuss step):
   - For each panel agent: call `prepare_step(phase, step, role=agent.role)`, Read CLAUDE.md
   - Spawn in parallel → collect outputs
   - Orchestrator synthesizes inline: read all summaries, produce recommendation + dissents + trade_offs
   - Submit synthesis: `submit_work(phase, "discuss", "orchestrator", synthesis, summary)`

   **Z-Thread** (trivial — execute only):
   - Call `prepare_task(phase, "01", task_info={"title": intent, "description": intent, "files": [], "wave": 1, "dependencies": [], "agent_role": "developer"})`
   - Read CLAUDE.md, spawn developer

d. **Complexity override after discuss:**
   - After discuss completes, check output for complexity_override recommendation
   - If discuss recommends downgrade (e.g., "specified"):
     - Call `save_decision(phase, "complexity_override", recommended_level, "Discuss panel assessed spec as comprehensive")`
     - Skip steps not in the downgraded pipeline profile (e.g., skip research for "specified")
     - Continue with adjusted pipeline

e. **Execute step — wave loop:**
   - Read `plan/output/tasks.toml` → group tasks by wave
   - **Wave 0 (stubs, if present):**
     - Spawn architect agent WITHOUT `isolation='worktree'` (direct commit to branch)
     - After stub task completes, verify stubs committed
     - All subsequent worktrees branch from this updated HEAD
   - **Before spawning worktree agents:** verify current branch with `git branch --show-current`.
     Include in each agent's prompt: "Your worktree MUST branch from `{current_branch}` at HEAD.
     Verify with `git log --oneline -1` that your branch includes the Wave 0 stubs."
   - **Wave 1+ (implementation):**
     - For each task: call `prepare_task(phase, task_id)`, Read CLAUDE.md
     - Spawn in **batches of 4-5 agents** maximum per batch: `Agent(isolation='worktree', prompt=content, subagent_type=task.agent_role)`
     - After each batch returns:
       - Verify all agents created worktrees (check for worktreePath in output)
       - If any agent failed to create a worktree, retry that agent once
       - Clean up failed worktree artifacts: `rm -rf .claude/worktrees/{failed_branch}`
       - Extract `total_tokens` from each agent's output; accumulate in a tokens list: `[{role, task, tokens}]`
     - **Worktree Merge Protocol** (after all batch agents return):
       0. Pre-merge check: `git diff --name-only {branch} $(git branch --show-current)` — verify changed files are a subset of the agent's assignment. If unexpected files appear, halt and report.
       0a. Clean worktree before merge: `git -C {worktree_path} clean -fd` to remove untracked files that could leak into the merge.
       1. Squash-merge each branch: `git merge --squash {branch} && git commit -m "feat({scope}): {task_title}"`
       2. On conflict → C-Thread halt: "Merge conflict in {files}. Resolve manually, re-run."
       3. On success → `git branch -d {branch}` cleanup
       4. After ALL wave N branches merged → wave N+1 from updated HEAD
   - After all waves complete:
     - Call `submit_work(phase, "execute", "orchestrator", {tasks_completed, waves, files_changed}, summary)`
     - Call `advance_step(phase, "execute")`

f. After all agents for non-execute steps return: call `mcp__dominion__advance_step(phase, step)`

g. **Review step — two-phase protocol (complex/major):**
   1. Call `prepare_step(phase, "review", role="security-auditor")` + `prepare_step(phase, "review", role="analyst")`
   2. Spawn specialists in parallel
   3. After specialists submit: if blocking findings exist, apply fixes:
      - Fix the code issues identified by specialists
      - Commit fixes: `git add {files} && git commit -m "fix(review): address {N} specialist findings"`
   4. Call `prepare_step(phase, "review")` (regenerates with specialist summaries + fix context)
   5. Spawn Reviewer with enriched brief
   6. After Reviewer submits: call `advance_step(phase, "review")`
   - Then: call `mcp__dominion__quality_gate(phase)` → verdict → proceed/retry/halt
   - If not `--auto`: present verdict to user (C-Thread checkpoint)

## Section 4: L-Thread Retry (--auto only)

When quality_gate returns action="retry":
1. Read blocking_findings from quality_gate response
2. For each finding, construct task_info: `{"title": "Fix: {desc}", "description": "Address {category} at {file}. Finding: {desc}", "files": ["{file}"], "wave": 1, "dependencies": [], "agent_role": "developer"}`
3. Call `prepare_task(phase, "fix-01", task_info=...)` for each fix task
4. Read each fix CLAUDE.md, spawn `Agent(isolation='worktree', prompt=content, subagent_type="developer")` for each
5. Squash-merge fix worktrees
6. Commit: `git commit -m "fix(review): address quality gate findings"`
7. Call `prepare_step(phase, "review")` → resets "complete" → "active", regenerates with fix summaries
8. Spawn review agent(s) (follow two-phase protocol if complex/major)
9. After review: call `advance_step(phase, "review")`
10. Circuit breaker checks (quality_gate updates state.toml):
    - Same-finding hash comparison
    - Retry count against max_retries
11. On circuit breaker trigger → C-Thread halt even in --auto mode

## Section 5: Completion

After review go/go-with-warnings:
1. Read review output for retrospective.knowledge_updates
2. Call `save_knowledge()` for each entry with content, tags, summary
3. Call `mcp__dominion__generate_phase_report(phase, tokens=accumulated_tokens_list)` → present metrics to user:
   "Phase {phase} complete:
    - {tasks_total} tasks across {waves} waves
    - {findings_by_severity} review findings
    - {retry_count} retries
    - {tokens.total} total tokens across {tokens.agents_spawned} agents"
4. If --auto: intent self-assessment
   - Read phase CLAUDE.md intent
   - Compare to execute + review summaries
   - Flag gaps as warnings
5. Output completion message
6. Include `<promise>pipeline complete</promise>` for ralph-loop compatibility
