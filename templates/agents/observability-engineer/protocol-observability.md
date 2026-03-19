# Observability Engineering Protocol

## Observability Audit

Assess current state across three pillars:
1. **Metrics** — what's measured? Prometheus, StatsD, CloudWatch? Check Golden Signals coverage (latency, traffic, errors, saturation)
2. **Logs** — structured or unstructured? Centralized? Retention policy? Correlation IDs present?
3. **Traces** — distributed tracing instrumented? OpenTelemetry? Span coverage across services?

## SLO Design

1. Define SLIs (Service Level Indicators) — measurable metrics that reflect user experience
   - Availability: successful requests / total requests
   - Latency: p50, p95, p99 response times
   - Correctness: correct responses / total responses
2. Set SLOs (Service Level Objectives) — target values with error budget
   - Example: 99.9% availability = 43.8 minutes downtime/month budget
3. Alert on error budget burn rate, NOT on thresholds
   - Fast burn (>14.4x): page immediately
   - Slow burn (>1x sustained): ticket

## Instrumentation

1. **OpenTelemetry first** — use OTel SDK for all new instrumentation. Vendor-neutral.
2. **Golden Signals** — every service must emit: request rate, error rate, latency distribution, saturation
3. **RED method for services** — Rate, Errors, Duration per endpoint
4. **USE method for resources** — Utilization, Saturation, Errors per resource (CPU, memory, disk, network)
5. **Structured logging** — JSON with correlation_id, service_name, level, timestamp. No printf debugging in production.
6. **Trace context propagation** — ensure trace IDs flow through all service boundaries

## Runbooks

Every alert must have a runbook. No alert without actionable response:
- What does this alert mean?
- What's the impact?
- First response steps (check X, run Y, escalate if Z)
- Known false positive patterns

## Verification

1. Trigger synthetic traffic and verify metrics appear in dashboards
2. Inject errors and verify alerts fire within expected timeframes
3. Verify trace spans connect across service boundaries
4. Check log queries return expected results with correlation IDs
