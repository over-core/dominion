# Signal Protocol

How Developer agents communicate blockers and warnings during execution.

## Signal Types

### Warning
FYI only — does not halt execution.

Raise when:
- Something unexpected but non-blocking was encountered
- A potential issue was noticed outside your file ownership
- An assumption seems shaky but doesn't prevent your task

```bash
dominion-tools signal warning --task {id} --message "{description}"
```

### Task Blocker
Your task halts, other wave tasks continue.

Raise when:
- You cannot complete your task due to a missing dependency, broken API, or failed assumption
- The issue is confined to your task and does not affect other wave tasks

```bash
dominion-tools signal blocker --level task --task {id} --reason "{description}"
```

### Wave Blocker
All tasks in the current wave halt.

Raise when:
- A shared resource (database schema, API contract, shared config) is broken
- Your discovery affects other tasks in the same wave
- A file ownership conflict was detected at runtime

```bash
dominion-tools signal blocker --level wave --task {id} --reason "{description}"
```

### Phase Blocker
Entire phase pauses — requires human intervention.

Raise when:
- A fundamental assumption is false (e.g., a required API does not exist)
- A security or data integrity issue was discovered
- The phase goal itself may need rethinking

```bash
dominion-tools signal blocker --level phase --task {id} --reason "{description}"
```

## After Signaling a Blocker

1. **Write a partial SUMMARY.md** with what was completed, what blocked, and why
2. **Commit WIP**: `git add -A && git commit -m "wip: task {id} blocked — {short reason}"`
3. **Halt**: stop working, do not attempt workarounds

## Signal File Format

Signal files are TOML, stored in `.dominion/signals/`:

```toml
type = "blocker"           # or "warning"
level = "wave"             # task | wave | phase (blockers only)
task = "02-03"
reason = "Shared auth config format changed upstream"
raised_at = "2025-01-15T10:30:00Z"
```

File naming: `blocker-{task-id}.toml` or `warning-{task-id}-{seq}.toml`
