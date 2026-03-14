# Bugfix Research Protocol

For bug investigation tasks:

1. **Reproduce** — understand the exact failure mode from the bug description
2. **Trace** — use serena to trace execution path from symptom to root cause:
   - `find_symbol` to locate relevant functions
   - `find_referencing_symbols` to trace call chains
   - `get_symbols_overview` to understand surrounding context
3. **Root cause analysis** — identify the specific code path causing the bug
   - Distinguish: is this a logic error, data error, timing error, or integration error?
4. **Impact analysis** — what else might be affected?
   - Same pattern used elsewhere? → Flag as systematic issue
   - External API involved? → Note version/contract constraints
5. **Fix hypothesis** — propose a fix approach with confidence level
6. **Write research.toml** — findings with root cause analysis, affected paths, fix hypothesis, regression risk
