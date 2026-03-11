# Claim Plan Presentation

Present the merge plan to the user as a clear diff-based summary.

## Plan Structure

Present in this order:

### 1. Compatible (auto-merge)

```
Will preserve (no changes needed):
  ✓ CLAUDE.md — {N} user-written sections kept intact
  ✓ .claude/agents/{name}.md — kept as custom agent
  ✓ .claude/settings.json — all permissions preserved
  ✓ .githooks/ — existing hooks preserved
```

### 2. Additions

```
Dominion will add:
  + .dominion/                    Project config directory
  + .dominion/agents/*.toml       {N} agent TOML configs
  + .dominion/state.toml          Session state tracking
  + .dominion/style.toml          Code style conventions
  + .dominion/roadmap.toml        Milestones and phases
  + .dominion/knowledge/          Knowledge layer
  + .dominion/specs/cli-spec.toml CLI command spec
  + .claude/agents/*.md           {N} new agent files
  + AGENTS.md                     Agent roster
  + dominion-cli/               CLI tool
```

### 3. Merges

For CLAUDE.md, show a section-level diff:
```
CLAUDE.md changes:
  = [Project] section — kept as-is (your content)
  = [Git Conventions] — kept as-is (your content)
  + [Agent System] — new Dominion section
  + [Documentation] — new Dominion section
  + [Quality Gates] — new Dominion section
  + [Decision Framework] — new Dominion section
```

### 4. Conflicts (if any)

Present each conflict with options as described in conflict-detection.md.

### 5. Reduced Wizard

After plan approval, run the reduced wizard:
```
Some questions still need your input:

  Direction: maintain / improve / restructure? (can't detect intent)
  Roadmap: What's the first milestone?
  Autonomy: Enable auto mode? [Y/n]
  Experience level: beginner / intermediate / advanced?

  Skip auto-detected sections? [Y / full setup]
```

Auto-detected sections (from existing setup + codebase analysis):
- Code style → confirmed from existing CLAUDE.md rules and codebase
- Git workflow → confirmed from existing config and hooks
- Tools → confirmed from settings.json
- Taste → extracted from existing CLAUDE.md rules

## Approval

```
Apply this plan? [Y / modify / cancel]
```

- **Y**: proceed to execution
- **modify**: user specifies changes, re-present plan
- **cancel**: abort claim, no changes made
