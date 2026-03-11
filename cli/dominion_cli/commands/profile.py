"""User profile and claim status commands."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import typer

from ..core.config import dominion_path
from ..core.formatters import error, info, output
from ..core.readers import read_toml, read_toml_optional, write_toml

app = typer.Typer(help="User profile management")

# User profile lives in ~/.claude/.dominion/
PROFILE_DIR = Path.home() / ".claude" / ".dominion"
PROFILE_PATH = PROFILE_DIR / "user-profile.toml"

VALID_LEVELS = ("beginner", "intermediate", "advanced")


@app.command()
def show(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Display current user profile."""
    if not PROFILE_PATH.exists():
        info("No profile found. Run /dominion:init to create one.")
        return

    profile = read_toml(PROFILE_PATH)
    user = profile.get("user", {})
    sessions = profile.get("sessions", {})
    prefs = user.get("preferences", {})
    opinions = profile.get("tool_opinions", {})

    data = {
        "experience_level": user.get("experience_level", "intermediate"),
        "sessions_count": sessions.get("count", 0),
        "first_session": sessions.get("first_session", ""),
        "last_session": sessions.get("last_session", ""),
        "preferences": prefs,
        "tool_opinions": opinions,
    }

    if json:
        output(data, json_mode=True)
        return

    info(f"  Experience: {data['experience_level']}")
    info(f"  Sessions: {data['sessions_count']} (first: {data['first_session'] or 'N/A'}, last: {data['last_session'] or 'N/A'})")
    if prefs:
        info("  Preferences:")
        for k, v in prefs.items():
            info(f"    {k}: {v}")
    if opinions:
        info("  Tool opinions:")
        for tool, opinion in opinions.items():
            if isinstance(opinion, dict):
                info(f"    {tool}: {opinion.get('rating', '?')}/5 — {opinion.get('notes', '')}")
            else:
                info(f"    {tool}: {opinion}")


@app.command()
def set(
    key: Annotated[str, typer.Argument(help="Preference key")],
    value: Annotated[str, typer.Argument(help="Preference value")],
) -> None:
    """Update a user profile preference."""
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    profile = read_toml_optional(PROFILE_PATH) or {"user": {"preferences": {}}, "sessions": {}}

    if key == "experience_level":
        if value not in VALID_LEVELS:
            error(f"Invalid level '{value}'. Must be one of: {', '.join(VALID_LEVELS)}")
            raise SystemExit(1)
        profile.setdefault("user", {})["experience_level"] = value
    else:
        profile.setdefault("user", {}).setdefault("preferences", {})[key] = value

    write_toml(PROFILE_PATH, profile)
    info(f"Set {key} = {value}")


@app.command()
def tick() -> None:
    """Increment session count in user profile."""
    if not PROFILE_PATH.exists():
        # Silently skip if no profile
        return

    profile = read_toml(PROFILE_PATH)
    sessions = profile.setdefault("sessions", {})
    count = sessions.get("count", 0) + 1
    sessions["count"] = count
    now = datetime.now(timezone.utc).isoformat()
    sessions["last_session"] = now
    if not sessions.get("first_session"):
        sessions["first_session"] = now

    write_toml(PROFILE_PATH, profile)
    info(f"Session {count} recorded.")


def claim_status(
    json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show brownfield claim provenance for this project."""
    dom = read_toml(dominion_path("dominion.toml"))
    claim = dom.get("claim", {})

    if not claim or not claim.get("claimed_at"):
        info("This project was initialized with /dominion:init (greenfield).")
        return

    data = {
        "claimed_at": claim.get("claimed_at", ""),
        "source_setup": claim.get("source_setup", ""),
        "preserved": claim.get("preserved", []),
        "added": claim.get("added", []),
    }

    if json:
        output(data, json_mode=True)
        return

    info(f"  Claimed: {data['claimed_at']}")
    info(f"  Source: {data['source_setup']}")
    if data["preserved"]:
        info(f"  Preserved: {len(data['preserved'])} artifacts")
        for a in data["preserved"]:
            if isinstance(a, dict):
                info(f"    {a.get('name', '')} — {a.get('sections', 0)} user-original sections")
            else:
                info(f"    {a}")
    if data["added"]:
        info(f"  Added: {len(data['added'])} artifacts")
        for a in data["added"]:
            if isinstance(a, dict):
                info(f"    {a.get('name', '')} — {a.get('source', '')}")
            else:
                info(f"    {a}")
