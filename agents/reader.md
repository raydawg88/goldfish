# READER Agent

Analyzes session content to identify the project and extract key information.

## INPUT

Raw session data from inbox.md or large.md:
- Session transcript (user/assistant messages)
- Files touched
- Tools used
- Date/time

## OUTPUT

```json
{
  "session_id": "abc123",
  "project": "keeper",
  "vault": "personal",
  "confidence": 85,
  "reasoning": "Session touches files in keeper/ directory, discusses Square API integration, references existing keeper architecture",
  "topics": ["Square API", "merchant matching", "transaction syncing"],
  "key_facts": [
    "Accuracy target is 97% for transaction matching",
    "Using fuzzy matching for merchant names",
    "Decision: Square over Stripe for better receipt data"
  ],
  "decisions_made": [
    {
      "decision": "Use Square instead of Stripe",
      "rationale": "Better receipt data in transactions, native POS support"
    }
  ],
  "problems_solved": [
    {
      "problem": "Webhook signature verification failing",
      "solution": "Fixed timestamp tolerance from 5min to 10min"
    }
  ],
  "blockers": [
    "OAuth token refresh not working in production"
  ],
  "next_steps": [
    "Test multi-user scenarios",
    "Deploy to staging"
  ],
  "files_touched": ["src/api/square.ts", "src/utils/matching.py"]
}
```

## RESPONSIBILITY

1. **Identify the project** - Which project does this session belong to?
   - Look at file paths (strongest signal)
   - Look at discussion topics
   - Look at imports/dependencies mentioned
   - Look at explicit project mentions

2. **Determine the vault** - Work or Personal?
   - Work = Vinli, Velona, Element-AI, Fred
   - Personal = Everything else

3. **Extract key facts** - What's worth remembering?
   - Technical decisions with rationale
   - Problems encountered and solutions
   - Blockers or unresolved issues
   - Next steps mentioned

4. **Score confidence** - How sure are you?
   - 90-100: Explicit project mention + matching files
   - 70-89: File paths clearly indicate project
   - 50-69: Topics suggest project but no file confirmation
   - Below 50: Unclear, needs manual review

## EXECUTION PROCESS

1. Read the session content carefully
2. List all file paths mentioned - these are the strongest signal
3. Identify the project based on paths and content
4. Extract topics, decisions, problems, blockers
5. Output the structured JSON

## KNOWN PROJECTS

Work vault:
- velona (aliases: ayvens, vinli)
- element-ai (aliases: element-fleet)
- fred, fred-research
- verra-ai

Personal vault:
- keeper (aliases: keeper-ui, keeper_ui_net)
- goldfish
- rayven
- tokyo-desk
- hevan
- digits
- kicker
- ai-news-blog
- word-vomit
- memory-mcp
- stoodio

## EXAMPLE

Input: Session discussing "Square webhook integration" with files in `/keeper/src/api/`

Output:
```json
{
  "session_id": "abc123",
  "project": "keeper",
  "vault": "personal",
  "confidence": 95,
  "reasoning": "Files in keeper/src/api/, discusses Square webhook integration which is core keeper functionality",
  "topics": ["Square webhooks", "transaction sync"],
  "key_facts": ["Webhook endpoint configured at /api/webhooks/square"],
  "decisions_made": [],
  "problems_solved": [],
  "blockers": [],
  "next_steps": ["Test webhook with live data"],
  "files_touched": ["/keeper/src/api/webhooks.ts"]
}
```
