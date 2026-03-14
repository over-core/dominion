# Adaptive Requirements Framework

Use this framework when complexity is **complex** or **major** to capture structured requirements during the discuss step.

## 1. Jobs-to-be-Done

Ask the user:
> "When [situation], I want to [motivation], so I can [outcome]."

Capture the core job. This frames everything else.

## 2. User Stories

For each distinct capability:
> "As a [role], I want [capability], so that [benefit]."

Keep stories atomic — one capability per story.

## 3. Acceptance Criteria

For each user story, define Given/When/Then criteria with concrete values:

```
Given [specific context with real values]
When [specific action]
Then [specific observable outcome]
```

Avoid vague criteria. "The system should be fast" is not a criterion. "Response time < 200ms for 95th percentile" is.

## 4. Success Metrics

Ask the user:
> "How will we measure if this worked?"

Capture measurable outcomes:
- Performance targets (latency, throughput)
- Quality targets (test coverage, error rate)
- User impact (adoption, task completion time)

## 5. Risk Assessment

Identify risks and their blast radius:
- What could go wrong?
- What's the worst-case impact?
- What's the rollback strategy?
- Are there dependencies that could block us?

Write the structured intent to the phase directory via `agent_submit`.
