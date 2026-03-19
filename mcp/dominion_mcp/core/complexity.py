"""Complexity detection — auto-assess task complexity, adapt pipeline depth."""

from __future__ import annotations

import re
from pathlib import Path

from .config import current_phase, phase_path, read_toml_optional
from .state import get_position

COMPLEXITY_LEVELS = ("trivial", "moderate", "complex", "major")

# Pipeline step subsets per complexity level.
PIPELINE_PROFILES: dict[str, list[str]] = {
    "trivial": ["execute"],
    "moderate": ["research", "plan", "execute", "audit"],
    "complex": ["discuss", "research", "plan", "execute", "audit", "review", "improve"],
    "major": ["discuss", "research", "plan", "execute", "audit", "review", "improve"],
}

# Dispatch mode overrides per complexity level.
DISPATCH_OVERRIDES: dict[str, dict[str, str]] = {
    "major": {"discuss": "panel", "improve": "panel"},
}

# Keyword patterns for pre-research complexity assessment.
_TRIVIAL_PATTERNS = re.compile(
    r"\b(fix typo|rename|bump version|update version|typo|whitespace|comment fix"
    r"|change label|fix spelling|update copyright)\b",
    re.IGNORECASE,
)
_MAJOR_PATTERNS = re.compile(
    r"\b(rewrite|architecture|redesign system|full rewrite|breaking change"
    r"|multi.?service|platform.?wide|cross.?cutting)\b",
    re.IGNORECASE,
)
_COMPLEX_PATTERNS = re.compile(
    r"\b(redesign|migrate|new system|overhaul|rearchitect"
    r"|new module|integration|multi.?component)\b",
    re.IGNORECASE,
)


def assess_complexity(intent: str, scope: str | None = None) -> str:
    """Pre-research complexity assessment from intent text.

    Keyword analysis produces a rough estimate. Conservative default is
    "moderate" for ambiguous inputs.  Scope narrows trivial detection
    (single-file hints).
    """
    text = f"{intent} {scope or ''}"

    if _TRIVIAL_PATTERNS.search(text):
        return "trivial"
    if _MAJOR_PATTERNS.search(text):
        return "major"
    if _COMPLEX_PATTERNS.search(text):
        return "complex"

    # Single-file hints suggest trivial.
    if scope and ("/" not in scope and "," not in scope):
        return "trivial"

    return "moderate"


def refine_complexity(dom_root: Path) -> str:
    """Post-research refinement from research.toml findings.

    Can upgrade (never downgrade) the current complexity_level in
    state.toml.  Returns the refined level.
    """
    pos = get_position(dom_root)
    current = pos.get("complexity_level") or "moderate"
    current_idx = COMPLEXITY_LEVELS.index(current) if current in COMPLEXITY_LEVELS else 1

    phase = current_phase(dom_root)
    if phase == 0:
        return current

    research_path = phase_path(dom_root, phase) / "research.toml"
    research = read_toml_optional(research_path)
    if not research:
        return current

    findings = research.get("findings", [])
    if not findings:
        return current

    # Count severity signals.
    high_count = sum(1 for f in findings if f.get("severity") == "high")
    categories = {f.get("category") for f in findings if f.get("category")}
    has_specialist_referral = any(f.get("specialist_referral") for f in findings)

    # Determine refined level.
    if high_count >= 5 or (high_count >= 3 and len(categories) >= 4):
        refined = "major"
    elif high_count >= 2 or len(categories) >= 3 or has_specialist_referral:
        refined = "complex"
    elif high_count >= 1:
        refined = "moderate"
    else:
        refined = current

    refined_idx = COMPLEXITY_LEVELS.index(refined)

    # Never downgrade.
    if refined_idx > current_idx:
        return refined
    return current


def get_effective_steps(complexity_level: str | None) -> list[str]:
    """Return the pipeline step list for a given complexity level.

    Returns full 7-step pipeline for unknown or missing levels.
    """
    if complexity_level and complexity_level in PIPELINE_PROFILES:
        return list(PIPELINE_PROFILES[complexity_level])
    return list(PIPELINE_PROFILES["complex"])


def get_dispatch_override(complexity_level: str | None, step: str) -> str | None:
    """Return dispatch mode override for a step at a given complexity.

    Returns None if no override applies.
    """
    if not complexity_level:
        return None
    overrides = DISPATCH_OVERRIDES.get(complexity_level, {})
    return overrides.get(step)
