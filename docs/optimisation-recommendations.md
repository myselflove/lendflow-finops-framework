# LendFlow FinOps Optimisation Recommendations Register

This register details the 18 prioritised cost optimisation initiatives across Compute, Database, Storage, Data Transfer, and Commercial Commitments.

## 1. Prioritisation Matrix & Summary Table

| ID | Category | Initiative Name | Monthly Savings ($) | Effort | Payback Period | Risk | Compliance Impact |
|---|---|---|---|---|---|---|---|
| **OPT-01** | Compute | Rightsizing 48 Over-provisioned EC2 Instances | $18,400 | Low | Immediate | Low | None |
| **OPT-02** | Compute | Non-Prod Auto-Stop Scheduler (Lambda/EventBridge) | $8,650 | Low | Immediate | Low | Excludes Staging-PCI |
| **OPT-03** | Compute | Graviton3 (c7g/m7g) Architecture Migration | $8,600 | Medium | 14 days | Low | Tested on ARM64 |
| **OPT-04** | Compute | Karpenter EKS Autoscaling with Spot Instances | $6,105 | Medium | 14 days | Medium | Non-critical workers only |
| **OPT-05** | Database | RDS Aurora Serverless v2 for Read Workloads | $9,000 | Medium | 7 days | Low | Multi-AZ protected |
| **OPT-06** | Database | Downgrade Non-Prod RDS to db.t4g.medium | $3,200 | Low | Immediate | Low | Non-prod only |
| **OPT-07** | Database | DynamoDB Provisioned to On-Demand (Tiered) | $2,000 | Low | Immediate | Zero | None |
| **OPT-08** | Storage | S3 Intelligent-Tiering & Deep Archive Policy | $9,880 | Low | Immediate | Zero | SOC 2 WORM Preserved |
| **OPT-09** | Storage | Purge 42 Orphaned/Unattached EBS Volumes | $1,470 | Low | Immediate | Zero | Snapshot pre-deletion |
| **OPT-10** | Storage | Migrate 60 gp2 EBS Volumes to gp3 (20% discount) | $2,850 | Low | Immediate | Zero | No downtime migration |
| **OPT-11** | Network | Implement S3 Gateway VPC Endpoints | $4,200 | Low | Immediate | Zero | Bypasses NAT Gateways |
| **OPT-12** | Network | Topology Aware Routing for EKS Microservices | $2,600 | Medium | 7 days | Low | Reduces Cross-AZ chatter |
| **OPT-13** | Network | Consolidate NAT Gateways in Non-Prod VPCs | $1,520 | Low | Immediate | Low | Non-prod only |
| **OPT-14** | Commercial | 3-Year Compute Savings Plans (72% base) | $21,800 | Low | 1st Month | Zero | Stable baseline |
| **OPT-15** | Commercial | 1-Year RDS Reserved Instances (db.r6g) | $7,400 | Low | 1st Month | Zero | Prod DB cluster |
| **OPT-16** | Observability | CloudWatch Logs Retention & Metric Stream Filtering | $2,100 | Low | Immediate | Zero | 30-day hot -> S3 Glacier |
| **OPT-17** | Observability | Decommission 3 Idling OpenSearch Test Clusters | $1,800 | Low | Immediate | Zero | Verified inactive |
| **OPT-18** | Governance | Automated Tag Enforcement & Quarantine SCP | $800 | Medium | Immediate | Low | Halts unapproved untagged |
| **TOTAL** | | | **$102,475** | | | | |

---

## 2. Detailed Technical Breakdown for High-Impact Initiatives

### OPT-01: EC2 Instance Rightsizing ($18,400/mo)
- **Current State**: 48 `m5.2xlarge` instances running across ECS/EKS clusters supporting borrower portal and underwriting APIs. CloudWatch telemetry confirms average CPU is 12.8% and peak CPU is 34.2%.
- **Target State**: Downsize to `m6i.xlarge` (4 vCPU, 16 GiB RAM).
- **Execution Plan**: Deploy updated Terraform node templates via blue/green deployment. Verify response latency percentiles (P95 < 120ms, P99 < 250ms).

### OPT-08: S3 Intelligent-Tiering Lifecycle Policies ($9,880/mo)
- **Current State**: 180 TB of application data, scanned loan PDF documentation, and bank statement extracts residing in S3 Standard storage. Over 65% of objects have not been accessed for >90 days.
- **Target State**: Transition all historical documentation buckets (`lendflow-document-archive-*`) to S3 Intelligent-Tiering with Archive Access Tier (90 days) and Deep Archive Access Tier (180 days).
- **Compliance Lock**: All legal and audit trails under `lendflow-audit-*` remain in compliant S3 Object Lock governance mode.

### OPT-14 & OPT-15: Savings Plans & Reserved Instances ($29,200/mo)
- **Commitment Formula**: Calculated based on 70% of minimum hourly on-demand compute spend over past 90 days.
- **Compute Savings Plan**: $28.50/hour commitment covering EC2, Fargate, and Lambda across all regions.
- **RDS RI**: Standard All Upfront / Partial Upfront 1-Year RI for Aurora PostgreSQL writer and primary reader nodes.
