# ISO 25010 Quality Rubric

Shared rubric for quality baseline (Researcher) and post-phase assessment (Reviewer). Score each applicable characteristic 1–5. Not all characteristics apply to every phase — score only those affected by the current scope.

## Scoring Scale

| Score | Meaning |
|-------|---------|
| 1 — Poor | Systemic issues, patterns missing or actively harmful |
| 2 — Below Average | Several major issues, practices applied inconsistently |
| 3 — Average | Adequate practices, some gaps, no systemic failures |
| 4 — Good | Consistent practices, minor gaps only |
| 5 — Excellent | Strong uniform practices, minimal improvement possible |

## Quality Characteristics

### 1. Functional Suitability
Assess correctness of behavior, completeness of feature coverage, appropriateness of function design for actual use cases. Score 1 if core functions produce wrong results or critical features missing. Score 5 if all specified behaviors correct and function design matches real usage patterns.

### 2. Performance Efficiency
Assess time behavior under expected load, resource utilization (CPU, memory, disk, network), capacity limits. Score 1 if response times unacceptable or resource consumption unbounded. Score 5 if performance targets met with headroom and resource usage optimized.

### 3. Compatibility
Assess co-existence with other systems sharing resources, interoperability via APIs/protocols/data formats. Score 1 if system conflicts with co-residents or cannot exchange data with required integrations. Score 5 if clean co-existence and standards-based interoperability throughout.

### 4. Usability
Assess learnability for new users, operability for experienced users, error protection/recovery, interface consistency, accessibility. Score 1 if users cannot complete tasks without external help or errors are unrecoverable. Score 5 if self-explanatory workflows, consistent patterns, graceful error handling.

### 5. Reliability
Assess maturity (failure frequency), availability under normal operation, fault tolerance (continued operation during faults), recoverability (data/state restoration after failure). Score 1 if frequent failures with data loss. Score 5 if failures rare, degraded mode available, recovery automated.

### 6. Security
Assess confidentiality (data access control), integrity (prevention of unauthorized modification), non-repudiation (audit trails), accountability (action traceability), authenticity (identity verification). Score 1 if secrets exposed or no access control. Score 5 if defense-in-depth applied, secrets managed, audit trail complete.

### 7. Maintainability
Assess modularity (component independence), reusability (component extraction), analysability (ease of diagnosing issues), modifiability (change cost), testability (validation ease). Score 1 if monolithic, changes cause cascading failures, untestable. Score 5 if loosely coupled, single-responsibility, well-tested.

### 8. Portability
Assess adaptability to different environments, installability (setup complexity), replaceability (substitution of components). Score 1 if hardcoded to single environment or installation requires tribal knowledge. Score 5 if environment-agnostic, single-command install, components swappable.

## Usage

### Researcher (Baseline)
- Score at end of explore step. Record in `research.toml` as structured data.
- Score only characteristics relevant to phase scope.
- Evidence-grade each score: `confirmed` (code/config proof), `supported` (multiple signals), `inferred` (single signal or absence).

### Reviewer (Post-Phase Delta)
- Score at review step after implementation. Compare against Researcher baseline.
- Report delta per characteristic. Score drops flag review findings; improvements validate methodology.
- Deltas of ±0 are normal — only report characteristics with non-zero delta.
