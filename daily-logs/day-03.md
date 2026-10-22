# FinOps Daily Log — Day 03: Compute & Instance Utilisation Profiling

**Date**: Sprint 1, Day 3  
**Focus**: CloudWatch Utilisation Metrics & Sizing Audit  

## Completed Work Today
- Analyzed 2,400 instance utilization records across production and non-production clusters.
- Identified that average CPU utilization across 48 `m5.2xlarge` instances is only **14.2%** (peak 34.2%).
- Flagged 32 development/testing instances operating at <5% average CPU.
- Drafted rightsizing candidate list to migrate from `m5.2xlarge` to `m6i.xlarge` and `c7g` Graviton3 instances.

## Planned Checkpoints
- [x] Compute audit complete.
- [ ] Analyze RDS database clusters and replica topology.
