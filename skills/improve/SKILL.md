---
name: improve
description: Add project-specific knowledge via conversation — standalone, not a pipeline step
---

# /dominion:improve

Standalone command to add or update project-specific knowledge files.

## Flow

1. Ask: "What knowledge would you like to capture? Examples: API patterns, deployment details, domain conventions."
2. Read existing knowledge index: `.dominion/knowledge/index.toml`
3. If topic exists: show current content, ask what to update
4. If new topic: suggest topic name and tags
5. Tags must be from fixed set: discuss, research, plan, execute, review
   - These determine which pipeline steps receive this knowledge
6. User provides or confirms content
7. Call `mcp__dominion__save_knowledge(topic, content, tags, summary)`
8. Confirm: "Knowledge saved: {topic} (tags: {tags}). Will be included in {step} CLAUDE.md briefs."

## Review Existing Knowledge

If user asks to review or list knowledge:
1. Read `knowledge/index.toml` → list all entries (topic, summary, tags)
2. For each entry, offer: update content / update tags / delete
3. To delete: remove the .md file and the index entry
