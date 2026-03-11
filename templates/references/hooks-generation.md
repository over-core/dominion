# Hookify Governance Rules

Generate hookify rules using `/hookify:writing-rules` with the exact specifications below.

## Prerequisites

Check hookify is installed: look for `/hookify` in available skills.
If NOT installed: STOP. "Install hookify: /plugin marketplace install hookify"

## Rule 1: Block Source Diving

Invoke `/hookify:writing-rules` and request a rule with these exact parameters:
- **Name:** block-source-diving
- **Event:** PreToolUse on Read tool
- **Pattern:** file path matches `(node_modules|\.venv|vendor|site-packages|dist-packages|\.cargo/registry)`
- **Action:** block
- **Message:**
  BLOCKED: Do not read library source code.
  Use documentation fallback chain from dominion.toml [documentation.sources].
  Terminal: Stop and ask the user.

## Rule 2: Warn on Active Blocker

Invoke `/hookify:writing-rules` and request a rule with these exact parameters:
- **Name:** warn-blocker-active
- **Event:** PreToolUse on Edit and Write tools
- **Pattern:** any file path
- **Condition:** `.dominion/state.toml` exists AND contains `status = "blocked"`
- **Action:** warn
- **Message:**
  WARNING: A blocker is active. Run: dominion-cli state blockers

## Rule 3: Session Start — Auto-Resume

Invoke `/hookify:writing-rules` and request a rule with these exact parameters:
- **Name:** dominion-session-start
- **Event:** UserPromptSubmit (first prompt only)
- **Condition:** `.dominion/state.toml` exists
- **Action:** command that runs `dominion-cli state resume`
- **Behavior:** lightweight, read-only, skip if no .dominion/ directory

## Rule 4: Session End — Auto-Checkpoint

Invoke `/hookify:writing-rules` and request a rule with these exact parameters:
- **Name:** dominion-session-end
- **Event:** Stop
- **Condition:** `.dominion/state.toml` exists
- **Action:** command that runs `dominion-cli state checkpoint`
- **Behavior:** non-blocking, fail silently

## Verification

After creating each rule, verify:
1. Read the generated `.claude/hookify.{name}.local.md` file
2. Check the YAML frontmatter has a valid `event:` field
3. Valid events: PreToolUse, PostToolUse, UserPromptSubmit, Stop (consult hookify docs)
4. If event is invalid: delete the rule file and re-invoke /hookify:writing-rules
