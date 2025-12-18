#!/usr/bin/env python3
"""
🐠 Goldfish Reader
Scans Claude Code session files and extracts key information.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

def load_config():
    """Load Goldfish configuration."""
    config_path = Path.home() / ".goldfish" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {
        "memory_path": str(Path.home() / "Goldfish"),
        "vaults": {"personal": {}, "work": {}},
        "default_vault": "personal"
    }

def extract_session_info(filepath: str) -> dict:
    """Extract key information from a session file."""

    result = {
        "filepath": filepath,
        "filename": os.path.basename(filepath),
        "session_id": os.path.basename(filepath).replace(".jsonl", ""),
        "date": None,
        "message_count": 0,
        "first_user_message": None,
        "topics": [],
        "files_touched": set(),
        "directories_created": set(),
        "tools_used": set(),
        "is_agent_session": "agent-" in os.path.basename(filepath),
        "file_size": os.path.getsize(filepath),
        "error": None
    }

    # Get file modification time as date
    try:
        mtime = os.path.getmtime(filepath)
        result["date"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    except:
        pass

    # Skip empty files
    if result["file_size"] == 0:
        result["error"] = "Empty file"
        return result

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            messages = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except json.JSONDecodeError:
                    continue

            result["message_count"] = len(messages)

            # Find first user message
            for msg in messages:
                if msg.get("type") == "user":
                    content = msg.get("message", {})
                    if isinstance(content, dict):
                        text = content.get("content", "")
                        if isinstance(text, list):
                            text_parts = []
                            for block in text:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    text_parts.append(block.get("text", ""))
                            text = " ".join(text_parts)
                        result["first_user_message"] = text[:500] if text else None
                    elif isinstance(content, str):
                        result["first_user_message"] = content[:500]
                    break

            # Extract files touched and tools used
            for msg in messages:
                if msg.get("type") == "assistant":
                    content = msg.get("message", {})
                    if isinstance(content, dict):
                        tool_calls = content.get("content", [])
                        if isinstance(tool_calls, list):
                            for block in tool_calls:
                                if isinstance(block, dict):
                                    tool_name = block.get("name", "")
                                    if tool_name:
                                        result["tools_used"].add(tool_name)

                                    tool_input = block.get("input", {})
                                    if isinstance(tool_input, dict):
                                        for key in ["file_path", "path", "filepath"]:
                                            if key in tool_input:
                                                fp = tool_input[key]
                                                if fp:
                                                    result["files_touched"].add(fp)

                                        cmd = tool_input.get("command", "")
                                        if isinstance(cmd, str) and "mkdir" in cmd:
                                            match = re.search(r'mkdir\s+(?:-p\s+)?["\']?([^"\'&;]+)', cmd)
                                            if match:
                                                result["directories_created"].add(match.group(1).strip())

            # Convert sets to lists
            result["files_touched"] = sorted(list(result["files_touched"]))
            result["directories_created"] = sorted(list(result["directories_created"]))
            result["tools_used"] = sorted(list(result["tools_used"]))
            result["topics"] = extract_topics(result)

    except Exception as e:
        result["error"] = str(e)
        result["files_touched"] = []
        result["directories_created"] = []
        result["tools_used"] = []

    return result

def extract_topics(session_info: dict) -> list:
    """Extract topics from session content."""
    topics = set()

    msg = (session_info.get("first_user_message", "") or "").lower()

    tech_keywords = {
        "api": "API", "auth": "Auth", "database": "Database",
        "postgres": "PostgreSQL", "supabase": "Supabase", "react": "React",
        "next": "Next.js", "typescript": "TypeScript", "python": "Python",
        "fastapi": "FastAPI", "docker": "Docker", "git": "Git",
        "deploy": "Deployment", "test": "Testing", "debug": "Debugging",
        "css": "CSS", "tailwind": "Tailwind", "ui": "UI",
        "setup": "Setup", "install": "Installation", "config": "Config",
        "mcp": "MCP", "claude": "Claude/AI", "agent": "AI Agents",
    }

    for keyword, topic in tech_keywords.items():
        if keyword in msg:
            topics.add(topic)

    for fp in session_info.get("files_touched", []):
        fp_lower = fp.lower()
        if ".py" in fp_lower: topics.add("Python")
        if ".ts" in fp_lower or ".tsx" in fp_lower: topics.add("TypeScript")
        if ".js" in fp_lower or ".jsx" in fp_lower: topics.add("JavaScript")
        if "test" in fp_lower: topics.add("Testing")
        if ".md" in fp_lower: topics.add("Documentation")

    return sorted(list(topics))

def classify_session(session_info: dict, config: dict) -> dict:
    """Classify session into vault and project."""

    msg = (session_info.get("first_user_message", "") or "").lower()
    files = session_info.get("files_touched", [])
    vaults = list(config.get("vaults", {}).keys())

    classification = {
        "vault": config.get("default_vault", "personal"),
        "project": "UNCLEAR",
        "confidence": 50,
        "reasoning": ""
    }

    # Try to identify project from file paths
    project_patterns = defaultdict(int)
    for fp in files:
        parts = fp.split("/")
        for part in parts:
            if part and part not in ["Users", ".", "..", "Desktop", "Documents", "Projects", "src", "lib", "app", "components"]:
                if not part.startswith(".") and len(part) > 2:
                    project_patterns[part] += 1

    if project_patterns:
        likely_project = max(project_patterns, key=project_patterns.get)
        classification["project"] = likely_project
        classification["confidence"] = min(90, 50 + project_patterns[likely_project] * 10)
        classification["reasoning"] = f"Files in '{likely_project}' directory"

    # Check for vault keywords in message
    for vault_name, vault_config in config.get("vaults", {}).items():
        keywords = vault_config.get("keywords", [])
        for keyword in keywords:
            if keyword.lower() in msg:
                classification["vault"] = vault_name
                classification["reasoning"] += f"; matched '{keyword}' keyword"
                break

    return classification

def main():
    """Main function to process all session files."""

    config = load_config()
    memory_path = Path(os.path.expanduser(config["memory_path"]))
    goldfish_dir = Path.home() / ".goldfish"

    # Find all session files
    claude_dir = Path.home() / ".claude" / "projects"

    session_files = []
    for jsonl_file in claude_dir.rglob("*.jsonl"):
        if "agent-" not in jsonl_file.name:
            session_files.append(str(jsonl_file))

    print(f"🐠 Goldfish Reader")
    print(f"Found {len(session_files)} session files")

    all_sessions = []

    for filepath in sorted(session_files):
        session_info = extract_session_info(filepath)
        classification = classify_session(session_info, config)

        all_sessions.append({
            "info": session_info,
            "classification": classification
        })

    # Summary
    by_project = defaultdict(list)
    for s in all_sessions:
        project = s["classification"]["project"]
        by_project[project].append(s)

    print(f"\nProjects found: {len(by_project)}")
    for project, sessions in sorted(by_project.items()):
        print(f"  {project}: {len(sessions)} sessions")

    # Save results
    output_path = goldfish_dir / "state" / "session-analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    json_sessions = []
    for s in all_sessions:
        json_sessions.append({
            "info": {k: v if not isinstance(v, set) else list(v) for k, v in s["info"].items()},
            "classification": s["classification"]
        })

    with open(output_path, 'w') as f:
        json.dump(json_sessions, f, indent=2, default=str)

    print(f"\nAnalysis saved to: {output_path}")

if __name__ == "__main__":
    main()
