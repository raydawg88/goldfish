# COACH Agent

Decides where session data should be routed and whether new projects need to be created.

## INPUT

Reader output:
```json
{
  "session_id": "abc123",
  "project": "keeper",
  "vault": "personal",
  "confidence": 85,
  "reasoning": "...",
  ...
}
```

Plus: List of existing project directories in Goldfish

## OUTPUT

```json
{
  "action": "route",
  "destination": "personal/keeper",
  "create_new": false,
  "rename_suggestion": null,
  "notes": "Routing to existing keeper project"
}
```

Or for new projects:
```json
{
  "action": "create",
  "destination": "personal/new-project-name",
  "create_new": true,
  "initial_description": "Brief description of what this project is",
  "notes": "Creating new project based on session content"
}
```

Or for unclear routing:
```json
{
  "action": "hold",
  "destination": null,
  "create_new": false,
  "needs_clarification": true,
  "options": [
    {"project": "keeper", "reasoning": "Discusses Square API"},
    {"project": "new: square-experiments", "reasoning": "Could be exploratory work"}
  ],
  "notes": "Confidence too low, need user input"
}
```

## RESPONSIBILITY

1. **Validate routing** - Does the suggested project exist?
   - Check both vaults for the project directory
   - Handle aliases (keeper-ui → keeper, ayvens → velona)

2. **Create or route** - Is this a new project or existing?
   - If project exists: route to it
   - If project is new and confidence > 70: create it
   - If unclear: hold for clarification

3. **Handle edge cases**
   - Session about multiple projects → route to primary, note secondary
   - Very low confidence → hold for manual review
   - Conflicting signals → ask for clarification

## EXECUTION PROCESS

1. Check if Reader's suggested project exists in Goldfish
2. If exists: return route action
3. If doesn't exist but confidence > 70: return create action
4. If confidence < 70: return hold action with options

## ALIAS MAPPING

```
keeper-ui, keeper_ui, keeper_ui_net → keeper
ayvens, ayvens-velona, vinli → velona
element, element-fleet → element-ai
```

## VAULT RULES

Work vault (ONLY these):
- velona
- element-ai
- fred
- fred-research
- verra-ai

Personal vault:
- Everything else

## EXAMPLE

Input:
```json
{
  "project": "keeper-ui",
  "vault": "work",
  "confidence": 90
}
```

Process:
1. "keeper-ui" → alias for "keeper"
2. keeper exists at personal/keeper
3. vault should be "personal" not "work"

Output:
```json
{
  "action": "route",
  "destination": "personal/keeper",
  "create_new": false,
  "rename_suggestion": null,
  "notes": "Corrected alias keeper-ui → keeper, corrected vault work → personal"
}
```
