"""Tests for core/events module — JSONL event emission and reading."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dominion_mcp.core.events import emit_event, read_events


@pytest.mark.asyncio
async def test_emit_event_creates_jsonl(dom_root: Path):
    """emit_event writes a valid JSON line with all required fields."""
    result = await emit_event(dom_root, "01", "step.started", step="research", role="researcher")

    events_file = dom_root / "phases" / "01" / "events.jsonl"
    assert events_file.exists()

    line = events_file.read_text().strip()
    parsed = json.loads(line)
    assert parsed["event"] == "step.started"
    assert parsed["phase"] == "01"
    assert parsed["step"] == "research"
    assert parsed["role"] == "researcher"
    assert "ts" in parsed
    # Return value matches what was written
    assert result == parsed


@pytest.mark.asyncio
async def test_emit_event_appends(dom_root: Path):
    """Multiple events append to the same file."""
    await emit_event(dom_root, "01", "step.started")
    await emit_event(dom_root, "01", "step.completed")

    events_file = dom_root / "phases" / "01" / "events.jsonl"
    lines = [l for l in events_file.read_text().strip().splitlines() if l]
    assert len(lines) == 2
    assert json.loads(lines[0])["event"] == "step.started"
    assert json.loads(lines[1])["event"] == "step.completed"


@pytest.mark.asyncio
async def test_emit_event_optional_fields(dom_root: Path):
    """Omitted optional fields are not present in the output."""
    result = await emit_event(dom_root, "01", "phase.started")

    assert "step" not in result
    assert "role" not in result
    assert "task_id" not in result
    assert "data" not in result
    # Required fields are present
    assert "ts" in result
    assert result["event"] == "phase.started"
    assert result["phase"] == "01"


@pytest.mark.asyncio
async def test_emit_event_creates_parent_dirs(dom_root: Path):
    """emit_event creates phase dir if it doesn't exist yet."""
    # Phase 99 doesn't exist in the fixture
    result = await emit_event(dom_root, "99", "phase.started")

    events_file = dom_root / "phases" / "99" / "events.jsonl"
    assert events_file.exists()
    assert result["phase"] == "99"


def test_read_events_returns_recent(dom_root: Path):
    """read_events returns the most recent N events in chronological order."""
    events_file = dom_root / "phases" / "01" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)

    # Write 5 events
    for i in range(5):
        entry = {"ts": f"2026-03-18T09:0{i}:00Z", "event": f"evt-{i}", "phase": "01"}
        events_file.open("a").write(json.dumps(entry) + "\n")

    # Read last 3
    result = read_events(dom_root, "01", limit=3)
    assert len(result) == 3
    # Chronological: most recent last
    assert result[0]["event"] == "evt-2"
    assert result[1]["event"] == "evt-3"
    assert result[2]["event"] == "evt-4"


def test_read_events_with_filter(dom_root: Path):
    """event_filter limits returned events to matching types."""
    events_file = dom_root / "phases" / "01" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)

    entries = [
        {"ts": "2026-03-18T09:00:00Z", "event": "step.started", "phase": "01"},
        {"ts": "2026-03-18T09:01:00Z", "event": "step.completed", "phase": "01"},
        {"ts": "2026-03-18T09:02:00Z", "event": "step.started", "phase": "01"},
        {"ts": "2026-03-18T09:03:00Z", "event": "task.assigned", "phase": "01"},
    ]
    for entry in entries:
        events_file.open("a").write(json.dumps(entry) + "\n")

    result = read_events(dom_root, "01", event_filter={"step.started"})
    assert len(result) == 2
    assert all(e["event"] == "step.started" for e in result)


def test_read_events_no_file(dom_root: Path):
    """read_events returns empty list when events.jsonl doesn't exist."""
    result = read_events(dom_root, "42")
    assert result == []


@pytest.mark.asyncio
async def test_start_phase_emits_event(dom_root: Path):
    """start_phase emits a phase_started event."""
    import dominion_mcp.tools.setup as setup_mod
    from dominion_mcp.tools.setup import start_phase

    original = setup_mod.find_dominion_root
    setup_mod.find_dominion_root = lambda: dom_root
    try:
        result = await start_phase(intent="Test feature", pipeline=["research", "plan", "execute", "review"])
    finally:
        setup_mod.find_dominion_root = original

    phase = result["phase"]
    events = read_events(dom_root, phase=phase)
    phase_events = [e for e in events if e["event"] == "phase_started"]
    assert len(phase_events) == 1
    assert phase_events[0]["data"]["pipeline"] == ["research", "plan", "execute", "review"]


@pytest.mark.asyncio
async def test_advance_step_emits_event(dom_root_with_plan: Path):
    """advance_step emits a step_advanced event."""
    import dominion_mcp.tools.progress as prog_mod
    from dominion_mcp.tools.progress import advance_step

    original = prog_mod.find_dominion_root
    prog_mod.find_dominion_root = lambda: dom_root_with_plan
    try:
        result = await advance_step(phase="01", step="research")
    finally:
        prog_mod.find_dominion_root = original

    events = read_events(dom_root_with_plan, phase="01")
    advance_events = [e for e in events if e["event"] == "step_advanced"]
    assert len(advance_events) == 1
    assert advance_events[0]["data"]["from_step"] == "research"


@pytest.mark.asyncio
async def test_submit_work_emits_event(dom_root_with_plan: Path):
    """submit_work emits work_submitted event."""
    import json
    import dominion_mcp.tools.submit as submit_mod

    original = submit_mod.find_dominion_root
    submit_mod.find_dominion_root = lambda: dom_root_with_plan
    try:
        content = json.dumps({"items": [{"severity": "medium", "category": "test", "description": "d", "file": "f.py"}]})
        await submit_mod.submit_work(phase="01", step="research", role="researcher", content=content, summary="Test")
    finally:
        submit_mod.find_dominion_root = original

    events = read_events(dom_root_with_plan, phase="01")
    work_events = [e for e in events if e["event"] == "work_submitted"]
    assert len(work_events) >= 1
    assert work_events[0]["role"] == "researcher"


@pytest.mark.asyncio
async def test_signal_blocker_emits_event(dom_root_with_plan: Path):
    """signal_blocker emits blocker_signaled event."""
    import dominion_mcp.tools.submit as submit_mod

    # Create task dir
    task_dir = dom_root_with_plan / "phases" / "01" / "tasks" / "t1"
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "status").write_text("active")
    (task_dir / "output").mkdir(exist_ok=True)

    original = submit_mod.find_dominion_root
    submit_mod.find_dominion_root = lambda: dom_root_with_plan
    try:
        await submit_mod.signal_blocker(phase="01", task_id="t1", reason="Stuck on dependency")
    finally:
        submit_mod.find_dominion_root = original

    events = read_events(dom_root_with_plan, phase="01")
    blocker_events = [e for e in events if e["event"] == "blocker_signaled"]
    assert len(blocker_events) == 1
    assert blocker_events[0]["data"]["reason"] == "Stuck on dependency"


@pytest.mark.asyncio
async def test_start_phase_with_objective(dom_root: Path):
    """start_phase links to objective when objective param provided."""
    from dominion_mcp.core.objective import create_objective, read_objectives

    # Create an objective first
    obj = await create_objective(dom_root, name="Auth Rewrite", description="Rewrite auth")

    import dominion_mcp.tools.setup as setup_mod
    original = setup_mod.find_dominion_root
    setup_mod.find_dominion_root = lambda: dom_root
    try:
        result = await setup_mod.start_phase(intent="Implement JWT", pipeline=["research", "plan", "execute", "review"], objective=obj["id"])
    finally:
        setup_mod.find_dominion_root = original

    phase = result["phase"]

    # Verify objective is linked
    objectives = read_objectives(dom_root)
    auth_obj = [o for o in objectives if o["id"] == obj["id"]][0]
    assert phase in auth_obj["phases"]

    # Verify event includes objective_id
    events = read_events(dom_root, phase=phase)
    started = [e for e in events if e["event"] == "phase_started"][0]
    assert started["data"]["objective_id"] == obj["id"]


@pytest.mark.asyncio
async def test_start_phase_custom_pipeline(dom_root: Path):
    """start_phase accepts a custom pipeline subset."""
    import dominion_mcp.tools.setup as setup_mod

    original = setup_mod.find_dominion_root
    setup_mod.find_dominion_root = lambda: dom_root
    try:
        result = await setup_mod.start_phase(
            intent="Quick scan",
            pipeline=["research", "review"],
        )
    finally:
        setup_mod.find_dominion_root = original

    assert result["pipeline"] == ["research", "review"]
    phase_dir = dom_root / "phases" / result["phase"]
    assert (phase_dir / "research").exists()
    assert (phase_dir / "review").exists()
    assert not (phase_dir / "plan").exists()
    assert not (phase_dir / "execute").exists()

    # Verify pipeline persisted in state.toml
    from dominion_mcp.core.state import get_position
    pos = get_position(dom_root)
    assert pos["pipeline"] == ["research", "review"]


@pytest.mark.asyncio
async def test_get_progress_reads_stored_pipeline(dom_root: Path):
    """get_progress returns the stored pipeline, not re-derived from complexity."""
    import dominion_mcp.tools.setup as setup_mod
    import dominion_mcp.tools.progress as prog_mod

    original_setup = setup_mod.find_dominion_root
    original_prog = prog_mod.find_dominion_root
    setup_mod.find_dominion_root = lambda: dom_root
    prog_mod.find_dominion_root = lambda: dom_root
    try:
        await setup_mod.start_phase(
            intent="Quick audit",
            pipeline=["research", "review"],
        )
        progress = await prog_mod.get_progress()
    finally:
        setup_mod.find_dominion_root = original_setup
        prog_mod.find_dominion_root = original_prog

    # Should reflect custom pipeline, NOT moderate's default
    assert progress["pipeline"] == ["research", "review"]


@pytest.mark.asyncio
async def test_start_phase_rejects_invalid_pipeline_step(dom_root: Path):
    """start_phase returns error for unknown step names."""
    import dominion_mcp.tools.setup as setup_mod

    original = setup_mod.find_dominion_root
    setup_mod.find_dominion_root = lambda: dom_root
    try:
        result = await setup_mod.start_phase(
            intent="Test",
            pipeline=["research", "bogus"],
        )
    finally:
        setup_mod.find_dominion_root = original

    assert "error" in result
    assert "bogus" in result["error"]


@pytest.mark.asyncio
async def test_start_phase_rejects_misordered_pipeline(dom_root: Path):
    """start_phase returns error when pipeline violates canonical order."""
    import dominion_mcp.tools.setup as setup_mod

    original = setup_mod.find_dominion_root
    setup_mod.find_dominion_root = lambda: dom_root
    try:
        result = await setup_mod.start_phase(
            intent="Test",
            pipeline=["plan", "research"],
        )
    finally:
        setup_mod.find_dominion_root = original

    assert "error" in result
    assert "canonical order" in result["error"]


@pytest.mark.asyncio
async def test_save_knowledge_emits_event(dom_root: Path):
    """save_knowledge emits knowledge_saved event."""
    import dominion_mcp.tools.knowledge as knowledge_mod

    original = knowledge_mod.find_dominion_root
    knowledge_mod.find_dominion_root = lambda: dom_root
    try:
        await knowledge_mod.save_knowledge(
            topic="test-topic", content="# Test\n\nContent about src/auth.py",
            tags="research,plan", summary="Test knowledge"
        )
    finally:
        knowledge_mod.find_dominion_root = original

    events = read_events(dom_root, phase="01")
    k_events = [e for e in events if e["event"] == "knowledge_saved"]
    assert len(k_events) == 1
    assert k_events[0]["data"]["topic"] == "test-topic"
