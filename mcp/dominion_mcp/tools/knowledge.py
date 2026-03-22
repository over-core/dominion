"""Knowledge tool — save_knowledge.

Manages project-specific knowledge files in .dominion/knowledge/.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..server import mcp
from ..core.config import find_dominion_root, read_toml_optional, write_toml

VALID_TAGS = {"discuss", "research", "plan", "execute", "review"}

# Regex to extract file paths from content (v0.4.3: expanded beyond src/lib/app prefixes)
_FILE_PATH_RE = re.compile(r'(?:^|\s)([\w][\w\-\.]*/[\w/\-\.]+)', re.MULTILINE)

# Regex to detect loose file references that the path regex might miss
_LOOSE_FILE_RE = re.compile(r'\b[\w\-]+\.(?:py|ts|js|rs|go|java|toml|yaml|yml|json|md|sql)\b')


@mcp.tool()
async def save_knowledge(
    topic: str, content: str, tags: str, summary: str
) -> dict:
    """Store/update a knowledge file in .dominion/knowledge/.

    Args:
        topic: Knowledge file topic (used as filename: {topic}.md).
        content: Markdown content.
        tags: Comma-separated tags from fixed set: discuss, research, plan, execute, review.
        summary: One-line description for index.toml entry.
    """
    if not content or not content.strip():
        return {"error": "Content is required."}
    if not summary or not summary.strip():
        return {"error": "Summary is required."}

    tag_list = [t.strip() for t in tags.split(",")]
    invalid = set(tag_list) - VALID_TAGS
    if invalid:
        return {"error": f"Invalid tags: {', '.join(invalid)}. Valid: {', '.join(VALID_TAGS)}"}

    try:
        dom_root = find_dominion_root()
    except ValueError:
        return {"error": ".dominion/ directory not found."}

    knowledge_dir = dom_root / "knowledge"
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    # Extract referenced files from content
    referenced_files = list(set(_FILE_PATH_RE.findall(content)))

    # Auto-split at >50KB
    content_bytes = content.encode("utf-8")
    split = False

    if len(content_bytes) > 50 * 1024:
        # Split by ## headers
        parts = _split_by_headers(content)
        split = True
        paths = []
        for i, part in enumerate(parts, 1):
            part_topic = f"{topic}-part{i}"
            part_path = knowledge_dir / f"{part_topic}.md"
            part_path.write_text(part)
            paths.append(part_path)
            _update_index(
                dom_root,
                part_topic,
                f"{summary} (part {i})",
                tag_list,
                f"{part_topic}.md",
                referenced_files,
            )
        result_path = str(paths[0].relative_to(dom_root.parent))
    else:
        file_path = knowledge_dir / f"{topic}.md"
        file_path.write_text(content)
        _update_index(dom_root, topic, summary, tag_list, f"{topic}.md", referenced_files)
        result_path = str(file_path.relative_to(dom_root.parent))

    result: dict = {
        "status": "saved",
        "path": result_path,
        "split": split,
    }

    # Warn if referenced_files is empty but content mentions file-like names
    if not referenced_files:
        loose = list(set(_LOOSE_FILE_RE.findall(content)))
        if loose:
            result["warning"] = (
                f"No referenced_files extracted but content mentions: {', '.join(loose[:5])}. "
                "Consider adding explicit directory-prefixed file paths (e.g., src/auth/login.py) "
                "so knowledge is scoped to relevant agents."
            )

    return result


def _update_index(
    dom_root: Path,
    topic: str,
    summary: str,
    tags: list[str],
    path: str,
    referenced_files: list[str],
) -> None:
    """Add/update an entry in knowledge/index.toml."""
    index_path = dom_root / "knowledge" / "index.toml"
    index = read_toml_optional(index_path) or {}
    entries = index.get("entries", [])

    # Update existing or append new
    found = False
    for entry in entries:
        if entry.get("topic") == topic:
            entry["summary"] = summary
            entry["tags"] = tags
            entry["path"] = path
            entry["referenced_files"] = referenced_files
            found = True
            break

    if not found:
        entries.append({
            "topic": topic,
            "summary": summary,
            "tags": tags,
            "path": path,
            "referenced_files": referenced_files,
        })

    index["entries"] = entries
    write_toml(index_path, index)


def _split_by_headers(content: str) -> list[str]:
    """Split markdown content by ## headers into parts."""
    parts: list[str] = []
    current: list[str] = []

    for line in content.splitlines(keepends=True):
        if line.startswith("## ") and current:
            parts.append("".join(current))
            current = []
        current.append(line)

    if current:
        parts.append("".join(current))

    # If no headers found, return as single part
    return parts if len(parts) > 1 else [content]
