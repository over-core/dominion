# CLI Spec Delivery & Proving Ground

## Step 1: Deliver CLI Spec

Copy `@templates/cli-spec.toml` to `.dominion/specs/cli-spec.toml` in the target project.

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
Validate dominion-tools against .dominion/specs/cli-spec.toml.

For each command in the spec:
1. Run the command (it should work against the .dominion/ files just created)
2. Verify output format matches the behavior description
3. Verify --json flag produces valid JSON
4. Report pass/fail per command

Expected: all 8 commands pass.
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
