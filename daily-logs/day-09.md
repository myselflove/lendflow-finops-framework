# FinOps Daily Log — Day 09: Auto-Scaling & Karpenter Spot Provisioning

**Date**: Sprint 2, Day 9  
**Focus**: HPA, Karpenter Provisioners & Non-Prod Scheduling  

## Completed Work Today
- Built HPA configurations for `lendflow-api-gateway` (CPU & request rate targets) and `lendflow-payments` (PCI DSS locked min 6 replicas).
- Created Karpenter dynamic provisioners for Graviton3 (`m7g`) and Spot instance workers.
- Authored AWS EventBridge/Lambda non-production power scheduler (`nonprod-schedule-rule.json`) yielding $8,650/mo savings.

## Planned Checkpoints
- [x] Auto-scaling and Spot architecture configured.
- [ ] Develop interactive FastAPI backend and simulation engine.
