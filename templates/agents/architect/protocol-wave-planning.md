# Wave Planning Protocol

## Wave Structure

Waves are parallel execution units. Tasks within a wave can run simultaneously. Tasks in wave N+1 depend on wave N.

1. **Topological sort** tasks by `depends_on` field into waves
2. **Co-locate coupled modules** — tasks touching related files belong in the same wave
3. **Check file ownership conflicts** — no two tasks in the same wave should modify the same files
4. **Critical path tasks** get `critical_path: true` — these determine minimum phase duration

## Plan.toml Format

Each task in plan.toml must have:
- `id` — unique within phase (e.g., "01-01")
- `title` — concise task description
- `wave` — wave number (1-based)
- `assigned_to` — agent role
- `model` — model override if needed (default from agent TOML)
- `depends_on` — list of task IDs
- `file_ownership` — files this task may modify
- `token_estimate` — estimated tokens for this task
- `acceptance_criteria` — list of verifiable criteria
- `verify_command` — command to verify completion (optional)
- `knowledge_refs` — knowledge files relevant to this task (optional)

## Wave Transitions

Generate handoff notes between waves documenting:
- What wave N produced
- What wave N+1 needs from wave N
- Any state changes or interface contracts
