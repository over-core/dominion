# Hookify Governance Rules

Generate hookify rules for documentation fallback chain enforcement.

## Rule 1: Block Source Diving

Prevent agents from reading library source code instead of using documentation.

Create a hookify rule that blocks Read tool calls to paths matching:
- `~/.cargo/registry/*`
- `node_modules/*`
- `.venv/lib/*`
- `vendor/*`
- `site-packages/*`
- Any path containing `/dist-packages/`

Block message:
```
BLOCKED: Do not read library source code for API learning.
Use the documentation fallback chain:
{list from dominion.toml [documentation.sources]}
Terminal: Stop and ask the user.
```

## Rule 2: Warn on Missing Dominion State

If `.dominion/state.toml` exists but position.status = "blocked":
Warn on any code-modifying tool call:
```
WARNING: A blocker is active. Check: dominion-tools state blockers
```

(This rule is informational in v0.1 — becomes enforcement in v0.2+)

## Rule 3: Session Start — Auto-Resume

Hook type: `UserPromptSubmit` (fires on first user message of a session)

Create a hookify rule that runs on the first prompt of each session:

Behavior:
1. Check if `.dominion/state.toml` exists — if not, skip
2. Run `dominion-tools state resume` to get current position
3. Check for stale locks: if `lock.locked_at` is older than `lock.expires_after_hours`, clear the lock
4. Check `.dominion/signals/` for active blocker files — count them
5. Present status line:
   ```
   Dominion: Phase {N} "{title}", step {step}. {blocker_count} blockers. {backlog_count} backlog items.
   ```
6. If blocker_count > 0: append "Run /dominion:status for details."
7. If step = "idle" and phase = 0: "Dominion initialized. Run /dominion:orchestrate to start."

Skip conditions:
- No `.dominion/` directory (not a Dominion project)
- No `state.toml` (init not complete)

Implementation note: This hook should be lightweight — read state.toml and signals directory, format output. Do NOT run expensive commands or modify state.

## Rule 4: Session End — Auto-Checkpoint

Hook type: `Stop` (fires when session ends)

Create a hookify rule that runs on session end:

Behavior:
1. Check if `.dominion/state.toml` exists — if not, skip
2. Run `dominion-tools state checkpoint`
3. This updates `position.last_session` and clears expired locks

Skip conditions:
- No `.dominion/` directory
- No `state.toml`

Implementation note: Must be non-blocking and fast. Do not prompt user. If checkpoint fails, fail silently — session end should never block.

## Implementation

Check if the `hookify` plugin is installed (look for `/hookify` in available skills).

**If hookify is installed (preferred):**

Use `/hookify:writing-rules` to create each rule as a `.claude/hookify.{name}.local.md` file:

- Rule 1 → `hookify.block-source-diving.local.md` with `event: file`, conditions on `file_path` matching library paths, `action: block`
- Rule 2 → `hookify.warn-blocker-active.local.md` with `event: bash` + `event: file`, condition checking state.toml blocker status, `action: warn`
- Rule 3 → `hookify.dominion-session-start.local.md` with `event: prompt`, inline `dominion-tools state resume`
- Rule 4 → `hookify.dominion-session-end.local.md` with `event: stop`, inline `dominion-tools state checkpoint`

Hookify provides declarative markdown rules with regex pattern matching, conditions, and warn/block actions. The `/hookify:writing-rules` skill documents the exact YAML frontmatter format, condition operators, and pattern syntax.

**If hookify is NOT installed:**

STOP. Tell the user:
```
Hookify plugin is required for governance hook generation.
Install: /plugin marketplace install hookify
Then re-run /dominion:init to generate hooks.
```

Do not attempt to write native hooks manually — without hookify's rule format and pattern matching documentation, the hooks will be malformed.
