---
name: validate
description: Check Dominion config integrity, agent consistency, and CLI completeness. Run after init or whenever you suspect config drift.
---

# /dominion:validate

Run all validation checks against the current Dominion setup.

## Pre-check

Verify `.dominion/` directory exists. If not:
```
No Dominion setup found. Run /dominion:init first.
```

## Run Checks

Follow [checks.md](references/checks.md) — execute each check in order.

## Report

Format output as:
```
dominion validate
  [PASS] TOML integrity
  [PASS] Agent TOML-MD consistency (8/8)
  [PASS] AGENTS.md roster complete
  [WARN] settings.json — missing optional: sequential-thinking
  [PASS] CLI completeness (8/8 commands)
  [PASS] Documentation fallback chain
  [PASS] CLAUDE.md exists
  [PASS] State consistency

  7 passed, 1 warning, 0 failed
```

## Exit Status

- All pass (with or without warnings): report success
- Any fail: report failures with actionable fix suggestions
