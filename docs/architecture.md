# Architecture Document
## LendFlow Technologies — Infrastructure Cost Optimisation and FinOps Framework
**Author:** Cloud FinOps & Infrastructure Architecture Engineering Group
**Classification:** Open Architecture
**Version:** 1.0.0
**Date:** 2026-10-16
**Status:** PRODUCTION READY

---

## 1. Executive Summary

LendFlow Technologies runs a cloud-native fintech platform processing **500,000+ loan applications per month** across **12 microservices** on AWS in the **ap-south-1 (Mumbai)** region. This architecture document defines the current-state and target-state infrastructure, compliance isolation zones, FinOps data flow, and the 90-day optimization roadmap delivering **>=33% AWS cost reduction** from $180,000/month to <=120,000/month.

---

## 2. Current-State Architecture

### 2.1 Global Design Principles

- **Region Strategy:** Primary workloads in ap-south-1 (RBI mandate); EU customer data in eu-west-1 / eu-central-1 (GDPR)
- **Availability:** All critical services spanning 3 Availability Zones (ap-south-1a, ap-south-1b, ap-south-1c)
- **Compute:** Amazon EKS with managed node groups (currently x86 EC2 instances; target Graviton3)
- **Network:** Multi-tier VPC with public, private-app, private-data, and PCI-isolated subnets
- **Security:** WAF + Shield at edge; security groups + NACLs at tier boundaries; KMS encryption at rest

### 2.2 High-Level Network Topology

```
Internet
    |
[AWS WAF + Shield Standard]
    |
[Public Subnet — ALB (Application Load Balancer)]
    |  TLS Termination
    |
[Private App Subnet — EKS Worker Nodes (3 AZs)]
    |                                    |
[Microservices 1-6, 8-12]      [PCI Isolated Subnet]
    |                                    |
    |                         [lendflow-payments ONLY]
    |                         [Strict SG: ingress ALB only]
    |
[Private Data Subnet — RDS Aurora / ElastiCache]
    |
[S3 (via VPC Endpoint), CloudTrail, CloudWatch]
```

### 2.3 EKS Cluster Configuration (Current State)

| Parameter                  | Current Value             | Target State (Post-Optimization)    |
|----------------------------|---------------------------|-------------------------------------|
| Node instance types        | m5.xlarge, c5.2xlarge (x86) | c7g.xlarge, m7g.xlarge (Graviton3) |
| Node group strategy        | On-Demand only            | On-Demand (steady-state) + Spot (batch)|
| Scaling                    | Cluster Autoscaler        | Karpenter (faster, cost-aware)      |
| Node rightsizing           | Over-provisioned ~40%     | VPA + resource limit tuning         |
| Reserved capacity          | 0% RI coverage            | 70%+ 1-year RI/Savings Plans        |
| Non-prod environments      | Running 24x7              | Scheduled off 12h/day + weekends    |

---

## 3. Microservices Architecture

### 3.1 Service Catalog

```
lendflow-gateway  ------>  lendflow-auth
       |
       +---------> lendflow-ingestion  -----> lendflow-credit-scoring
                         |                          |
                         |                   lendflow-underwriting
                         |                          |
                         +-> lendflow-doc-verify     |
                         |                          |
                         +-> lendflow-payments       | (PCI Isolated)
                         |                          |
                         +-> lendflow-ledger <-------+
                         |
                         +-> lendflow-notifications
                         |
                         +-> lendflow-analytics
                         |
                         +-> lendflow-audit (writes all events)
                         |
                         `-> lendflow-collections
```

### 3.2 Compliance Isolation Map

```
┌─────────────────────────────────────────────────────────────────┐
│  COMPLIANCE ZONES                                               │
│                                                                 │
│  ┌─── PCI DSS ENCLAVE ──────────────────────────────────────┐  │
│  │  lendflow-payments                                        │  │
│  │  - Dedicated subnet (no shared resources with non-PCI)   │  │
│  │  - Min 3 instances across 3 AZs                          │  │
│  │  - All traffic via ALB only (no direct pod access)       │  │
│  │  - Tokenized CHD only (no raw PAN in any data store)     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─── RBI MANDATE ZONE ─────────────────────────────────────┐  │
│  │  lendflow-ingestion  (min 2 AZ — Loan API)               │  │
│  │  lendflow-credit-scoring (min 3 AZ — Credit Engine)      │  │
│  │  All services: ap-south-1 only for India lending data    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─── SOC 2 TYPE II AUDIT ZONE ─────────────────────────────┐  │
│  │  lendflow-audit                                           │  │
│  │  - Writes to S3 with Object Lock (WORM, Compliance mode) │  │
│  │  - 12-month minimum retention (365-day lock period)      │  │
│  │  - CloudTrail multi-region trail to same S3 bucket       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─── GDPR DATA RESIDENCY ZONE ─────────────────────────────┐  │
│  │  EU Customer Data: eu-west-1 / eu-central-1 only         │  │
│  │  India Lending Data: ap-south-1 only                     │  │
│  │  Cross-region transfer: Prohibited without SCCs          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Database Architecture

### 4.1 RDS / Aurora Topology

| Service                  | Database Type          | Instance Class     | Multi-AZ  | Read Replicas | Storage     |
|--------------------------|------------------------|--------------------|-----------|---------------|-------------|
| lendflow-ingestion       | Aurora PostgreSQL 15.4 | db.r6g.xlarge      | Yes (2AZ) | 1             | gp3 500GB   |
| lendflow-payments        | Aurora PostgreSQL 15.4 | db.r6g.2xlarge     | Yes (3AZ) | 2             | gp3 200GB   |
| lendflow-ledger          | Aurora PostgreSQL 15.4 | db.r6g.2xlarge     | Yes (3AZ) | 2             | gp3 1TB     |
| lendflow-credit-scoring  | Aurora PostgreSQL 15.4 | db.r6g.xlarge      | Yes (3AZ) | 1             | gp3 300GB   |
| lendflow-auth            | RDS PostgreSQL 15.4    | db.t3.medium       | Yes (2AZ) | 0             | gp3 100GB   |
| lendflow-audit           | RDS PostgreSQL 15.4    | db.r6g.large       | Yes (3AZ) | 1             | gp3 2TB     |

### 4.2 ElastiCache Redis Clusters

| Cluster                  | Purpose                         | Node Type       | Nodes | Multi-AZ |
|--------------------------|---------------------------------|-----------------|-------|----------|
| lendflow-session         | Auth session caching            | cache.r6g.large | 2     | Yes      |
| lendflow-rate-limit      | API rate limiting counters      | cache.t3.medium | 2     | Yes      |
| lendflow-app-cache       | Application-level caching       | cache.r6g.xlarge| 3     | Yes      |

---

## 5. FinOps Data Flow Architecture

```
                     ┌─────────────────────────────┐
                     │   AWS Cost Explorer API     │
                     │   (Simulated in demo mode)  │
                     └─────────────┬───────────────┘
                                   │ Cost + Usage Data
                     ┌─────────────v───────────────┐
                     │  analysis/scripts/           │
                     │  cost_ingestion.py           │
                     │  (Pandas ETL pipeline)       │
                     └─────────────┬───────────────┘
                                   │ Structured DataFrames
          ┌────────────────────────v───────────────────────────┐
          │          app/backend/ (FastAPI)                    │
          │                                                    │
          │  /api/waterfall    -> waterfall_engine.py         │
          │  /api/compliance   -> compliance_checker.py       │
          │  /api/unit-econ    -> unit_economics.py           │
          │  /api/reports      -> report_generator.py         │
          └────────────────────────┬───────────────────────────┘
                                   │ REST JSON API
          ┌────────────────────────v───────────────────────────┐
          │          app/frontend/ (React + Vite)              │
          │                                                    │
          │  Executive Dashboard   -> dashboards/executive/    │
          │  Engineering Dashboard -> dashboards/eng-manager/  │
          │  Team Dashboard        -> dashboards/team/         │
          └───────────────────────────────────────────────────-┘
                                   |
          ┌────────────────────────v───────────────────────────┐
          │       presentation/exports/                        │
          │  FinOps_Report_YYYYMMDD.xlsx (OpenPyXL)           │
          │  Executive_Deck_YYYYMMDD.pptx (python-pptx)       │
          └────────────────────────────────────────────────────┘
```

---

## 6. Savings Waterfall — Detailed Technical Design

### Step 1: Eliminate Idle and Orphaned Resources

**Non-Production Scheduler (A-13)**
- Target: dev and staging EKS node groups
- Schedule: Shutdown 20:00 IST, Start 08:00 IST (weekdays); Full shutdown weekends
- Mechanism: Lambda + EventBridge cron rule
- Compliance impact: None (prod untouched)
- Baseline: $75,000 EC2+EKS * 30% non-prod fraction * 50% time saving = ~$11,250/month

**Orphaned Resource Cleanup (A-04, A-05, A-06)**
- EBS volumes with no attachments >7 days: Snapshot then delete
- ELBs with 0 requests over 14 days: Deregister and delete
- Elastic IPs not associated with running instance: Release
- Combined savings estimate: ~$2,200/month

**S3 Intelligent-Tiering and Lifecycle (A-07)**
- Audit logs >30 days: Transition to S3 Standard-IA
- Audit logs >90 days: Transition to S3 Glacier Instant Retrieval
- Audit logs >365 days: Transition to S3 Glacier Deep Archive
- Compliance safe: Object Lock preserved across tier transitions
- Savings estimate: ~$3,500/month

**Vendor API Audit (A-22)**
- Bureau check API deduplication (cache positive lookups 7 days)
- OCR vendor batch consolidation
- SMS gateway tier optimization
- Savings estimate: ~$2,000/month

**Step 1 Total: ~$18,950/month**
**Post-Step-1 Baseline: $180,000 - $18,950 = $161,050/month**

### Step 2: Right-Size Active Capacity

**Graviton3 Migration (A-08)**
- Eligible services: lendflow-gateway, lendflow-auth, lendflow-ingestion, lendflow-notifications, lendflow-analytics, lendflow-collections
- NOT migrated: lendflow-payments (PCI stability window), lendflow-credit-scoring (ML model validation required first)
- Instance mapping: m5.xlarge -> m7g.xlarge (20% cheaper, 40% better perf/dollar)
- Savings: 30% on $161,050 * 40% eligible compute fraction = ~$19,326/month

**RDS Right-Sizing + gp2->gp3 (A-09)**
- db.r6g.2xlarge -> db.r6g.xlarge for lendflow-auth (P95 CPU <15%)
- gp2->gp3 for all RDS instances: 20% cheaper, 3x baseline IOPS free
- Performance Insights review confirms <30% average utilization on 3 of 6 clusters
- Savings: ~$8,000/month

**EKS HPA + VPA Tuning (A-10)**
- Current: resource requests over-provisioned by avg 45% (CPU) and 38% (memory)
- VPA recommendation mode -> update mode for non-prod; manual apply for prod
- HPA min replicas right-sized: lendflow-notifications 5->2, lendflow-analytics 4->2 off-peak
- Savings: ~$6,000/month

**Step 2 Total: ~$33,326/month**
**Post-Step-2 Baseline: $161,050 - $33,326 = $127,724/month**

### Step 3: Commitments and Spot Discounts

**Savings Plans Portfolio (A-14)**
- Compute Savings Plan: 1-year, partial upfront on $80,000/month post-rightsized compute
- Effective discount: 28% average vs. On-Demand
- Savings: ~$22,400/month

**Spot Instance Batch Workers (A-16)**
- lendflow-analytics data pipeline workers: 100% Spot (stateless, checkpointing enabled)
- lendflow-credit-scoring batch risk model retraining: 80% Spot worker pools
- Interruption handling: Karpenter graceful drain + SQS job queuing
- Savings: ~$6,000/month

**Note:** RI/Savings Plans applied to post-Step-2 baseline of $127,724 only.
The 28% discount on $80k compute component = $22,400 savings.

**Step 3 Total: ~$28,400/month**
**Final Monthly Spend: $127,724 - $28,400 = $99,324/month**

---

## 7. Compliance Architecture — Zero-Compromise Design

### 7.1 Ring-Fenced Compliance Budgets

The following resources are EXCLUDED from all cost optimization waterfall calculations:

| Service                   | Reason for Exclusion             | Protected Cost Estimate |
|---------------------------|----------------------------------|------------------------|
| lendflow-payments (3 AZ)  | PCI DSS min instance requirement | ~$8,000/month          |
| lendflow-audit (S3 lock)  | SOC 2 12-month WORM retention    | ~$3,500/month          |
| lendflow-credit-scoring 3AZ| RBI min 3 AZ mandate            | ~$5,000/month          |
| CloudTrail all-region     | SOC 2 continuous audit           | ~$800/month            |
| VPC Flow Logs             | PCI DSS + SOC 2 requirement      | ~$400/month            |

### 7.2 Policy Enforcement Architecture

```
GitHub Pull Request
        |
[Infracost PR Comment]  <-- policies/terraform/infracost-policy.rego
        |
[OPA policy check in CI]  <-- policies/opa/
        |                     - pci_dss.rego (min 3 AZ payments)
        |                     - rbi_framework.rego (min AZ rules)
        |                     - data_residency.rego (region rules)
        |                     - tagging.rego (mandatory tags)
        |
[BLOCK if policy DENY]
        |
[ALLOW if all policies PASS]
        |
[Terraform Plan -> Apply]
        |
[AWS Config continuous rules]  <-- policies/aws/config-rules.json
        |
[SNS alert on Config rule violation]
```

---

## 8. FinOps Governance Model

### 8.1 Inform Phase (Days 1-30)
- Deploy cost allocation tagging across all 12 services (A-01)
- Enable Cost Explorer hourly granularity
- Baseline current-state cost per service and per 1,000 loans (A-20)
- Identify all orphaned resources (A-04, A-05, A-06)

### 8.2 Optimise Phase (Days 31-60)
- Execute non-prod scheduling (A-13)
- Complete Graviton3 migration for eligible services (A-08)
- Right-size RDS clusters (A-09)
- Tune EKS HPA/VPA (A-10)
- Purchase Savings Plans (A-14) and Spot enablement (A-16)

### 8.3 Operate Phase (Days 61-90)
- Activate daily anomaly detection and alerting (A-02)
- Launch executive FinOps dashboard (A-19)
- Configure budget circuit breakers (A-21)
- Conduct first FinOps governance board review (A-25)
- Generate SOC2/PCI/RBI audit readiness report (A-26)
- Measure final savings vs $60,000/month target

---

## 9. Disaster Recovery Architecture

| Scenario               | Strategy          | RPO      | RTO      | Monthly DR Cost |
|------------------------|-------------------|----------|----------|-----------------|
| AZ failure             | Multi-AZ failover | <1 min   | <2 min   | Included in HA  |
| Region failure (prod)  | Warm standby      | 15 min   | 30 min   | ~$12,000/month  |
| Region failure (audit) | Pilot light       | 60 min   | 4 hours  | ~$1,500/month   |
| Data corruption        | Point-in-time RDS | 5 min    | 2 hours  | Included in RDS |

DR cost optimization opportunity (A-23): Convert warm standby to pilot light for non-critical services.
Estimated savings: ~$3,000/month while maintaining RBI-compliant RPO/RTO for loan processing.

---

## 10. Technology Stack Reference

| Layer            | Technology                           | Version   |
|------------------|--------------------------------------|-----------|
| Backend API      | Python + FastAPI + Uvicorn           | 3.14 / 0.115+ |
| Data Processing  | Pandas + NumPy                       | 2.x / 1.26+ |
| Data Validation  | Pydantic                             | 2.x       |
| Report: Excel    | OpenPyXL                             | 3.1+      |
| Report: PowerPoint | python-pptx                        | 0.6+      |
| Testing          | Pytest + pytest-asyncio              | 8.x       |
| Frontend         | React + TypeScript + Vite            | 18.x / 5.x |
| Styling          | Tailwind CSS                         | 3.x       |
| Charts           | Recharts                             | 2.x       |
| Icons            | Lucide React                         | 0.4+      |
| Policy Engine    | Open Policy Agent (OPA)              | 0.68+     |
| IaC              | Terraform (simulation/plan only)     | 1.9+      |

---

## Document Control

| Version | Date       | Author                       | Change                          |
|---------|------------|------------------------------|---------------------------------|
| 1.0.0   | 2026-10-16 | FinOps Engineering Group     | Initial architecture            |

---

*LendFlow FinOps Architecture Specification*
