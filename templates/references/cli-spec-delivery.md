# CLI Spec Delivery & Proving Ground

## Step 1: Deliver CLI Spec

Copy [cli-spec.toml](../cli-spec.toml) to `.dominion/specs/cli-spec.toml` in the target project.

## Step 2: Determine CLI Language

From discovery results:
- Use the primary detected language
- If multi-language project, recommend the primary language by file count
- Ask user to confirm: "CLI will be implemented in {language}. OK? [Y / change]"

Map language to CLI framework recommendation:
- Rust → clap
- Python → click + rich (or typer if detected)
- TypeScript → commander (or yargs if detected)
- Go → cobra (or standard flag package)
- Java → picocli
- Ruby → thor
- PHP → symfony/console
- Other → user's choice

## Step 3: Spawn Developer Agent

Spawn a Developer agent with this prompt:

```
Read .dominion/specs/cli-spec.toml and implement all commands as a CLI tool.

Language: {detected language}
Framework: {recommended CLI framework}
Write to: dominion-tools/

Requirements:
- Read CLAUDE.md for code conventions
- Implement every command in cli-spec.toml [commands]
- Each command reads the TOML files specified in its 'reads' field
- Each command produces output matching its 'behavior' description
- Support --json flag for machine-readable output on all commands
- Include a --help flag with descriptions from the spec
- Follow the project's pre-commit checks

Do NOT:
- Add commands not in the spec
- Add configuration files not needed
- Over-engineer — this is a ~200-500 line CLI tool
```

## Step 4: Spawn Tester Agent

After Developer completes, spawn a Tester agent:

```
Write a test suite and validate dominion-tools against .dominion/specs/cli-spec.toml.

Write tests to: dominion-tools/tests/
Use the project's test runner and conventions from CLAUDE.md.

### Functional Tests (per command)

For each command in cli-spec.toml [commands]:
1. Run the command against the .dominion/ files just created
2. Verify output format matches the behavior description
3. Verify --json flag produces valid, parseable JSON
4. Verify --json output contains expected keys matching the command's reads/behavior

### Error Handling Tests

For each command, test graceful failure:
- Missing .dominion/ directory entirely → clear error, not a stack trace
- Missing individual TOML files the command reads → specific error naming the missing file
- Malformed TOML (invalid syntax) → parse error with file path, not crash
- Empty TOML files (valid but no data) → sensible defaults or empty output, not crash

### Edge Case Tests

- `agents list` with zero agent files → empty table, no crash
- `agents show` with nonexistent role → "not found" message listing available roles
- `state resume` when state.toml has phase = 0 → "no active phase" message
- `validate` with intentionally broken setup → reports failures, doesn't falsely pass
- `knowledge sync` with empty index.toml → creates minimal MEMORY.md

### CLI UX Tests

- `--help` on every command and on the root → prints usage, exits 0
- Unknown command → helpful error suggesting valid commands, exits non-zero
- Exit codes: 0 for success, non-zero for failure
- No command (bare `dominion-tools`) → prints help or status summary

### JSON Schema Consistency

For every command that supports --json:
- Output is valid JSON (parseable)
- Top-level structure is an object (not array, not bare value)
- Keys use snake_case consistently
- Empty results return empty objects/arrays, not null

### Test Report

After running all tests, produce a summary:
  dominion-tools test results
    [PASS] validate — functional (3/3)
    [PASS] validate — error handling (4/4)
    [PASS] state resume — functional (2/2)
    ...
    [FAIL] agents show — edge case: nonexistent role (expected exit 1, got 0)

    N passed, M failed

Expected: all tests pass.
```

## Step 5: Handle Failures

If Tester reports failures:
1. Feed failure details back to Developer agent
2. Developer fixes (max 2 retries)
3. Re-run Tester

If still failing after retries:
- Report to user: "CLI proving ground failed on {N} commands. Details: {failures}"
- This is v0.1's canary — valuable feedback for tuning agent templates
- Ask user: "Continue with partial CLI? [Y / manual fix / abort]"
