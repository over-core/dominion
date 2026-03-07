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

## Implementation

Use the hookify skill/API to create these rules. Store rule definitions
in `.claude/hooks/` following hookify conventions.
