# LendFlow Auto-Scaling & Dynamic Resource Policies

## 1. Architecture Overview

LendFlow's legacy infrastructure utilized static provisioning sized for peak traffic (Month 6 peak: 140 loan applications/minute during business hours 09:00 - 19:00 IST). Outside business hours and on weekends, average traffic drops by **74%**, yet infrastructure remained running at 100% capacity.

This policy establishes **Horizontal Pod Autoscaling (HPA)**, **Karpenter dynamic node provisioning**, and **automated non-production environment power scheduling**.

---

## 2. HPA Scaling Specifications

### A. Loan Application Ingestion Gateway (`lendflow-api-gateway`)
- **Metric**: Target average CPU utilization: **65%**; Target HTTP request rate: **1,200 req/sec** per pod.
- **Min Replicas**: 4 (spread across 3 AZs: `ap-south-1a`, `ap-south-1b`, `ap-south-1c`).
- **Max Replicas**: 32 pods.
- **Scale-Up Behavior**: Rate of 100% increase every 15 seconds (immediate burst response).
- **Scale-Down Stabilization Window**: 300 seconds (prevent thrashing).

### B. Core Underwriting Engine (`lendflow-underwriting`)
- **Metric**: SQS Queue Depth (`loan-submission-queue`) > 250 unprocessed items per pod.
- **Min Replicas**: 2 pods.
- **Max Replicas**: 24 pods.
- **Node Affinity**: Karpenter Spot Instances with fallback to On-Demand Graviton3.

### C. Payment Orchestration Service (`lendflow-payments`)
- **Compliance Lock**: PCI DSS v4.0 Section 10 & RBI IT Multi-AZ requirement.
- **Min Replicas**: **STRICT MINIMUM 6 PODS** (2 pods per AZ across 3 AZs).
- **Max Replicas**: 20 pods.
- **Affinity**: AWS On-Demand instances only. Zero Spot instances permitted.

---

## 3. Non-Production Power Scheduler

All non-production environments (`dev`, `qa`, `sandbox`) are scheduled via AWS EventBridge and AWS Lambda:
- **Shutdown Trigger**: Monday to Friday at 20:00 IST (14:30 UTC); Saturday & Sunday all day.
- **Startup Trigger**: Monday to Friday at 07:30 IST (02:00 UTC).
- **Weekly Operating Hours**: Reduced from 168 hours to 62.5 hours per week (62.8% idle reduction).
- **Exclusion Mechanism**: Resources tagged with `AutoStopExclude=true` and `ApprovalTicket=FINOPS-XXXX` are bypassed.
- **Monthly Net Savings**: **$8,650 / month**.
