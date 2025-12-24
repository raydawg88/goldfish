#!/usr/bin/env python3
"""
Goldfish Reader Agent
Scans Claude Code session files and extracts key information.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

def extract_session_info(filepath: str) -> dict:
    """Extract key information from a session file."""

    result = {
        "filepath": filepath,
        "filename": os.path.basename(filepath),
        "session_id": os.path.basename(filepath).replace(".jsonl", ""),
        "date": None,
        "message_count": 0,
        "conversation_messages": 0,  # Actual user/assistant messages (not metadata)
        "first_user_message": None,
        "topics": [],
        "files_touched": set(),
        "directories_created": set(),
        "tools_used": set(),
        "is_agent_session": "agent-" in os.path.basename(filepath),
        "is_metadata_only": False,  # True if only file-history-snapshot, summary, etc.
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

            # Count actual conversation messages vs metadata
            metadata_types = {"file-history-snapshot", "summary", "progress"}
            conversation_count = 0
            for msg in messages:
                msg_type = msg.get("type", "")
                if msg_type in ("user", "assistant"):
                    conversation_count += 1

            result["conversation_messages"] = conversation_count
            result["is_metadata_only"] = (conversation_count == 0 and len(messages) > 0)

            # Find first user message
            for msg in messages:
                if msg.get("type") == "user":
                    content = msg.get("message", {})
                    if isinstance(content, dict):
                        text = content.get("content", "")
                        if isinstance(text, list):
                            # Extract text from content blocks
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

                                    # Extract file paths from tool inputs
                                    tool_input = block.get("input", {})
                                    if isinstance(tool_input, dict):
                                        for key in ["file_path", "path", "filepath"]:
                                            if key in tool_input:
                                                fp = tool_input[key]
                                                if fp:
                                                    result["files_touched"].add(fp)

                                        # Check for mkdir commands
                                        cmd = tool_input.get("command", "")
                                        if isinstance(cmd, str) and "mkdir" in cmd:
                                            # Extract directory from mkdir command
                                            match = re.search(r'mkdir\s+(?:-p\s+)?["\']?([^"\'&;]+)', cmd)
                                            if match:
                                                result["directories_created"].add(match.group(1).strip())

            # Convert sets to lists for JSON serialization
            result["files_touched"] = sorted(list(result["files_touched"]))
            result["directories_created"] = sorted(list(result["directories_created"]))
            result["tools_used"] = sorted(list(result["tools_used"]))

            # Extract topics from first message and file paths
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

    # From first message
    msg = session_info.get("first_user_message", "") or ""
    msg_lower = msg.lower()

    # Common tech topics
    tech_keywords = {
        "api": "API Development",
        "auth": "Authentication",
        "database": "Database",
        "postgres": "PostgreSQL",
        "supabase": "Supabase",
        "react": "React",
        "next": "Next.js",
        "typescript": "TypeScript",
        "python": "Python",
        "fastapi": "FastAPI",
        "docker": "Docker",
        "git": "Git",
        "deploy": "Deployment",
        "test": "Testing",
        "debug": "Debugging",
        "refactor": "Refactoring",
        "css": "CSS/Styling",
        "tailwind": "Tailwind CSS",
        "ui": "UI Design",
        "ux": "UX Design",
        "setup": "Setup/Configuration",
        "install": "Installation",
        "config": "Configuration",
        "mcp": "MCP Servers",
        "claude": "Claude/AI",
        "agent": "AI Agents",
        "scrape": "Web Scraping",
        "automation": "Automation",
        "square": "Square API",
        "payment": "Payments",
    }

    for keyword, topic in tech_keywords.items():
        if keyword in msg_lower:
            topics.add(topic)

    # From file paths
    for fp in session_info.get("files_touched", []):
        fp_lower = fp.lower()
        if ".py" in fp_lower:
            topics.add("Python")
        if ".ts" in fp_lower or ".tsx" in fp_lower:
            topics.add("TypeScript")
        if ".js" in fp_lower or ".jsx" in fp_lower:
            topics.add("JavaScript")
        if "component" in fp_lower:
            topics.add("React Components")
        if "api" in fp_lower:
            topics.add("API Development")
        if "test" in fp_lower:
            topics.add("Testing")
        if ".md" in fp_lower:
            topics.add("Documentation")

    return sorted(list(topics))

def load_config():
    """Load Goldfish config.yaml."""
    import yaml
    config_path = Path.home() / "Library" / "CloudStorage" / "Dropbox-Personal" / "Goldfish" / ".goldfish" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {"default_vault": "personal", "consolidation_rules": [], "vaults": {}}


# Directories that are NEVER project names - these are path infrastructure
EXCLUDED_DIRS = {
    # System paths
    "Users", "rayhernandez", ".", "..", "Desktop", "Documents", "Downloads",
    "Library", "CloudStorage", "Dropbox-Personal", "Applications",
    # Goldfish structure
    "Goldfish", "personal", "work", "private", "goldfish",
    # Common code directories
    "src", "lib", "app", "components", "pages", "api", "public", "static",
    "node_modules", "dist", "build", "out", ".next", "__pycache__",
    "tests", "test", "spec", "scripts", "config", "utils", "helpers",
    "docs", "doc", "documentation", "examples", "assets", "images", "styles",
    # Claude paths
    "claude", "projects", "agents", "commands", "skills",
    # Paths with special prefixes that get extracted wrong
    "-users-rayhernandez",
}

# File extensions and patterns that are never project names
EXCLUDED_PATTERNS = {".py", ".md", ".json", ".yaml", ".yml", ".js", ".ts", ".tsx", ".jsx", ".sh", ".jsonl"}


def classify_session(session_info: dict) -> dict:
    """Classify session into vault and project using config rules."""

    msg = (session_info.get("first_user_message", "") or "").lower()
    files = session_info.get("files_touched", [])

    config = load_config()
    consolidation_rules = config.get("consolidation_rules", [])
    vaults_config = config.get("vaults", {})
    default_vault = config.get("default_vault", "personal")

    classification = {
        "vault": default_vault,
        "project": "UNCLEAR",
        "confidence": 50,
        "reasoning": ""
    }

    # Build alias-to-project mapping from config
    alias_map = {}  # alias.lower() -> (project_name, vault)
    for rule in consolidation_rules:
        project_name = rule.get("name", "").lower()
        vault = rule.get("vault", default_vault)
        alias_map[project_name] = (project_name, vault)
        for alias in rule.get("aliases", []):
            alias_map[alias.lower()] = (project_name, vault)

    # Extract potential project names from file paths
    project_candidates = defaultdict(int)
    for fp in files:
        parts = fp.split("/")
        for part in parts:
            part_lower = part.lower()
            # Skip excluded directories and short/hidden names
            if part_lower in {d.lower() for d in EXCLUDED_DIRS}:
                continue
            if part.startswith(".") or part.startswith("-") or len(part) <= 2:
                continue
            # Skip file names with extensions (these aren't project names)
            if any(part_lower.endswith(ext) for ext in EXCLUDED_PATTERNS):
                continue
            # Skip UUIDs (session IDs that look like: 0d3b1f09-0dfa-4768...)
            if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-', part_lower):
                continue
            # Skip anything that looks like a number or starts with numbers
            if part_lower[0].isdigit():
                continue
            project_candidates[part_lower] += 1

    # First priority: check if any candidate matches a known alias
    for candidate, count in sorted(project_candidates.items(), key=lambda x: -x[1]):
        if candidate in alias_map:
            project_name, vault = alias_map[candidate]
            classification["project"] = project_name
            classification["vault"] = vault
            classification["confidence"] = min(95, 60 + count * 10)
            classification["reasoning"] = f"Matched '{candidate}' to known project '{project_name}'"
            break

    # Second priority: check user message for project keywords
    if classification["project"] == "UNCLEAR":
        for alias, (project_name, vault) in alias_map.items():
            if alias in msg:
                classification["project"] = project_name
                classification["vault"] = vault
                classification["confidence"] = 70
                classification["reasoning"] = f"Message contains project keyword '{alias}'"
                break

    # Third priority: check vault keywords in message
    if classification["project"] == "UNCLEAR":
        for vault_name, vault_config in vaults_config.items():
            keywords = vault_config.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in msg:
                    classification["vault"] = vault_name
                    classification["reasoning"] = f"Message contains vault keyword '{keyword}'"
                    break

    # Fourth priority: use most common directory as project guess
    if classification["project"] == "UNCLEAR" and project_candidates:
        likely_project = max(project_candidates, key=project_candidates.get)
        classification["project"] = likely_project
        classification["confidence"] = min(70, 40 + project_candidates[likely_project] * 10)
        classification["reasoning"] = f"Best guess from path frequency: '{likely_project}'"

    # Fifth priority: setup/config detection from message or paths
    if classification["project"] == "UNCLEAR":
        # Check for .claude path patterns in files
        claude_path_detected = any("/.claude/" in fp for fp in files)

        if claude_path_detected:
            classification["project"] = "claude-setup"
            classification["vault"] = "personal"
            classification["confidence"] = 65
            classification["reasoning"] = "Working on Claude Code configuration (/.claude/ path)"
        elif any(kw in msg for kw in ["setup", "install", "config", "configure"]):
            classification["project"] = "claude-setup"
            classification["vault"] = "personal"
            classification["confidence"] = 55
            classification["reasoning"] = "Appears to be setup/configuration work"
        elif "mcp" in msg:
            classification["project"] = "claude-setup"
            classification["vault"] = "personal"
            classification["confidence"] = 55
            classification["reasoning"] = "MCP server configuration"

    # Sixth priority: research fallback for sessions with content but no files
    # These are valuable research/ideation sessions that should be captured
    if classification["project"] == "UNCLEAR":
        has_content = bool(session_info.get("first_user_message"))
        has_files = bool(session_info.get("files_touched"))
        conversation_count = session_info.get("conversation_messages", 0)

        if has_content and not has_files and conversation_count >= 2:
            # Extract a topic name from the first message
            first_msg = session_info.get("first_user_message", "")
            topic = extract_research_topic(first_msg)

            if topic:
                project_name = f"{topic}-research"
            else:
                project_name = "research"

            classification["project"] = project_name.lower().replace(" ", "-")
            classification["vault"] = "personal"
            classification["confidence"] = 60
            classification["reasoning"] = f"Research session: '{topic or 'general'}'"

    return classification


def extract_research_topic(message: str) -> str:
    """Extract a topic name from a research session's first message."""
    if not message:
        return ""

    # Clean up the message
    msg = message.lower().strip()

    # Remove common command prefixes
    msg = re.sub(r'^<command-message>.*?</command-message>\s*', '', msg)
    msg = re.sub(r'^<command-name>.*?</command-name>\s*', '', msg)
    msg = re.sub(r'^<command-args>\s*', '', msg)
    msg = re.sub(r'</command-args>\s*$', '', msg)

    # Common research-related phrases to strip
    prefixes_to_strip = [
        r"^i'?d? like (?:for )?you to ",
        r"^i want (?:you )?to ",
        r"^can you ",
        r"^please ",
        r"^do (?:all )?(?:the )?research (?:you can )?on ",
        r"^research ",
        r"^help me (?:with |understand )?",
        r"^let'?s? ",
    ]

    for pattern in prefixes_to_strip:
        msg = re.sub(pattern, '', msg, flags=re.IGNORECASE)

    # Extract key topic words (first few meaningful words)
    # Remove common filler words
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                  "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
                  "be", "have", "has", "had", "do", "does", "did", "will", "would",
                  "could", "should", "may", "might", "must", "shall", "can", "need",
                  "about", "all", "also", "any", "because", "before", "between",
                  "both", "each", "few", "first", "how", "into", "it", "its", "just",
                  "last", "like", "make", "many", "more", "most", "new", "no", "not",
                  "now", "only", "other", "our", "out", "over", "own", "same", "so",
                  "some", "still", "such", "than", "that", "their", "them", "then",
                  "there", "these", "they", "this", "those", "through", "too", "under",
                  "up", "very", "what", "when", "where", "which", "while", "who",
                  "why", "you", "your", "i", "me", "my", "we", "us"}

    words = re.findall(r'\b[a-z][a-z0-9]*\b', msg)
    topic_words = [w for w in words if w not in stop_words and len(w) > 2][:3]

    if topic_words:
        return " ".join(topic_words).title()

    return ""

def format_session_report(session_info: dict, classification: dict) -> str:
    """Format a session analysis report."""

    lines = [
        "═" * 60,
        f"Session: {session_info['filename']}",
        f"Date: {session_info['date']}",
        f"Messages: {session_info['message_count']}",
        f"Size: {session_info['file_size'] / 1024:.1f} KB",
        "",
    ]

    if session_info.get("error"):
        lines.append(f"ERROR: {session_info['error']}")
        lines.append("═" * 60)
        return "\n".join(lines)

    lines.append("FIRST USER MESSAGE:")
    msg = session_info.get("first_user_message", "(none)")
    if msg:
        # Truncate and clean up
        msg = msg[:300].replace("\n", " ").strip()
        if len(session_info.get("first_user_message", "")) > 300:
            msg += "..."
        lines.append(f'"{msg}"')
    else:
        lines.append("(no user message found)")
    lines.append("")

    if session_info.get("topics"):
        lines.append("KEY TOPICS:")
        for topic in session_info["topics"][:8]:
            lines.append(f"  - {topic}")
        lines.append("")

    if session_info.get("files_touched"):
        lines.append(f"FILES TOUCHED ({len(session_info['files_touched'])} total):")
        for fp in session_info["files_touched"][:10]:
            lines.append(f"  - {fp}")
        if len(session_info["files_touched"]) > 10:
            lines.append(f"  ... and {len(session_info['files_touched']) - 10} more")
        lines.append("")

    if session_info.get("directories_created"):
        lines.append("DIRECTORIES CREATED:")
        for d in session_info["directories_created"][:5]:
            lines.append(f"  - {d}")
        lines.append("")

    lines.append("READER ASSESSMENT:")
    lines.append(f"  Project: {classification['project']}")
    lines.append(f"  Vault: {classification['vault']}")
    lines.append(f"  Confidence: {classification['confidence']}%")
    lines.append(f'  Reasoning: "{classification["reasoning"]}"')
    lines.append("═" * 60)

    return "\n".join(lines)

def main():
    """Main function to process all session files."""

    # Find all session files
    claude_dir = Path.home() / ".claude" / "projects"

    session_files = []
    for jsonl_file in claude_dir.rglob("*.jsonl"):
        # Skip agent sessions for main analysis
        if "agent-" not in jsonl_file.name:
            session_files.append(str(jsonl_file))

    # Note: Skip history.jsonl - it's a session index with a different format, not a transcript

    print(f"\n{'═' * 60}")
    print("           🐠 GOLDFISH READER ANALYSIS")
    print(f"{'═' * 60}")
    print(f"\nFound {len(session_files)} session files to analyze\n")

    all_sessions = []
    skipped_metadata = 0
    skipped_empty = 0

    for filepath in sorted(session_files):
        session_info = extract_session_info(filepath)

        # Skip metadata-only sessions (file-history-snapshot, etc.)
        if session_info.get("is_metadata_only"):
            skipped_metadata += 1
            continue

        # Skip empty/abandoned sessions (less than 2 conversation messages)
        if session_info.get("conversation_messages", 0) < 2:
            skipped_empty += 1
            continue

        classification = classify_session(session_info)

        # Store for later
        all_sessions.append({
            "info": session_info,
            "classification": classification
        })

        # Print report
        print(format_session_report(session_info, classification))
        print()

    if skipped_metadata or skipped_empty:
        print(f"Skipped: {skipped_metadata} metadata-only, {skipped_empty} empty/abandoned")

    # Summary
    print(f"\n{'═' * 60}")
    print("                    SUMMARY")
    print(f"{'═' * 60}")

    by_vault = defaultdict(list)
    by_project = defaultdict(list)

    for s in all_sessions:
        vault = s["classification"]["vault"]
        project = s["classification"]["project"]
        by_vault[vault].append(s)
        by_project[project].append(s)

    print("\nBy Vault:")
    for vault, sessions in sorted(by_vault.items()):
        print(f"  {vault}: {len(sessions)} sessions")

    print("\nBy Project:")
    for project, sessions in sorted(by_project.items()):
        print(f"  {project}: {len(sessions)} sessions")

    # Save results
    output_path = Path.home() / "Library" / "CloudStorage" / "Dropbox-Personal" / "Goldfish" / ".goldfish" / "session-analysis.json"

    # Convert to JSON-serializable format
    json_sessions = []
    for s in all_sessions:
        json_sessions.append({
            "info": {
                k: v if not isinstance(v, set) else list(v)
                for k, v in s["info"].items()
            },
            "classification": s["classification"]
        })

    with open(output_path, 'w') as f:
        json.dump(json_sessions, f, indent=2, default=str)

    print(f"\nAnalysis saved to: {output_path}")

if __name__ == "__main__":
    main()
