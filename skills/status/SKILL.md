---
name: status
description: Display project status dashboard — current phase, pipeline progress, blockers, backlog
---

<IMPORTANT>
This skill is read-only. It does not modify any state.
</IMPORTANT>

**Step 1: Check Dominion project**

Use Glob to check if `.dominion/dominion.toml` exists.

If not found: print "Not a Dominion project. Run /dominion:init first." and stop.

**Step 2: Build dashboard**

Follow [dashboard.md](references/dashboard.md)

**Step 3: Present dashboard**

Print the assembled dashboard to the user. No follow-up actions unless the user asks.
