# Domain Knowledge Capture Protocol (DKCP)

7-phase adaptive interview for capturing domain knowledge.

## Phase 1: Domain Mapping

**Agent:** Researcher
**Thinking:** Normal

1. Read `@data/taxonomy/domains.toml`
2. Ask: "What domain does this project operate in?"
3. Match the answer against the taxonomy
4. If match found: use the domain's `follow_ups` to ask targeted questions about subdomains
5. If no match: use Context7 or WebSearch to research the domain, then ask clarifying questions
6. Record: domain name, subdomains involved, key terminology

Output: domain map with terms and subdomain scope.

## Phase 2: Stakeholder Mapping

**Agent:** Researcher
**Thinking:** Normal

Ask one at a time:
1. "Who are the primary users of this system?"
2. "Who are the secondary stakeholders (ops, compliance, support)?"
3. "Are there regulatory bodies that oversee this domain?"
4. "What breaks if this system fails? Who gets hurt?"

Record: stakeholder list with roles and impact levels.

## Phase 3: Regulatory Scan

**Agent:** Researcher
**Thinking:** High effort

Based on domain and stakeholders identified in Phases 1-2:
1. Check taxonomy for regulatory follow-ups (HIPAA, PCI-DSS, GDPR, etc.)
2. Ask: "Are any of these regulations applicable?" (present as checklist)
3. For each applicable regulation: ask about compliance level, current status, and specific requirements
4. Use WebSearch to verify current regulatory requirements if needed

Record: applicable regulations, compliance requirements, certification needs.

## Phase 4: Deep Probe

**Agent:** Advisor
**Thinking:** Ultrathink

Review all knowledge captured in Phases 1-3. Identify:
- Areas where captured knowledge is thin (few details, vague answers)
- Contradictions between stakeholder needs and regulatory requirements
- Domain-specific edge cases that weren't covered

For each gap, ask one targeted follow-up question. Continue until:
- All major gaps are filled, OR
- User indicates they've shared everything they know

## Phase 5: Artifact Grounding

**Agent:** Researcher
**Thinking:** Normal

Anchor domain concepts to actual codebase:
1. Use Serena to search for domain terms in the codebase (class names, function names, comments)
2. For each domain concept: find the corresponding code symbols
3. If a concept has no code representation: note it as "not yet implemented" or "implicit"
4. If code uses different terminology than the domain: note the mapping

Output: concept-to-code mapping table.

## Phase 6: Knowledge Structuring

**Agent:** Advisor
**Thinking:** High effort

Organize captured knowledge into structured files:
1. **Glossary** — domain terms with definitions and code mappings
2. **Constraints** — regulatory requirements, compliance rules, business rules
3. **Stakeholder map** — who cares about what, impact levels
4. **Domain patterns** — common patterns in this domain (e.g., "all financial calculations use decimal, never float")

Write each as a `.md` file in `.dominion/knowledge/`.
Update `.dominion/knowledge/index.toml` with entries for each new file.

## Phase 7: Calibration

**Agent:** Advisor
**Thinking:** Normal

Present the structured knowledge back to the user:
1. Show glossary — "Are these definitions accurate?"
2. Show constraints — "Did I capture all the important rules?"
3. Show stakeholder map — "Is this complete?"
4. Show domain patterns — "Are these patterns correct?"

For each correction:
- Update the relevant knowledge file
- Note what was corrected (helps improve future interviews)

After calibration, proceed to output routing.
