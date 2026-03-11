# CLI Installation

Install the pre-built dominion-cli from the Dominion plugin distribution.

## Prerequisites

1. Check `uv` is on PATH:
   ```bash
   uv --version
   ```
   If missing: STOP. Tell user:
   "uv is required. Install: https://docs.astral.sh/uv/getting-started/installation/"

## Install

1. Locate the plugin's cli/ directory:
   ```bash
   PLUGIN_CLI=$(ls -d ~/.claude/plugins/cache/dominion/dominion/*/cli/ 2>/dev/null | tail -1)
   ```
   If empty: STOP. "Dominion plugin installation not found."

2. Install dominion-cli as an isolated tool:
   ```bash
   uv tool install dominion-cli --from "$PLUGIN_CLI" --python 3.14
   ```

3. Verify installation:
   ```bash
   dominion-cli --version
   ```
   Expected: version matching plugin version.

4. Smoke test:
   ```bash
   dominion-cli --help
   dominion-cli validate --help
   dominion-cli validate --json    # verify JSON output mode (primary agent interface)
   dominion-cli agents list --json
   ```

5. Copy cli-spec.toml to project:
   ```bash
   cp {plugin_path}/templates/cli-spec.toml .dominion/specs/cli-spec.toml
   ```

## Upgrade (for existing projects)

If dominion-cli is already installed but version is stale:
```bash
uv tool install dominion-cli --from "$PLUGIN_CLI" --python 3.14 --force-reinstall
```
