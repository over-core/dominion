"""Panel mode — multi-perspective debate for strategic decisions."""

from __future__ import annotations

from pathlib import Path

from .config import read_toml_optional
from .methodology import assemble_methodology, get_condition_signals

PANEL_CONFIGURATIONS: dict[str, list[str]] = {
    "architecture": ["architect", "security-auditor", "analyst"],
    "feature_strategy": ["architect", "innovation-engineer", "reviewer"],
    "performance": ["analyst", "architect"],
    "retrospective": ["reviewer", "innovation-engineer", "analyst"],
    "security": ["security-auditor", "architect", "reviewer"],
    "creative": ["innovation-engineer", "architect", "analyst"],
}

STEP_PANEL_TYPES: dict[str, str] = {
    "discuss": "architecture",
    "improve": "retrospective",
}

FACILITATION_TEMPLATE = """\
You are facilitating a multi-perspective panel debate on: {topic}

Panel participants: {participants}

## Debate Protocol
1. Present the topic and context to all perspectives.
2. Each perspective states their position with rationale.
3. Identify points of agreement and disagreement.
4. Challenge assumptions — ask "what if this fails?"
5. Synthesize into a recommendation with noted dissents.

## Output Format
Produce a structured panel output:
- **Recommendation**: The panel's consensus recommendation
- **Dissents**: Any minority positions that disagreed (with rationale)
- **Trade-offs**: Key trade-offs the panel identified

Do NOT seek false consensus. Real dissent is more valuable than polite agreement.\
"""


def get_panel_participants(
    decision_type: str, active_agents: list[str]
) -> list[str]:
    """Return panel participant roles filtered to active agents.

    Raises ValueError for unknown decision types.
    """
    if decision_type not in PANEL_CONFIGURATIONS:
        raise ValueError(
            f"Unknown panel decision type '{decision_type}'. "
            f"Valid types: {', '.join(PANEL_CONFIGURATIONS)}"
        )

    configured = PANEL_CONFIGURATIONS[decision_type]
    return [role for role in configured if role in active_agents]


def get_panel_context(
    dom_root: Path, decision_type: str, topic: str
) -> dict:
    """Build panel facilitation context with combined methodology.

    Returns dict with decision_type, topic, participants, methodology
    excerpts per role, facilitation instructions, and output format.
    """
    dominion = read_toml_optional(dom_root / "dominion.toml") or {}
    active = dominion.get("agents", {}).get("active", [])

    participants = get_panel_participants(decision_type, active)

    if len(participants) < 2:
        # Fall back to all configured participants if too few are active.
        participants = list(PANEL_CONFIGURATIONS[decision_type])

    signals = get_condition_signals(dom_root)

    # Assemble methodology excerpts for each participant.
    perspectives: dict[str, str] = {}
    for role in participants:
        agent_path = dom_root / "agents" / role / "agent.toml"
        if agent_path.exists():
            model = "opus"  # Panel always uses Opus-level curation
            perspectives[role] = assemble_methodology(dom_root, role, signals, model)

    facilitation = FACILITATION_TEMPLATE.format(
        topic=topic,
        participants=", ".join(participants),
    )

    return {
        "decision_type": decision_type,
        "topic": topic,
        "participants": participants,
        "perspectives": perspectives,
        "facilitation": facilitation,
        "output_format": {
            "recommendation": "str — panel consensus",
            "dissents": "list[str] — minority positions with rationale",
            "trade_offs": "list[str] — key trade-offs identified",
        },
    }


def get_step_panel_type(step: str) -> str:
    """Map pipeline step to panel decision type.

    Returns "architecture" as default for unmapped steps.
    """
    return STEP_PANEL_TYPES.get(step, "architecture")
