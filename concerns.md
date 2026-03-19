# v0.3.0 Plan — Quality Audit

Deep analysis of `docs/plans/plan_v0.3.0.md` against the current codebase on `feat/v0.2.2-collaboration`. Findings organized by severity, then category.

---

## CRITICAL — Will cause implementation failures

### C1. submit_work step advancement: spec contradicts data flow traces

The data flow examples (line 1379) say submit_work advances `state.toml position.step` to the next step (e.g., research complete → step = "plan"). But the detailed spec (line 1815) explicitly says **"Does NOT advance position.step — step advancement is the orchestrator's responsibility (see advance_step tool)."** The advance_step tool exists specifically for this purpose.

The data flow traces at lines 1379, 1428, 1495 are all wrong per the spec. Anyone implementing from the traces will build a different system than someone implementing from the spec.

**Fix:** Remove all step-advancement language from the data flow traces. Add explicit `advance_step()` calls to each trace.

---

### C2. Orchestrator context pressure — no mitigation strategy

The orchestrator (main Claude session) must call `prepare_step` for every step/agent, receiving the **full CLAUDE.md content** in the MCP response (~1-2K tokens each). It then passes this content again in the Agent spawn prompt. For a complex pipeline:

- 5 steps, some with 3 agents = ~8-12 prepare_step calls
- Each returns 1-2K tokens of CLAUDE.md content in the response
- Plus tasks.toml reading, wave management, merge protocol output
- L-Thread retry adds more prepare_step + prepare_task calls

Conservative estimate: **40-80K tokens** of MCP response content accumulates in the orchestrator's context for a complex pipeline with one retry cycle. The plan states a 150K token budget (memory file) but doesn't analyze orchestrator context specifically.

**Risk:** L-Thread sessions will hit compaction before pipeline completes. ralph-loop restarts mitigate this, but interactive sessions can't recover mid-pipeline.

**Fix options:**
- `prepare_step` returns only dispatch info (thread_type, agents) + file path. Orchestrator passes the *path* to the Agent, and the Agent reads the file itself (for subagents — the orchestrator reads and passes content; for worktree agents, place CLAUDE.md in the worktree root for auto-load)
- Minimize what prepare_step returns in `claude_md_content` — perhaps only the first N lines or a summary, with a pointer to the full file

---

### C3. Decisions stored in gitignored state.toml — will be lost

`save_decision` writes to `state.toml [[decisions]]` (line 1966). state.toml is gitignored (line 767). Decisions are architectural choices ("chose OAuth2 over JWT because...") that should persist and be shared with the team.

Current behavior: decisions survive within a pipeline run and across phases (state.toml accumulates). But:
- If state.toml is manually deleted or corrupted → all decisions lost
- Decisions are not committed to git → team members don't see them
- EchoVault is "recommended, agent-managed" — not guaranteed to exist

**Fix:** Move decisions to a committed file (e.g., `.dominion/decisions.toml` or append to `knowledge/`). Or keep in state.toml but also write to a committed location.

---

### C4. Review retry lifecycle — status management undefined

During L-Thread retry after no-go:
1. advance_step marks review as "complete" (line 2501)
2. quality_gate returns "retry"
3. Fix tasks execute
4. Orchestrator calls prepare_step(phase, "review") again
5. prepare_step (line 1637): "If already 'complete', leave unchanged" — status stays "complete"
6. New Reviewer spawns, calls submit_work → overwrites verdict.toml
7. Orchestrator calls advance_step again — but advance_step (line 1947) verifies status is "active" or has submissions

**Problem:** advance_step may reject because review is already "complete" from the previous run. The entire retry-review lifecycle needs a status reset mechanism that the plan doesn't define.

**Fix:** Either add a `reset_step(phase, step)` tool, or make advance_step idempotent on "complete" status, or have prepare_step reset status to "active" on re-call when output already exists.

---

### C5. `[outstanding]` contradicts itself — referenced after declared removed

Line 863: `"[outstanding] removed — no read/write mechanism."`
Line 1600: start_phase should `"Preserve [[decisions]] and [outstanding]"`

Direct contradiction. start_phase can't preserve a section that doesn't exist.

**Fix:** Remove the [outstanding] reference from start_phase spec (line 1600).

---

## HIGH — Will cause confusion or require design decisions during implementation

### H1. Tool count inconsistency: "9" vs "11"

- Line 1574: "11 tools, down from 21 in v0.2.x"
- Line 1576: "3 setup + 2 agent + 6 pipeline = 11 total"
- Line 2809: "9 MCP tools (focused, non-overlapping)"
- Actual count from detailed specs: 3 + 2 + 5 + 1 = **11**

The "9" at line 2809 is stale. The "6 pipeline" at line 1576 includes save_knowledge (which has its own module).

**Fix:** Standardize on 11 everywhere. Clarify grouping: 3 setup + 2 agent + 5 pipeline + 1 knowledge = 11.

---

### H2. Execute step output filename undefined

submit_work maps steps to output filenames (lines 1806-1810):
- Research → `findings.toml`
- Plan → `tasks.toml`
- Review → `verdict.toml`
- Discuss → `findings.toml`
- **Execute → ???**

Line 2148 says "execute step doesn't produce a single TOML artifact." But submit_work always converts content to TOML (line 1801). What file does it write for execute tasks? The plan is silent.

**Fix:** Specify the filename (e.g., `result.toml` or `submission.toml`), or document that execute task submissions skip TOML conversion and only write summary.md.

---

### H3. tasks.toml lookup hardcodes architect role in key path

Plan output lives at `[findings.architect.tasks]` because submit_work namespaces everything under `[findings.{role}]`. prepare_task reads tasks.toml and finds tasks at this path (line 1722).

If someone configures a different role for the plan step, the key path becomes `[findings.{other_role}.tasks]` and prepare_task's lookup breaks.

**Fix:** Either store the role that produced the plan in state.toml so prepare_task knows where to look, or use a role-independent key path for plan output.

---

### H4. Orchestrate skill carries extreme complexity as natural language

The orchestrate skill (~100-150 lines of prose) encodes: argument parsing, state recovery, circuit breaker management, 6 thread types, wave loops, worktree merge protocol, L-Thread retries, knowledge saving, intent self-assessment, and completion promises.

v0.3.0's orchestrate is MORE complex than v0.2.x's (adds L-Thread, circuit breaker, worktree merge, two-phase review), yet the plan criticizes v0.2.x for "complexity without validation." A misinterpreted instruction in the skill prose means a derailed pipeline with no code-level safety net.

**Risk:** This is the single highest-risk artifact in the design. No mitigation proposed.

---

### H5. Missing skill specifications: status, improve, individual step skills

- **status skill** (line 137): "where are we?" — No specification of what it reads, shows, or formats
- **improve skill** (line 2890): "standalone command" — No specification of conversation flow, questions, or save_knowledge usage. Current improve has 2 reference files (agent-methodology-design.md, skill-quality-guide.md) — fate unspecified
- **Individual step skills** (research, plan, execute, review, discuss): Listed as SKILL.md files but no outline of their contents. Must handle standalone invocation (auto-create phase), prepare_step calls, thread-type dispatch. Are they simplified orchestrate copies?

**Fix:** Add outline for each, or state they're deferred to implementation.

---

### H6. F-Thread synthesis: orchestrator calls submit_work with role="orchestrator"

Line 247: orchestrator submits synthesis via `submit_work(phase, "discuss", synthesis, summary)` as "orchestrator" namespace. But "orchestrator" is not in the agent roster. Does submit_work validate roles against the roster? If yes → this call is rejected. If no → undocumented.

**Fix:** Explicitly state that submit_work does NOT validate roles against the roster, or add "orchestrator" as a valid pseudo-role.

---

### H7. prepare_step two-phase review contradiction

Line 1635-1636: With role override, writes to `phases/{phase}/{step}/agents/{role}/CLAUDE.md` (separate files per role).
Line 1703: "the file on disk is overwritten each time (only last one persists)."

These describe mutually exclusive behaviors. Line 1635 is the correct design (agent subdirs); line 1703 is stale text from before subdirs were added.

**Fix:** Remove line 1703 or clarify it only applies to the primary (no-role-override) CLAUDE.md.

---

### H8. refine_complexity trigger in multi-agent research

Line 1381: "On research complete, internally calls refine_complexity()." But at complex/major, 3 agents submit to research (P-Thread). Which submit_work call triggers refinement? First? Last? All?

If triggered on every submission, complexity could be upgraded after the first agent submits but before others finish — changing the pipeline mid-research.

**Fix:** Trigger refinement only when ALL research agents have submitted (all status files complete), or trigger on first submission but don't apply upgrade until step advances.

---

## MEDIUM — Design smells, edge cases, and fragile assumptions

### M1. assess_complexity keyword matching is brittle

"Fix the authentication vulnerability in our OAuth2 implementation" contains "fix" → trivial? But this is clearly not trivial. The plan acknowledges orchestrate can override (line 2042) but doesn't specify the UX: does it present the assessment and ask? Does it just override silently?

---

### M2. Same-finding detection hash is too strict

SHA-256 of sorted (category, file, description) strings. If the reviewer rewords "SQL injection vulnerability" → "SQL injection in query builder," the hash changes. The circuit breaker misses semantically identical findings with different wording.

---

### M3. Source-diving hook references plugin paths not in target project

The hookify rule (line 2790-2800) blocks reading `*/skills/*|*/mcp/dominion_mcp/*`. But these are Dominion PLUGIN paths, installed at `~/.claude/plugins/` or similar — not in the target project directory. The hook pattern would never match in the target project's context.

**Fix:** Use the plugin's actual installed path, or drop this hook since agents shouldn't be looking at plugin internals anyway.

---

### M4. Knowledge index lacks file-path metadata for relevance filtering

Line 1728: prepare_task includes knowledge entries "whose content references files in the task's files list." But the index schema (line 1212-1224) stores only topic, summary, tags, path — no file references. To check file-path relevance, prepare_task would need to READ every knowledge file's content. For 20+ files, this is expensive I/O.

**Fix:** Add a `referenced_files` field to index.toml entries, populated by save_knowledge.

---

### M5. validation.py fate unspecified

Current codebase has `core/validation.py` (integrity checks). The plan's "Deleted" section doesn't list it. The "Stays" section doesn't list it. The "Added" section doesn't list it. The core module count (line 2903) lists 6 modules and doesn't include validation.

**Fix:** Explicitly state whether validation.py is deleted, kept, or merged into another module.

---

### M6. Onboard data files fate unspecified: roles.toml, domains.toml, infrastructure.toml

The plan's directory listing (line 608-612) shows languages.toml, frameworks.toml, registry.toml. The current codebase also has roles.toml, domains.toml, infrastructure.toml. With only 7 agents and "all deployed by default" (line 2341), roles.toml is dead data. domains.toml and infrastructure.toml are used by the current detection flow — are they still used?

**Fix:** Explicitly list which data files are kept, deleted, or modified.

---

### M7. Version bump locations in CLAUDE.md still say 6

The project CLAUDE.md says "Bump version in 6 locations" including templates/schemas/dominion.toml and templates/mcp-spec.toml. v0.3.0 deletes templates/ entirely, reducing to 4 locations. The plan notes the reduction (line 2859) but doesn't mention updating CLAUDE.md's versioning instructions.

---

### M8. No rollback mechanism for failed phases

If a phase goes wrong, there's no way to undo. Worktree merges commit to the feature branch during execute waves. Rolling back requires manual git operations. The plan has "abandoned" status but no restoration path.

---

### M9. Concurrent orchestrate invocations can corrupt state.toml

Two Claude sessions = two MCP server processes = independent asyncio.Locks. Both could write state.toml simultaneously. write_toml_locked only protects within a single process.

---

### M10. session-start.sh parses TOML with grep — fragile

Lines 2761-2763 use `grep '^phase = '` to parse state.toml. Works only for simple single-line string values. If TOML formatting changes (e.g., inline tables, multiline values), grep breaks. Acceptable for machine-generated files but fragile for maintenance.

---

### M11. Post-research complexity upgrade skips discuss step

If refine_complexity upgrades moderate → complex after research, the discuss step (F-Thread panel) was never executed. Research used B-Thread (single agent) instead of P-Thread (3 agents). Completed steps are not re-run (line 2539). The upgrade improves remaining steps but can't compensate for insufficient research.

---

### M12. All 7 agents deployed — no project-based selection

Innovation Engineer (TRIZ/TOC/SIT) is deployed for every project. Every complex research step spawns 3 Opus agents. For a simple CRUD app, Innovation Engineer adds cost without proportional value. No mechanism to skip specialists based on project characteristics.

---

### M13. CLAUDE.md naming creates ambiguity with auto-loading

Project root CLAUDE.md (committed, human-edited) and ephemeral phase/step CLAUDE.md files (gitignored, machine-generated) share the same filename. Claude Code auto-loads all CLAUDE.md files in the directory tree. If phases/ aren't properly gitignored from auto-loading scope, agents could receive conflicting instructions.

---

### M14. Multi-phase state.toml growth

state.toml accumulates [[phases]] and [[decisions]]. After 20 phases, state.toml could be 200+ lines. prepare_step reads all of it for every step. CLAUDE.md prior-phases section grows unboundedly. No archival/cleanup mechanism specified.

---

## LOW — Cosmetic, adoption friction, or philosophical

### L1. Python >= 3.14 requirement

pyproject.toml requires Python >= 3.14 (released Oct 2025). Limits adoption for users on older Python. `uv tool install` mitigates this (uv can manage Python versions), but it's still friction.

---

### L2. "No methodology" claim vs. heuristics content

The plan argues against teaching Claude methodology. But review heuristics (line 2437) include "flag excessive restating comments, over-abstracted single-use wrappers, generic error messages" — this IS methodology (how to review). The distinction between "methodology" and "heuristics" is philosophical, not practical. The system is simpler, but the critique of v0.2.x overstates the philosophical change.

---

### L3. docs/architecture.md will be completely stale

Architecture map references 17 agents, 21 tools, 7-step pipeline, 6 dispatch modes. All change in v0.3.0. The plan doesn't mention updating it. Gitignored but referenced in CLAUDE.md as the canonical architecture map.

---

### L4. Memory files will be stale after implementation

MEMORY.md references "201 tests, 21 MCP tools, 17 agents." All numbers change. Memory files (project_mcp_redesign.md, project_v030_filesystem_design.md) reference v0.2.x concepts that will be obsolete.

---

### L5. Ship skill scope is ambitious for this version

Ship (lines 2582-2678) is a full feature: 10 steps, two modes, auto-fix rules, verification gates, platform-aware PR creation. Including it alongside the complete MCP rewrite adds significant scope. Could be v0.3.1.

---

### L6. Discuss schema validation is absent

submit_work for discuss accepts "any valid structure" (line 1800). But the F-Thread panel protocol expects specific format (recommendation, dissents, trade_offs). No validation means malformed panel output passes silently.

---

### L7. No test command storage

Execute heuristic says "run tests before submitting." Ship says "detect test command from CLAUDE.md/config." But neither config.toml nor CLAUDE.md additions specify a concrete test command field. The developer agent must infer `pytest`, `npm test`, `cargo test` from language detection — never explicitly stored.

---

## SUMMARY

| Severity | Count | Key themes |
|----------|-------|------------|
| CRITICAL | 5 | State management contradictions, context pressure, data loss risk |
| HIGH | 8 | Missing specs, fragile coupling, complexity concentration |
| MEDIUM | 14 | Edge cases, dead code, design smells |
| LOW | 7 | Adoption, scope, cosmetic |
| **Total** | **34** | |

**Top 3 risks to address before implementation:**
1. **C2** — Orchestrator context pressure will cause L-Thread sessions to fail
2. **C4** — Review retry status management will break autonomous mode
3. **H4** — Orchestrate skill complexity exceeds what natural language can reliably encode
