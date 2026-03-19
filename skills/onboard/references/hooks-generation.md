# Hooks Generation (v0.3.0)

Generate hook scripts in `.claude/hooks/` and register in settings.local.json.

v0.3.0 change: agents CAN read `.dominion/` (CLAUDE.md, knowledge). Only WRITES are blocked.

## Hook 1: Block .dominion/ Writes

Prevents agents from writing to `.dominion/` directly. Must use MCP tools.

Write `.claude/hooks/block-dominion-writes.sh`:
```bash
#!/bin/sh
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""')
case "$FILE" in
  */.dominion/*)
    echo '{"decision":"block","reason":"Cannot write to .dominion/ directly. Use MCP tools: submit_work(), save_knowledge(), signal_blocker()."}'
    ;;
esac
exit 0
```

Register in settings.local.json:
```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Edit", "hooks": [{"type": "command", "command": ".claude/hooks/block-dominion-writes.sh"}]},
      {"matcher": "Write", "hooks": [{"type": "command", "command": ".claude/hooks/block-dominion-writes.sh"}]}
    ]
  }
}
```

## Hook 2: Session Start (auto-resume)

Outputs pipeline state for instant context recovery. Critical for ralph-loop.

Write `.claude/hooks/session-start.sh`:
```bash
#!/bin/sh
[ -f ".dominion/state.toml" ] || exit 0
PHASE=$(grep '^phase = ' .dominion/state.toml 2>/dev/null | head -1 | cut -d'"' -f2 || echo "00")
STEP=$(grep '^step = ' .dominion/state.toml 2>/dev/null | head -1 | cut -d'"' -f2 || echo "idle")
STATUS=$(grep '^status = ' .dominion/state.toml 2>/dev/null | head -1 | cut -d'"' -f2 || echo "ready")
if [ "$STEP" != "idle" ]; then
  echo "{\"systemMessage\":\"Dominion pipeline active: phase ${PHASE}, step ${STEP}, status ${STATUS}. Run /dominion:status for details.\"}"
fi
exit 0
```

Register as SessionStart hook in settings.local.json.

## Hook 3: Prefer Serena (conditional)

Only generate if Serena is detected in config.toml [tools].available.

Write `.claude/hooks/prefer-serena.sh`:
```bash
#!/bin/sh
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')
case "$FILE" in
  *.py|*.ts|*.js|*.tsx|*.jsx|*.rs|*.go|*.java|*.cpp|*.c|*.rb)
    echo '{"systemMessage":"CONTEXT BUDGET: Reading source file (~2000 tokens). Consider Serena find_symbol/get_symbols_overview (~50 tokens) unless you need the entire file."}'
    ;;
esac
exit 0
```

Register as PreToolUse:Read hook. Does NOT block — just reminds.

## Post-Generation

Make all hook scripts executable:
```bash
chmod +x .claude/hooks/*.sh
```

## NOT Generated (removed in v0.3.0)

- ~~hookify source-diving rule~~ — plugin paths don't match target project
- ~~block-dominion-access.sh (read blocking)~~ — agents now read .dominion/ freely
- ~~dominion-cli references~~ — CLI removed in v0.2.0
