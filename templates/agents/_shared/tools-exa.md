# Exa Research Workflow

When Exa MCP is available, use it for external research alongside context7.

## Tool Routing

| Need | Primary | Fallback |
|------|---------|----------|
| Library documentation | context7 `query-docs` | Exa `web_search_exa` |
| Code examples | Exa `get_code_context_exa` | Manual GitHub search via Bash |
| Security advisories | Exa `web_search_exa` | WebSearch |
| Best practices | Exa `web_search_exa` | WebSearch |

## Usage Patterns

- `web_search_exa` — semantic search, returns clean text (not encrypted blobs). Use for documentation, advisories, best practices.
- `get_code_context_exa` — searches GitHub, Stack Overflow, official docs for working code examples. Unique capability.
- Prefer Exa over WebSearch for all external research. Exa returns structured, readable content.

## When NOT to Use

- Internal project code — use serena or Grep
- Already-indexed libraries — use context7 first (faster)
