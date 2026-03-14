#!/usr/bin/env bash
# Dominion governance hook: block direct .dominion/ file access.
# Agents must use mcp__dominion__* tools instead.
#
# PreToolUse hook for Read|Edit|Write tools.
# Exit 2 = block, exit 0 = allow.
set -euo pipefail

# Tool input is passed via stdin as JSON
input=$(cat)

# Extract file_path from tool input
file_path=$(echo "$input" | jq -r '.file_path // empty')

if [ -z "$file_path" ]; then
    exit 0
fi

# Block if path contains .dominion/ and is a data file (TOML or agent memory)
if echo "$file_path" | grep -q '\.dominion/' ; then
    if echo "$file_path" | grep -qE '\.(toml|json)$' ; then
        echo "Use mcp__dominion__* tools. Direct .dominion/ access is not allowed." >&2
        exit 2
    fi
fi

exit 0
