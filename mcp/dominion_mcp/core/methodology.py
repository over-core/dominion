"""Conditional methodology assembly and model-aware curation."""

from __future__ import annotations

from pathlib import Path

from .config import read_toml, read_toml_optional

MODEL_BUDGETS: dict[str, int] = {
    "opus": 500_000,
    "sonnet": 150_000,
    "haiku": 30_000,
}


def get_budget(agent_toml: dict) -> int:
    """Get token budget for an agent based on its model.

    Checks agent.max_tokens override first, then MODEL_BUDGETS for model.
    """
    agent = agent_toml.get("agent", {})
    override = agent.get("max_tokens")
    if override is not None:
        return override
    model = agent.get("model", "sonnet")
    return MODEL_BUDGETS.get(model, 150_000)


def get_condition_signals(dom_root: Path) -> dict:
    """Build condition signal map from project state.

    Reads dominion.toml, style.toml, state.toml, user-profile.toml to build:
    {
        "phase_type": str | None,      # from state.toml or intent
        "languages": list[str],         # from dominion.toml [project].languages
        "framework": list[str],         # from dominion.toml [project].frameworks
        "tools_available": list[str],   # from dominion.toml [tools]
        "agents_active": list[str],     # from dominion.toml [agents].active
        "direction_mode": str | None,   # from dominion.toml [direction].mode
        "task_type": str | None,        # from current task in plan.toml (if in execute)
        "complexity_level": str | None, # from state.toml or pipeline assessment
        "user_skill_level": str | None, # from user-profile.toml
        "testing_style": list[str],     # from style.toml [testing].styles
    }
    """
    dominion = read_toml_optional(dom_root / "dominion.toml") or {}
    style = read_toml_optional(dom_root / "style.toml") or {}
    state = read_toml_optional(dom_root / "state.toml") or {}
    profile = read_toml_optional(dom_root / "user-profile.toml") or {}

    project = dominion.get("project", {})
    tools = dominion.get("tools", {})
    agents = dominion.get("agents", {})
    direction = dominion.get("direction", {})
    position = state.get("position", {})
    testing = style.get("testing", {})

    return {
        "phase_type": position.get("phase_type"),
        "languages": project.get("languages", []),
        "framework": project.get("frameworks", []),
        "tools_available": [
            name
            for name, conf in tools.items()
            if isinstance(conf, dict) and conf.get("enabled", True)
        ]
        if isinstance(tools, dict)
        else [],
        "agents_active": agents.get("active", []),
        "direction_mode": direction.get("mode"),
        "task_type": position.get("task_type"),
        "complexity_level": position.get("complexity_level"),
        "user_skill_level": profile.get("experience_level"),
        "testing_style": testing.get("styles", []),
    }


def evaluate_conditions(conditions: dict, signals: dict) -> bool:
    """Check if ALL conditions match the signals.

    Each condition key maps to a signal. Values can be:
    - list: signal value must contain at least one matching element (OR within key)
    - str: signal value must equal or contain the string

    ALL condition keys must match (AND across keys).
    Empty conditions dict = always True.
    """
    for key, required in conditions.items():
        signal_value = signals.get(key)
        if signal_value is None:
            return False

        if isinstance(required, list):
            # required is a list of acceptable values
            if isinstance(signal_value, list):
                # Both lists: intersection must be non-empty
                if not set(required) & set(signal_value):
                    return False
            else:
                # Signal is scalar, must be in required list
                if signal_value not in required:
                    return False
        else:
            # required is a scalar
            if isinstance(signal_value, list):
                if required not in signal_value:
                    return False
            else:
                if signal_value != required:
                    return False

    return True


def curate_sections(sections: list[dict], signals: dict, model: str) -> list[dict]:
    """Select methodology sections based on conditions and model.

    - always_include sections are always included
    - For Opus (permissive): include if ANY condition key matches
    - For Sonnet (strict): include only if ALL conditions match

    Returns filtered list of section dicts, preserving order.
    """
    result = []
    for section in sections:
        if section.get("always_include", False):
            result.append(section)
            continue

        conditions = section.get("conditions", {})
        if not conditions:
            # No conditions = always include
            result.append(section)
            continue

        if model == "opus":
            # Permissive: include if ANY condition key has a matching value
            for key, required in conditions.items():
                single_condition = {key: required}
                if evaluate_conditions(single_condition, signals):
                    result.append(section)
                    break
        else:
            # Strict (sonnet, haiku, default): ALL conditions must match
            if evaluate_conditions(conditions, signals):
                result.append(section)

    return result


def _serialize_phases(phases: list[dict]) -> str:
    """Serialize [[methodology.phases]] into markdown."""
    if not phases:
        return ""
    lines = ["## Workflow Phases", ""]
    for i, phase in enumerate(phases, 1):
        name = phase.get("name", f"Phase {i}")
        purpose = phase.get("purpose", "")
        lines.append(f"### {i}. {name}")
        if purpose:
            lines.append(f"**Purpose:** {purpose}")

        # Handle both list and string formats for activities
        activities = phase.get("key_activities") or phase.get("activities", "")
        if isinstance(activities, list):
            for activity in activities:
                lines.append(f"- {activity}")
        elif isinstance(activities, str) and activities.strip():
            for line in activities.strip().split("\n"):
                stripped = line.strip()
                if stripped:
                    if not stripped.startswith("-"):
                        stripped = f"- {stripped}"
                    lines.append(stripped)
        lines.append("")
    return "\n".join(lines)


def _serialize_methods(methods: list[dict]) -> str:
    """Serialize [[methodology.methods]] into markdown."""
    if not methods:
        return ""
    lines = ["## Methods", ""]
    for method in methods:
        name = method.get("name", "")
        source = method.get("source", "")
        purpose = method.get("purpose", "")
        lines.append(f"### {name}")
        if source:
            lines.append(f"**Source:** {source}")
        if purpose:
            lines.append(f"**Purpose:** {purpose}")
        lines.append("")
    return "\n".join(lines)


def _serialize_tool_routing(routing: list[dict] | dict) -> str:
    """Serialize [[methodology.tool_routing]] or [methodology.tool_routing] into markdown."""
    if not routing:
        return ""
    lines = ["## Tool Routing", "", "| Tool | Use For |", "|------|---------|"]

    if isinstance(routing, list):
        for entry in routing:
            tool = entry.get("tool", "")
            use_for = entry.get("use_for", "")
            lines.append(f"| {tool} | {use_for} |")
    elif isinstance(routing, dict):
        for tool, use_for in routing.items():
            lines.append(f"| {tool} | {use_for} |")

    lines.append("")
    return "\n".join(lines)


def _serialize_routing_rules(rules: list[dict]) -> str:
    """Serialize [[methodology.routing_rules]] into markdown."""
    if not rules:
        return ""
    lines = ["## Specialist Routing Rules", ""]
    for rule in rules:
        role = rule.get("role", "")
        triggers = rule.get("triggers", [])
        note = rule.get("note", "")
        trigger_str = ", ".join(triggers) if isinstance(triggers, list) else str(triggers)
        lines.append(f"- **{role}**: {trigger_str}")
        if note:
            lines.append(f"  ({note})")
    lines.append("")
    return "\n".join(lines)


def _serialize_mode_adaptation(adaptation: dict) -> str:
    """Serialize [methodology.mode_adaptation] into markdown."""
    if not adaptation:
        return ""
    lines = ["## Mode Adaptation", ""]
    for mode, description in adaptation.items():
        lines.append(f"- **{mode}:** {description}")
    lines.append("")
    return "\n".join(lines)


def assemble_methodology(dom_root: Path, role: str, signals: dict, model: str) -> str:
    """Assemble curated methodology text for an agent.

    1. Read agent TOML for methodology content
    2. Evaluate section conditions against signals with model-aware curation
    3. Read matching section .md files
    4. Serialize TOML-inline methodology (phases, methods, tool routing)
    5. Concatenate and return
    """
    agent_toml = read_toml(dom_root / "agents" / role / "agent.toml")
    methodology = agent_toml.get("methodology", {})
    sections = methodology.get("sections", [])

    # Part 1: Conditional section .md files
    selected = curate_sections(sections, signals, model)

    parts = []
    for section in selected:
        section_file = section.get("file", "")
        section_path = dom_root / "agents" / role / section_file
        if section_path.exists():
            parts.append(section_path.read_text())

    # Part 2: TOML-inline methodology content
    phases = methodology.get("phases", [])
    if phases:
        parts.append(_serialize_phases(phases))

    methods = methodology.get("methods", [])
    if methods:
        parts.append(_serialize_methods(methods))

    tool_routing = methodology.get("tool_routing", [])
    if tool_routing:
        parts.append(_serialize_tool_routing(tool_routing))

    routing_rules = methodology.get("routing_rules", [])
    if routing_rules:
        parts.append(_serialize_routing_rules(routing_rules))

    mode_adaptation = methodology.get("mode_adaptation")
    if mode_adaptation:
        parts.append(_serialize_mode_adaptation(mode_adaptation))

    return "\n\n".join(part for part in parts if part)
