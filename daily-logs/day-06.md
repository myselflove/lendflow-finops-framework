# FinOps Daily Log — Day 06: Data Transfer & Cross-AZ Networking Analysis

**Date**: Sprint 1, Day 6  
**Focus**: Inter-AZ Traffic, NAT Gateways & VPC Endpoints  

## Completed Work Today
- Evaluated 3,600 data transfer log events totaling $20,000/month.
- Discovered that $4,200/month is incurred by S3 API calls routed through public NAT Gateways rather than private S3 Gateway Endpoints.
- Identified high cross-AZ chatty microservices between Underwriting and Risk engines.
- Designed Gateway VPC endpoints and EKS Topology Aware Routing architecture.

## Planned Checkpoints
- [x] Network optimization opportunities documented.
- [ ] Formalize Tagging taxonomy and dark spend analysis.
