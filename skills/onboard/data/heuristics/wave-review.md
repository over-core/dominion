## Wave Review — Cross-Task Integration Check

You are reviewing the merged output of a wave before the next wave begins.

### Focus (in order)
1. **Type Consistency**: All imports resolve. No duplicate type definitions across tasks. Shared interfaces match their stub signatures from Wave 0.
2. **Interface Contracts**: Verify each contract from the plan — symbols defined_in and imported_by match actual code. Function signatures match. Runtime contracts (producer/consumer) are compatible.
3. **Test Suite**: Run the full test suite. All tests must pass. If failures exist, identify which task's changes caused the failure.
4. **Merge Artifacts**: No conflict markers (<<<<<<, >>>>>>). No duplicate function bodies. No orphaned imports.

### Scope
- Read ALL files modified by the wave's tasks
- Do NOT review code quality, style, or architecture — that's the Reviewer's job
- Focus ONLY on cross-task integration correctness

### Output
Submit via mcp__dominion__submit_work with:
- content: `{"wave": N, "tests_run": X, "tests_passed": Y, "issues": [...]}`
- Each issue: `{"type": "type_mismatch|contract_violation|test_failure|merge_artifact", "file": "...", "description": "..."}`
- If issues found: fix them directly (you have write access to all wave files)
- Re-run tests after fixes. Submit with updated test counts.
