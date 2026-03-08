---
name: study
description: Evaluate an existing plugin's skills/agents, security-review them, and produce Dominion-native artifacts refined beyond the originals.
---

# /dominion:study

Internalize external plugins into Dominion-native artifacts.

## Flag Parsing

- `<plugin>`: Required. The plugin name or path to study.
- `--skill <name>`: Study one specific skill from the plugin
- `--agent <name>`: Study one specific agent from the plugin
- No skill/agent flag: study the entire plugin

## Pre-check

1. Read `.dominion/dominion.toml` — verify project is initialized
2. Locate the plugin: check installed plugins list, resolve path
3. If plugin not found: "Plugin '{name}' not found. Is it installed?"

## Step 1: Read & Assess

Follow `@references/inventory-assessment.md`

Produces: inventory of skills/agents/hooks, security findings, benefit assessment per item.

## Step 2: Kill Gate

Follow `@references/kill-gate.md`

For each assessed item: pass or kill. Items that don't pass are dropped — no further processing.

## Step 3: Recreate

Follow `@references/recreation.md`

For each item that passed the kill gate: create Dominion-native version.

## Post-study

1. Present summary: "{N} items studied, {passed} passed kill gate, {created} artifacts created"
2. List created artifacts with paths
3. Run `dominion-tools agents generate` if any agents were created
4. Commit all new files
5. Inform user: "The studied plugin can now be uninstalled if desired."
