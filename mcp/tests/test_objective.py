"""Tests for dominion_mcp.core.objective — multi-session feature tracking."""

from __future__ import annotations

from pathlib import Path

import pytest

from dominion_mcp.core.config import read_toml_optional
from dominion_mcp.core.objective import (
    complete_objective,
    create_objective,
    get_objective,
    link_phase_to_objective,
    read_objectives,
)


# -- create_objective -------------------------------------------------------


@pytest.mark.asyncio
async def test_create_objective(dom_root: Path):
    result = await create_objective(dom_root, "Auth Rewrite", "Rewrite auth module")
    assert result["id"] == "auth-rewrite"
    assert result["name"] == "Auth Rewrite"
    assert result["status"] == "in-progress"
    assert result["summary"] == "Rewrite auth module"
    assert result["phases"] == []

    # Verify persisted
    data = read_toml_optional(dom_root / "objectives.toml")
    assert data is not None
    assert len(data["objectives"]) == 1
    assert data["objectives"][0]["id"] == "auth-rewrite"


@pytest.mark.asyncio
async def test_create_objective_duplicate(dom_root: Path):
    await create_objective(dom_root, "Auth Rewrite", "Rewrite auth module")
    await create_objective(dom_root, "Auth Rewrite", "Second description")

    objs = read_objectives(dom_root)
    assert len(objs) == 1


@pytest.mark.asyncio
async def test_create_objective_slugify(dom_root: Path):
    result = await create_objective(
        dom_root, "My SUPER  Feature!!!", "Testing slug generation"
    )
    slug = result["id"]
    # Lowercase, hyphens, no special chars, max 30
    assert slug == "my-super-feature"
    assert len(slug) <= 30


# -- link_phase_to_objective ------------------------------------------------


@pytest.mark.asyncio
async def test_link_phase_to_objective(dom_root: Path):
    await create_objective(dom_root, "Rate Limiting", "Add rate limits")
    result = await link_phase_to_objective(dom_root, "01", "rate-limiting")
    assert result["status"] == "linked"
    assert result["phase"] == "01"

    objs = read_objectives(dom_root)
    assert "01" in objs[0]["phases"]


@pytest.mark.asyncio
async def test_link_phase_idempotent(dom_root: Path):
    await create_objective(dom_root, "Rate Limiting", "Add rate limits")
    await link_phase_to_objective(dom_root, "01", "rate-limiting")
    await link_phase_to_objective(dom_root, "01", "rate-limiting")

    objs = read_objectives(dom_root)
    assert objs[0]["phases"].count("01") == 1


@pytest.mark.asyncio
async def test_link_phase_not_found(dom_root: Path):
    result = await link_phase_to_objective(dom_root, "01", "nonexistent")
    assert "error" in result


# -- get_objective ----------------------------------------------------------


@pytest.mark.asyncio
async def test_get_objective_all_active(dom_root: Path):
    await create_objective(dom_root, "Feature A", "First")
    await create_objective(dom_root, "Feature B", "Second")
    await complete_objective(dom_root, "feature-a")

    active = get_objective(dom_root)
    assert isinstance(active, list)
    assert len(active) == 1
    assert active[0]["id"] == "feature-b"


@pytest.mark.asyncio
async def test_get_objective_enriched(dom_root: Path):
    await create_objective(dom_root, "Rate Limiting", "Add rate limits")
    await link_phase_to_objective(dom_root, "01", "rate-limiting")

    result = get_objective(dom_root, "rate-limiting")
    assert isinstance(result, dict)
    assert "phases_detail" in result
    assert len(result["phases_detail"]) == 1
    assert result["phases_detail"][0]["id"] == "01"
    assert result["phases_detail"][0]["intent"] == "Add rate limiting"


# -- complete_objective -----------------------------------------------------


@pytest.mark.asyncio
async def test_complete_objective(dom_root: Path):
    await create_objective(dom_root, "Auth Rewrite", "Rewrite auth")
    result = await complete_objective(dom_root, "auth-rewrite", summary="Done!")
    assert result["status"] == "complete"

    objs = read_objectives(dom_root)
    obj = objs[0]
    assert obj["status"] == "complete"
    assert obj["completed"] != ""
    assert obj["summary"] == "Done!"
