# STRIDE Threat Analysis Protocol

Apply STRIDE threat modeling to code changes:

| Threat | Question | Check |
|--------|----------|-------|
| **S**poofing | Can an attacker impersonate a user or system? | Auth mechanisms, session management, token validation |
| **T**ampering | Can data be modified in transit or at rest? | Input validation, data integrity, signed payloads |
| **R**epudiation | Can actions be denied? | Audit logging, transaction logs, non-repudiation |
| **I**nformation Disclosure | Can sensitive data leak? | Error messages, logs, API responses, debug info |
| **D**enial of Service | Can the system be overwhelmed? | Rate limiting, resource bounds, timeout handling |
| **E**levation of Privilege | Can permissions be escalated? | Access control, role boundaries, admin interfaces |

## Finding Format

Each security finding in security-findings.toml must include:
- `threat_type`: S | T | R | I | D | E
- `severity`: critical | high | medium | low
- `cwe_id`: CWE number if applicable
- `title`: short description
- `description`: technical detail + attack scenario
- `remediation`: specific fix with code guidance
- `evidence`: file:line references
