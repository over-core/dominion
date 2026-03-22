"""Tests for v0.4.0 progress tools — advance_step execute fix, quality_gate filter, generate_phase_report."""

from pathlib import Path

import pytest

from dominion_mcp.core.config import write_toml


@pytest.fixture()
def _patch_dom_root(dom_root_with_plan: Path, monkeypatch: pytest.MonkeyPatch):
    """Monkeypatch find_dominion_root to return the test fixture."""
    monkeypatch.setattr(
        "dominion_mcp.tools.progress.find_dominion_root",
        lambda: dom_root_with_plan,
    )
    return dom_root_with_plan


@pytest.fixture()
def _patch_dom_root_bare(dom_root: Path, monkeypatch: pytest.MonkeyPatch):
    """Monkeypatch find_dominion_root to return the bare test fixture."""
    monkeypatch.setattr(
        "dominion_mcp.tools.progress.find_dominion_root",
        lambda: dom_root,
    )
    return dom_root


# -- advance_step execute fix -----------------------------------------------


@pytest.mark.asyncio
async def test_advance_step_execute_checks_tasks_not_output(_patch_dom_root: Path):
    """Execute step should check task completions, not step/output/ dir."""
    from dominion_mcp.tools.progress import advance_step

    dom = _patch_dom_root
    phase_dir = dom / "phases" / "01"

    # Set up execute step as active
    (phase_dir / "execute" / "status").write_text("active")

    # Create tasks with complete status (NOT step-level output)
    tasks_dir = phase_dir / "tasks"
    for tid in ("01", "02"):
        task_dir = tasks_dir / tid
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "status").write_text("complete")
        out_dir = task_dir / "output"
        out_dir.mkdir()
        (out_dir / "result.toml").write_text("[ok]\n")

    # Clear execute/output/ — this is the bug scenario
    execute_output = phase_dir / "execute" / "output"
    for f in execute_output.iterdir():
        f.unlink()

    result = await advance_step("01", "execute")
    assert result.get("status") == "advanced"


@pytest.mark.asyncio
async def test_advance_step_execute_fails_with_incomplete_tasks(_patch_dom_root: Path):
    """Execute step should fail if any tasks are not complete."""
    from dominion_mcp.tools.progress import advance_step

    dom = _patch_dom_root
    phase_dir = dom / "phases" / "01"
    (phase_dir / "execute" / "status").write_text("active")

    tasks_dir = phase_dir / "tasks"
    t1 = tasks_dir / "01"
    t1.mkdir(parents=True, exist_ok=True)
    (t1 / "status").write_text("complete")

    t2 = tasks_dir / "02"
    t2.mkdir(parents=True, exist_ok=True)
    (t2 / "status").write_text("active")

    result = await advance_step("01", "execute")
    assert "error" in result
    assert "02" in result["error"]


# -- quality_gate verified-fixed filter -------------------------------------


@pytest.mark.asyncio
async def test_quality_gate_filters_verified_fixed(_patch_dom_root: Path):
    """Findings marked verified-fixed should not count as blocking."""
    from dominion_mcp.tools.progress import quality_gate

    dom = _patch_dom_root
    review_output = dom / "phases" / "01" / "review" / "output"
    write_toml(review_output / "verdict.toml", {
        "findings": {
            "reviewer": {
                "verdict": "go-with-warnings",
                "items": [
                    {"severity": "critical", "category": "security", "file": "a.py", "description": "SQL injection", "action": "verified-fixed"},
                    {"severity": "high", "category": "perf", "file": "b.py", "description": "N+1 query", "action": "verified-fixed"},
                    {"severity": "medium", "category": "style", "file": "c.py", "description": "naming"},
                ],
            },
        },
    })

    result = await quality_gate("01")
    assert len(result["blocking_findings"]) == 0
    assert result["action"] == "proceed"


@pytest.mark.asyncio
async def test_quality_gate_reviewer_overwrites_stale_specialist(_patch_dom_root: Path):
    """Cross-cutting reviewer verdict should overwrite stale specialist finding."""
    from dominion_mcp.tools.progress import quality_gate

    dom = _patch_dom_root
    review_output = dom / "phases" / "01" / "review" / "output"
    write_toml(review_output / "verdict.toml", {
        "findings": {
            "security-auditor": {
                "items": [
                    {"severity": "critical", "category": "security", "file": "a.py", "description": "SQL injection"},
                ],
            },
            "reviewer": {
                "verdict": "go-with-warnings",
                "items": [
                    {"severity": "critical", "category": "security", "file": "a.py", "description": "SQL injection", "action": "verified-fixed"},
                ],
            },
        },
    })

    result = await quality_gate("01")
    assert len(result["blocking_findings"]) == 0
    assert result["action"] == "proceed"


@pytest.mark.asyncio
async def test_quality_gate_blocks_unfixed_findings(_patch_dom_root: Path):
    """Unfixed critical findings should still block."""
    from dominion_mcp.tools.progress import quality_gate

    dom = _patch_dom_root
    review_output = dom / "phases" / "01" / "review" / "output"
    write_toml(review_output / "verdict.toml", {
        "findings": {
            "reviewer": {
                "verdict": "no-go",
                "items": [
                    {"severity": "critical", "category": "security", "file": "a.py", "description": "SQL injection"},
                ],
            },
        },
    })

    result = await quality_gate("01")
    assert len(result["blocking_findings"]) == 1
    assert result["action"] == "halt"


# -- quality_gate v0.4.3 dedup improvements --------------------------------


@pytest.mark.asyncio
async def test_quality_gate_dedup_different_descriptions(_patch_dom_root: Path):
    """Same finding with different wording should dedup by category|file."""
    from dominion_mcp.tools.progress import quality_gate

    dom = _patch_dom_root
    review_output = dom / "phases" / "01" / "review" / "output"
    write_toml(review_output / "verdict.toml", {
        "findings": {
            "analyst": {
                "items": [
                    {"severity": "critical", "category": "runtime", "file": "main.py:5", "description": "Relative imports will crash"},
                ],
            },
            "reviewer": {
                "verdict": "go-with-warnings",
                "items": [
                    {"severity": "critical", "category": "runtime", "file": "main.py:5", "description": "Relative imports fixed", "action": "verified-fixed"},
                ],
            },
        },
    })

    result = await quality_gate("01")
    assert len(result["blocking_findings"]) == 0
    assert result["action"] == "proceed"


@pytest.mark.asyncio
async def test_quality_gate_finding_id_supersession(_patch_dom_root: Path):
    """Reviewer referencing a specialist finding_id should supersede it."""
    from dominion_mcp.tools.progress import quality_gate

    dom = _patch_dom_root
    review_output = dom / "phases" / "01" / "review" / "output"
    write_toml(review_output / "verdict.toml", {
        "findings": {
            "security-auditor": {
                "items": [
                    {"finding_id": "security-auditor-01", "severity": "critical", "category": "security", "file": "auth.py", "description": "SQL injection found"},
                ],
            },
            "reviewer": {
                "verdict": "go-with-warnings",
                "items": [
                    {"finding_id": "security-auditor-01", "severity": "critical", "category": "security", "file": "auth.py", "description": "SQL injection patched", "action": "verified-fixed"},
                ],
            },
        },
    })

    result = await quality_gate("01")
    assert len(result["blocking_findings"]) == 0
    assert result["action"] == "proceed"


@pytest.mark.asyncio
async def test_quality_gate_multiple_findings_same_file(_patch_dom_root: Path):
    """Two distinct findings in same file — only the unfixed one should block."""
    from dominion_mcp.tools.progress import quality_gate

    dom = _patch_dom_root
    review_output = dom / "phases" / "01" / "review" / "output"
    write_toml(review_output / "verdict.toml", {
        "findings": {
            "reviewer": {
                "verdict": "no-go",
                "items": [
                    {"severity": "critical", "category": "security", "file": "auth.py", "description": "SQL injection", "action": "verified-fixed"},
                    {"severity": "high", "category": "perf", "file": "auth.py", "description": "N+1 query"},
                ],
            },
        },
    })

    result = await quality_gate("01")
    assert len(result["blocking_findings"]) == 1
    assert result["blocking_findings"][0]["category"] == "perf"


@pytest.mark.asyncio
async def test_quality_gate_backward_compat_no_finding_ids(_patch_dom_root: Path):
    """Findings without finding_ids should still work via structural dedup."""
    from dominion_mcp.tools.progress import quality_gate

    dom = _patch_dom_root
    review_output = dom / "phases" / "01" / "review" / "output"
    write_toml(review_output / "verdict.toml", {
        "findings": {
            "analyst": {
                "items": [
                    {"severity": "high", "category": "perf", "file": "db.py", "description": "Missing index on users table"},
                ],
            },
            "reviewer": {
                "verdict": "go-with-warnings",
                "items": [
                    {"severity": "high", "category": "perf", "file": "db.py", "description": "Index added to users table", "action": "verified-fixed"},
                ],
            },
        },
    })

    result = await quality_gate("01")
    assert len(result["blocking_findings"]) == 0
    assert result["action"] == "proceed"


# -- generate_phase_report --------------------------------------------------


@pytest.mark.asyncio
async def test_generate_phase_report_basic(_patch_dom_root: Path):
    """Phase report should compute metrics from filesystem data."""
    from dominion_mcp.tools.progress import generate_phase_report

    dom = _patch_dom_root

    # Create task statuses
    tasks_dir = dom / "phases" / "01" / "tasks"
    for tid in ("01", "02"):
        td = tasks_dir / tid
        td.mkdir(parents=True, exist_ok=True)
        (td / "status").write_text("complete")

    # Create review verdict
    review_output = dom / "phases" / "01" / "review" / "output"
    write_toml(review_output / "verdict.toml", {
        "findings": {
            "reviewer": {
                "verdict": "go-with-warnings",
                "items": [
                    {"severity": "high", "category": "perf", "file": "b.py", "description": "N+1"},
                    {"severity": "medium", "category": "style", "file": "c.py", "description": "naming"},
                ],
            },
        },
    })

    result = await generate_phase_report("01")
    assert result["phase"] == "01"
    assert result["tasks_total"] >= 2
    assert result["tasks_completed"] == 2
    assert result["tasks_failed"] == 0
    assert result["waves"] == 2
    assert "high" in result["findings_by_severity"]

    # Verify report.toml was written
    report_path = dom / "phases" / "01" / "report.toml"
    assert report_path.exists()


@pytest.mark.asyncio
async def test_generate_phase_report_no_phase(_patch_dom_root_bare: Path):
    """Missing phase returns error."""
    from dominion_mcp.tools.progress import generate_phase_report

    result = await generate_phase_report("99")
    assert "error" in result
