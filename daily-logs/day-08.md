# FinOps Daily Log — Day 08: Policy-as-Code & Guardrail Development

**Date**: Sprint 2, Day 8  
**Focus**: AWS SCPs, AWS Config Rules, OPA Rego & Terraform Policies  

## Completed Work Today
- Developed 4 syntactically valid AWS Service Control Policies (`mandatory-tags.json`, `restrict-gpu.json`, `approved-regions.json`, `max-instance-limits.json`).
- Authored OPA Rego policy `policies/opa/finops_guardrails.rego` enforcing mandatory tags, approved instance types, Graviton adoption, and PCI DSS compliance locks.
- Configured Infracost CI/CD budget guardrail policy.

## Planned Checkpoints
- [x] Policy-as-Code suite created.
- [ ] Build Kubernetes Auto-Scaling configurations (HPA, Karpenter, VPA).
