# How Goldfish Works

A technical overview of the Goldfish memory system.

## The Problem

Claude Code has no persistent memory between sessions. Every conversation starts fresh. This means:

- You re-explain context every time
- Claude forgets decisions you made together
- There's no continuity between work sessions
- Valuable context is lost forever

## The Solution

Goldfish creates a persistent memory layer for Claude Code through:

1. **Automatic session capture**
2. **Organized project storage**
3. **Tiered memory hierarchy**
4. **Claude-aware configuration**

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code Session                   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   ~/.claude/CLAUDE.md                    │
│  (Tells Claude that Goldfish exists and how to use it)  │
└─────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│   Session Start      │    │   Auto-Save (5 min)  │
│   Read small.md      │    │   Capture transcripts│
└──────────────────────┘    └──────────────────────┘
              │                           │
              ▼                           ▼
┌──────────────────────────────────────────────────────────┐
│                    ~/Goldfish/                           │
│  ├── personal/                                           │
│  │   └── project/goldfish/{small,medium,large,inbox}.md │
│  └── work/                                               │
│      └── project/goldfish/{small,medium,large,inbox}.md │
└──────────────────────────────────────────────────────────┘
```

## Components

### 1. CLAUDE.md Configuration

The installer injects a section into `~/.claude/CLAUDE.md` that tells Claude:

- Goldfish exists and is active
- How to use the commands (`/gfsave`, `/gfstatus`, `/gfnew`)
- When to read memory files (session start, hotwords)
- Where memories are stored
- Rules to follow (never claim it doesn't exist, etc.)

This is the critical piece that makes Claude "aware" of the memory system.

### 2. Auto-Save Service

A background service runs every 5 minutes:

**On macOS:** launchd agent (`~/Library/LaunchAgents/com.goldfish.autosave.plist`)
**On Linux:** cron job

The service runs two scripts:

1. **reader.py** — Scans `~/.claude/projects/` for session files, extracts:
   - First user message
   - Files touched
   - Tools used
   - Session date and duration

2. **transcript-appender.py** — For each session:
   - Determines which project it belongs to
   - Appends transcript to that project's `large.md`
   - Flags `inbox.md` as needing processing

### 3. Memory Files

Each project has four memory files:

| File | Purpose | Size | When Read |
|------|---------|------|-----------|
| `small.md` | Quick context | ~500 words | Every session start |
| `medium.md` | Working context | ~2000 words | On "remember" |
| `large.md` | Full transcripts | Unlimited | On "ultra remember" |
| `inbox.md` | Processing queue | Variable | During `/gfsave` |

### 4. Quality Save (`/gfsave`)

When you run `/gfsave`, Claude becomes the summarization engine:

1. Reads raw transcripts from `large.md`
2. Analyzes what happened, what decisions were made
3. Updates `small.md` with current status and key facts
4. Updates `medium.md` with session summaries
5. Clears the `inbox.md` flag

This is why summaries are high quality — Claude writes them with full context understanding.

## The Memory Hierarchy

### small.md (Quick Context)

Loaded automatically at session start. Contains:

- Project description
- Current status
- **Token estimates** for all memory files (e.g., `Tokens: small ~440 | medium ~1.4k | large ~25k`)
- Key decisions and WHY
- Recent work (2-3 bullets)
- Stack/technologies

**Target size:** 300-500 words (~100-150 tokens)

### medium.md (Working Context)

Loaded when user says "remember". Contains:

- Session-by-session summaries
- What was built, what problems were solved
- Blockers and their resolutions
- More detailed history

**Target size:** 1000-2000 words

### large.md (Full History)

Loaded when user says "ultra remember". Contains:

- Complete session transcripts
- Every file touched
- Every tool used
- Raw, unprocessed history

**Size:** Unlimited (grows with project)

## Hotword System

The hotwords trigger different levels of memory loading:

| Hotword | Files Loaded | Use Case |
|---------|--------------|----------|
| *(none)* | `small.md` | Quick check-in, simple tasks |
| "remember" | `small.md` + `medium.md` | Resuming work, need context |
| "ultra remember" | All three | Deep dive, debugging history |

### Token-Aware Loading

Before loading `medium.md` or `large.md`, Claude checks the token estimates in `small.md` and asks for confirmation:

**Example — "remember":**
> "Session history (medium.md) is ~1.4k tokens. Load it?"

**Example — "ultra remember":**
> "Full transcripts (large.md) is ~25k tokens — that's substantial. Load all of it, or looking for something specific?"

This prevents accidentally burning expensive context on simple questions. The token estimates are calculated during `/gfsave` (bytes ÷ 4 ≈ tokens) and stored in the `small.md` header.

### Auto-Prompting for /gfsave

To prevent quality summaries from piling up, Claude checks for unprocessed sessions at session start:

```bash
grep -r "NEEDS_PROCESSING" ~/Goldfish/*/*/goldfish/inbox.md 2>/dev/null | wc -l
```

If 3 or more sessions are waiting, Claude prompts:

> "You have [X] sessions waiting for quality summaries. Run /gfsave?"

This ensures you don't forget to generate summaries while keeping it non-intrusive for quick sessions.

## Vault System

Vaults are top-level organizational units:

```
~/Goldfish/
├── personal/     # Vault 1
├── work/         # Vault 2
└── client-x/     # Vault 3 (custom)
```

Benefits:
- Keep different contexts separate
- Different projects don't bleed into each other
- Easy to backup/sync specific vaults
- Mental organization

## Session Routing

When a session is captured, the system determines which project it belongs to by:

1. **File paths** — Most files touched in `/path/to/project-name/`
2. **Keywords** — Matching vault keywords in the conversation
3. **Explicit mention** — User said "this is project X"

If unclear, sessions go to a default location for manual sorting.

## Security & Privacy

- **Local only** — All data stays on your machine
- **No network calls** — Scripts don't phone home
- **Your data** — Stored in plain markdown, fully readable
- **Sync optional** — Use Dropbox/iCloud only if YOU choose to

## Performance

- **Session start:** Reading `small.md` adds ~50ms
- **Auto-save:** Runs in background, no impact on Claude
- **Storage:** ~1MB per 100 sessions (varies by verbosity)
