# Inventory & Assessment

Step 1 of the study pipeline.

## Agents: Researcher + Security Auditor

### Inventory

1. Locate the plugin's directory (installed plugins path)
2. Read the plugin manifest (plugin.json or equivalent)
3. List all skills: read each skill file, note name, description, trigger conditions
4. List all agents: read each agent config, note role, model, tools
5. List all hooks: read hook definitions, note event triggers and commands
6. List all settings: note configuration options

Present inventory:
```
Plugin: {name} v{version}
  Skills: {count}
    - {name}: {description}
  Agents: {count}
    - {role}: {purpose}
  Hooks: {count}
    - {event}: {command}
```

### Security Review

For each skill and agent, the Security Auditor checks:
1. **Prompt injection**: Does the skill accept external input that could manipulate agent behavior?
2. **Data exfiltration**: Does the skill send data to external services without user knowledge?
3. **Permission escalation**: Does the skill request permissions beyond what it needs?
4. **Unsafe operations**: Does the skill run destructive commands, modify system files, or access credentials?

Security findings are rated: safe / caution / dangerous.
- **dangerous**: item is immediately killed, does not proceed to kill gate
- **caution**: noted, proceeds to kill gate with warning
- **safe**: proceeds normally

### Benefit Assessment

For each item (excluding dangerous ones), the Researcher evaluates:
1. What does this item do?
2. Does the project currently have this capability?
3. If not: would having it concretely improve development on *this project*?
4. If yes: what specific scenarios would trigger it?

Record assessment for each item: purpose, current_coverage, benefit_scenarios.
