"""Course correction — severity-based verdict assessment and halt logic."""

from __future__ import annotations

from pathlib import Path

from .config import current_phase, phase_path, read_toml_optional

VERDICT_TYPES = ("go", "go-with-warnings", "no-go")
HALT_SEVERITY_LEVELS = ("critical", "warning", "none")

# Finding severities that trigger no-go verdict.
_BLOCKING_SEVERITIES = {"high", "critical"}
# Finding categories that are especially blocking.
_BLOCKING_CATEGORIES = {"architecture", "security"}


def assess_verdict(dom_root: Path, phase_id: int | None = None) -> dict:
    """Assess review verdict from phase artifacts.

    Reads review.toml and test-report.toml. Analyzes finding severities.

    Returns:
        {
            "verdict": "go" | "go-with-warnings" | "no-go",
            "critical_findings": int,
            "warning_findings": int,
            "blocking_findings": list[dict],
            "summary": str,
        }
    """
    if phase_id is None:
        phase_id = current_phase(dom_root)
    if phase_id == 0:
        return {
            "verdict": "go",
            "critical_findings": 0,
            "warning_findings": 0,
            "blocking_findings": [],
            "summary": "No active phase.",
        }

    p_path = phase_path(dom_root, phase_id)
    review = read_toml_optional(p_path / "review.toml") or {}
    test_report = read_toml_optional(p_path / "test-report.toml") or {}

    findings = review.get("findings", []) + test_report.get("findings", [])

    if not findings:
        return {
            "verdict": "go",
            "critical_findings": 0,
            "warning_findings": 0,
            "blocking_findings": [],
            "summary": "No findings — clear to proceed.",
        }

    blocking: list[dict] = []
    warning_count = 0

    for f in findings:
        severity = f.get("severity", "").lower()
        category = f.get("category", "").lower()

        if severity in _BLOCKING_SEVERITIES:
            blocking.append(f)
        elif severity in ("medium", "warning"):
            if category in _BLOCKING_CATEGORIES:
                blocking.append(f)
            else:
                warning_count += 1
        elif severity == "low":
            warning_count += 1

    if blocking:
        verdict = "no-go"
        summary = (
            f"{len(blocking)} blocking finding(s) require attention before proceeding."
        )
    elif warning_count > 0:
        verdict = "go-with-warnings"
        summary = f"{warning_count} warning(s) recorded. Proceeding with caution."
    else:
        verdict = "go"
        summary = "All findings are informational — clear to proceed."

    return {
        "verdict": verdict,
        "critical_findings": len(blocking),
        "warning_findings": warning_count,
        "blocking_findings": blocking,
        "summary": summary,
    }


def should_halt(dom_root: Path, verdict: dict) -> bool:
    """Determine if the pipeline should halt based on verdict and config.

    Reads dominion.toml [auto].halt_on_severity (default "critical").
    """
    dominion = read_toml_optional(dom_root / "dominion.toml") or {}
    auto_config = dominion.get("auto", {})
    threshold = auto_config.get("halt_on_severity", "critical")

    if threshold == "none":
        return False

    verdict_type = verdict.get("verdict", "go")

    if threshold == "warning":
        return verdict_type in ("no-go", "go-with-warnings")
    # Default: "critical"
    return verdict_type == "no-go"


def get_correction_action(dom_root: Path, verdict: dict) -> dict:
    """Determine correction action based on verdict and autonomy mode.

    Returns:
        {
            "action": "proceed" | "halt" | "auto_fix",
            "reason": str,
            "fix_attempts_remaining": int,
            "blocking_findings": list[dict],
        }
    """
    verdict_type = verdict.get("verdict", "go")

    if verdict_type == "go":
        return {
            "action": "proceed",
            "reason": "No blocking findings.",
            "fix_attempts_remaining": 0,
            "blocking_findings": [],
        }

    dominion = read_toml_optional(dom_root / "dominion.toml") or {}
    auto_config = dominion.get("auto", {})
    autonomy = dominion.get("autonomy", {})
    mode = autonomy.get("mode", "interactive")
    max_fixes = auto_config.get("max_fix_attempts", 1)

    blocking = verdict.get("blocking_findings", [])

    if mode == "interactive" or not should_halt(dom_root, verdict):
        if verdict_type == "go-with-warnings" and not should_halt(dom_root, verdict):
            return {
                "action": "proceed",
                "reason": verdict.get("summary", "Warnings recorded."),
                "fix_attempts_remaining": 0,
                "blocking_findings": [],
            }
        return {
            "action": "halt",
            "reason": verdict.get("summary", "Review found blocking issues."),
            "fix_attempts_remaining": 0,
            "blocking_findings": blocking,
        }

    # Auto mode with halt threshold met.
    state = read_toml_optional(dom_root / "state.toml") or {}
    fix_attempts = state.get("fix_attempts", 0)

    if fix_attempts < max_fixes:
        return {
            "action": "auto_fix",
            "reason": f"Auto-fix attempt {fix_attempts + 1}/{max_fixes}.",
            "fix_attempts_remaining": max_fixes - fix_attempts - 1,
            "blocking_findings": blocking,
        }

    return {
        "action": "halt",
        "reason": f"Max fix attempts ({max_fixes}) exhausted. Halting for user review.",
        "fix_attempts_remaining": 0,
        "blocking_findings": blocking,
    }
