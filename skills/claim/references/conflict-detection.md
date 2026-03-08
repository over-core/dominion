# Claim Conflict Detection

Cross-reference existing setup against Dominion's methodology. Categorize everything.

## Conflict Categories

### Compatible (auto-merge)

Artifacts that can coexist without conflict:
- User-written CLAUDE.md rules → preserve alongside Dominion sections
- Custom agents with unique roles → keep as additional agents
- MCP permissions → extend, never reduce
- User hooks → keep alongside Dominion hooks
- PR templates → preserve existing
- Git hooks → preserve existing

### Conflicting (user decides)

Artifacts where Dominion and existing setup disagree:
- **Orchestration conflict**: GSD/Conductor pipeline vs Dominion pipeline. Present both, user picks one or uses Dominion for some phases and existing for others.
- **Agent overlap**: existing "reviewer" agent vs Dominion's Reviewer. Options: replace with Dominion version, keep existing, merge instructions.
- **Convention conflict**: existing CLAUDE.md says "use tabs" but detected style is spaces. Present both, user decides.
- **Hook conflict**: existing hook blocks an action that Dominion hooks expect to succeed.

For each conflict, present:
```
CONFLICT: {description}
  Existing: {what's currently configured}
  Dominion: {what Dominion would set up}
  Options:
    1. Keep existing
    2. Use Dominion version
    3. Merge (where possible)
  Your choice: [1/2/3]
```

### Missing (Dominion adds)

Artifacts that don't exist yet — Dominion creates them:
- `.dominion/` directory structure
- Agent TOML configs (`.dominion/agents/*.toml`)
- State tracking (`.dominion/state.toml`)
- Roadmap (`.dominion/roadmap.toml`)
- Style config (`.dominion/style.toml`)
- Knowledge layer (`.dominion/knowledge/`)
- CLI spec (`.dominion/specs/cli-spec.toml`)

## Orchestration Plugin Handling

If GSD or Conductor detected:
1. Do NOT recommend removing them
2. Present clear comparison: "GSD handles X, Dominion handles Y"
3. If user keeps both: configure Dominion to skip conflicting steps
4. If user switches to Dominion: preserve GSD/Conductor artifacts for reference but deactivate

## Output

Produce three lists:
- `compatible`: artifacts to auto-merge (no user input needed)
- `conflicting`: artifacts requiring user decision (with options)
- `missing`: artifacts Dominion will create
