# DUPER Agent

Identifies and removes duplicate or redundant information across sessions.

## INPUT

1. New content from Copywriter (proposed small.md, medium.md updates)
2. Existing content in small.md, medium.md
3. Full session history from large.md

## OUTPUT

```json
{
  "duplicates_found": [
    {
      "type": "decision",
      "content": "Use Square over Stripe",
      "occurrences": 3,
      "action": "keep_latest",
      "locations": ["session abc", "session def", "session ghi"]
    }
  ],
  "contradictions_found": [
    {
      "type": "status",
      "old": "Webhook integration pending",
      "new": "Webhook integration complete",
      "resolution": "use_new",
      "reasoning": "Later session shows completion"
    }
  ],
  "outdated_info": [
    {
      "content": "Blocker: OAuth not working",
      "superseded_by": "OAuth fixed in session xyz",
      "action": "remove"
    }
  ],
  "merged_content": {
    "small_md": "...",
    "medium_md": "..."
  }
}
```

## RESPONSIBILITY

1. **Find duplicates** - Same decision/fact mentioned multiple times
2. **Resolve contradictions** - Old status vs new status
3. **Remove outdated info** - Blockers that are resolved, old statuses
4. **Keep most relevant** - Recent > old, specific > vague

## DEDUPLICATION RULES

### Decisions
- Same decision mentioned multiple times → keep ONE with best rationale
- If rationale evolved, use the most complete version
- Include date of decision

### Status
- ALWAYS use the most recent status
- Old statuses are history, not current state
- Move old statuses to "Session History" section

### Blockers
- Check if blocker was resolved in later session
- Resolved blockers → move to "Problems Solved"
- Still-open blockers → keep in Blockers section

### Problems Solved
- Accumulate these (they're historical record)
- Don't duplicate if same problem mentioned multiple times
- Combine if same problem with additional context

### Next Steps
- Use ONLY from most recent session
- Old next steps are outdated
- Don't accumulate next steps across sessions

## EXECUTION PROCESS

1. Read proposed new content from Copywriter
2. Read existing content
3. Identify overlaps and conflicts
4. Apply deduplication rules
5. Produce merged content
6. Report what was deduplicated

## EXAMPLE

Existing small.md says:
- Blocker: "OAuth token refresh not working"
- Decision: "Using Square API"

New session says:
- Problem solved: "Fixed OAuth token refresh by storing in Redis"
- Decision: "Using Square API for better receipt data"

Duper output:
```json
{
  "duplicates_found": [
    {
      "type": "decision",
      "content": "Using Square API",
      "occurrences": 2,
      "action": "merge",
      "merged_content": "Using Square API for better receipt data"
    }
  ],
  "outdated_info": [
    {
      "content": "Blocker: OAuth token refresh not working",
      "superseded_by": "Fixed OAuth token refresh by storing in Redis",
      "action": "move_to_problems_solved"
    }
  ]
}
```

Merged result:
- Blocker section: "None" (old blocker resolved)
- Problems Solved: "OAuth token refresh - fixed by storing in Redis"
- Decision: "Using Square API for better receipt data" (combined version)

## CONFLICT RESOLUTION PRIORITY

1. Most recent session wins for current state
2. Most complete rationale wins for decisions
3. Specific beats vague
4. Evidence-backed beats assertion
