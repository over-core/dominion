# API Design Protocol

## Contract-First Design

Design the schema BEFORE writing code. The contract IS the deliverable.

1. **Understand consumers** — who calls this API? What do they need? Consumer-driven contracts beat speculative design.
2. **Choose protocol** — REST (CRUD resources), GraphQL (flexible queries), gRPC (high-perf internal). Don't mix without reason.
3. **Schema first** — write OpenAPI spec / GraphQL schema / .proto file. Validate with tooling (spectral, buf lint) before implementation.
4. **Version from day one** — URL versioning (/v1/) for REST, schema evolution for GraphQL, package versioning for gRPC. Never break consumers.

## Versioning & Compatibility

- **Additive changes are safe** — new fields, new endpoints, new optional parameters
- **Breaking changes require a new version** — removed fields, changed types, renamed endpoints
- Apply **Postel's Law**: be liberal in what you accept, conservative in what you send
- Run consumer-driven contract tests (Pact) when consumers are known

## Security Surface

Every API endpoint is an attack surface:
- Validate all input (type, range, format)
- Rate limit public endpoints
- Authenticate before authorizing
- Return minimal error details to clients (no stack traces, no internal paths)
- CORS configuration for browser-facing APIs

## Richardson Maturity

For REST APIs, target Level 2 minimum (resources + HTTP verbs + status codes). Level 3 (HATEOAS) only when consumers benefit from discoverability.
