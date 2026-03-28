"""Pipeline selection and validation for v0.5.1.

Replaces complexity.py. Pipeline is always explicit — the orchestrator picks
stages based on intent. suggest_pipeline() advises. validate_pipeline() enforces
canonical order and applies config insertions.
"""

from __future__ import annotations

import re

CANONICAL_ORDER = ["discuss", "research", "plan", "execute", "review"]

PRIMARY_ROLES: dict[str, str] = {
    "research": "researcher",
    "plan": "architect",
    "execute": "developer",
    "review": "reviewer",
    "discuss": "architect",
}

_ANALYSIS_PATTERNS = re.compile(
    r"\b(analyz|audit|assess|review codebase|document patterns|flag anti.?patterns"
    r"|security scan|code quality|technical debt|codebase health|improvement plan)\b",
    re.IGNORECASE,
)
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


def suggest_pipeline(intent: str, *, has_design_doc: bool = False) -> dict:
    """Suggest pipeline stages from intent keywords.

    Advisory only — orchestrator can override.
    Returns {pipeline: [...], reasoning: str, keywords_matched: [...]}.
    """
    keywords: list[str] = []

    if _ANALYSIS_PATTERNS.search(intent):
        match = _ANALYSIS_PATTERNS.search(intent)
        keywords = [match.group()] if match else []
        return {
            "pipeline": ["research", "review"],
            "reasoning": "Intent is codebase analysis — research and review only, no implementation",
            "keywords_matched": keywords,
        }

    if _MAJOR_PATTERNS.search(intent):
        match = _MAJOR_PATTERNS.search(intent)
        keywords = [match.group()] if match else []
        return {
            "pipeline": ["discuss", "research", "plan", "execute", "review"],
            "reasoning": "Intent indicates major architectural change — full pipeline with discuss",
            "keywords_matched": keywords,
        }

    if _COMPLEX_PATTERNS.search(intent):
        match = _COMPLEX_PATTERNS.search(intent)
        keywords = [match.group()] if match else []
        return {
            "pipeline": ["discuss", "research", "plan", "execute", "review"],
            "reasoning": "Intent indicates significant structural change — full pipeline with discuss",
            "keywords_matched": keywords,
        }

    if _TRIVIAL_PATTERNS.search(intent):
        match = _TRIVIAL_PATTERNS.search(intent)
        keywords = [match.group()] if match else []
        return {
            "pipeline": ["execute"],
            "reasoning": "Intent indicates a simple, localized change — execute only",
            "keywords_matched": keywords,
        }

    if has_design_doc:
        return {
            "pipeline": ["plan", "execute", "review"],
            "reasoning": "Design document available — spec-driven implementation",
            "keywords_matched": [],
        }

    return {
        "pipeline": ["research", "plan", "execute", "review"],
        "reasoning": "Feature addition with clear scope — standard pipeline",
        "keywords_matched": [],
    }


def validate_pipeline(pipeline: list[str], config: dict | None = None) -> list[str]:
    """Validate pipeline preserves canonical order. Apply config insertions.

    Returns effective pipeline (with any inserted custom steps).
    Raises ValueError if pipeline violates canonical order.
    """
    known = set(CANONICAL_ORDER)
    canonical_items = [s for s in pipeline if s in known]
    canonical_positions = [CANONICAL_ORDER.index(s) for s in canonical_items]
    if canonical_positions != sorted(canonical_positions):
        raise ValueError(
            f"Pipeline must preserve canonical order: {' -> '.join(CANONICAL_ORDER)}"
        )

    if config:
        base = list(pipeline)
        active = set(config.get("agents", {}).get("active", []))
        for ins in config.get("pipeline", {}).get("insertions", []):
            when = ins.get("when")
            if when and when not in active:
                continue
            after = ins.get("after")
            if after in base:
                idx = base.index(after) + 1
                base.insert(idx, ins["name"])
        return base

    return list(pipeline)


def valid_steps(config: dict | None = None) -> tuple[str, ...]:
    """Return all valid step names including custom insertions from config."""
    base = ("idle", "discuss", "research", "plan", "execute", "review")
    if config:
        custom = tuple(
            ins["name"]
            for ins in config.get("pipeline", {}).get("insertions", [])
            if ins.get("name")
        )
        return base + custom
    return base
