# Goldfish v2.1 Specification

**Token-Aware Loading + Automatic Pattern Detection**

---

## Overview

Two new capabilities integrated into the existing Goldfish flow:

1. **Token-Aware Manifest** — Claude sees what memory exists (with sizes/tokens) before deciding what to load
2. **Pattern Detection** — Goldfish automatically notices recurring behaviors and suggests rules

Both happen automatically. No new commands. `/gfsave` does everything.

---

## 1. Token-Aware Manifest

### Problem

Currently, Claude loads `small.md` automatically but has no idea what's in `medium.md` or `large.md`. It can't make intelligent decisions about what context to load because it doesn't know:
- How big each file is
- What topics they contain
- Whether loading them is worth the token cost

### Solution

Add a **manifest section** to the top of `small.md` that shows:
- File sizes and estimated token counts
- Last updated timestamps
- Key topics/tags from recent work
- Current project status

Claude reads this tiny manifest first, then can intelligently decide what else to load.

### Manifest Format

The manifest lives at the top of `small.md`, before the regular content:

```markdown
# project-name

**Brief description of the project**

Sessions: 23 | Messages: 2,847 | Last: 2 hours ago

<!--MANIFEST
tokens:
  small: 850
  medium: 6200
  large: 52000
updated:
  small: 2025-12-18T14:30:00
  medium: 2025-12-18T14:30:00
  large: 2025-12-18T12:15:00
topics:
  recent: [oauth, square-api, webhooks, error-handling]
  all: [oauth, square-api, webhooks, typescript, testing, deployment]
sessions:
  total: 23
  this_week: 7
  pending_inbox: 2
-->

## Quick Context
- **Stack:** TypeScript, Next.js, Square API, Supabase
- **Status:** OAuth flow working. Building webhook handlers.
- **Key files:** `src/lib/square.ts`, `src/api/webhooks/`

## Recent Work
- **Today:** Fixed token refresh edge case
- **Yesterday:** Completed OAuth integration
- **This week:** Square API foundation

## Key Decisions
- Using server-side OAuth (not client) for security
- Webhooks via Supabase edge functions
- Square SDK over raw API calls

---
*"remember" loads session history (6k tokens) | "ultra remember" loads full transcripts (52k tokens)*
```

### Manifest Fields

| Field | Description | How Generated |
|-------|-------------|---------------|
| `tokens.small` | Estimated tokens in small.md | `bytes / 4` approximation |
| `tokens.medium` | Estimated tokens in medium.md | `bytes / 4` approximation |
| `tokens.large` | Estimated tokens in large.md | `bytes / 4` approximation |
| `updated.small` | Last modified timestamp | File mtime |
| `updated.medium` | Last modified timestamp | File mtime |
| `updated.large` | Last modified timestamp | File mtime |
| `topics.recent` | Topics from last 5 sessions | Extracted during summarization |
| `topics.all` | All topics ever discussed | Cumulative, deduplicated |
| `sessions.total` | Total session count | Count from large.md |
| `sessions.this_week` | Sessions in last 7 days | Count with date filter |
| `sessions.pending_inbox` | Unprocessed sessions | Count from inbox.md |

### How Claude Uses the Manifest

**Session Start Behavior (updated CLAUDE.md section):**

```markdown
### On Session Start

1. Read the project's `small.md` file
2. Parse the manifest (in HTML comment at top)
3. Based on the task, decide if more context is needed:
   - Quick question → small.md is enough
   - Continuing previous work → offer to load medium.md
   - Searching history → warn about large.md size, suggest specific search
4. Tell the user what context you have and what's available

Example responses:

"I've loaded your project context. You have 7 sessions this week
(~6k tokens in medium.md). Want me to load the recent session history?"

"I see you have 52k tokens of full transcripts. Rather than loading
everything, tell me what you're looking for and I'll search for it."

"Your last session was 2 hours ago working on webhooks.
Ready to continue?"
```

### Generation

The manifest is regenerated every time `/gfsave` runs:

```python
def generate_manifest(project_path):
    """Generate manifest data for small.md header."""
    goldfish_dir = project_path / "goldfish"

    manifest = {
        "tokens": {
            "small": estimate_tokens(goldfish_dir / "small.md"),
            "medium": estimate_tokens(goldfish_dir / "medium.md"),
            "large": estimate_tokens(goldfish_dir / "large.md"),
        },
        "updated": {
            "small": get_mtime(goldfish_dir / "small.md"),
            "medium": get_mtime(goldfish_dir / "medium.md"),
            "large": get_mtime(goldfish_dir / "large.md"),
        },
        "topics": {
            "recent": extract_recent_topics(goldfish_dir, limit=5),
            "all": extract_all_topics(goldfish_dir),
        },
        "sessions": {
            "total": count_sessions(goldfish_dir / "large.md"),
            "this_week": count_sessions_since(goldfish_dir / "large.md", days=7),
            "pending_inbox": count_pending(goldfish_dir / "inbox.md"),
        }
    }

    return manifest

def estimate_tokens(filepath):
    """Rough token estimate: bytes / 4."""
    if not filepath.exists():
        return 0
    return filepath.stat().st_size // 4
```

---

## 2. Automatic Pattern Detection

### Problem

Users repeat the same behaviors across sessions:
- Running the same commands
- Explaining the same context
- Fixing the same types of bugs
- Making the same decisions

These patterns should become documented rules or automation, but users don't notice them because they happen gradually across many sessions.

### Solution

During `/gfsave`, Goldfish automatically:
1. Analyzes recent sessions for patterns
2. Detects repetition (2+ occurrences = pattern candidate, 3+ = strong pattern)
3. Reports findings with suggested actions
4. User approves which patterns to codify

### What Counts as a Pattern

| Pattern Type | Detection Method | Example | Suggested Action |
|--------------|------------------|---------|------------------|
| **Repeated Commands** | Same bash/npm command in 3+ sessions | `npm run lint` before every commit | Add to workflow docs or pre-commit |
| **Repeated Explanations** | Similar context explained 2+ times | "The auth flow works by..." | Document in small.md |
| **Recurring Fixes** | Same error type fixed 2+ times | TypeScript null errors | Add stricter config or lint rule |
| **Consistent Decisions** | Same choice made when options exist | Always async/await over .then() | Add to project conventions |
| **Workflow Patterns** | Same sequence of actions | Always: test → lint → commit | Document as standard workflow |

### Detection Logic

```python
def detect_patterns(sessions: list[Session], threshold: int = 2) -> list[Pattern]:
    """
    Analyze sessions for recurring patterns.

    Args:
        sessions: Recent sessions to analyze (default: last 10)
        threshold: Minimum occurrences to flag as pattern (default: 2)

    Returns:
        List of detected patterns with suggestions
    """
    patterns = []

    # 1. Command patterns
    command_counts = count_commands(sessions)
    for cmd, count in command_counts.items():
        if count >= threshold:
            patterns.append(Pattern(
                type="command",
                description=f"Ran `{cmd}` in {count} sessions",
                occurrences=count,
                suggestion="Consider adding to project scripts or workflow docs"
            ))

    # 2. Topic patterns (re-explanations)
    topic_explanations = find_repeated_explanations(sessions)
    for topic, count in topic_explanations.items():
        if count >= threshold:
            patterns.append(Pattern(
                type="explanation",
                description=f"Explained '{topic}' {count} times",
                occurrences=count,
                suggestion="Document in small.md to avoid re-explaining"
            ))

    # 3. Fix patterns
    fix_types = categorize_fixes(sessions)
    for fix_type, count in fix_types.items():
        if count >= threshold:
            patterns.append(Pattern(
                type="fix",
                description=f"Fixed {fix_type} errors {count} times",
                occurrences=count,
                suggestion="Add linting rule or type check to prevent"
            ))

    # 4. Decision patterns
    decisions = extract_decisions(sessions)
    for decision, count in decisions.items():
        if count >= threshold:
            patterns.append(Pattern(
                type="decision",
                description=f"Chose '{decision}' {count} times",
                occurrences=count,
                suggestion="Codify as project convention"
            ))

    return sorted(patterns, key=lambda p: p.occurrences, reverse=True)
```

### Pattern Storage

Patterns are tracked in a new section of `medium.md`:

```markdown
## Detected Patterns

Last analyzed: 2025-12-18 | Sessions analyzed: 10

### Active Patterns
- **[command]** `npm run lint` before commits (5x) — *documented in workflow*
- **[decision]** async/await over .then() (8x) — *added to conventions*

### New Patterns (pending review)
- **[explanation]** Square OAuth flow explained 3x
  → Suggest: Add to small.md under "Key Concepts"?
- **[fix]** TypeScript strict null errors fixed 2x
  → Suggest: Enable strictNullChecks?

### Dismissed Patterns
- **[command]** `git status` (12x) — *normal behavior, dismissed*
```

### Output During /gfsave

When patterns are detected, `/gfsave` reports them:

```
GOLDFISH SAVE COMPLETE

Projects Updated:
  ✓ keeper (2 sessions processed)
    - Status: OAuth flow working
    - Topics: webhooks, error-handling

Patterns Detected:
  ┌─────────────────────────────────────────────────────────────┐
  │ RECURRING: Explained "Square OAuth flow" 3 times            │
  │ → Suggest: Document in small.md?                            │
  │                                                             │
  │ RECURRING: Fixed null reference errors 2 times              │
  │ → Suggest: Enable strictNullChecks in tsconfig?             │
  │                                                             │
  │ CONSISTENT: Always using async/await (8 sessions)           │
  │ → Already following. Codify as convention?                  │
  └─────────────────────────────────────────────────────────────┘

Apply suggestions? (y/n/skip)
```

### User Response Options

| Response | What Happens |
|----------|--------------|
| `y` or `yes` | Apply all suggestions (update small.md, add conventions) |
| `n` or `no` | Dismiss all patterns for now |
| `skip` or `s` | Skip for this save, ask again next time |
| `1,3` | Apply suggestions 1 and 3 only |
| `d2` | Dismiss pattern 2 permanently (won't ask again) |

### Applying Patterns

When user approves a pattern:

**For explanations → Update small.md:**
```markdown
## Key Concepts

### Square OAuth Flow
(Auto-documented from session 2025-12-15)
The OAuth flow works by redirecting to Square, receiving a code,
exchanging it for tokens, and storing the refresh token in Supabase.
Token refresh happens automatically on 401 responses.
```

**For decisions → Update project CLAUDE.md or conventions:**
```markdown
## Project Conventions

- Use async/await, never .then() chains
- (Pattern detected across 8 sessions, codified 2025-12-18)
```

**For fixes → Flag for user action:**
```
ACTION NEEDED: Pattern suggests enabling strictNullChecks.
This requires manual tsconfig change. Add to your TODO?
```

**For commands → Document workflow:**
```markdown
## Workflow

### Before Committing
1. Run `npm run lint`
2. Run `npm test`
(Detected pattern: you do this every time)
```

---

## 3. Updated /gfsave Flow

### Current Flow
```
1. Trigger auto-save (capture transcripts)
2. Process inbox → summarize → update small.md and medium.md
3. Report what was saved
```

### New Flow
```
1. Trigger auto-save (capture transcripts)
2. Process inbox → summarize → update small.md and medium.md
3. Regenerate manifest (token counts, topics, timestamps)
4. Run pattern detection on recent sessions
5. Report save results + any detected patterns
6. If patterns found, prompt for action
7. Apply approved patterns
```

### Updated /gfsave Command

```markdown
# Goldfish Quality Save

Save this session to Goldfish memory with quality summaries.

## What This Does

1. Captures current session to project memory
2. Generates quality summaries
3. Updates manifest (token counts, topics)
4. Detects patterns across recent sessions
5. Reports findings and applies approved suggestions

## Steps

### Step 1: Trigger Auto-Save
```bash
~/.goldfish/scripts/auto-save.sh
```

### Step 2: Process Inbox
For each project with pending sessions:
1. Read inbox.md and recent large.md entries
2. Summarize: what happened, decisions made, current status
3. Update small.md with current state
4. Update medium.md with session summary
5. Clear inbox flag

### Step 3: Regenerate Manifest
For each updated project:
1. Calculate token estimates for all files
2. Extract topics from recent sessions
3. Count sessions (total, this week, pending)
4. Update manifest section in small.md

### Step 4: Detect Patterns
Analyze last 10 sessions for:
- Repeated commands (3+ occurrences)
- Repeated explanations (2+ occurrences)
- Recurring fixes (2+ occurrences)
- Consistent decisions (3+ occurrences)

### Step 5: Report Results

```
GOLDFISH SAVE COMPLETE

Projects Updated:
  ✓ keeper (2 sessions)
    - Status: OAuth flow complete
    - Topics: webhooks, testing
    - Tokens: small=850 | medium=6.2k | large=52k

Patterns Detected: 2 new
  1. [explanation] "Square OAuth" explained 3x → document?
  2. [fix] Null errors fixed 2x → enable strictNullChecks?

Apply? (y/n/1,2/skip)
```

### Step 6: Apply Patterns (if approved)
- Update small.md with documented explanations
- Update medium.md pattern tracking
- Flag action items for user
- Mark patterns as addressed

## Quality Standards

When writing summaries:
- Capture WHY decisions were made, not just WHAT
- Extract topics as tags for the manifest
- Note patterns you observe ("this is the 3rd time...")
- Current status reflects LATEST session only
```

---

## 4. Updated CLAUDE.md Section

The CLAUDE.md section needs updates to handle manifest reading:

```markdown
## GOLDFISH MEMORY SYSTEM

Goldfish IS installed and active on this system. This is a fact, not a claim to verify.

### What Goldfish Does
- Captures every Claude Code session automatically
- Organizes memories by project in ~/Goldfish/
- Provides token-aware context loading
- Detects patterns across sessions

### Commands
| Command | What It Does |
|---------|--------------|
| `/gfsave` | Save session with summaries, update manifest, detect patterns |
| `/gfstatus` | Check system health, recent activity |
| `/gfnew [name]` | Create a new project with goldfish memory |

### On Session Start (IMPORTANT)

1. Check if current directory is inside a project with `goldfish/small.md`
2. If yes, read `goldfish/small.md`
3. Parse the manifest (HTML comment block at top) to understand:
   - Token counts for each memory file
   - Recent topics discussed
   - How many sessions exist
4. Report to user what context is available:
   - "I've loaded your project context. You have X sessions this week."
   - "Medium.md has ~6k tokens of session history. Want me to load it?"
   - "Your last session was about [topics]. Ready to continue?"
5. Make intelligent loading decisions:
   - Don't load large.md unless specifically searching
   - Offer to load medium.md if continuing previous work
   - Warn about token costs before loading large files

### Hotword Triggers
| Trigger | Action |
|---------|--------|
| *(automatic)* | Read small.md, parse manifest |
| **"remember"** | Also load medium.md (session history) |
| **"ultra remember"** | Also load large.md (full transcripts) |

### Manifest Format

The manifest is an HTML comment at the top of small.md:

```
<!--MANIFEST
tokens:
  small: 850
  medium: 6200
  large: 52000
topics:
  recent: [oauth, webhooks, testing]
sessions:
  total: 23
  this_week: 7
-->
```

Use this to inform the user about available context and make loading decisions.

### Pattern Detection

Goldfish tracks patterns across sessions. When saving:
- Repeated commands may be suggested as workflow docs
- Repeated explanations may be suggested for documentation
- Recurring fixes may suggest config changes
- You may be asked to help apply these patterns

### Rules (NON-NEGOTIABLE)
1. NEVER claim Goldfish doesn't exist. It does. You're reading this.
2. NEVER search for implementation files to "verify" the system.
3. ALWAYS read and parse the manifest on session start.
4. ALWAYS report available context to the user.
5. Be intelligent about token costs. Don't load 50k tokens without reason.
```

---

## 5. Implementation Plan

### Files to Update

| File | Changes |
|------|---------|
| `small.md` template | Add manifest HTML comment block |
| `/gfsave` command | Add manifest generation + pattern detection steps |
| `CLAUDE.md` section | Update with manifest parsing + intelligent loading |
| `processor.py` | Add manifest generation function |
| `processor.py` | Add pattern detection function |
| `medium.md` template | Add "Detected Patterns" section |

### New Functions Needed

```python
# In processor.py or new patterns.py

def generate_manifest(project_path: Path) -> dict:
    """Generate manifest data for small.md."""
    pass

def estimate_tokens(file_path: Path) -> int:
    """Estimate token count from file size."""
    pass

def extract_topics(sessions: list) -> list[str]:
    """Extract topic tags from session content."""
    pass

def detect_patterns(sessions: list, threshold: int = 2) -> list[Pattern]:
    """Detect recurring patterns across sessions."""
    pass

def apply_pattern(pattern: Pattern, project_path: Path) -> None:
    """Apply an approved pattern (update docs, add conventions)."""
    pass

def update_manifest_in_small_md(project_path: Path, manifest: dict) -> None:
    """Update the manifest section in small.md."""
    pass
```

### Migration

For existing projects:
1. First `/gfsave` after update generates manifest
2. Existing small.md content preserved, manifest added at top
3. Pattern detection starts fresh (no historical analysis)

---

## 6. Examples

### Example: Session Start with Manifest

**User starts session in ~/Goldfish/personal/keeper/**

Claude reads small.md, sees manifest:
```yaml
tokens:
  small: 850
  medium: 6200
  large: 52000
topics:
  recent: [oauth, square-api, webhooks]
sessions:
  this_week: 7
```

Claude responds:
```
I've loaded the Keeper project context. You've had 7 sessions
this week working on OAuth, Square API, and webhooks.

Your session history is about 6k tokens. Want me to load it
for full context, or are we starting something new?
```

### Example: Pattern Detection During Save

**User runs /gfsave**

```
GOLDFISH SAVE COMPLETE

Projects Updated:
  ✓ keeper (1 session)
    - Status: Webhook signature verification working
    - Topics: webhooks, crypto, testing

📊 Manifest Updated:
    small: 920 tokens | medium: 7.1k | large: 58k
    Topics: +webhooks, +crypto

🔄 Patterns Detected:

  1. REPEATED EXPLANATION (3x)
     "How webhook signatures work"
     → Document this in small.md under Key Concepts?

  2. CONSISTENT COMMAND (5x)
     `npm run typecheck` before commits
     → Add to documented workflow?

Apply patterns? (y/n/1,2)
```

User types: `1`

```
✓ Applied pattern 1:
  Added "Webhook Signatures" section to small.md

Pattern 2 saved for next time.
```

### Example: small.md After Pattern Applied

```markdown
# keeper

**Square integration for Keeper app**

Sessions: 24 | Messages: 3,012 | Last: 10 min ago

<!--MANIFEST
tokens:
  small: 1100
  medium: 7100
  large: 58000
updated:
  small: 2025-12-18T16:45:00
  medium: 2025-12-18T16:45:00
  large: 2025-12-18T16:30:00
topics:
  recent: [webhooks, crypto, testing, oauth]
  all: [oauth, square-api, webhooks, typescript, testing, crypto]
sessions:
  total: 24
  this_week: 8
  pending_inbox: 0
-->

## Quick Context
- **Stack:** TypeScript, Next.js, Square API, Supabase
- **Status:** Webhook signature verification complete. Testing.

## Key Concepts

### Square OAuth Flow
Server-side OAuth: redirect → code → token exchange → store refresh token.
Auto-refresh on 401 responses.

### Webhook Signatures *(auto-documented 2025-12-18)*
Square webhooks include `x-square-signature` header. Verify by:
1. Get raw body (not parsed JSON)
2. HMAC-SHA256 with webhook signature key
3. Compare base64 result to header
Must use raw body or signature fails.

## Recent Work
- **Today:** Webhook signature verification
- **Yesterday:** OAuth token refresh logic
- **This week:** Square API integration complete

## Key Decisions
- Server-side OAuth for security
- Supabase edge functions for webhooks
- Square SDK over raw API

---
*"remember" = 7k tokens | "ultra remember" = 58k tokens*
```

---

## 7. Open Questions

1. **Pattern threshold** — Is 2 occurrences enough? Should commands require 3+?

2. **Historical analysis** — Should pattern detection look at ALL sessions or just recent N?

3. **Auto-apply** — Should some patterns (like adding topics) apply automatically without asking?

4. **Topic extraction** — Manual tags during summarization, or AI-extracted from content?

5. **Manifest format** — YAML in HTML comment (shown) or JSON? Or frontmatter?

---

## 8. Success Criteria

After implementing v2.1:

- [ ] Claude reads manifest on session start
- [ ] Claude reports available context with token counts
- [ ] Claude makes intelligent loading decisions
- [ ] /gfsave regenerates manifest
- [ ] /gfsave detects patterns (2+ threshold)
- [ ] User can approve/dismiss patterns
- [ ] Approved patterns update small.md or conventions
- [ ] Existing projects migrate cleanly

---

*Spec Version: 1.0 | Date: 2025-12-18 | Author: Ray + Claude*
