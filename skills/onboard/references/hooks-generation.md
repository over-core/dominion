# Hookify Governance Rules

Generate hookify rules using `/hookify:writing-rules` with the exact specifications below.
Native Claude Code hooks (Rules 2 & 3) are generated in settings-generation.md, not here.

## Prerequisites

Check hookify is installed: look for `/hookify` in available skills.
If NOT installed: STOP. "Install hookify: /plugin marketplace install hookify"

## Rule 1: Block Source Diving (hookify)

Invoke `/hookify:writing-rules` and request a rule with these exact parameters:
- **Name:** block-source-diving
- **Event:** all (must intercept Read tool, which `file` event does not cover)
- **Condition:** tool is Read AND file path matches library directories
- **Pattern:** file path matches `(node_modules|\.venv|vendor|site-packages|dist-packages|\.cargo/registry)`
- **Action:** block
- **Message:**
  BLOCKED: Do not read library source code.
  Use documentation fallback chain from dominion.toml [documentation.sources].
  Terminal: Stop and ask the user.

## Rule 2: Warn on Active Blocker (native hook)

**Not generated here.** This rule requires reading `.dominion/state.toml` content at runtime, which hookify conditions cannot express. Generated as a native Claude Code hook in [settings-generation.md](settings-generation.md) under the Hooks section.

## Rule 3: Session Start — Auto-Resume (native hook)

**Not generated here.** This rule requires checking `.dominion/state.toml` existence at runtime, which hookify conditions cannot express. Generated as a native Claude Code hook in [settings-generation.md](settings-generation.md) under the Hooks section.

## Rule 4: Session End — Auto-Checkpoint (hookify)

Invoke `/hookify:writing-rules` and request a rule with these exact parameters:
- **Name:** dominion-session-end
- **Event:** stop
- **Action:** command that runs `dominion-cli state checkpoint`
- **Behavior:** non-blocking, fail silently. The CLI command exits gracefully if no `.dominion/` directory exists.

## Verification

After creating each hookify rule, verify:
1. Read the generated `.claude/hookify.{name}.local.md` file
2. Check the YAML frontmatter has a valid `event:` field
3. Valid hookify events: `bash`, `file`, `stop`, `prompt`, `all`
4. If event is invalid: delete the rule file and re-invoke `/hookify:writing-rules`

Expected hookify files (2):
- `.claude/hookify.block-source-diving.local.md`
- `.claude/hookify.dominion-session-end.local.md`

Native hooks (Rules 2 & 3) are verified as part of settings verification, not here.
