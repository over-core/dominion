# Refactor Research Protocol

For refactoring and restructuring tasks:

1. **Scope analysis** — map the refactoring boundary using serena:
   - `get_symbols_overview` on affected modules
   - `find_referencing_symbols` to trace impact of proposed changes
   - Martin's coupling metrics: afferent/efferent coupling between modules
2. **Risk identification** — categorize by severity:
   - **high**: public API changes, shared module modifications, database schema changes
   - **medium**: internal interface changes affecting multiple consumers
   - **low**: encapsulated changes within a single module
3. **Pattern analysis** — identify existing patterns that should be preserved vs changed
   - Document which patterns are intentional vs accidental complexity
4. **Migration path** — for large refactors, propose incremental steps (Strangler Fig pattern)
5. **Write research.toml** — findings with impact maps, dependency analysis, proposed migration sequence
