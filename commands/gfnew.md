# 🐠 Goldfish New Project

Create a new project with Goldfish memory structure.

## Usage

The user will tell you the project name and which vault. Parse their request:
- "Create a new project called my-app in personal"
- "Let's start a work project named api-redesign"
- "New project: learning-rust in personal"

If they don't specify a vault, ask which one.

## Steps

### Step 1: Get Config

```bash
cat ~/.goldfish/config.json
```

Extract:
- `memory_path` - where to create the project
- `vaults` - available vault names

### Step 2: Validate Input

- Project name should be lowercase, use dashes for spaces
- Vault must exist in config

### Step 3: Create Directory Structure

```bash
PROJECT_PATH="[memory_path]/[vault]/[project-name]"
mkdir -p "$PROJECT_PATH/goldfish"
```

### Step 4: Create Memory Files

**small.md:**
```markdown
# [Project Name]

**[Ask user for one-line description or infer from context]**

Sessions: 0 | Last: Never

## Quick Context
- **Status:** New project, just created
- **Stack:** [To be determined]

## Recent Work
(No sessions yet)

---
*medium.md = working context | large.md = full history*
```

**medium.md:**
```markdown
# [Project Name]

**[Description]**

Sessions: 0 | Updated: [today's date]

## Session History

(No sessions yet)

---
*See large.md for complete chat transcripts*
```

**large.md:**
```markdown
# [Project Name] - Complete History

*Full session transcripts appended automatically*

(No sessions yet)
```

**inbox.md:**
```markdown
# [Project Name] - Inbox

No pending sessions.

Last updated: [today's date]
```

### Step 5: Confirm Creation

```
🐠 PROJECT CREATED

Name: [project-name]
Vault: [vault]
Path: [full path]/goldfish/

Memory files created:
  ✓ small.md (quick context)
  ✓ medium.md (working context)
  ✓ large.md (full history)
  ✓ inbox.md (processing queue)

Ready to use! Sessions in this project will be automatically captured.

Tip: When you're done working, run /gfsave to create quality summaries.
```

## Alternative: Natural Language

Users don't have to use /gfnew explicitly. They can just say:
- "This is a personal project called side-hustle"
- "Let's put this in the work vault as client-acme"

When you hear this, create the project structure the same way.

## Error Cases

**Vault doesn't exist:**
```
That vault doesn't exist. Available vaults: personal, work

Would you like to create the project in one of these?
```

**Project already exists:**
```
Project [name] already exists in [vault].

Would you like to:
1. Use the existing project (I'll load its context)
2. Create with a different name
```

**Invalid project name:**
```
Project names should be lowercase with dashes instead of spaces.

Suggested: [sanitized-name]

Use this name?
```
