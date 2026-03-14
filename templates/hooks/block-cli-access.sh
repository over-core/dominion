#!/usr/bin/env bash
# Dominion governance hook: block legacy dominion-cli access.
# Agents must use mcp__dominion__* tools instead.
#
# PreToolUse hook for Bash tool.
# Exit 2 = block, exit 0 = allow.
set -euo pipefail

# Tool input is passed via stdin as JSON
input=$(cat)

# Extract command from tool input
command=$(echo "$input" | jq -r '.command // empty')

if [ -z "$command" ]; then
    exit 0
fi

# Block if command starts with dominion-cli
if echo "$command" | grep -qE '^dominion-cli\b' ; then
    echo "Use mcp__dominion__* tools. CLI access is for humans only." >&2
    exit 2
fi

exit 0
