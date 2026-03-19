# CI/CD Protocol

## Current State Analysis

Before modifying pipelines:
1. Read existing CI configs (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)
2. Understand current build times and failure rates
3. Check existing caching strategies
4. Review deployment targets and environments

## Pipeline Design

1. **Fast feedback first** — lint and type-check before tests. Unit tests before integration. Fail fast.
2. **Immutable artifacts** — build once, deploy the same artifact to all environments. Never rebuild per environment.
3. **Cache aggressively** — dependency caches, build caches, Docker layer caches. Measure cache hit rates.
4. **Parallelize independent stages** — test suites can run in parallel with lint/security checks

## Container Optimization

1. **Multi-stage builds** — separate build dependencies from runtime image
2. **Minimal base images** — alpine or distroless. Every unnecessary package is attack surface.
3. **Layer ordering** — put rarely-changing layers (OS, deps) before frequently-changing layers (code)
4. **Pin versions** — use digest-pinned base images, not :latest

## Security Hardening

1. **Supply chain security** — scan dependencies (Snyk, Trivy), verify checksums, pin actions by SHA
2. **Secrets handling** — use CI platform secret stores, never echo secrets, mask in logs
3. **Least privilege** — CI service accounts get minimum permissions needed
4. **Image scanning** — scan built images for CVEs before pushing to registry

## Deployment Strategies

- **Rolling** — gradual replacement, zero downtime, easy rollback
- **Blue/green** — instant cutover, full rollback capability, double resources
- **Canary** — progressive traffic shift, metric-based promotion, automated rollback on error rate spike
- Choose based on risk tolerance and infrastructure capabilities
