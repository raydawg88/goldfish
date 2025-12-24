#!/usr/bin/env python3
"""
GOLDFISH TRANSCRIPT APPENDER (Tier 1: Auto-Save)

This runs automatically on session end / every 5 minutes.
It ONLY:
1. Reads session data extracted by reader.py
2. Appends raw transcripts to each project's large.md
3. Flags inbox.md with "new session needs processing"

NO quality summaries. That's Claude's job when /gfsave runs.
"""

import json
from pathlib import Path
from datetime import datetime

GOLDFISH_PATH = Path.home() / "Library" / "CloudStorage" / "Dropbox-Personal" / "Goldfish"
SESSION_ANALYSIS_PATH = GOLDFISH_PATH / ".goldfish" / "session-analysis.json"
PROCESSED_SESSIONS_PATH = GOLDFISH_PATH / ".goldfish" / "processed-sessions.json"

# Project to vault mapping
WORK_PROJECTS = {"velona", "element-ai", "fred", "fred-research", "verra-ai"}


def load_processed_sessions() -> set:
    """Load list of already-processed session IDs."""
    if PROCESSED_SESSIONS_PATH.exists():
        with open(PROCESSED_SESSIONS_PATH) as f:
            return set(json.load(f))
    return set()


def save_processed_sessions(processed: set):
    """Save list of processed session IDs."""
    with open(PROCESSED_SESSIONS_PATH, 'w') as f:
        json.dump(list(processed), f, indent=2)


def get_project_from_path(filepath: str) -> tuple:
    """Extract project name and vault from session filepath."""
    path = Path(filepath)

    # Look for project indicators in the path
    parts = path.parts

    # Check for Goldfish directory structure
    if "Goldfish" in parts:
        idx = parts.index("Goldfish")
        if len(parts) > idx + 2:
            vault = parts[idx + 1]  # work or personal
            project = parts[idx + 2]
            return (project, vault)

    # Check for project name in path
    for part in reversed(parts):
        part_lower = part.lower()
        # Skip common non-project directories
        if part_lower in {'.claude', 'projects', 'users', 'rayhernandez', 'library'}:
            continue
        # Check if it looks like a project
        if '-' in part or part_lower.isalpha():
            vault = "work" if part_lower in WORK_PROJECTS else "personal"
            return (part_lower, vault)

    return (None, None)


def format_transcript(session: dict) -> str:
    """Format a session as a readable transcript."""
    lines = []

    session_id = session.get("session_id", "unknown")[:8]
    date = session.get("date", "unknown")
    message_count = session.get("message_count", 0)

    lines.append(f"\n\n---\n")
    lines.append(f"## Session: {session_id}...")
    lines.append(f"**Date:** {date}")
    lines.append(f"**Messages:** {message_count}")
    lines.append("")

    # First user message as summary
    first_msg = session.get("first_user_message", "")
    if first_msg:
        preview = first_msg[:500]
        if len(first_msg) > 500:
            preview += "..."
        lines.append("**First message:**")
        lines.append(f"> {preview}")
        lines.append("")

    # Files touched
    files = session.get("files_touched", [])
    if files:
        lines.append("**Files touched:**")
        for f in files[:20]:
            lines.append(f"- `{f}`")
        if len(files) > 20:
            lines.append(f"- ... and {len(files) - 20} more")
        lines.append("")

    # Tools used
    tools = session.get("tools_used", [])
    if tools:
        lines.append(f"**Tools:** {', '.join(tools[:10])}")
        lines.append("")

    lines.append(f"*Raw transcript in ~/.claude session files*")

    return "\n".join(lines)


def update_inbox(project_path: Path, session: dict):
    """Add new session flag to inbox.md."""
    inbox_path = project_path / "goldfish" / "inbox.md"

    session_id = session.get("session_id", "unknown")[:8]
    date = session.get("date", datetime.now().strftime("%Y-%m-%d %H:%M"))
    first_msg = session.get("first_user_message", "")[:200]

    new_entry = f"""
---
## NEW SESSION: {session_id}...
**Date:** {date}
**Status:** NEEDS_PROCESSING

**Preview:**
> {first_msg}...

*Run /gfsave to generate quality summaries*
---
"""

    # Read existing or create new
    if inbox_path.exists():
        content = inbox_path.read_text()
    else:
        content = f"# {project_path.name} - Inbox\n\nNew sessions waiting for quality summaries.\n"

    # Append new entry at the top (after header)
    lines = content.split("\n")
    header_end = 0
    for i, line in enumerate(lines):
        if line.startswith("---") or line.startswith("## NEW SESSION"):
            header_end = i
            break
        header_end = i + 1

    new_content = "\n".join(lines[:header_end]) + new_entry + "\n".join(lines[header_end:])

    inbox_path.parent.mkdir(parents=True, exist_ok=True)
    inbox_path.write_text(new_content)


def append_to_large_md(project_path: Path, session: dict):
    """Append session transcript to large.md."""
    large_path = project_path / "goldfish" / "large.md"

    transcript = format_transcript(session)

    # Read existing or create new
    if large_path.exists():
        content = large_path.read_text()
    else:
        content = f"# {project_path.name} - Complete History\n\n*Full session transcripts appended automatically*\n"

    # Append transcript
    content += transcript

    large_path.parent.mkdir(parents=True, exist_ok=True)
    large_path.write_text(content)


def main():
    """Append new session transcripts and flag inbox."""
    print("=" * 60)
    print("  GOLDFISH TRANSCRIPT APPENDER (Tier 1: Auto-Save)")
    print("=" * 60)
    print()

    # Load session analysis from reader
    if not SESSION_ANALYSIS_PATH.exists():
        print("No session-analysis.json found. Run reader.py first.")
        return

    with open(SESSION_ANALYSIS_PATH) as f:
        raw_data = json.load(f)

    # Handle both list format (new) and dict format (old)
    if isinstance(raw_data, list):
        # New format: list of {info: {...}, classification: {...}}
        sessions = []
        for item in raw_data:
            info = item.get("info", {})
            classification = item.get("classification", {})
            # Merge info and classification
            session = {
                "session_id": info.get("session_id"),
                "filepath": info.get("filepath"),
                "date": info.get("date"),
                "message_count": info.get("message_count", 0),
                "first_user_message": info.get("first_user_message"),
                "files_touched": info.get("files_touched", []),
                "tools_used": info.get("tools_used", []),
                "project": classification.get("project"),
                "vault": classification.get("vault"),
            }
            sessions.append(session)
    else:
        # Old format: dict with "sessions" key
        sessions = raw_data.get("sessions", [])

    print(f"Found {len(sessions)} total sessions")

    # Load already-processed sessions
    processed = load_processed_sessions()
    print(f"Already processed: {len(processed)} sessions")

    # Find new sessions
    new_sessions = []
    for session in sessions:
        session_id = session.get("session_id")
        if session_id and session_id not in processed:
            new_sessions.append(session)

    if not new_sessions:
        print("\nNo new sessions to process.")
        return

    print(f"\nNew sessions to append: {len(new_sessions)}")

    # Process each new session
    for session in new_sessions:
        filepath = session.get("filepath", "")
        session_id = session.get("session_id", "unknown")

        # Get project/vault from classification first, fallback to path detection
        project = session.get("project")
        vault = session.get("vault")

        # Skip UNCLEAR or None projects
        if not project or project == "UNCLEAR":
            project, vault = get_project_from_path(filepath)

        if not project or project == "UNCLEAR":
            print(f"  SKIP: {session_id[:8]}... (couldn't determine project)")
            continue

        # Normalize vault
        if not vault or vault not in ("work", "personal"):
            vault = "work" if project.lower() in WORK_PROJECTS else "personal"

        # Find project directory
        project_path = GOLDFISH_PATH / vault / project.lower()

        if not project_path.exists():
            # Try the other vault
            other_vault = "personal" if vault == "work" else "work"
            alt_path = GOLDFISH_PATH / other_vault / project.lower()
            if alt_path.exists():
                project_path = alt_path
                vault = other_vault
            elif project.lower().startswith("no-category/"):
                # Auto-create no-category subdirectories
                project_path.mkdir(parents=True, exist_ok=True)
                goldfish_dir = project_path / "goldfish"
                goldfish_dir.mkdir(exist_ok=True)
                # Create initial small.md
                topic = project.split("/")[-1].replace("-", " ").title()
                small_md = goldfish_dir / "small.md"
                small_md.write_text(f"""# {topic}

**Uncategorized session**

Sessions: 1 | Last: {session.get('date', 'unknown')}

## Context
This session didn't match any project and wasn't explicit research.
If it becomes important, move it to a proper project folder.

---
*"remember" = medium.md | "ultra remember" = large.md*
""")
                print(f"  CREATE: {vault}/{project.lower()}/")
            else:
                print(f"  SKIP: {session_id[:8]}... (project dir doesn't exist: {project_path})")
                continue

        print(f"  {session_id[:8]}... -> {vault}/{project.lower()}")

        # Append to large.md
        append_to_large_md(project_path, session)

        # Update inbox.md
        update_inbox(project_path, session)

        # Mark as processed
        processed.add(session_id)

    # Save processed list
    save_processed_sessions(processed)

    print()
    print(f"Appended {len(new_sessions)} sessions to large.md files")
    print("Inbox.md files updated with NEEDS_PROCESSING flags")
    print()
    print("Run /gfsave to generate quality summaries.")


if __name__ == "__main__":
    main()
