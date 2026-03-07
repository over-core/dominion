# Agent Completion Signal Protocol

Any step that spawns agents must follow this protocol to survive context compaction.

## 1. Pre-Spawn Checkpoint

Before spawning agents, persist execution state to disk:

Write to `.dominion/execution.toml`:
```toml
[current]
step = "execute"        # which pipeline step
wave = 1                # wave number (if applicable)
spawned_at = "ISO8601"  # when agents were launched

[[current.agents]]
task_id = "01-01"
agent_role = "developer"
worktree = ".worktrees/dominion-01-01"
status = "spawned"      # spawned | complete | failed | stale
```

## 2. Agent Completion Marker

Each agent writes a marker on completion (BEFORE writing SUMMARY.md):

File: `.dominion/signals/complete-{task-id}.toml`
```toml
task_id = "01-01"
completed_at = "ISO8601"
exit_status = "success"  # success | failed | blocked
commit_hash = "abc123"   # last commit made
```

This is in ADDITION to SUMMARY.md (which is the detailed record).
The completion marker is the lightweight signal; SUMMARY.md is the full report.

## 3. Orchestrator Monitoring (Notification-Driven)

The orchestrator is an LLM — it cannot run a while loop. Monitoring is event-driven:

**Happy path (no compaction):**
1. Spawn all wave agents in parallel via Agent tool with `run_in_background: true`
2. Each agent writes `complete-{task-id}.toml` marker before returning its result
3. Orchestrator receives a **notification** when each background agent finishes
4. As each notification arrives: read the completion marker, update execution.toml
5. When all tasks in execution.toml are marked complete → proceed to verify + merge

**No polling needed in the happy path.** Notifications ARE the signal. Completion markers are the persistent safety net.

## 4. Compaction Recovery (Polling Fallback)

Background agents run as subprocesses — they **survive context compaction**. But the orchestrator loses its notification channel. After compaction:

1. Read `.dominion/execution.toml` — recover list of spawned agents
2. For each agent with status = "spawned":
   a. Check `.dominion/signals/complete-{task-id}.toml` — if exists, mark complete
   b. Check if worktree has commits on its branch (`git log dominion/{task-id}`) — if yes, agent made progress
   c. Check if SUMMARY.md exists — if yes, agent completed but marker was missed
   d. If none of the above: agent may still be running or was lost
3. For agents with no evidence of completion:
   - **Poll** for completion markers every **30 seconds** (agents are likely still running)
   - **Timeout** after 15 minutes of no new completions → mark remaining as "stale"
4. For stale agents: prompt user: "Agent for task {id} may have been lost. Re-spawn? [Y/n]"

## 5. Idempotent Re-Execution Guard

Before re-spawning a task:
1. If worktree branch has commits → agent made progress, ask user before re-spawning
2. If SUMMARY.md exists → agent completed, just mark as done
3. If completion marker exists → agent completed, mark as done
4. If nothing exists → safe to re-spawn

## 6. Cleanup

After all agents complete and merge:
- Delete completion markers: `rm .dominion/signals/complete-*.toml`
- Clear `[current]` section from execution.toml
- Keep execution.toml for the history record (append to [[history]])
