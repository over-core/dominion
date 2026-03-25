"""Metrics — effort parsing, quality scoring, metric commands, delta computation.

Shared utilities for quality_gate, prepare_step, and generate_phase_report.
"""

from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Effort — 1-10 blast radius scale
# ---------------------------------------------------------------------------

EFFORT_LABELS: dict[int, str] = {
    1: "Trivial", 2: "Minimal", 3: "Small",
    4: "Contained", 5: "Moderate", 6: "Cross-module",
    7: "Subsystem", 8: "Cross-cutting", 9: "Architectural",
    10: "Redesign",
}


def parse_effort_level(effort: object) -> int | None:
    """Parse effort level 1-10 from int or string. Returns None if invalid."""
    if effort is None:
        return None
    try:
        level = int(effort)
    except (ValueError, TypeError):
        return None
    if 1 <= level <= 10:
        return level
    return None


def validate_effort_level(effort: object) -> str | None:
    """Return warning string if effort is present but not valid 1-10.

    Returns None if valid or absent.
    """
    if effort is None:
        return None
    level = parse_effort_level(effort)
    if level is None:
        return f"Invalid effort '{effort}'. Must be integer 1-10 (blast radius scale)."
    return None


def aggregate_effort(items: list[dict]) -> dict:
    """Aggregate effort levels across finding items.

    Returns {mean, max, distribution: {localized, cross_cutting, structural},
             with_effort, without_effort}.
    """
    levels: list[int] = []
    without_effort = 0
    for item in items:
        level = parse_effort_level(item.get("effort"))
        if level is not None:
            levels.append(level)
        else:
            without_effort += 1

    if not levels:
        return {
            "mean": 0.0,
            "max": 0,
            "distribution": {"localized": 0, "cross_cutting": 0, "structural": 0},
            "with_effort": 0,
            "without_effort": without_effort,
        }

    return {
        "mean": round(sum(levels) / len(levels), 1),
        "max": max(levels),
        "distribution": {
            "localized": sum(1 for lv in levels if lv <= 3),
            "cross_cutting": sum(1 for lv in levels if 4 <= lv <= 6),
            "structural": sum(1 for lv in levels if lv >= 7),
        },
        "with_effort": len(levels),
        "without_effort": without_effort,
    }


# ---------------------------------------------------------------------------
# Pre-analysis metric commands per language
# ---------------------------------------------------------------------------

_METRIC_COMMANDS: dict[str, list[dict]] = {
    "python": [
        {"name": "loc", "label": "Python LOC",
         "command": "find . -name '*.py' -not -path '*/.*' | xargs wc -l 2>/dev/null | tail -1"},
        {"name": "test_count", "label": "Test files",
         "command": "find . -name 'test_*.py' -o -name '*_test.py' | wc -l"},
        {"name": "todo_count", "label": "TODO/FIXME",
         "command": "grep -rn 'TODO\\|FIXME' --include='*.py' | wc -l"},
    ],
    "typescript": [
        {"name": "loc", "label": "TypeScript LOC",
         "command": "find . \\( -name '*.ts' -o -name '*.tsx' \\) -not -path '*/node_modules/*' | xargs wc -l 2>/dev/null | tail -1"},
        {"name": "test_count", "label": "Test files",
         "command": "find . \\( -name '*.test.ts' -o -name '*.spec.ts' \\) | wc -l"},
    ],
    "javascript": [
        {"name": "loc", "label": "JavaScript LOC",
         "command": "find . \\( -name '*.js' -o -name '*.jsx' \\) -not -path '*/node_modules/*' | xargs wc -l 2>/dev/null | tail -1"},
    ],
    "rust": [
        {"name": "loc", "label": "Rust LOC",
         "command": "find . -name '*.rs' -not -path '*/target/*' | xargs wc -l 2>/dev/null | tail -1"},
        {"name": "test_count", "label": "Test modules",
         "command": "grep -rl '#\\[cfg(test)\\]' --include='*.rs' | wc -l"},
    ],
    "go": [
        {"name": "loc", "label": "Go LOC",
         "command": "find . -name '*.go' -not -path '*/vendor/*' | xargs wc -l 2>/dev/null | tail -1"},
        {"name": "test_count", "label": "Test files",
         "command": "find . -name '*_test.go' | wc -l"},
    ],
}

# CLI tool metric commands (only run if tool in config.tools.cli)
_CLI_METRIC_COMMANDS: dict[str, list[dict]] = {
    "radon": [
        {"name": "complexity_avg", "label": "Avg complexity (radon)",
         "command": "radon cc -s -a . 2>/dev/null | tail -1"},
        {"name": "maintainability", "label": "Maintainability (radon)",
         "command": "radon mi -s . 2>/dev/null | head -20"},
    ],
    "vulture": [
        {"name": "dead_code", "label": "Dead code items (vulture)",
         "command": "vulture . --min-confidence 80 2>/dev/null | wc -l"},
    ],
    "ruff": [
        {"name": "lint_violations", "label": "Lint violations (ruff)",
         "command": "ruff check --statistics . 2>/dev/null | tail -5"},
    ],
}


def get_metric_commands(
    languages: list[str], cli_tools: list[str] | None = None
) -> list[dict]:
    """Return metric collection commands for languages + detected CLI tools.

    Deduplicates by command name (first language wins).
    """
    seen: set[str] = set()
    result: list[dict] = []
    for lang in languages:
        for cmd in _METRIC_COMMANDS.get(lang.lower(), []):
            if cmd["name"] not in seen:
                seen.add(cmd["name"])
                result.append(cmd)
    for tool in cli_tools or []:
        for cmd in _CLI_METRIC_COMMANDS.get(tool.lower(), []):
            if cmd["name"] not in seen:
                seen.add(cmd["name"])
                result.append(cmd)
    return result


def format_metrics_section(metrics: dict[str, str]) -> str:
    """Format collected metrics as a markdown section for CLAUDE.md injection.

    Args:
        metrics: {label: raw_output_string}
    Returns empty string if no metrics.
    """
    if not metrics:
        return ""
    lines = ["## Pre-Analysis Metrics", ""]
    for label, value in metrics.items():
        lines.append(f"- **{label}**: {value.strip()}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Weighted quality scoring
# ---------------------------------------------------------------------------

_SEVERITY_DEDUCTIONS: dict[str, float] = {
    "critical": 2.0,
    "high": 1.0,
    "medium": 0.3,
    "low": 0.1,
}

_WEIGHT_BUCKETS: dict[str, tuple[float, list[str]]] = {
    "architecture":  (0.25, ["architecture", "design", "modularity"]),
    "code_quality":  (0.20, ["style", "quality", "duplication", "complexity"]),
    "testing":       (0.20, ["testing", "coverage", "ci"]),
    "security":      (0.15, ["security", "vulnerability", "license", "supply-chain"]),
    "performance":   (0.10, ["performance", "scalability", "memory"]),
    "documentation": (0.10, ["documentation", "naming"]),
}


def _category_to_bucket(category: str) -> str:
    """Map a finding category to its weight bucket."""
    cat = category.lower()
    for bucket, (_, categories) in _WEIGHT_BUCKETS.items():
        if cat in categories:
            return bucket
    return "code_quality"


def compute_quality_score(items: list[dict]) -> dict:
    """Compute weighted 0-10 quality score from review findings.

    Each bucket starts at 10. Findings deduct by severity. Floor at 0.
    Final score = weighted sum of bucket scores.

    Returns {score, breakdown: {bucket: {raw, weight, weighted}}, deductions: int}.
    """
    bucket_scores: dict[str, float] = {b: 10.0 for b in _WEIGHT_BUCKETS}

    deduction_count = 0
    for item in items:
        if item.get("action") in ("verified-fixed", "warn"):
            continue
        severity = item.get("severity", "medium")
        category = item.get("category", "quality")
        bucket = _category_to_bucket(category)
        deduction = _SEVERITY_DEDUCTIONS.get(severity, 0.3)
        bucket_scores[bucket] = max(0.0, bucket_scores[bucket] - deduction)
        deduction_count += 1

    score = 0.0
    breakdown: dict[str, dict] = {}
    for bucket, (weight, _) in _WEIGHT_BUCKETS.items():
        raw = round(bucket_scores[bucket], 1)
        weighted = round(raw * weight, 2)
        score += weighted
        breakdown[bucket] = {"raw": raw, "weight": weight, "weighted": weighted}

    return {
        "score": round(score, 1),
        "breakdown": breakdown,
        "deductions": deduction_count,
    }


# ---------------------------------------------------------------------------
# Delta audit — compare current findings to knowledge baseline
# ---------------------------------------------------------------------------


# Map keywords found in knowledge topics → canonical finding category.
# Built from weight bucket categories + common domain synonyms.
_CATEGORY_KEYWORDS: list[tuple[str, str]] = [
    # security bucket
    ("security", "security"), ("vulnerab", "security"), ("license", "security"),
    ("supply-chain", "security"), ("auth", "security"), ("injection", "security"),
    ("cve", "security"), ("cwe", "security"), ("owasp", "security"),
    ("secret", "security"), ("credential", "security"), ("xss", "security"),
    ("csrf", "security"), ("encrypt", "security"), ("tls", "security"),
    # architecture bucket
    ("architect", "architecture"), ("design", "architecture"), ("modulari", "architecture"),
    ("coupling", "architecture"), ("cohesion", "architecture"), ("layer", "architecture"),
    ("circular", "architecture"), ("dependency", "architecture"), ("structur", "architecture"),
    # testing bucket
    ("test", "testing"), ("coverage", "testing"), ("ci", "testing"),
    ("assert", "testing"), ("fixture", "testing"), ("mock", "testing"),
    # performance bucket
    ("perform", "performance"), ("scal", "performance"), ("memory", "performance"),
    ("n+1", "performance"), ("latency", "performance"), ("cache", "performance"),
    ("query", "performance"), ("slow", "performance"), ("bottleneck", "performance"),
    # code_quality bucket
    ("quality", "quality"), ("style", "quality"), ("duplicat", "quality"),
    ("complex", "quality"), ("dead-code", "quality"), ("lint", "quality"),
    ("refactor", "quality"), ("naming", "quality"), ("readab", "quality"),
    # documentation bucket
    ("document", "documentation"), ("readme", "documentation"), ("comment", "documentation"),
    ("docstring", "documentation"),
]


def _infer_category(topic: str) -> str:
    """Infer finding category from knowledge topic name.

    Scans for domain keywords (substrings) in priority order.
    Falls back to 'quality' if nothing matches.
    """
    topic_lower = topic.lower()
    for keyword, category in _CATEGORY_KEYWORDS:
        if keyword in topic_lower:
            return category
    return "quality"


def compute_delta(
    current_items: list[dict], knowledge_entries: list[dict]
) -> dict:
    """Compare current findings to knowledge-derived baseline.

    Builds baseline from knowledge entries tagged with "review".
    Matches by finding_id when available, fallback to (category, file).

    Returns {new, resolved, persistent, trend, summary}.
    """

    def _key(item: dict) -> str:
        fid = item.get("finding_id", "")
        if fid:
            return fid
        return f"{item.get('category', '')}|{item.get('file', '')}"

    # Build baseline from knowledge entries tagged with "review"
    baseline_items: list[dict] = []
    for entry in knowledge_entries:
        if "review" not in entry.get("tags", []):
            continue
        for ref_file in entry.get("referenced_files", []):
            baseline_items.append({
                "category": _infer_category(entry.get("topic", "")),
                "file": ref_file,
                "finding_id": "",
            })

    current_map = {_key(i): i for i in current_items}
    baseline_map = {_key(i): i for i in baseline_items}

    current_keys = set(current_map)
    baseline_keys = set(baseline_map)

    new_count = len(current_keys - baseline_keys)
    resolved_count = len(baseline_keys - current_keys)
    persistent_count = len(current_keys & baseline_keys)

    if not baseline_items:
        trend = "baseline"
    elif resolved_count > new_count:
        trend = "improving"
    elif new_count > resolved_count:
        trend = "declining"
    else:
        trend = "stable"

    return {
        "new": new_count,
        "resolved": resolved_count,
        "persistent": persistent_count,
        "trend": trend,
        "summary": f"{new_count} new, {resolved_count} resolved, {persistent_count} persistent — {trend}",
    }
