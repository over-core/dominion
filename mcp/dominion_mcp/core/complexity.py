"""Complexity detection, pipeline profiles, and dispatch table for v0.4.0.

Assesses task complexity from intent keywords, maps (step, complexity) to
thread types and agent roles, and refines complexity post-research.

v0.4.0: Added "specified" level for tasks with comprehensive design docs.
"""

from __future__ import annotations

import re
from pathlib import Path

from .config import read_toml_optional

COMPLEXITY_LEVELS = ("trivial", "specified", "moderate", "complex", "major")

# ---------------------------------------------------------------------------
# Pipeline profiles per complexity
# ---------------------------------------------------------------------------

PIPELINE_PROFILES: dict[str, list[str]] = {
    "trivial": ["execute"],
    "specified": ["plan", "execute", "review"],
    "moderate": ["research", "plan", "execute", "review"],
    "complex": ["discuss", "research", "plan", "execute", "review"],
    "major": ["discuss", "research", "plan", "execute", "review"],
}

# ---------------------------------------------------------------------------
# Dispatch table: (step, complexity) → (thread_type, [(role, model), ...])
# ---------------------------------------------------------------------------

DISPATCH_TABLE: dict[tuple[str, str], tuple[str, list[tuple[str, str]]]] = {
    ("research", "moderate"): ("B-Thread", [("researcher", "opus")]),
    ("research", "complex"): ("P-Thread", [("researcher", "opus"), ("innovation-engineer", "opus"), ("security-auditor", "opus")]),
    ("research", "major"): ("P-Thread", [("researcher", "opus"), ("innovation-engineer", "opus"), ("security-auditor", "opus")]),

    ("plan", "specified"): ("B-Thread", [("architect", "opus")]),
    ("plan", "moderate"): ("B-Thread", [("architect", "opus")]),
    ("plan", "complex"): ("B-Thread", [("architect", "opus")]),
    ("plan", "major"): ("B-Thread", [("architect", "opus")]),

    ("execute", "trivial"): ("Z-Thread", [("developer", "sonnet")]),
    ("execute", "specified"): ("P-Thread", [("developer", "sonnet")]),
    ("execute", "moderate"): ("P-Thread", [("developer", "sonnet")]),
    ("execute", "complex"): ("P-Thread", [("developer", "sonnet")]),
    ("execute", "major"): ("P-Thread", [("developer", "sonnet")]),

    ("review", "specified"): ("B-Thread", [("reviewer", "opus")]),
    ("review", "moderate"): ("B-Thread", [("reviewer", "opus")]),
    ("review", "complex"): ("P-Thread", [("reviewer", "opus"), ("security-auditor", "opus"), ("analyst", "opus")]),
    ("review", "major"): ("P-Thread", [("reviewer", "opus"), ("security-auditor", "opus"), ("analyst", "opus")]),

    ("discuss", "complex"): ("F-Thread", [("architect", "opus"), ("security-auditor", "opus"), ("innovation-engineer", "opus")]),
    ("discuss", "major"): ("F-Thread", [("architect", "opus"), ("security-auditor", "opus"), ("innovation-engineer", "opus"), ("analyst", "opus")]),
}

# Primary roles that MUST be present for each step.
_PRIMARY_ROLES: dict[str, str] = {
    "research": "researcher",
    "plan": "architect",
    "execute": "developer",
    "review": "reviewer",
    "discuss": "architect",
}


def get_dispatch(
    step: str, complexity: str, active_agents: list[str]
) -> tuple[str, list[dict]]:
    """Look up dispatch info for (step, complexity), filtered by active agents.

    Returns (thread_type, agents_list) where agents_list contains dicts with
    'role' and 'model' keys.

    Degradation rules:
    - P-Thread with 1 remaining agent → B-Thread
    - F-Thread with 1 remaining agent → B-Thread
    - Primary role missing → raises ValueError
    """
    key = (step, complexity)
    if key not in DISPATCH_TABLE:
        raise ValueError(
            f"No dispatch entry for ({step}, {complexity}). "
            f"Step must be in pipeline profile for this complexity level."
        )

    thread_type, agent_list = DISPATCH_TABLE[key]
    active_set = set(active_agents)

    # Check primary role
    primary = _PRIMARY_ROLES.get(step)
    if primary and primary not in active_set:
        raise ValueError(
            f"Primary role '{primary}' for step '{step}' is not in active agents. "
            f"Add it to config.toml [agents].active."
        )

    # Filter to active agents
    filtered = [
        {"role": role, "model": model}
        for role, model in agent_list
        if role in active_set
    ]

    # Degrade thread type if too few agents
    if len(filtered) <= 1:
        if thread_type in ("P-Thread", "F-Thread"):
            thread_type = "B-Thread"

    return thread_type, filtered


# ---------------------------------------------------------------------------
# Keyword-based complexity assessment
# ---------------------------------------------------------------------------

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


def assess_complexity(intent: str, *, has_design_doc: bool = False) -> dict:
    """Pre-research complexity assessment from intent text.

    Returns dict with complexity, reasoning, keywords_matched.
    Conservative default is "moderate" for ambiguous inputs.

    When has_design_doc is True and no escalation keywords match, returns
    "specified" instead of "moderate" — skipping discuss and research steps.
    """
    keywords: list[str] = []

    if _MAJOR_PATTERNS.search(intent):
        match = _MAJOR_PATTERNS.search(intent)
        keywords = [match.group()] if match else []
        return {
            "complexity": "major",
            "reasoning": "Intent indicates major architectural change",
            "keywords_matched": keywords,
        }

    if _COMPLEX_PATTERNS.search(intent):
        match = _COMPLEX_PATTERNS.search(intent)
        keywords = [match.group()] if match else []
        return {
            "complexity": "complex",
            "reasoning": "Intent indicates significant structural change or new integration",
            "keywords_matched": keywords,
        }

    if _TRIVIAL_PATTERNS.search(intent):
        match = _TRIVIAL_PATTERNS.search(intent)
        keywords = [match.group()] if match else []
        return {
            "complexity": "trivial",
            "reasoning": "Intent indicates a simple, localized change",
            "keywords_matched": keywords,
        }

    if has_design_doc:
        return {
            "complexity": "specified",
            "reasoning": "Design document available — spec-driven implementation (plan, execute, review)",
            "keywords_matched": [],
        }

    return {
        "complexity": "moderate",
        "reasoning": "Feature addition with clear scope, no cross-cutting concerns detected",
        "keywords_matched": [],
    }


# ---------------------------------------------------------------------------
# Post-research refinement
# ---------------------------------------------------------------------------


def refine_complexity(dom_root: Path, phase: str) -> dict:
    """Post-research complexity refinement from research findings.

    Can UPGRADE complexity (never downgrade). Reads findings.toml from
    the research step, analyzes severity and category spread.

    Returns dict with previous, refined, upgraded (bool).
    """
    state = read_toml_optional(dom_root / "state.toml") or {}
    current = state.get("position", {}).get("complexity_level", "moderate")
    current_idx = COMPLEXITY_LEVELS.index(current) if current in COMPLEXITY_LEVELS else 1

    findings_path = dom_root / "phases" / phase / "research" / "output" / "findings.toml"
    findings_data = read_toml_optional(findings_path)
    if not findings_data:
        return {"previous": current, "refined": current, "upgraded": False}

    # Collect all items across all role namespaces
    all_items: list[dict] = []
    for key, value in findings_data.get("findings", {}).items():
        if isinstance(value, dict):
            items = value.get("items", [])
            if isinstance(items, list):
                all_items.extend(items)

    if not all_items:
        return {"previous": current, "refined": current, "upgraded": False}

    # Count severity signals
    high_count = sum(1 for f in all_items if f.get("severity") in ("high", "critical"))
    categories = {f.get("category") for f in all_items if f.get("category")}

    # Determine refined level
    if high_count >= 5 or (high_count >= 3 and len(categories) >= 4):
        refined = "major"
    elif high_count >= 2 or len(categories) >= 3:
        refined = "complex"
    elif high_count >= 1:
        refined = "moderate"
    else:
        refined = current

    refined_idx = COMPLEXITY_LEVELS.index(refined)

    # Never downgrade
    if refined_idx > current_idx:
        return {"previous": current, "refined": refined, "upgraded": True}
    return {"previous": current, "refined": current, "upgraded": False}


def get_pipeline(complexity: str) -> list[str]:
    """Return the pipeline step list for a complexity level."""
    if complexity in PIPELINE_PROFILES:
        return list(PIPELINE_PROFILES[complexity])
    return list(PIPELINE_PROFILES["complex"])
