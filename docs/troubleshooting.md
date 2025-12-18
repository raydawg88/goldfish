# Troubleshooting Goldfish

Common issues and how to fix them.

## Quick Diagnostics

Run `/gfstatus` in Claude Code to check system health. This will show you:
- Installation status
- Memory location
- Vault/project counts
- Last auto-save time
- Pending processing
- Service status

## Common Issues

### "Claude doesn't know about Goldfish"

**Symptoms:**
- Claude says "I don't see any Goldfish installation"
- Claude searches for scripts instead of using commands
- Commands like `/gfsave` don't work

**Solutions:**

1. **Start a new session** — Claude reads CLAUDE.md at startup, not during a session
   ```bash
   # Close current Claude session and start fresh
   claude
   ```

2. **Check CLAUDE.md injection** — Verify Goldfish section exists:
   ```bash
   grep "GOLDFISH:START" ~/.claude/CLAUDE.md
   ```

   If not found, reinstall:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/raydawg88/goldfish/main/install.sh | bash
   ```

3. **Check for syntax errors** — If you edited CLAUDE.md manually:
   ```bash
   cat ~/.claude/CLAUDE.md | head -100
   ```
   Look for broken markdown or missing closing tags.

### "Auto-save isn't running"

**Symptoms:**
- `large.md` files aren't updating
- `/gfstatus` shows old "last save" time

**Solutions:**

1. **Check service status (macOS):**
   ```bash
   launchctl list | grep goldfish
   ```

   If not listed, reload:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.goldfish.autosave.plist
   ```

2. **Check service status (Linux):**
   ```bash
   crontab -l | grep goldfish
   ```

   If not listed, add manually:
   ```bash
   (crontab -l 2>/dev/null; echo "*/5 * * * * ~/.goldfish/scripts/auto-save.sh") | crontab -
   ```

3. **Run manually to test:**
   ```bash
   ~/.goldfish/scripts/auto-save.sh
   ```
   Check output for errors.

4. **Check logs:**
   ```bash
   cat ~/.goldfish/logs/goldfish.log | tail -50
   ```

### "Sessions aren't being captured"

**Symptoms:**
- You've been working but nothing appears in `large.md`
- `inbox.md` stays empty

**Solutions:**

1. **Check if Claude Code is saving sessions:**
   ```bash
   ls -la ~/.claude/projects/
   ```
   You should see `.jsonl` files with recent timestamps.

2. **Check reader output:**
   ```bash
   cd ~/.goldfish/scripts && python3 reader.py
   ```
   Look for errors or "0 sessions found".

3. **Check processed sessions list:**
   ```bash
   cat ~/.goldfish/state/processed-sessions.json | wc -l
   ```
   If this is very high, sessions might already be processed.

4. **Reset processed list:**
   ```bash
   rm ~/.goldfish/state/processed-sessions.json
   ~/.goldfish/scripts/auto-save.sh
   ```

### "Sessions going to wrong project"

**Symptoms:**
- Work sessions appearing in personal vault
- Sessions mixed between projects

**Solutions:**

1. **Add project aliases** in `~/.goldfish/config.json`:
   ```json
   "projects": {
     "my-project": {
       "vault": "work",
       "aliases": ["myproject", "my_project", "the-project"]
     }
   }
   ```

2. **Add vault keywords:**
   ```json
   "vaults": {
     "work": {
       "keywords": ["client", "sprint", "deploy", "production"]
     }
   }
   ```

3. **Be explicit** when starting work:
   ```
   "This is my work project called api-redesign"
   ```

### "Permission denied" errors

**Symptoms:**
- Scripts fail with permission errors
- Can't write to memory files

**Solutions:**

1. **Fix script permissions:**
   ```bash
   chmod +x ~/.goldfish/scripts/*.sh
   chmod +x ~/.goldfish/scripts/*.py
   ```

2. **Fix memory directory permissions:**
   ```bash
   chmod -R 755 ~/Goldfish
   ```

3. **Check disk space:**
   ```bash
   df -h ~
   ```

### "/gfsave produces poor summaries"

**Symptoms:**
- Summaries are too generic
- Important details missing
- Status outdated

**Solutions:**

1. **Provide more context** when running `/gfsave`:
   ```
   /gfsave

   Focus on the authentication work we did today.
   The key decision was using JWT instead of sessions.
   ```

2. **Edit summaries manually** — Memory files are just markdown:
   ```bash
   nano ~/Goldfish/personal/my-project/goldfish/small.md
   ```

3. **Clear and regenerate:**
   ```bash
   # Backup first
   cp ~/Goldfish/personal/my-project/goldfish/small.md ~/small.md.backup

   # Clear summaries (keep large.md)
   echo "" > ~/Goldfish/personal/my-project/goldfish/small.md
   echo "" > ~/Goldfish/personal/my-project/goldfish/medium.md

   # Run /gfsave again
   ```

### "Config file is corrupted"

**Symptoms:**
- Scripts crash with JSON errors
- Installer won't complete

**Solutions:**

1. **Check JSON syntax:**
   ```bash
   python3 -c "import json; json.load(open('$HOME/.goldfish/config.json'))"
   ```

2. **View the error:**
   ```bash
   cat ~/.goldfish/config.json
   ```
   Look for missing commas, brackets, or quotes.

3. **Reset to default:**
   ```bash
   cat > ~/.goldfish/config.json << 'EOF'
   {
     "version": "2.0.0",
     "memory_path": "~/Goldfish",
     "vaults": {
       "personal": {"description": "Personal projects", "keywords": []},
       "work": {"description": "Work projects", "keywords": []}
     },
     "default_vault": "personal",
     "auto_save": {"enabled": true, "interval_minutes": 5, "cooldown_seconds": 180},
     "projects": {}
   }
   EOF
   ```

## Getting Help

If you're still stuck:

1. **Check logs:** `~/.goldfish/logs/goldfish.log`
2. **Run diagnostics:** `/gfstatus` in Claude
3. **Open an issue:** https://github.com/raydawg88/goldfish/issues

Include:
- macOS/Linux version
- Output of `/gfstatus`
- Relevant log entries
- Steps to reproduce
