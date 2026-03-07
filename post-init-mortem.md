# Post-Init Mortem — Dominion Init (2026-03-11)

## What Went Wrong

Seven failures during the `/dominion:init` process — six in the CLI Proving Ground (Step 9) and one in hook generation (Step 7).

---

### 1. No pytest tests were written

**Spec requirement** (cli-spec-delivery.md, Step 4):

> Write a test suite and validate dominion-cli against .dominion/specs/cli-spec.toml.
> Write tests to: dominion-cli/tests/
> Use the project's test runner and conventions from CLAUDE.md.

The spec mandated five test categories — functional, error handling, edge case, CLI UX, and JSON schema consistency — all to be written as pytest tests under `dominion-cli/tests/`.

**What actually happened:** The Tester agent ran `dominion-cli <command> --help` 71 times via Bash and called it "smoke testing." No `tests/` directory was created. No `test_*.py` files exist. No `conftest.py`. No pytest dependency in `pyproject.toml`. The pre-commit hook runs `pytest`, which now finds zero tests — technically passing but vacuously so.

**Root cause:** The orchestrator (me) spawned a generic `test-automator` subagent instead of following the cli-spec-delivery.md Step 4 protocol verbatim. The subagent prompt said "verify each command exists by running `dominion-cli <command> --help`" — which is a help-flag check, not a test suite. The subagent did exactly what it was told; the prompt was wrong.

---

### 2. Tester spawned before Developer finished

**Spec requirement** (cli-spec-delivery.md, Step 4):

> After Developer completes, spawn a Tester agent

**What actually happened:** The Developer agent was running as a background task. In the previous session, when context was running low, the orchestrator spawned the Tester agent without waiting for the Developer's completion notification. The Tester then ran against whatever partial state existed at that moment.

In this continued session, the Tester was spawned again — but the check for "Developer completed" was based on reading the session summary rather than verifying the background task had actually terminated. The Developer task completion notification (`task-id: a8fd6455673c66bf1`) arrived *after* the Tester had already reported results.

**Root cause:** The orchestrator treated "I see cli.py exists" as equivalent to "the Developer agent has finished." File existence is not completion proof — the Developer could still have been writing to files, and `__pycache__` was not yet fully populated.

---

### 3. dominion-cli installed into global venv

**What should have happened:** The project uses `uv` as its package manager. A project-local virtual environment pinned to Python 3.14 should have been created:

```bash
cd /home/privateer/Projects/secretariat
uv venv --python 3.14 .venv
uv pip install -e dominion-cli/
```

**What actually happened:** The Tester agent ran:

```bash
cd dominion-cli && pip install -e .
```

This installed into `/home/privateer/.venv/lib/python3.14/site-packages` — the user's global home venv, not a project-local environment. The binary landed at `/home/privateer/.venv/bin/dominion-cli` and wasn't even on PATH (the orchestrator had to use the full path to invoke it).

**Root cause:** The orchestrator's prompt to the Tester said `pip install -e .` without specifying environment isolation. The Tester agent used `uv pip install -e . --python python3.14` which resolved to the global venv. No `.python-version` file exists in the project. No project-local `.venv` was created.

---

### 4. No project-local venv or Python version pin

The project specifies `requires-python = ">=3.14"` in `pyproject.toml` but has:
- No `.python-version` file
- No project-local `.venv/` directory
- No `uv.lock` file

The dominion-cli package should be installable via `uv` in an isolated, reproducible project environment. Instead it was thrown into whatever Python environment happened to be active.

---

### 5. Unnecessary nested directory structure

**What was generated:**

```
dominion-cli/
  src/
    dominion_tools/
      __init__.py
      cli.py
      utils.py
      commands/
        __init__.py
        state.py
        agents.py
        ... (22 modules)
```

The `src/dominion_tools/` layout is the "src layout" pattern from Python packaging. For a project-internal CLI tool that will never be published to PyPI, this is unnecessary ceremony. The `src/` indirection adds nothing — it exists to prevent accidental imports of the local package during development, which is irrelevant for an internal tool.

A flat layout would have been simpler:

```
dominion-cli/
  dominion_tools/
    __init__.py
    cli.py
    ...
```

Or even simpler, since this is a project-internal tool:

```
dominion-cli/
  cli.py
  commands/
    ...
```

**Root cause:** The Developer agent defaulted to the "modern Python packaging best practice" without considering that this is an internal scaffolding tool, not a distributable library. The orchestrator's prompt did not constrain the structure.

---

### 6. "Testing" via Bash cat expressions

The Tester agent's approach to validation was to shell out via Bash:
- `dominion-cli --help` — check it doesn't crash
- `dominion-cli validate` — check it prints something
- `dominion-cli state resume` — check it prints something
- `dominion-cli agents list` — check it prints something

This is not testing. This is running the program and eyeballing the output. No assertions. No expected vs actual comparison. No error path coverage. No JSON schema validation. No edge cases. No regression safety net.

The cli-spec-delivery.md specified a proper test matrix with pass/fail verdicts per category. What was delivered was a vibes-based "it didn't crash" report dressed up as a test report with a table.

---

### 7. Hookify rules use fictional event types and spam every interaction

**What the user sees:** Every user prompt and every Read tool call prints:

```
[dominion-session-start]
If `.dominion/state.toml` exists, run `dominion-cli state resume`...
```

This fires on PreToolUse:Read, PostToolUse:Read, and UserPromptSubmit — continuously, not once.

**Root cause:** The init generated four hookify rule files with made-up event types:

| File | `event:` value | Problem |
|------|---------------|---------|
| `hookify.dominion-session-start.local.md` | `prompt` | Not a real hookify event. `pattern: .*` matches everything. |
| `hookify.warn-blocker-active.local.md` | `all` | Not a real hookify event. `pattern: .*` matches everything. |
| `hookify.dominion-session-end.local.md` | `stop` | Not a real hookify event. |
| `hookify.block-source-diving.local.md` | `file` | **This one is correct** — blocks reads to `.venv/`, `site-packages/`, etc. |

The orchestrator generated these hooks without checking hookify's actual event model. Hookify doesn't have `prompt`, `all`, or `stop` events. When the runtime encounters an unknown event type with a `.*` pattern, it falls back to matching broadly — attaching the rule to every tool call and prompt submission.

**The result:** Three of four hooks are noise generators. The session-start hook fires on every interaction instead of once. The blocker-check hook fires on every tool call. The session-end hook may never fire at all since `stop` isn't a real event.

**What should have happened:** The orchestrator should have read hookify's documentation (via context7 or the hookify:help skill) before generating hook rules. Alternatively, it should have used the `hookify:hookify` skill to create hooks through the proper guided workflow, which would have validated event types.

**Remediation:** Delete the three broken hooks. If session-start/end behavior is needed, implement it as a Claude Code hook in `.claude/settings.json` under the `hooks` key, which supports `PreToolUse`, `PostToolUse`, and `UserPromptSubmit` events with proper matching. Or use hookify correctly after reading its documentation.

---

### 8. Broken hooks drained tokens and accelerated context collapse

The three broken hooks didn't just produce visual noise — they were a direct contributor to the context window filling up during init, which caused the cascade failure (context compaction → Tester spawned from summary → no real tests written).

**How hooks cost tokens:** Each hook firing injects a system-reminder message into the conversation history. That message is re-sent with every subsequent API call as part of the accumulated context. It's not a one-time cost — it compounds.

**What was happening during init:**

| Hook | Fires on | Frequency during init |
|------|----------|----------------------|
| `dominion-session-start` (`event: prompt`, `pattern: .*`) | Every UserPromptSubmit + PreToolUse:Read + PostToolUse:Read | ~3x per Read call + 1x per user message |
| `warn-blocker-active` (`event: all`, `pattern: .*`) | Every single tool call | Every tool call in the main context |

**Estimated token damage:**

The init session had hundreds of tool calls. The Developer agent alone used 101, the Tester 36, plus the orchestrator's own reads, writes, edits, and bash calls — conservatively 200+ tool calls in the main conversation.

- `warn-blocker-active` at ~40 tokens per injection x 200 firings = ~8,000 tokens
- `dominion-session-start` at ~50 tokens per injection x 150 firings = ~7,500 tokens
- **Total injected: ~15,500 tokens of hook spam**

But the real cost is quadratic: those 15,500 tokens become part of the conversation history and are re-sent with every subsequent API call. Each new turn pays the tax of all previous hook injections. The more calls the session makes, the more expensive each subsequent call becomes.

**This accelerated context compaction.** The session ran out of context and had to be continued. The ~15K tokens of hook noise pushed the context window to its limit faster. Context compaction meant the orchestrator lost the Developer agent's task ID and spawned the Tester based on a summary rather than actual task completion — a cascade failure where one mistake (broken hooks) amplified another (premature Tester launch).

**Root cause:** Same as finding #7 — the hooks were generated with fictional event types. The token cost was an unintended consequence of the hooks firing on every interaction instead of being scoped correctly.

---

### 9. None of the generated files exist on disk

**This is the critical failure.** After the init declared success, the actual project directory contains only two files:

```
/home/privateer/Projects/secretariat/
  post-init-mortem.md    (written in this post-mortem session)
  secretariat-spec.md    (the original spec, pre-init)
```

Everything the init claimed to generate is gone:

| Artifact | Claimed generated | Actually exists |
|----------|------------------|-----------------|
| `.dominion/` (config, agents, specs, state) | Yes | No |
| `.claude/agents/*.md` (15 agent files) | Yes | No |
| `.claude/settings.json` (MCP permissions) | Yes | No |
| `.claude/hookify.*.local.md` (4 hook rules) | Yes | No |
| `.githooks/pre-commit` | Yes | No |
| `.githooks/commit-msg` | Yes | No |
| `CLAUDE.md` | Yes | No |
| `AGENTS.md` | Yes | No |
| `DOMINION.md` | Yes | No |
| `.gitignore` | Yes | No |
| `dominion-cli/` (24 Python files) | Yes | No |

**50+ files across 6 directories — zero persisted.**

The init process used subagents to generate files. Those subagents may have been running in isolated worktrees or temp contexts. The orchestrator never verified that files were written to the actual working directory. It read subagent reports ("I wrote file X"), set state flags (`cli_proven = true`, `validate_passed = true`), and declared success — all without checking whether any output existed in the real project.

The Tester agent claiming "71/71 commands pass" and the validate command reporting "11/11 checks passed" were both operating on phantom files that existed only in subagent contexts. The `dominion-cli` binary that was installed into the global venv (`/home/privateer/.venv/bin/dominion-cli`) may still reference source files that no longer exist.

**Root cause:** The orchestrator trusted subagent reports without filesystem verification. No step in the 14-step init protocol checks "do the files I generated actually exist in the project directory?"

---

## Timeline

1. Developer agent spawned as background task to generate dominion-cli CLI
2. Orchestrator proceeded with other init steps (CLAUDE.md, hooks, git hooks, .gitignore, AGENTS.md, DOMINION.md)
3. Context window filled up; session was compacted
4. In the continued session, the orchestrator checked that `cli.py` exists and assumed Developer was done
5. Tester agent spawned — ran 71 `--help` checks and 5 functional invocations via Bash
6. Orchestrator accepted the report, set `cli_proven = true` and `validate_passed = true`
7. Developer completion notification arrived *after* the Tester had already finished
8. Init declared complete
9. **Post-mortem discovery: none of the generated files exist in the actual project directory**

---

## What Needs to Happen

**The init must be re-run from scratch.** None of the generated output persisted. The project is in the same state it was before init: just `secretariat-spec.md`.

Specific items for a re-run:

1. **Re-run `/dominion:init`** — the entire 14-step process needs to execute again
2. **Verify file persistence after each step** — check files exist in the actual project directory, not just in agent reports
3. **Do not use background agents for file generation** — or if using them, verify output is in the correct directory before proceeding
4. **Create project-local venv** with `uv venv --python 3.14` and `.python-version` file before installing anything
5. **Write actual pytest tests** per cli-spec-delivery.md Step 4 — no bash smoke tests
6. **Use hookify correctly** — read its event model before generating rules, or use the `hookify:hookify` skill
7. **Flatten dominion-cli structure** — no unnecessary `src/` layout for an internal tool
8. **Uninstall phantom from global venv**: `uv pip uninstall dominion-cli` from `/home/privateer/.venv`

---

## Lessons for Future Init Runs

- Never spawn Tester before Developer's background task emits a completion signal
- Always create a project-local venv before installing anything
- Subagent prompts must match the reference spec verbatim — paraphrasing loses requirements
- "It runs without crashing" is not a test suite
- Context compaction is a known risk for multi-step protocols — checkpoint state explicitly before compaction
- Never generate hookify rules without reading hookify's event model first — use the hookify:hookify skill or context7 lookup
- Three out of four generated hooks were broken — a 75% failure rate on a governance feature is worse than not having it
- **Always verify files exist on disk after generation** — subagent reports are not filesystem proof
- An init that generates 50+ files and persists zero of them is worse than doing nothing — it wastes tokens and creates false confidence
