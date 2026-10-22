# FinOps Daily Log — Day 04: Database Tier & Aurora Replica Audit

**Date**: Sprint 1, Day 4  
**Focus**: RDS Aurora, DynamoDB & Cache Sizing  

## Completed Work Today
- Audited 6 RDS Aurora read replicas running 24/7 across Staging and Production.
- Identified that 4 staging replicas idle at <8% CPU and can be consolidated.
- Evaluated Aurora Serverless v2 migration for dynamic auto-scaling from 0.5 to 16 ACUs.
- Quantified prospective savings: **$14,200/month** on database tier.

## Planned Checkpoints
- [x] Database optimization roadmap established.
- [ ] Run S3 storage bucket inventory and EBS volume audit.
