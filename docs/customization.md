# Customizing Goldfish

Goldfish works great out of the box, but you can customize it to match your workflow.

## Configuration File

All settings live in `~/.goldfish/config.json`:

```json
{
  "version": "2.0.0",
  "memory_path": "~/Goldfish",
  "vaults": {
    "personal": {
      "description": "Side projects and personal stuff",
      "keywords": ["hobby", "personal", "learning"]
    },
    "work": {
      "description": "Day job projects",
      "keywords": ["client", "work", "business"]
    }
  },
  "default_vault": "personal",
  "auto_save": {
    "enabled": true,
    "interval_minutes": 5,
    "cooldown_seconds": 180
  },
  "projects": {}
}
```

## Changing Memory Location

To move your memories to a different location (e.g., Dropbox for sync):

1. Edit `~/.goldfish/config.json`
2. Change `memory_path`:
   ```json
   "memory_path": "~/Dropbox/Goldfish"
   ```
3. Move your existing memories:
   ```bash
   mv ~/Goldfish ~/Dropbox/Goldfish
   ```
4. Restart Claude Code

## Adding Vaults

Add new vaults by editing the `vaults` section:

```json
"vaults": {
  "personal": {
    "description": "Side projects",
    "keywords": ["hobby", "personal"]
  },
  "work": {
    "description": "Day job",
    "keywords": ["work", "office"]
  },
  "freelance": {
    "description": "Client work",
    "keywords": ["client", "freelance", "contract"]
  },
  "learning": {
    "description": "Courses and experiments",
    "keywords": ["learn", "tutorial", "course"]
  }
}
```

Then create the directory:

```bash
mkdir -p ~/Goldfish/freelance
mkdir -p ~/Goldfish/learning
```

## Project Aliases

If you refer to a project by different names, add aliases:

```json
"projects": {
  "my-saas": {
    "vault": "personal",
    "description": "My SaaS side project",
    "aliases": ["saas", "the-app", "my-app"]
  },
  "acme-corp": {
    "vault": "work",
    "description": "Acme Corporation client project",
    "aliases": ["acme", "client-acme"]
  }
}
```

Now sessions mentioning "acme" or "client-acme" will route to the `acme-corp` project.

## Vault Keywords

Keywords help auto-route sessions to the right vault:

```json
"vaults": {
  "work": {
    "description": "Work projects",
    "keywords": ["client", "sprint", "jira", "standup", "deployment"]
  }
}
```

If a session mentions "client" or "deployment", it's more likely to route to the work vault.

## Auto-Save Settings

Adjust how often sessions are captured:

```json
"auto_save": {
  "enabled": true,
  "interval_minutes": 5,
  "cooldown_seconds": 180
}
```

- `interval_minutes`: How often auto-save runs (default: 5)
- `cooldown_seconds`: Minimum time between saves (default: 180 / 3 minutes)

For heavy usage, you might increase the interval:

```json
"auto_save": {
  "enabled": true,
  "interval_minutes": 10,
  "cooldown_seconds": 300
}
```

## Disabling Auto-Save

If you prefer manual saves only:

```json
"auto_save": {
  "enabled": false
}
```

Then run `/gfsave` manually when you want to capture sessions.

## Custom Memory Templates

You can customize how new projects are created by editing the templates in `/gfnew` command, or by manually creating projects with your preferred structure.

Example custom `small.md`:

```markdown
# Project Name

**Description**

Status: 🟢 Active | 🟡 Paused | 🔴 Blocked

## Current Sprint
- [ ] Task 1
- [ ] Task 2

## Tech Stack
- Frontend:
- Backend:
- Database:

## Key Decisions
| Decision | Why | Date |
|----------|-----|------|

## Recent Work
-

---
*Updated: YYYY-MM-DD*
```

## Syncing Across Devices

To sync your memories across multiple machines:

### Option 1: Dropbox

```json
"memory_path": "~/Dropbox/Goldfish"
```

### Option 2: iCloud

```json
"memory_path": "~/Library/Mobile Documents/com~apple~CloudDocs/Goldfish"
```

### Option 3: Git

Initialize your Goldfish directory as a git repo:

```bash
cd ~/Goldfish
git init
git add .
git commit -m "Initial goldfish memories"
git remote add origin <your-repo-url>
git push -u origin main
```

Then pull on other machines. Note: `large.md` files can get big, so consider `.gitignore`-ing them.

## Backup Strategy

Recommended backup approach:

1. **Regular backups**: Your memory path (`~/Goldfish`) contains all your memories
2. **Version control**: Consider git for the memory folder
3. **Cloud sync**: Dropbox/iCloud provides automatic backup

The `~/.goldfish/` system folder can be recreated by reinstalling, so backing it up is optional.

## Resetting Goldfish

To start fresh without uninstalling:

```bash
# Clear processed sessions (will reprocess everything)
rm ~/.goldfish/state/processed-sessions.json

# Clear a specific project's memories
rm -rf ~/Goldfish/personal/project-name/goldfish/*

# Clear all memories (nuclear option)
rm -rf ~/Goldfish/*/*/goldfish/*
```

## Advanced: Custom Routing Logic

For complex routing needs, you can modify `~/.goldfish/scripts/reader.py` to add custom classification logic. Look for the `classify_session` function.

Example: Route all sessions mentioning "secret-project" to a hidden vault:

```python
if "secret-project" in msg.lower():
    classification["vault"] = "private"
    classification["project"] = "secret-project"
    classification["confidence"] = 100
```
