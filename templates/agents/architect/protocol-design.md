# Design Protocol

For greenfield features, refactors, and new-feature phase types:

1. **Read research.toml** — internalize findings (severity-sorted), assumptions (unverified first), opportunities, specialist referrals
2. **Search EchoVault** for prior planning decisions, wave grouping pitfalls, task splitting patterns
3. **Apply WBS** (Work Breakdown Structure): phase goal → deliverables → atomic tasks
   - Each task = one agent, one commit boundary, one responsibility
   - Scope each task with `file_ownership` list
4. **Specialist routing** — check specialist referrals from findings:
   - Specialist exists in `.dominion/agents/` → assign to specialist
   - Not exists → assign to Developer with referral in `knowledge_refs`
   - Default: Developer. Config/generation: Secretary.
5. **Dependency analysis** (CPM-lite): build DAG, identify critical path, flag tasks that can't slip
6. **Wave grouping**: topological sort into waves, co-locate coupled modules, check file ownership conflicts
7. **Budget validation**: read `max_tokens_per_task`, estimate per task, split if >80% budget
8. **Write plan.toml** via direct file write to phase directory
9. **Record ADRs** for decomposition trade-offs and routing decisions via `save_decision`
