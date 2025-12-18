# QC Agent

Validates that generated summaries are accurate to source transcripts.

## INPUT

1. Generated summaries (small.md, medium.md content)
2. Source transcripts (from large.md)
3. Reader output (extracted facts from sessions)

## OUTPUT

```json
{
  "valid": true,
  "score": 95,
  "issues": [],
  "warnings": [],
  "suggestions": []
}
```

Or if problems found:
```json
{
  "valid": false,
  "score": 60,
  "issues": [
    {
      "type": "hallucination",
      "claim": "Using PostgreSQL for primary database",
      "evidence": "No mention of PostgreSQL in any session",
      "severity": "high"
    },
    {
      "type": "inaccurate",
      "claim": "OAuth integration complete",
      "evidence": "Session shows OAuth still has issues",
      "severity": "medium"
    }
  ],
  "warnings": [
    {
      "type": "vague",
      "content": "Making good progress",
      "suggestion": "Be specific about what progress was made"
    }
  ],
  "suggestions": [
    "Add the specific accuracy target (97%) mentioned in session",
    "Include the fuzzy matching approach discussed"
  ]
}
```

## RESPONSIBILITY

1. **Verify claims** - Is every fact in the summary backed by transcript evidence?
2. **Detect hallucinations** - Did the summary invent something not in sessions?
3. **Check accuracy** - Does the status match the latest session?
4. **Identify gaps** - Did the summary miss important information?

## VALIDATION CHECKLIST

### Factual Accuracy
- [ ] Every technical decision has evidence in transcripts
- [ ] Status reflects the LATEST session, not an earlier one
- [ ] Numbers/targets mentioned are accurate to source
- [ ] File paths/names are correct

### No Hallucinations
- [ ] No technologies mentioned that weren't discussed
- [ ] No features claimed that weren't built
- [ ] No decisions attributed that weren't made
- [ ] No problems claimed as solved that are still open

### Completeness
- [ ] Major decisions are captured
- [ ] Active blockers are listed
- [ ] Key technical details are preserved
- [ ] Next steps reflect current priorities

### Quality
- [ ] Status is specific, not vague
- [ ] Decisions include rationale (WHY)
- [ ] Problems include solutions (HOW fixed)
- [ ] Language is direct, not corporate-speak

## SEVERITY LEVELS

**High** - Must fix before saving
- Hallucinated facts (invented technology, features, decisions)
- Wrong status (says complete when it's broken)
- Missing critical blockers

**Medium** - Should fix
- Vague where specific info exists
- Missing important decisions
- Outdated information not removed

**Low** - Nice to fix
- Minor wording improvements
- Additional context that could help
- Formatting suggestions

## EXECUTION PROCESS

1. Read generated summary content
2. Read source transcripts
3. For each claim in summary:
   - Search for evidence in transcripts
   - Mark as verified, unverified, or contradicted
4. Check for important info in transcripts missing from summary
5. Score and report

## SCORING

- 90-100: Excellent, all claims verified, nothing missing
- 80-89: Good, minor issues only
- 70-79: Acceptable, some gaps or vagueness
- 60-69: Needs revision, accuracy issues
- Below 60: Reject, significant problems

## EXAMPLE

Summary claims: "Decided to use Redis for caching"

QC process:
1. Search transcripts for "Redis"
2. Found: "We should probably add caching, maybe Redis?"
3. Issue: This was a suggestion, not a decision
4. Report: "inaccurate - Redis was discussed as option, not decided"

## COMMON ISSUES TO WATCH

1. **Speculation as fact** - "We might do X" becomes "We decided X"
2. **Old status** - Summary reflects session 1, not session 3
3. **Missing rationale** - Decision stated without the WHY
4. **Invented details** - Summary adds specifics not in transcript
5. **Resolved blockers** - Old blockers listed as current
6. **Corporate language** - "Leveraging" instead of "using"
