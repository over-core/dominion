# Kill Gate

Step 2 of the study pipeline. The Advisor decides which items proceed to recreation.

## Gate Criteria

For each item that passed security review, the Advisor must answer:

1. **Concrete scenarios**: Name at least 2 specific situations in this project where this item would fire.
   - "When the developer edits API endpoints" — concrete
   - "It might help with code quality" — too vague, KILL

2. **Outcome improvement**: What measurably improves when this item is used?
   - "Catches OpenAPI spec drift before it reaches production" — measurable
   - "Generally makes things better" — not measurable, KILL

3. **Existing coverage**: Does a Dominion agent or skill already cover this?
   - If fully covered: KILL (avoid duplication)
   - If partially covered: note what's additive, proceed if substantial

## Presentation

```
Kill Gate Results:
  PASS: {name} — {reason}
    Scenarios: {scenario_1}, {scenario_2}
    Improves: {outcome}

  KILL: {name} — {reason}
    Why: {explanation}
```

## Strictness

This gate is intentionally strict. The cost of recreating a useless skill is wasted tokens and artifact bloat. The cost of killing a marginally useful skill is zero — the original plugin remains available.

If zero items pass: "No items from {plugin} passed the benefit threshold for this project. The plugin's capabilities are either already covered by Dominion agents or not concretely applicable."
