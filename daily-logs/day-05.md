# FinOps Daily Log — Day 05: Storage Hygiene & Zombie Volume Identification

**Date**: Sprint 1, Day 5  
**Focus**: EBS Volumes, Snapshots & S3 Storage Classes  

## Completed Work Today
- Audited 500 storage resources across all AWS accounts.
- Identified 42 unattached/orphaned EBS gp2 volumes consuming **$1,470/month** in pure waste.
- Discovered 140 TB of historical loan application PDFs in S3 Standard storage with no access for >90 days.
- Designed S3 Intelligent-Tiering and Glacier Deep Archive lifecycle policy.

## Planned Checkpoints
- [x] Storage waste quantified.
- [ ] Audit data transfer logs and cross-AZ traffic paths.
