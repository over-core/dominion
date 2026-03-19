# Serena Workflow

When serena MCP is available, use it as the PRIMARY tool for code navigation. Prefer serena over Grep/Glob for all code-level queries.

## Tool Selection

| Task | Use Serena | Use Grep/Glob |
|------|-----------|---------------|
| Read function body | `find_symbol` with `include_body=True` | NO |
| Find references | `find_referencing_symbols` | NO |
| Get file overview | `get_symbols_overview` | NO |
| Find file by name | NO | `find_file` or Glob |
| Search for pattern in non-code | NO | Grep |
| Count/list files | NO | Glob |

## Serena Patterns

1. **Start broad, narrow down:** `get_symbols_overview` on a file → `find_symbol` for specific functions
2. **Check impact before changing:** `find_referencing_symbols` before modifying any public interface
3. **Read bodies only when needed:** Use `include_body=False` first to scan, then `include_body=True` for specific symbols
4. **Use name_path patterns:** `ClassName/method_name` for targeted lookup

## Fallback

If serena is unavailable or returns errors, fall back to Grep/Glob + Read. Do not halt on serena failure unless the codebase is too large to navigate without it.
