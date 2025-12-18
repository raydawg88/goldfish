# Frequently Asked Questions

## General

### What is Goldfish?

Goldfish is a persistent memory system for Claude Code. It automatically captures your sessions, organizes them by project, and makes Claude remember context between conversations.

### Why is it called Goldfish?

Irony. Goldfish are famous for their supposedly short memory. This tool gives Claude the opposite — perfect recall of everything.

### Is this an official Anthropic product?

No. Goldfish is an open-source community project that works with Claude Code. It's not made by or affiliated with Anthropic.

### Does this work with other AI assistants?

Currently, Goldfish is designed specifically for Claude Code. The architecture could theoretically be adapted for other assistants, but that's not supported yet.

## Privacy & Security

### Does Goldfish send my data anywhere?

No. Everything stays on your machine. The scripts don't make any network calls. Your memories are stored locally in plain markdown files.

### Can I see exactly what's being stored?

Yes. All memories are stored as readable markdown files in `~/Goldfish/`. Open any `small.md`, `medium.md`, or `large.md` file to see exactly what's there.

### Is it safe to use with sensitive projects?

Goldfish stores data locally, so it's as secure as your machine. For extra-sensitive work:
- Use a separate vault with encryption
- Exclude certain projects from auto-save
- Review memory files periodically
- Use full-disk encryption on your machine

### Can I exclude certain sessions from capture?

Currently, all Claude Code sessions are captured. To exclude a project:
1. Don't create a Goldfish project for it
2. Sessions without a matching project are stored in a holding area but not summarized

A future update may add explicit exclusion rules.

## Usage

### Do I need to do anything special for Goldfish to work?

After installation, just use Claude Code normally. Sessions are captured automatically. For best results:
- Tell Claude which project you're working on
- Run `/gfsave` after significant work sessions
- Use hotwords ("remember", "ultra remember") to load more context

### How do I know it's working?

Run `/gfstatus` to check system health. You can also:
- Check `~/.goldfish/logs/goldfish.log` for auto-save activity
- Look at `~/Goldfish/[vault]/[project]/goldfish/large.md` for captured sessions

### What are the hotwords?

| Say This | Claude Does |
|----------|-------------|
| *(nothing)* | Loads quick context (small.md) automatically |
| "remember" | Tells you token cost, asks to confirm, then loads medium.md |
| "ultra remember" | Warns about size, asks to confirm, then loads large.md |

### Why does Claude ask before loading more context?

To save tokens (and money). Loading a 50k-token transcript for a simple question is wasteful. Claude checks the token estimates in `small.md` and confirms before loading larger files. The estimates are updated every time you run `/gfsave`.

### How often should I run /gfsave?

Run `/gfsave` after significant work sessions — when you've made important decisions, solved problems, or completed features. The auto-save captures raw transcripts continuously, but `/gfsave` creates the quality summaries.

### Can I edit the memory files manually?

Yes! They're just markdown. Edit them however you like:
- Fix inaccurate summaries
- Add notes Claude didn't capture
- Remove sensitive information
- Reorganize content

### What happens if I rename a project?

Memory files stay where they are. You'll need to:
1. Rename the project directory
2. Update any aliases in `config.json`
3. Sessions will need to be re-routed to the new name

## Technical

### How much disk space does Goldfish use?

Roughly 1MB per 100 sessions, but this varies based on conversation length. Most users won't notice the space usage unless they have thousands of sessions.

### Does Goldfish slow down Claude Code?

No noticeable impact. Reading `small.md` at session start adds ~50ms. Auto-save runs in the background every 5 minutes.

### Can I use Goldfish on multiple machines?

Yes! Point `memory_path` to a synced folder (Dropbox, iCloud, etc.):

```json
"memory_path": "~/Dropbox/Goldfish"
```

The system files (`~/.goldfish/`) are machine-specific, but your memories sync.

### What happens during a conflict in synced folders?

If two machines edit the same memory file simultaneously, your sync service (Dropbox, etc.) will create a conflict file. Resolve manually by merging the content.

### Can I back up my memories?

Yes. Your memories are in `~/Goldfish/`. Backup methods:
- Time Machine (macOS)
- Cloud sync (Dropbox, iCloud)
- Manual copy
- Git (for version control)

### How do I move memories to a new machine?

1. Install Goldfish on the new machine
2. Copy `~/Goldfish/` from old machine to new machine
3. Update `memory_path` in config if needed

## Troubleshooting

### Claude says it doesn't know about Goldfish

Start a new Claude Code session. Claude reads CLAUDE.md at startup, not during a session. If still broken, reinstall.

### Sessions aren't being captured

1. Check if auto-save is running: `launchctl list | grep goldfish`
2. Run manually: `~/.goldfish/scripts/auto-save.sh`
3. Check logs: `cat ~/.goldfish/logs/goldfish.log`

### How do I completely reset Goldfish?

```bash
# Uninstall
goldfish uninstall

# Remove memories (optional)
rm -rf ~/Goldfish

# Reinstall
curl -fsSL https://raw.githubusercontent.com/raydawg88/goldfish/main/install.sh | bash
```

## Contributing

### Can I contribute to Goldfish?

Yes! Issues and PRs are welcome at https://github.com/raydawg88/goldfish

### I have a feature idea

Open an issue on GitHub describing your idea. We're especially interested in:
- Better session routing
- More intelligent summarization
- Cross-platform support (Windows)
- Integration with other tools

### I found a bug

Please open an issue with:
- macOS/Linux version
- Steps to reproduce
- Output of `/gfstatus`
- Relevant log entries
