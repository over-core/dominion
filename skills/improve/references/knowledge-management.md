# Knowledge Management

Manage the three-tier knowledge system during the improve step.

## Step 1: Scan for Knowledge-Worthy Items

Read all SUMMARY.md files for the current phase: `.dominion/phases/{N}/summaries/task-*.md`

Look for:
- **Recurring gotchas**: same friction reported by multiple tasks
- **Key decisions**: design choices with lasting impact (from Decisions Made sections)
- **Discovered patterns**: effective approaches that should be documented
- **API/integration knowledge**: specific behaviors, workarounds, or quirks discovered

## Step 2: Create or Update Knowledge Files

For each knowledge-worthy item:

1. Check if a relevant knowledge file already exists in `.dominion/knowledge/`
2. If yes: append the new information to the existing file
3. If no: create a new file in `.dominion/knowledge/` with a descriptive name (e.g., `database-gotchas.md`, `api-patterns.md`)

Knowledge file format:
```markdown
# {Topic}

## {Subtopic or Source Phase}
- {Specific knowledge item}
- {Specific knowledge item}
```

Keep entries concise — one line per item. These are reference material, not prose.

## Step 3: Update Knowledge Index

Read `.dominion/knowledge/index.toml` (create from [knowledge-index.toml](../../../templates/schemas/knowledge-index.toml) if not exists).

For each new or updated knowledge file:
1. If file already has an index entry: update the `summary` field with current content
2. If file is new: add a new `[[entries]]` entry with:
   - `file` = filename
   - `hot` = true (default for new entries — demote later if MEMORY.md is crowded)
   - `priority` = next available priority number
   - `summary` = condensed version (2-5 bullet points)
   - `tags` = relevant topic tags
   - `source_phase` = current phase number

## Step 4: Budget Management

Count total lines that would be in MEMORY.md from all `hot = true` entries:
- Current state section: ~5 lines
- Documentation chain: ~4 lines
- Each hot entry's summary: count lines
- Pointer section for non-hot files: ~1 line per file

If total exceeds `memory_budget_lines` (200):
1. Identify lowest-priority hot entries
2. Candidates for demotion: entries from older phases with no recent references, entries about resolved issues
3. Set `hot = false` for demoted entries
4. Present demotions to user: "{file} demoted from hot cache — still available on demand"

## Step 5: Sync

After all index changes are made, the improve skill's Step 5 will run `dominion-tools knowledge sync` to rebuild MEMORY.md.

## Rules

- Never delete knowledge files — only demote from hot cache
- Never touch global MEMORY.md (~/.claude/memory/MEMORY.md) — that's the user's space
- Write to project MEMORY.md path only (~/.claude/projects/<hash>/memory/MEMORY.md)
- Knowledge files are committed to git — they travel with the repo
