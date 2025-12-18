# 🐠 Goldfish Status

Check Goldfish system health and recent activity.

## Run These Checks

### 1. Version Check
```bash
cat ~/.goldfish/version 2>/dev/null || echo "NOT INSTALLED"
```

### 2. Config Check
```bash
cat ~/.goldfish/config.json 2>/dev/null | head -10
```

### 3. Memory Location
```bash
MEMORY_PATH=$(python3 -c "import json; print(json.load(open('$HOME/.goldfish/config.json'))['memory_path'])" 2>/dev/null)
echo "Memory path: $MEMORY_PATH"
ls -la "$MEMORY_PATH" 2>/dev/null | head -10
```

### 4. Vaults and Projects
```bash
for vault in $(ls ~/Goldfish 2>/dev/null); do
    echo "=== $vault ==="
    ls ~/Goldfish/$vault 2>/dev/null
done
```

### 5. Pending Processing
```bash
grep -r "NEEDS_PROCESSING" ~/Goldfish/*/*/goldfish/inbox.md 2>/dev/null | wc -l
```

### 6. Last Auto-Save
```bash
if [ -f ~/.goldfish/state/last-save ]; then
    LAST=$(cat ~/.goldfish/state/last-save)
    NOW=$(date +%s)
    AGO=$((NOW - LAST))
    echo "Last save: $AGO seconds ago"
else
    echo "No auto-save recorded yet"
fi
```

### 7. Recent Log Activity
```bash
tail -20 ~/.goldfish/logs/goldfish.log 2>/dev/null || echo "No logs yet"
```

### 8. Auto-Save Service Status
For Mac:
```bash
launchctl list | grep goldfish
```

For Linux:
```bash
crontab -l | grep goldfish
```

## Report Format

```
🐠 GOLDFISH STATUS

Installation: ✓ v2.0.0
Location: ~/.goldfish/

Memory Path: ~/Goldfish
Vaults:
  • personal (5 projects)
  • work (2 projects)

Recent Activity:
  Last auto-save: 3 minutes ago
  Pending processing: 2 projects

Auto-Save Service: ✓ Running

System Health: ✓ All good
```

## If Something Is Wrong

**"NOT INSTALLED"**
- Goldfish isn't installed. Run the installer.

**"No auto-save recorded"**
- Auto-save hasn't run yet. Wait 5 minutes or run manually:
  `~/.goldfish/scripts/auto-save.sh`

**"Service not found"**
- Auto-save service isn't running. Reinstall or check:
  - Mac: `launchctl load ~/Library/LaunchAgents/com.goldfish.autosave.plist`
  - Linux: Check crontab

**"Permission denied"**
- Scripts need execute permission:
  `chmod +x ~/.goldfish/scripts/*.sh`

**"Memory path not found"**
- The configured memory location doesn't exist
- Check config.json and create the directory
