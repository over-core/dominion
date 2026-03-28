---
name: orchestrate
description: Drive the development pipeline — select stages, dispatch agents, manage retries and completion
---

# /dominion:orchestrate

Drive the Dominion pipeline from intent to completion. Manages state recovery, agent dispatch, wave execution, review retry, and circuit breaker.

Usage: `/dominion:orchestrate "Add rate limiting to the API endpoints"`
Auto mode: `/dominion:orchestrate --auto "Add rate limiting"`
Resume mode: `/dominion:orchestrate --resume`

## Section 0: Resume Mode

If `--resume` flag is present OR session context contains "PIPELINE READY":
1. Call `mcp__dominion__get_progress()`
2. If no active phase (step == "idle"): "No active pipeline. Use `/dominion:orchestrate` to start a new one."
3. Otherwise: read phase, step, pipeline from progress response
4. Find current step index in pipeline → resume from that step through end
5. Skip to Section 3 (Step Loop) — no phase initialization needed

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
3. Call `mcp__dominion__suggest_pipeline_tool(intent, has_design_doc=True/False)` → returns suggested pipeline stages + reasoning + keywords matched
4. Evaluate the suggestion — adjust based on intent nuance the keyword matcher may miss:
   - Does the intent describe work that genuinely needs research, or is context already known?
   - Is a discuss step valuable here, or is the scope already clear?
   - Would skipping plan make sense (e.g., single-file change with obvious approach)?
5. Present to user in plain language:
   "I'll run **research → plan → execute → review**. Skipping discuss since the scope is clear. OK?"
   - In `--auto` mode: accept the suggestion (but never go below `["execute"]`)
6. Call `mcp__dominion__start_phase(intent, pipeline=[...])` → creates phase + step directories

**Skipped stage effects** (downstream agents handle missing context gracefully):
| Skipped | Effect |
|---------|--------|
| discuss | No panel discussion. You choose the pipeline directly. |
| research | No findings.toml. Plan works from intent + knowledge only. |
| plan | No tasks.toml. Execute uses inline task_info parameter. |
| execute | No implementation. Analysis-only pipeline. |
| review | No verdict. Ship uses manual mode PR body. |

### Objective Linking

After start_phase:
1. Call `mcp__dominion__get_objective()` → list active objectives
2. If active objectives exist AND intent keywords overlap with an objective name/summary:
   - Ask user: "Link this phase to objective '{name}'?"
   - If yes: call `mcp__dominion__link_phase_to_objective(phase, objective_id)`
3. If active objectives exist but no match: ask "Create a new objective for this work?"
   - If yes: call `mcp__dominion__create_objective(name, description)` then link the new phase
4. If NO objectives exist: skip silently — do not prompt the user about objectives
5. In `--auto` mode: auto-link if intent overlaps, auto-create only if objectives already exist

## Section 3: Step Loop

For each step in pipeline (skipping completed):

a. Call `mcp__dominion__prepare_step(phase, step, agents=[...])` → returns claude_md_path + agents list + metric_commands

   **Choosing agents for each step:**
   Start with the default agent for each stage:
   - research → researcher
   - plan → architect
   - execute → developer
   - review → reviewer
   - discuss → architect (+ others for panel)

   Then consider the intent — add specialists when warranted:
   - Security-related intent → add `security-auditor` to research and review
   - Broad architectural scope → add `analyst` to review
   - High uncertainty or exploration → add `innovation-engineer` to research
   - Large blast radius (many files/services affected) → add `security-auditor` + `analyst` to review

   Pass all chosen roles via the `agents` parameter. First entry is the primary agent.

a1. **Pre-analysis metrics:** If metric_commands is non-empty (research step):
   - For each command: run via Bash, capture stdout (timeout 30s each, ignore failures)
   - Collect results into a JSON dict: `{label: output}` (using each command's "label" as key)
   - Write the dict to `.dominion/phases/{phase}/research/metrics.json`
   - Call `mcp__dominion__prepare_step(phase, step, agents=[...])` AGAIN — it reads metrics.json and injects into CLAUDE.md
   This ensures metrics survive retries: metrics.json persists, and prepare_step reads it on regeneration.

b. Read CLAUDE.md from returned path via Read tool

c. Dispatch agents based on count:

   **Single agent** (one agent in list):
   - Spawn single `Agent(prompt=claude_md_content, subagent_type=agents[0].role)`
   - IMPORTANT: agents[0].role resolves to `.claude/agents/{role}.md` — a Dominion agent.
     Do NOT use plugin agents from your system prompt (e.g., python-development:python-pro).
     Dominion agents are purpose-built for this pipeline with correct model assignment and hard stops.

   **Multiple agents — parallel dispatch** (two or more agents in list):
   - For each agent: call `prepare_step(phase, step, role=agent.role)`, Read its CLAUDE.md
   - Spawn ALL agents in parallel with their respective content, using `subagent_type=agent.role`
   - Same rule: use Dominion agents, NOT plugin agents

   **Panel synthesis** (discuss step, or multi-specialist review):
   - For each panel agent: call `prepare_step(phase, step, role=agent.role)`, Read CLAUDE.md
   - Spawn in parallel → collect outputs
   - Orchestrator synthesizes inline using the Panel Discussion Framework (below)
   - Submit synthesis: `submit_work(phase, step, "orchestrator", synthesis, summary)`

### Panel Discussion Framework

When synthesizing multi-agent outputs (discuss step, multi-specialist review):
1. Read all agent submissions
2. For each position: steelman the strongest counter-argument
3. Identify shared assumptions across all agents — challenge them
4. Find productive tensions between positions
5. Produce:
   - **Recommendation**: what survives criticism
   - **Dissents**: minority positions with rationale
   - **Trade-offs**: what's gained vs what's lost
6. Submit synthesis as step output

### Post-Research Dispatch Adjustment

After research completes, read the research summary:
- If findings include high-severity security items → add `security-auditor` to review
- If findings span 3+ categories with high severity → add `analyst` to review
- If findings are low-severity and narrow → keep default single reviewer

d. **Pipeline adjustment after discuss:**
   - After discuss completes, read the discuss output
   - Check for `pipeline_adjustment` — a recommendation to add or remove stages from the remaining pipeline
   - Check for `specialist_additions` — recommendations to add specialist agents to specific steps
   - Adjust dispatch for remaining steps accordingly
   - Call `save_decision(phase, "pipeline_adjustment", adjustment, "Discuss panel recommendation")`

e. **Execute step — wave loop:**
   - If pipeline is `["execute"]` only (no plan step was run), create task_info inline:
     `{"title": intent, "description": intent, "files": [], "wave": 1, "dependencies": [], "agent_role": "developer"}`
     Call `prepare_task(phase, "01", task_info=...)`, Read CLAUDE.md, spawn developer.
   - Otherwise read `plan/output/tasks.toml` → group tasks by wave
   - **Wave 0 (stubs, if present):**
     - Spawn architect agent WITHOUT `isolation='worktree'` (direct commit to branch)
     - After stub task completes, verify stubs committed
     - All subsequent worktrees branch from this updated HEAD
   - **Pre-wave cleanup** (before spawning worktree agents for each wave):
     1. Verify current branch: `git branch --show-current` → store as `{current_branch}`
     2. Stash dirty state: `git stash --include-untracked -m "dominion-pre-wave-{N}"` (ignore "nothing to stash")
     3. Remove stale worktrees: `for wt in $(git worktree list --porcelain | grep -oP '(?<=worktree ).+\.claude/worktrees/.+'); do git worktree remove --force "$wt"; done`
     4. Include in each agent's prompt: "Your worktree MUST branch from `{current_branch}` at HEAD.
        Verify with `git log --oneline -1` that your branch includes the Wave 0 stubs.
        Do NOT commit directly to `{current_branch}`. All work must be in your worktree."
   - **Wave 1+ (implementation):**
     - For each task: call `prepare_task(phase, task_id)`, Read CLAUDE.md
     - For each task: call `mcp__dominion__register_agent(phase, "execute", task.agent_role, task_id)` before spawning
     - Spawn in **batches of 4-5 agents** maximum per batch: `Agent(isolation='worktree', prompt=content, subagent_type=task.agent_role)`
     - **Stall detection** (after each batch returns):
       - Call `mcp__dominion__check_agent_health(phase)` → check for stalled agents
       - For each stalled agent: re-prepare task and re-spawn (up to 1 retry per task)
       - Proceed with partial results if all retries exhausted
     - **Post-batch verification** (after each batch returns):
       a. For each agent: check for worktreePath in output. If missing, agent committed directly — log warning: "Agent {role} for task {id} did not create worktree"
       b. For each worktree branch: verify base with `git merge-base --is-ancestor {current_branch} {worktree_branch}`. If not ancestor → flag: "Worktree {branch} branched from wrong base"
       c. **Unsubmitted work detection**: for each agent, call `get_progress()` and check if task status is "complete". If NOT complete but agent returned:
          - Check for uncommitted changes: `git -C {worktree_path} status --porcelain`
          - If uncommitted changes: commit on behalf: `git -C {worktree_path} add -A && git -C {worktree_path} commit -m "feat: auto-commit unsubmitted work for task {id}"`
          - Submit on behalf: `submit_work(phase, "execute", role, '{"commit": "auto", "tests_run": 0, "tests_passed": 0}', "Auto-submitted: agent failed to submit")`
          - Log warning: "Agent for task {id} failed to submit — auto-submitted with zero test verification"
       d. Extract `total_tokens` from each agent's output; accumulate in a tokens list: `[{role, task, tokens}]`
     - **Worktree Merge Protocol** (after all batch agents return):
       0. Pre-merge: ensure clean state: `git status --porcelain` — if dirty, `git stash --include-untracked -m "dominion-pre-merge"`
       0a. Clean each worktree: `git -C {worktree_path} clean -fd`
       0b. Pre-merge file check: `git diff --name-only {branch} {current_branch}` — verify changed files are a subset of the agent's assignment. If unexpected files appear, halt and report.
       1. Squash-merge each branch: `git merge --squash {branch} && git commit -m "feat({scope}): {task_title}"`
       2. On conflict → halt: "Merge conflict in {files}. Resolve manually, re-run."
       3. On success → `git worktree remove .claude/worktrees/{worktree_name}` THEN `git branch -d {branch}`
       4. After ALL wave N branches merged → pop stash if exists (`git stash pop`, ignore errors)
   - **Wave-landing review** (after wave N merge, before wave N+1):
     - IF wave N had > 2 tasks:
       - Create task_info: `{"title": "Wave {N} integration review", "description": "Verify cross-task consistency", "files": [{all files from wave N tasks}], "wave": N, "dependencies": [{wave N task IDs}], "agent_role": "developer"}`
       - Call `prepare_task(phase, "wave-review-{N}", task_info)` → uses wave-review.md heuristic automatically
       - Read CLAUDE.md, spawn Developer (Sonnet) WITHOUT `isolation='worktree'` (runs on merged branch)
       - If issues found: developer fixes inline, commits `"fix(wave-{N}): resolve cross-task integration issues"`
     - ELSE: run test suite directly as quick sanity check
     - Continue to wave N+1 from updated HEAD
   - **Post-execute cleanup** (after all waves complete):
     - Remove ALL remaining worktrees: `for wt in $(git worktree list --porcelain | grep -oP '(?<=worktree ).+\.claude/worktrees/.+'); do git worktree remove --force "$wt"; done`
     - Verify: `git worktree list` shows only main worktree
     - Pop any remaining stash: `git stash pop` (ignore errors)
   - **Integration validation** (after cleanup, before submitting execute):
     1. Run full test suite: the project's test command from config
     2. If tests fail: spawn a single developer agent WITHOUT `isolation='worktree'` with prompt: "Integration issues detected after multi-agent merge. Test failures: {output}. Read the failing test files and the source files they test. Fix cross-module integration issues only. Do NOT refactor working code."
     3. Re-run tests. If still failing after 1 fix attempt → halt: "Integration test failures persist. Manual intervention needed."
   - After integration passes:
     - Call `submit_work(phase, "execute", "orchestrator", {tasks_completed, waves, files_changed}, summary)`
     - Call `advance_step(phase, "execute")`

f. After all agents for non-execute steps return:
   - Call `mcp__dominion__advance_step(phase, step)`
   - **Session memory**: If EchoVault is available (`mcp__echovault__*` tools exist):
     - Read agent summaries from `.dominion/phases/{phase}/{step}/output/summary.md`
     - For each agent that submitted: call `mcp__echovault__memory_save(key="dominion/{phase}/{step}/{role}", content="{summary}")`
   - **Before preparing agents for the NEXT step**: query EchoVault:
     - Call `mcp__echovault__memory_search(query="dominion {next_step} {intent[:100]}", limit=3)`
     - If results: append `## Prior Session Memory\n{results}` to the CLAUDE.md content before passing to agent

g0. **Analysis completion (research + review pipeline with no execute):**
   After research and review complete (no plan/execute in this pipeline):
   1. Read all research findings from `.dominion/phases/{phase}/research/output/`
   2. Read all review findings from `.dominion/phases/{phase}/review/output/`
   3. **Save knowledge entries** — for each major finding category:
      - Call `save_knowledge(topic, content, tags="research,plan,execute,review", summary)` with:
        - Prescriptive guidance (not just observations)
        - Real code examples with file:line from the findings
        - `referenced_files` populated from the findings' file references
      - Categories: framework-patterns, security-findings, performance-analysis, test-coverage, dependency-health, improvement-priorities
      - Incorporate review corrections: severity changes, new findings, quantitative fixes
   4. **Present summary to user** inline (NOT a file):
      "Analysis complete. {N} knowledge entries saved to .dominion/knowledge/:
       - framework-patterns: {summary}
       - security-findings: {summary}
       - ..."
   5. Do NOT write docs/ files. Knowledge entries ARE the analysis output.
      They persist across phases, are injected into agent briefs, and are committed to git.
      Agents read knowledge; agents don't read docs/.
   6. Commit knowledge: `git add .dominion/knowledge/ && git commit -m "feat(knowledge): seed from codebase analysis"`
   7. Skip to Section 5 (Completion)

g. **Review step — specialist-enriched protocol:**
   0. **Pre-review cleanup**: remove ALL stale worktrees before spawning any review agents:
      `for wt in $(git worktree list --porcelain | grep -oP '(?<=worktree ).+\.claude/worktrees/.+'); do git worktree remove --force "$wt"; done`
      Verify: `ls .claude/worktrees/ 2>/dev/null` should be empty or not exist.
      This prevents reviewers from reading stale code in old worktree directories.
   1. If specialist agents were selected (from intent analysis or post-research adjustment):
      - Call `prepare_step(phase, "review", role="security-auditor")` and/or `prepare_step(phase, "review", role="analyst")` as appropriate
      - Spawn specialists in parallel
      - After specialists submit: if blocking findings exist, apply fixes:
        - Fix the code issues identified by specialists
        - Commit fixes: `git add {files} && git commit -m "fix(review): address {N} specialist findings"`
      - Call `prepare_step(phase, "review")` (regenerates with specialist summaries + fix context)
      - Spawn Reviewer with enriched brief
   2. If no specialists needed (narrow scope, low risk):
      - Call `prepare_step(phase, "review")` directly
      - Spawn single Reviewer
   3. After Reviewer submits: call `advance_step(phase, "review")`
   - Then: call `mcp__dominion__quality_gate(phase)` → verdict → proceed/retry/halt
   - If not `--auto`: present verdict to user

## Section 4: Retry on Quality Gate Failure (--auto only)

When quality_gate returns action="retry":
1. Read blocking_findings from quality_gate response
2. For each finding, construct task_info: `{"title": "Fix: {desc}", "description": "Address {category} at {file}. Finding: {desc}", "files": ["{file}"], "wave": 1, "dependencies": [], "agent_role": "developer"}`
3. Call `prepare_task(phase, "fix-01", task_info=...)` for each fix task
4. Read each fix CLAUDE.md, spawn `Agent(isolation='worktree', prompt=content, subagent_type="developer")` for each
5. Squash-merge fix worktrees
6. Commit: `git commit -m "fix(review): address quality gate findings"`
7. Call `prepare_step(phase, "review")` → resets "complete" → "active", regenerates with fix summaries
8. Spawn review agent(s) — follow specialist-enriched protocol if specialists were used in the original review
9. After review: call `advance_step(phase, "review")`
10. Circuit breaker checks (quality_gate updates state.toml):
    - Same-finding hash comparison
    - Retry count against max_retries
11. On circuit breaker trigger → halt even in --auto mode

## Section 5: Completion

After review go/go-with-warnings:
1. Read review output for retrospective.knowledge_updates
2. Call `save_knowledge()` for each entry with content, tags, summary
3. **Report revision** (analysis phases only — when pipeline produced docs/reports, NOT implementation phases):
   a. Read review findings from `verdict.toml` — collect all items where action != "verified-fixed"
   b. Read specialist findings from security-auditor and analyst outputs
   c. Identify corrections that should flow back to published reports:
      - Severity changes (reviewer downgraded/upgraded)
      - New findings not in original reports
      - Quantitative corrections (wrong counts, misleading claims)
      - Missing analysis areas flagged by reviewers
   d. For EACH published report file that needs correction:
      - Read the current report
      - Apply corrections inline (add missing sections, fix numbers, add new findings, adjust severities)
      - Commit: `git add {file} && git commit -m "fix(reports): incorporate review findings into {filename}"`
   e. Do this directly — do NOT spawn a subagent for report corrections
4. Call `mcp__dominion__generate_phase_report(phase, tokens=accumulated_tokens_list)` → present metrics to user:
   "Phase {phase} complete:
    - {tasks_total} tasks across {waves} waves
    - {findings_by_severity} review findings
    - {retry_count} retries
    - {tokens.total} total tokens across {tokens.agents_spawned} agents"
5. If --auto: intent self-assessment
   - Read phase CLAUDE.md intent
   - Compare to execute + review summaries
   - Flag gaps as warnings
6. Output completion message
7. Include `<promise>pipeline complete</promise>` for ralph-loop compatibility
