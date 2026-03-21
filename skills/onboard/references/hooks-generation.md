# Hooks Generation (v0.3.1)

Generate hook scripts in `.claude/hooks/` and register in settings.local.json.

v0.3.0 change: agents CAN read `.dominion/` (CLAUDE.md, knowledge). Only WRITES are blocked.
v0.3.1 change: fix hook response format to official API (exit code 2 + stderr for blocking, plain stdout for context). Add secret detection, sensitive file alerts, precompact state preservation.

## Hook 1: Block .dominion/ Writes

Prevents agents from writing to `.dominion/` directly. Must use MCP tools.

Write `.claude/hooks/block-dominion-writes.sh`:
```bash
#!/bin/sh
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""')
case "$FILE" in
  */.dominion/*|*/.dominion)
    echo "Cannot write to .dominion/ directly. Use MCP tools: submit_work(), save_knowledge(), signal_blocker()." >&2
    exit 2
    ;;
esac
exit 0
```

Exit code 2 = block. Stderr content is fed to Claude as the denial reason.

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
  echo "Dominion pipeline active: phase ${PHASE}, step ${STEP}, status ${STATUS}. Run /dominion:status for details."
fi
exit 0
```

Plain stdout on exit 0 is automatically injected as context into the conversation.

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
    echo "CONTEXT BUDGET: Reading source file (~2000 tokens). Consider Serena find_symbol/get_symbols_overview (~50 tokens) unless you need the entire file."
    ;;
esac
exit 0
```

Plain stdout on exit 0 passes context to Claude without blocking.

Register as PreToolUse:Read hook. Does NOT block — just reminds.

## Hook 4: Secret Detection (always generated)

Scans user prompts for leaked API keys and credentials. Blocks submission if found.

Write `.claude/hooks/detect-secrets.sh`:
```bash
#!/bin/sh
INPUT=$(cat)
CONTENT=$(echo "$INPUT" | jq -r '.prompt // ""')
if echo "$CONTENT" | grep -qE '(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36,}|AKIA[A-Z0-9]{16}|-----BEGIN (RSA |EC )?PRIVATE KEY)'; then
  echo "Potential secret detected in prompt. Remove API keys, tokens, or private keys before submitting." >&2
  exit 2
fi
exit 0
```

Patterns: Anthropic/OpenAI keys (sk-), GitHub tokens (ghp_), AWS access keys (AKIA), PEM private keys.

Register as UserPromptSubmit hook in settings.local.json.

## Hook 5: Sensitive File Alert (always generated)

Warns when reading files that likely contain credentials. Non-blocking.

Write `.claude/hooks/sensitive-file-alert.sh`:
```bash
#!/bin/sh
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')
case "$FILE" in
  *.env|*.env.*|*.key|*.pem|*.p12|*.pfx|*credentials*|*secrets*|*_secret*)
    echo "SENSITIVE FILE: ${FILE} may contain credentials. Do not include raw secrets in output or commits."
    ;;
esac
exit 0
```

Exit 0 = non-blocking. Stdout is injected as context so Claude is aware of sensitivity.

Register as PreToolUse:Read hook. When Serena is also detected, both sensitive-file-alert and prefer-serena go in the same Read matcher hooks array.

## Hook 6: PreCompact State Preservation (always generated)

Dumps pipeline state before context compaction so position survives compression.

Write `.claude/hooks/pre-compact.sh`:
```bash
#!/bin/sh
[ -f ".dominion/state.toml" ] || exit 0
echo "=== DOMINION PIPELINE STATE (preserved across compaction) ==="
echo ""
grep -E '^(phase|step|status|intent) = ' .dominion/state.toml 2>/dev/null | sed 's/^/  /'
echo ""
if [ -d ".dominion/phases" ]; then
  LATEST=$(ls -1d .dominion/phases/*/ 2>/dev/null | tail -1)
  if [ -n "$LATEST" ]; then
    echo "Latest phase dir: ${LATEST}"
    ls -1 "$LATEST" 2>/dev/null | head -5 | sed 's/^/  /'
  fi
fi
echo ""
echo "Resume with: /dominion:status or /dominion:orchestrate"
exit 0
```

Reads `[position]` table from state.toml (phase, step, status, intent). Shows latest phase directory contents. Plain stdout is preserved in compacted context.

Register as PreCompact hook in settings.local.json.

## Post-Generation

Make all hook scripts executable:
```bash
chmod +x .claude/hooks/*.sh
```

## NOT Generated (removed in v0.3.0)

- ~~hookify source-diving rule~~ — plugin paths don't match target project
- ~~block-dominion-access.sh (read blocking)~~ — agents now read .dominion/ freely
- ~~dominion-cli references~~ — CLI removed in v0.2.0
