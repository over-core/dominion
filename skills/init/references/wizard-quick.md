# Quick Start Wizard

## Present Discovery Results

Format the summary as:

```
Analyzing project...

Detected:
  Languages:    [list with primary marked]
  Frameworks:   [list by category]
  Infrastructure: [list]
  Project shape: [monorepo/workspace/single]

MCPs installed:
  [INSTALLED] context7 (required)
  [INSTALLED] serena (required)
  [MISSING]   sequential-thinking (recommended)
  ...
```

## Recommend Setup

Cross-reference [registry.toml](../../../registry/registry.toml) against detected stack. Present:

```
Recommended setup:
  Agents:   8 core (Researcher, Architect, Developer, Tester, Reviewer, Advisor, Security Auditor, Secretary)
  MCPs:     [installed required + recommended]
  Git:      [detected or default: conventional commits, squash merge]
  Style:    [detected formatters + linters per language]
  Hooks:    source-diving prevention, documentation fallback enforcement
  Co-author: AI co-author trailers enabled (default)
```

## Missing MCP Warnings

For each missing required MCP:
```
WARNING: [name] is not installed.
  Purpose: [from registry]
  Impact:  [missing_consequence from registry]
  Install: [install_command from registry]
```

For missing recommended MCPs, list them as suggestions without blocking.

## Approval Prompt

```
Generate with these defaults? [Y / full setup / customize]
```

- **Y** — proceed directly to generation (Task 9 reference files)
- **full setup** — switch to [wizard-full.md](wizard-full.md)
- **customize** — ask: "Which sections would you like to customize?" and present:
  1. Direction (maintain/improve/restructure)
  2. Code style
  3. Git workflow
  4. Tools & MCPs
  5. Taste (do's and don'ts)

  Then run only the selected sections from [wizard-full.md](wizard-full.md), using defaults for the rest.
