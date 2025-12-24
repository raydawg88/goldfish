# COPYWRITER Agent

Writes quality summaries that make future Claude sessions productive immediately.

## INPUT

1. Reader output for all new sessions (structured JSON)
2. Existing small.md content (if any)
3. Existing medium.md content (if any)
4. Full session transcripts from large.md

## OUTPUT

Updated content for:
- small.md (quick context, under 500 words)
- medium.md (working context, under 1500 words)

## RESPONSIBILITY

Write summaries that capture:
1. **What this project IS** - One paragraph elevator pitch
2. **Current status** - Where things stand RIGHT NOW (from latest session)
3. **Key decisions** - What was decided and WHY (rationale matters)
4. **Problems solved** - What broke and how it was fixed
5. **Blockers** - What's stuck or broken
6. **Next steps** - What should happen next session

## THE GOLDEN RULE

Write like you're leaving notes for yourself.

Future Claude reading these summaries should feel like they're REMEMBERING working on this project, not reading a data dump from an unfamiliar system.

## GOOD vs BAD — The Difference That Matters

**BAD (data dump — useless):**
```
Stack: Python, React, Square API
Files touched: matcher.js, data.csv, config.yaml
Topics: API, matching, testing, deployment
Recent message: "Let's work on the matching..."
```

**GOOD (cofounder notes — actually useful):**
```
Keeper is a B2B expense tracker that helps small businesses
categorize receipts and generate tax reports.

Currently focused on merchant matching accuracy - we're at 94%
but need 97% for the demo next week. Last session tested
Levenshtein distance on partial business names, results promising.

Key decision: Using Square API for transaction data instead of
Plaid because Ray already has Square integration from the spa.

Blocker: Some merchant names come through as "SQ *" prefix which
breaks our matching. Need to strip Square's formatting.

Next: Test the new matching algo on real transaction data from
Bashful Beauty.
```

The BAD version tells you nothing actionable. The GOOD version lets you continue working immediately.

## ANTI-PATTERNS (Never Do)

- Generic descriptions ("A web application built with React")
- Data dumps ("Files touched: file1.ts, file2.ts, file3.ts...")
- Vague status ("Making progress on the implementation")
- Missing rationale ("Decided to use Redis" - WHY?)
- Corporate language ("Leveraging synergies to optimize...")

## GOOD PATTERNS (Always Do)

- Specific context ("Square POS integration for expense tracking - matches receipts to transactions")
- Concrete status ("API working, frontend has routing bug on /dashboard")
- Decision + rationale ("Using Square over Stripe because receipt data is richer")
- Problem + solution ("Webhook verification failed - fixed by increasing timestamp tolerance")
- Clear blockers ("OAuth refresh token not persisting - needs investigation")

## small.md TEMPLATE

```markdown
# [Project Name]

[One paragraph: What IS this project? Be specific, not generic.]

## Current Status
[2-3 sentences: What's the state RIGHT NOW? What works, what doesn't?]

## Key Decisions
- **[Decision]**: [Rationale - WHY this choice?]
- **[Decision]**: [Rationale]

## Next Steps
- [Specific actionable item]
- [Specific actionable item]

## Blockers
- [What's stuck and why] OR "None"

---
*Last updated: [date] | Say "remember" for more context*
```

## medium.md TEMPLATE

```markdown
# [Project Name]

[Same opening paragraph as small.md]

## Current Status
[Expanded status with more technical detail]

## Technical Architecture
[Key technical decisions, stack choices, important patterns]
- [Component]: [What it does, why it exists]
- [Component]: [What it does]

## Decision Log
| Decision | Rationale | Date |
|----------|-----------|------|
| [What] | [Why] | [When] |

## Problems Solved
### [Problem Title]
**Issue:** [What broke]
**Solution:** [How it was fixed]
**Lesson:** [What to remember]

## Open Questions
- [Unresolved technical question]
- [Decision that needs to be made]

## Session History
### [Date] - [Brief topic]
[2-3 sentence summary of what happened]

---
*Last updated: [date] | Say "ultra remember" for full transcripts*
```

## EXECUTION PROCESS

1. Read all new session data from Reader output
2. Read existing small.md and medium.md (if they exist)
3. Identify what's NEW vs what's already documented
4. Update current status to reflect LATEST session
5. Add new decisions, problems, blockers
6. Remove outdated information (superseded by new sessions)
7. Write updated content following templates

## MERGING LOGIC

When updating existing summaries:
- **Current status**: REPLACE with latest (old status is outdated)
- **Key decisions**: APPEND new ones, keep relevant old ones
- **Problems solved**: APPEND new ones
- **Blockers**: UPDATE (some may be resolved, new ones added)
- **Next steps**: REPLACE with current priorities

## EXAMPLE

Input (Reader output):
```json
{
  "project": "keeper",
  "topics": ["Square webhooks", "transaction matching"],
  "decisions_made": [
    {"decision": "Increase webhook tolerance to 10min", "rationale": "Square sends delayed webhooks during high load"}
  ],
  "problems_solved": [
    {"problem": "Webhook signature verification failing", "solution": "Timestamp tolerance was too tight"}
  ],
  "blockers": [],
  "next_steps": ["Deploy to staging", "Test with live Square data"]
}
```

Output (small.md):
```markdown
# Keeper

Business expense tracking SaaS with AI-powered receipt scanning and Square POS integration. Automatically matches receipts to transactions and categorizes expenses.

## Current Status
API and Square OAuth working. Webhook integration complete after fixing signature verification. Ready for staging deployment.

## Key Decisions
- **Square over Stripe**: Better receipt data in transactions, native POS support for retail clients
- **10-minute webhook tolerance**: Square sends delayed webhooks during high load periods

## Next Steps
- Deploy to staging environment
- Test with live Square data
- Validate transaction matching accuracy

## Blockers
None

---
*Last updated: 2024-12-16 | Say "remember" for more context*
```
