# Cloud Operations Protocol

## Cloud State Audit

Before changing anything, understand reality:
1. Read existing IaC files (Terraform, CDK, Pulumi, CloudFormation)
2. Check for drift between IaC and actual cloud state (`terraform plan`, `cdk diff`)
3. Review IAM policies — principle of least privilege
4. Check infrastructure-map.md in knowledge files for documented topology

## IaC Implementation

1. **Module design** — reusable, parameterized modules. Don't copy-paste infrastructure blocks.
2. **State management** — remote state with locking. Never commit state files.
3. **Environment parity** — dev/staging/prod should differ by parameters, not structure.
4. **Validate before apply** — `terraform validate`, `tflint`, `checkov` for security scanning.

## Security & Compliance

- **Least privilege** — IAM roles scoped to exactly what's needed. No wildcard permissions.
- **Defense in depth** — security groups + NACLs + WAF + encryption at rest + in transit
- **Secrets management** — use secret manager services, never environment variables for sensitive data
- **Audit logging** — CloudTrail/Cloud Audit Logs enabled, log retention configured

## Cost Optimization

- **Right-size resources** — check utilization before provisioning. Oversized instances waste money.
- **Reserved/spot for predictable workloads** — calculate break-even for reserved instances
- **Tag everything** — cost allocation tags enable tracking by team/project/environment
- **Run infracost** on terraform plans to estimate cost impact before applying

## Knowledge Updates

After every cloud change, update infrastructure-map.md in knowledge files with:
- What changed and why
- Current topology summary
- Cost implications
