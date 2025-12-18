
<img width="1536" height="1024" alt="ChatGPT Image Dec 18, 2025, 08_53_41 PM" src="https://github.com/user-attachments/assets/3d4cabca-bc40-48e9-a589-52d40d29b19a" />

# 🐠 Goldfish

**Persistent, organized memory for Claude Code.**

Claude Code is powerful, but it forgets everything between sessions. Goldfish fixes that.

---

## The Problem

Every time you start a Claude Code session, you're starting from zero. Claude doesn't remember:
- What you built yesterday
- Why you made that architecture decision
- Where you left off on that bug
- The context that took 20 minutes to explain

You end up re-explaining the same things. Over and over.

## The Solution

Goldfish gives Claude Code a **real memory system**:

- **Automatic capture** — Every session is recorded without you doing anything
- **Organized by project** — Memories are grouped by what you're working on
- **Tiered recall** — Quick context loads automatically, deep history on demand
- **You control it** — Your memories, your organization, your rules

When you return to a project, Claude already knows the context. No re-explaining. Just pick up where you left off.

---

## How It's Different From Built-in Memory

Claude Code has basic memory. Goldfish is something else entirely.

| Feature | Claude Code Built-in | Goldfish |
|---------|---------------------|----------|
| Remembers sessions | Last few, vaguely | Every session, forever |
| Organization | None | Projects, vaults, hierarchy |
| Context loading | Random/automatic | Intentional, tiered, token-aware |
| User control | None | Full control |
| Cross-project | Mixed together | Cleanly separated |
| Searchable history | No | Yes (full transcripts) |
| Quality summaries | No | AI-generated summaries |
| Token transparency | No | Shows token costs before loading |
| Portable | No | Sync via Dropbox/iCloud |

**Goldfish isn't just memory. It's a second brain for your development work.**

---

## Quick Start

### Install (One Command)

```bash
curl -fsSL https://raw.githubusercontent.com/raydawg88/goldfish/main/install.sh | bash
```

The installer will:
1. Check prerequisites (Claude Code, Python 3)
2. Ask where to store memories (default: `~/Goldfish`)
3. Help you set up vaults (personal, work, or custom)
4. Install everything automatically
5. Show you how to use it

**Important:** Start a new Claude Code session after installing.

### Usage

Once installed, just talk naturally:

```
"Let's put this project in the personal vault"
"This is a work project called api-redesign"
"Create a new project for my side hustle"
```

Claude handles the rest. Your sessions are captured automatically.

### Hotwords

Control how much context Claude loads:

| Say This | What Happens |
|----------|--------------|
| *(automatic)* | Claude reads `small.md` — quick context, key decisions |
| **"remember"** | Claude asks to confirm, then loads `medium.md` — session history |
| **"ultra remember"** | Claude warns about size, then loads `large.md` — full transcripts |

**Token-aware loading:** Before loading medium or large files, Claude tells you the estimated token cost and asks for confirmation. No more accidentally burning 50k tokens on a simple question.

### Commands

| Command | What It Does |
|---------|--------------|
| `/gfsave` | Save session with quality AI-generated summaries |
| `/gfstatus` | Check system health and recent activity |
| `/gfnew` | Create a new project (or just ask Claude naturally) |

---

## How It Works

### The Memory Hierarchy

```
~/Goldfish/
├── personal/                    # Your personal vault
│   ├── side-project/
│   │   └── goldfish/
│   │       ├── small.md         # Quick context (auto-loaded)
│   │       ├── medium.md        # Working context ("remember")
│   │       ├── large.md         # Full transcripts ("ultra remember")
│   │       └── inbox.md         # Pending sessions
│   └── another-project/
│       └── goldfish/
│           └── ...
└── work/                        # Your work vault
    └── client-project/
        └── goldfish/
            └── ...
```

### What Each File Contains

**`small.md`** — Quick Context (Auto-loaded)
- Project description and current status
- **Token estimates** for all memory files (e.g., `Tokens: small ~440 | medium ~1.4k | large ~25k`)
- Key decisions and WHY they were made
- Recent work summary

**`medium.md`** — Working Context
- Session-by-session summaries
- What happened, what was built
- Problems solved, blockers hit

**`large.md`** — Full History
- Complete transcripts of every session
- Nothing lost, everything searchable
- The ultimate reference

**`inbox.md`** — Processing Queue
- New sessions waiting to be summarized
- Cleared when you run `/gfsave`

### The Flow

1. **You work** — Just use Claude Code normally
2. **Auto-capture** — Sessions are saved to `large.md` automatically (every 5 min)
3. **You save** — Run `/gfsave` to generate quality summaries
4. **Next session** — Claude reads your context and remembers everything

---

## Vaults

Vaults keep different types of work separate. Common setups:

**Freelancer/Agency:**
```
~/Goldfish/
├── client-acme/
├── client-globex/
└── internal/
```

**Employee + Side Projects:**
```
~/Goldfish/
├── work/
└── personal/
```

**Learner:**
```
~/Goldfish/
├── courses/
├── experiments/
└── projects/
```

Create whatever structure makes sense for your life.

---

## Requirements

- **macOS** (Linux support coming, Windows later)
- **Claude Code** installed and working
- **Python 3** (comes with macOS)

---

## Uninstall

```bash
goldfish uninstall
```

This removes:
- System files (`~/.goldfish/`)
- Claude commands
- Auto-save service
- Goldfish section from CLAUDE.md

This does NOT remove:
- Your memories (`~/Goldfish/`) — those are yours forever

---

## Philosophy

Goldfish is built on a few beliefs:

1. **Your context is valuable.** The 30 minutes you spent explaining your codebase shouldn't evaporate when the session ends.

2. **Memory should be organized.** Not everything dumped in one place. Projects are separate. Work is separate from personal.

3. **You should control it.** Your memories, stored where you want, synced how you want, deleted when you want.

4. **AI should know its limits.** Goldfish makes Claude aware of what it knows and doesn't know. No hallucinating memories.

---

## FAQ

**Does this send my data anywhere?**
No. Everything stays on your machine (or your Dropbox/iCloud if you choose that for sync). Goldfish just organizes local files.

**Will this slow down Claude Code?**
No. Reading a small markdown file adds milliseconds. Auto-save runs in the background.

**What if I work on multiple machines?**
Point the memory location to a synced folder (Dropbox, iCloud, etc.). Your memories follow you.

**Can I edit the memory files manually?**
Yes! They're just markdown. Edit, reorganize, delete — it's your data.

**What if Claude "forgets" Goldfish exists?**
This was a problem we solved. The CLAUDE.md configuration explicitly tells Claude that Goldfish is installed and how to use it. Claude can't "forget" because it reads the instructions every session.

---

## Contributing

Issues and PRs welcome. This is an open source project.

---

## License

MIT

---

## Credits

Created by [Ray Hernandez](https://github.com/raydawg88) and Claude.

Because AI that forgets everything is only half useful.

---

**🐠 Give Claude a memory. Install Goldfish.**
