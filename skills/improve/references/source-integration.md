# Source Integration

Extract domain knowledge from external sources for `/dominion:improve --from`.

## Source Types

### Notion (`--from notion`)
1. Verify Notion MCP is available (check state.toml `[[mcp_status]]`)
2. If unavailable: "Notion MCP not available. Provide a Notion API token or use --from url with exported pages."
3. If available: ask for the database or page URL
4. Extract: page content, database entries, comments
5. Structure into domain knowledge format

### Confluence (`--from confluence`)
1. Ask for Confluence URL and space key
2. Use WebFetch to retrieve pages via REST API
3. Extract: page content, labels, child pages
4. Structure into domain knowledge format

### Obsidian (`--from obsidian:<vault-path>`)
1. Verify the vault path exists on the local filesystem
2. Read the vault's `.obsidian/` directory to understand structure
3. Use Glob to find `.md` files
4. Read files, following `[[wikilinks]]` to build a knowledge graph
5. Structure into domain knowledge format

### URL (`--from url:<url>`)
1. Use WebFetch to retrieve the page
2. Extract meaningful content (skip navigation, ads, boilerplate)
3. If the page links to sub-pages: ask if those should be included
4. Structure into domain knowledge format

### Local File (`--from file:<path>`)
1. Verify the file exists (must be within the project directory)
2. Read the file content
3. If it's a directory: read all `.md`, `.txt`, `.pdf` files within
4. Structure into domain knowledge format

### Plugin Reference (`--from plugin:<name>`)
1. Locate the plugin: check installed Claude Code plugins for the named plugin
2. Read all plugin artifacts: skills, agents, hooks, configs, package manifest
3. **Security Gate**: invoke Security Auditor's Improve Mode before any extraction:
   - **Inventory**: catalog all plugin artifacts (skills, agents, hooks, configs)
   - **Security Assessment**: evaluate each artifact for command injection, permission escalation, data exfiltration, filesystem escape, secret exposure, supply chain concerns
   - **Kill Gate**: present findings to user per artifact
     - **Unsafe** artifacts are killed — no further processing
     - **Conditional** artifacts require user acknowledgment of risks
     - **Safe** artifacts pass to the normal improve pipeline
4. Only artifacts that pass the kill gate proceed to post-extraction
5. Structure passing artifacts into domain knowledge format

## Post-extraction

After extracting from any source:
1. Cross-reference extracted terms against the codebase (using Serena)
2. Identify conflicts between source knowledge and existing `.dominion/knowledge/` files
3. Present a summary: "Extracted {N} concepts, {N} constraints, {N} patterns from {source}"
4. Proceed to ad-hoc pipeline Step 2 (Investigate) with extracted knowledge as input
