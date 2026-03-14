#!/usr/bin/env bash
# Dominion governance hook: verify agent called agent_submit before stopping.
#
# SubagentStop hook. Checks state.toml for submission record.
# Returns systemMessage warning if agent didn't submit work.
# Exit 0 always (advisory, not blocking).
set -euo pipefail

# Find .dominion/state.toml relative to current directory
state_file=""
dir="$(pwd)"
while [ "$dir" != "/" ]; do
    if [ -f "$dir/.dominion/state.toml" ]; then
        state_file="$dir/.dominion/state.toml"
        break
    fi
    dir="$(dirname "$dir")"
done

if [ -z "$state_file" ]; then
    exit 0
fi

# Check if agent submission is recorded in state
# Look for a recent submission timestamp (within last 60 seconds would be ideal,
# but simple presence check is sufficient for the hook)
if grep -q 'last_submission' "$state_file" 2>/dev/null; then
    exit 0
fi

# Agent may not have submitted — warn the orchestrator
echo '{"systemMessage": "Warning: The agent may not have called agent_submit(). Check phase_status() to verify work was recorded."}'
exit 0
