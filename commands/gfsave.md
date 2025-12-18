# 🐠 Goldfish Quality Save

Save this session to Goldfish memory with quality AI-generated summaries.

## What This Does

1. Triggers auto-save to capture raw transcripts
2. Processes inbox.md files through the agent pipeline
3. Updates small.md and medium.md with quality summaries
4. Reports what was saved

## Steps

### Step 1: Trigger Auto-Save

```bash
~/.goldfish/scripts/auto-save.sh
```

### Step 2: Check What Needs Processing

```bash
grep -r "NEEDS_PROCESSING" ~/Goldfish/*/*/goldfish/inbox.md 2>/dev/null
```

If nothing needs processing, report "All memories up to date" and stop.

### Step 3: For Each Project Needing Processing

Run the agent pipeline (you ARE the agents):

**3a. Read the project's files:**
- Read `goldfish/inbox.md` to see what sessions are new
- Read `goldfish/large.md` for the raw transcripts
- Read `goldfish/small.md` and `goldfish/medium.md` for existing summaries

**3b. Analyze what happened:**
- What was the user working on?
- What decisions were made and WHY?
- What problems were solved?
- What blockers exist?
- What are the next steps?

**3c. Update small.md:**
- Current status (from LATEST session)
- Key decisions with rationale
- Stack/technologies used
- Recent work summary (2-3 bullets)

**3d. Update medium.md:**
- Add session summary for each new session
- What happened, what was built
- Problems solved, blockers hit

**3e. Clear the inbox:**
Replace inbox.md content with:
```markdown
# [Project Name] - Inbox

All sessions processed. Memory up to date.

Last updated: [current date]
```

### Step 4: Report Results

```
🐠 GOLDFISH SAVE COMPLETE

Projects Updated:
  ✓ keeper (2 sessions)
    - Added: Square webhook decision
    - Status: OAuth integration complete

  ✓ side-project (1 session)
    - Added: Initial setup notes

All inbox flags cleared.
```

## Quality Standards

When writing summaries:

**DO:**
- Capture WHY decisions were made, not just WHAT
- Use current status from LATEST session only
- Write like leaving notes for yourself
- Be specific: "Using PostgreSQL for user data" not "Set up database"
- Include blockers and next steps

**DON'T:**
- Write generic descriptions
- Use corporate language
- Duplicate information that's already there
- Include outdated status (old blockers that are resolved)

## If No Projects Need Processing

```
🐠 GOLDFISH: All memories up to date.

No projects need processing.
Last auto-save: [check ~/.goldfish/state/last-save]

To force a refresh:
  rm ~/.goldfish/state/processed-sessions.json
  ~/.goldfish/scripts/auto-save.sh
```
