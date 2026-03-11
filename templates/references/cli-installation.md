# CLI Installation

Install the pre-built dominion-cli from the Dominion plugin distribution.

## Prerequisites

1. Check `uv` is on PATH:
   ```bash
   uv --version
   ```
   If missing: STOP. Tell user:
   "uv is required. Install: https://docs.astral.sh/uv/getting-started/installation/"

## Locate Plugin Root

Determine the Dominion plugin root directory. Use these methods in order:

### Method 1: Derive from skill base directory (preferred)

When this skill loaded, the system message showed:
```
Base directory for this skill: <path>/skills/init
```

The plugin root is two directories up from that base directory. Extract it:
```bash
PLUGIN_ROOT="<the path, minus /skills/init>"
```

Verify it contains the cli/ directory:
```bash
test -d "$PLUGIN_ROOT/cli" && echo "Found CLI at $PLUGIN_ROOT/cli"
```

### Method 2: Search the plugin cache (fallback)

If Method 1 is not available:
```bash
PLUGIN_ROOT=$(ls -d ~/.claude/plugins/cache/dominion/dominion/*/ 2>/dev/null | sort -V | tail -1)
```

Verify:
```bash
test -d "${PLUGIN_ROOT}cli" && echo "Found plugin at $PLUGIN_ROOT"
```

### Method 3: Ask the user (terminal)

If neither method works: STOP. Tell user:
"Could not locate the Dominion plugin directory. Please provide the path to your Dominion plugin installation."

## Install

1. Install dominion-cli as an isolated tool:
   ```bash
   uv tool install dominion-cli --from "${PLUGIN_ROOT}/cli"
   ```

2. Verify installation:
   ```bash
   dominion-cli --version
   ```
   Expected: version matching plugin version (check .claude-plugin/plugin.json in PLUGIN_ROOT).

3. Smoke test:
   ```bash
   dominion-cli --help
   dominion-cli validate --help
   dominion-cli validate --json
   dominion-cli agents list --json
   ```

4. Copy cli-spec.toml to project:
   ```bash
   cp "${PLUGIN_ROOT}/templates/cli-spec.toml" .dominion/specs/cli-spec.toml
   ```

## Upgrade (for existing projects)

If dominion-cli is already installed but version is stale:
```bash
uv tool install dominion-cli --from "${PLUGIN_ROOT}/cli" --force-reinstall
```
