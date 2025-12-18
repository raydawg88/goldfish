# Getting Started with Goldfish

This guide will get you up and running with Goldfish in under 5 minutes.

## Prerequisites

- **macOS** (Linux support coming soon)
- **Claude Code** installed and working
- **Python 3** (comes pre-installed on macOS)

## Installation

Run this single command in your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/raydawg88/goldfish/main/install.sh | bash
```

The installer will walk you through:

1. **Memory Location** — Where to store your memories (default: `~/Goldfish`)
2. **Vaults** — How to organize your projects (default: `personal` and `work`)

That's it. Installation takes about 30 seconds.

## After Installation

**Important:** Start a NEW Claude Code session for changes to take effect. Claude reads its configuration at startup.

## Your First Project

Once you're in a new Claude Code session, just start working and tell Claude where to put things:

```
"This is a personal project called my-app"
"Let's put this in the work vault"
"Create a new project for my side hustle"
```

Claude will create the project structure and start capturing your sessions automatically.

## Memory Recall (Hotwords)

Control how much context Claude loads:

| What You Say | What Happens |
|--------------|--------------|
| *(nothing)* | Claude reads quick context automatically |
| **"remember"** | Claude loads working context (more detail) |
| **"ultra remember"** | Claude loads complete session history |

## Commands

| Command | What It Does |
|---------|--------------|
| `/gfsave` | Save with quality summaries (run after big sessions) |
| `/gfstatus` | Check system health |
| `/gfnew` | Create a new project |

## What Happens Behind the Scenes

1. **Every 5 minutes**, Goldfish captures your Claude Code sessions
2. **Raw transcripts** are appended to `large.md` in your project
3. **When you run `/gfsave`**, Claude creates quality summaries in `small.md` and `medium.md`
4. **Next session**, Claude reads your context and remembers everything

## Directory Structure

After installation, you'll have:

```
~/.goldfish/              # System files (don't edit)
├── config.json           # Your configuration
├── scripts/              # Auto-save scripts
└── agents/               # Summary generation agents

~/Goldfish/               # Your memories (yours to keep)
├── personal/             # Personal vault
│   └── my-project/
│       └── goldfish/
│           ├── small.md  # Quick context
│           ├── medium.md # Working context
│           ├── large.md  # Full history
│           └── inbox.md  # Pending sessions
└── work/                 # Work vault
    └── ...
```

## Next Steps

- Read [How It Works](how-it-works.md) for a deeper understanding
- Read [Customization](customization.md) to tailor Goldfish to your workflow
- Check [Troubleshooting](troubleshooting.md) if you run into issues

## Uninstalling

If you ever want to remove Goldfish:

```bash
goldfish uninstall
```

This removes system files but **keeps your memories safe**. Delete `~/Goldfish` manually if you want to remove everything.
