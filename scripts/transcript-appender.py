#!/usr/bin/env python3
"""
🐠 Goldfish Transcript Appender
Appends raw transcripts to large.md and flags inbox.md for processing.
"""

import json
import os
from pathlib import Path
from datetime import datetime


def load_config():
    """Load Goldfish configuration."""
    config_path = Path.home() / ".goldfish" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {
        "memory_path": str(Path.home() / "Goldfish"),
        "vaults": {"personal": {}, "work": {}},
        "default_vault": "personal",
        "projects": {}
    }


def get_paths(config):
    """Get paths from config."""
    memory_path = Path(os.path.expanduser(config["memory_path"]))
    goldfish_dir = Path.home() / ".goldfish"
    return memory_path, goldfish_dir


def load_processed_sessions(goldfish_dir: Path) -> set:
    """Load list of already-processed session IDs."""
    processed_path = goldfish_dir / "state" / "processed-sessions.json"
    if processed_path.exists():
        with open(processed_path) as f:
            return set(json.load(f))
    return set()


def save_processed_sessions(goldfish_dir: Path, processed: set):
    """Save list of processed session IDs."""
    processed_path = goldfish_dir / "state" / "processed-sessions.json"
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    with open(processed_path, 'w') as f:
        json.dump(list(processed), f, indent=2)


def get_vault_for_project(project: str, config: dict) -> str:
    """Determine vault for a project based on config."""
    # Check explicit project mappings
    projects = config.get("projects", {})
    if project.lower() in projects:
        return projects[project.lower()].get("vault", config.get("default_vault", "personal"))

    # Check vault keywords
    for vault_name, vault_config in config.get("vaults", {}).items():
        keywords = vault_config.get("keywords", [])
        for keyword in keywords:
            if keyword.lower() in project.lower():
                return vault_name

    return config.get("default_vault", "personal")


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

    first_msg = session.get("first_user_message", "")
    if first_msg:
        preview = first_msg[:500]
        if len(first_msg) > 500:
            preview += "..."
        lines.append("**First message:**")
        lines.append(f"> {preview}")
        lines.append("")

    files = session.get("files_touched", [])
    if files:
        lines.append("**Files touched:**")
        for f in files[:20]:
            lines.append(f"- `{f}`")
        if len(files) > 20:
            lines.append(f"- ... and {len(files) - 20} more")
        lines.append("")

    tools = session.get("tools_used", [])
    if tools:
        lines.append(f"**Tools:** {', '.join(tools[:10])}")
        lines.append("")

    return "\n".join(lines)


def update_inbox(project_path: Path, session: dict):
    """Add new session flag to inbox.md."""
    inbox_path = project_path / "goldfish" / "inbox.md"

    session_id = session.get("session_id", "unknown")[:8]
    date = session.get("date", datetime.now().strftime("%Y-%m-%d %H:%M"))
    first_msg = (session.get("first_user_message", "") or "")[:200]

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

    if inbox_path.exists():
        content = inbox_path.read_text()
    else:
        content = f"# {project_path.name} - Inbox\n\nNew sessions waiting for quality summaries.\n"

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

    if large_path.exists():
        content = large_path.read_text()
    else:
        content = f"# {project_path.name} - Complete History\n\n*Full session transcripts appended automatically*\n"

    content += transcript

    large_path.parent.mkdir(parents=True, exist_ok=True)
    large_path.write_text(content)


def main():
    """Append new session transcripts and flag inbox."""
    print("🐠 Goldfish Transcript Appender")
    print()

    config = load_config()
    memory_path, goldfish_dir = get_paths(config)
    vaults = list(config.get("vaults", {}).keys())

    # Load session analysis
    session_analysis_path = goldfish_dir / "state" / "session-analysis.json"
    if not session_analysis_path.exists():
        print("No session-analysis.json found. Run reader.py first.")
        return

    with open(session_analysis_path) as f:
        raw_data = json.load(f)

    # Parse sessions
    sessions = []
    if isinstance(raw_data, list):
        for item in raw_data:
            info = item.get("info", {})
            classification = item.get("classification", {})
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
        sessions = raw_data.get("sessions", [])

    print(f"Found {len(sessions)} total sessions")

    processed = load_processed_sessions(goldfish_dir)
    print(f"Already processed: {len(processed)}")

    new_sessions = [s for s in sessions if s.get("session_id") and s.get("session_id") not in processed]

    if not new_sessions:
        print("\nNo new sessions to process.")
        return

    print(f"\nNew sessions: {len(new_sessions)}")

    appended_count = 0
    for session in new_sessions:
        session_id = session.get("session_id", "unknown")
        project = session.get("project")
        vault = session.get("vault")

        if not project or project == "UNCLEAR":
            print(f"  SKIP: {session_id[:8]}... (no project)")
            continue

        # Determine vault
        if not vault or vault not in vaults:
            vault = get_vault_for_project(project, config)

        project_path = memory_path / vault / project.lower()

        # Check if project exists
        if not project_path.exists():
            # Try other vaults
            found = False
            for v in vaults:
                alt_path = memory_path / v / project.lower()
                if alt_path.exists():
                    project_path = alt_path
                    vault = v
                    found = True
                    break

            if not found:
                print(f"  SKIP: {session_id[:8]}... (project not found: {project})")
                continue

        print(f"  {session_id[:8]}... -> {vault}/{project.lower()}")

        append_to_large_md(project_path, session)
        update_inbox(project_path, session)
        processed.add(session_id)
        appended_count += 1

    save_processed_sessions(goldfish_dir, processed)

    print()
    print(f"Appended {appended_count} sessions to large.md files")
    print("Inbox.md files flagged for processing")
    print("\nRun /gfsave to generate quality summaries.")


if __name__ == "__main__":
    main()
