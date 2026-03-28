"""Panel mode — F-Thread multi-perspective debate for discuss step.

v0.3.0: Simplified from methodology-based panel to configuration-only.
Panel context is now assembled by prepare.py into CLAUDE.md, not here.
"""

from __future__ import annotations

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


def get_facilitation_prompt(topic: str, participants: list[str]) -> str:
    """Generate facilitation prompt for F-Thread panel."""
    return FACILITATION_TEMPLATE.format(
        topic=topic,
        participants=", ".join(participants),
    )
