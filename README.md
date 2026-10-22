# LendFlow FinOps Framework
### Cloud-Native Infrastructure Cost Optimisation & FinOps Governance Platform

[![CI/CD Pipeline](https://github.com/placeholder/lendflow-finops-framework/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Terraform](https://img.shields.io/badge/Terraform-1.5+-844FBA.svg?logo=terraform&logoColor=white)](https://www.terraform.io)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Tests Passing](https://img.shields.io/badge/Tests-117%20Passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Executive Overview

**LendFlow Technologies** is a high-growth fintech platform that scaled rapidly to **500,000+ monthly loan applications** across **12 distributed microservices**. However, cloud infrastructure expenditure on AWS surged from **$50,000 to $180,000/month**. While company revenue grew from $500k to $1M, gross margins shrank from **75% to 55%** due to unoptimized infrastructure waste, idle non-prod workloads, cross-AZ NAT gateway fees, and unreserved compute capacity.

This repository provides an enterprise-ready **FinOps & Cloud Architecture Framework** that enforces a **90-day, zero-double-counting waterfall optimization model** across the **Inform &rarr; Optimise &rarr; Operate** lifecycle. It reduces AWS spend from **$180,000/month to $77,525/month** (achieving **$102,475/month in run-rate savings**, surpassing the $60,000/mo minimum target) while strictly maintaining compliance rings for **PCI DSS v4.0**, **RBI IT Framework**, and **SOC 2 Type II**.

---

## Architecture: 12 Microservices & Isolation Zones

```
                           +----------------------------------+
                           |  Internet & Client Applications  |
                           +-----------------+----------------+
                                             |
                                  [AWS WAF / Shield]
                                             v
                           +-----------------+----------------+
                           |     lendflow-gateway (EKS)       |
                           +--------+----------------+--------+
                                    |                |
           +------------------------+                +------------------------+
           |                                                                  |
           v                                                                  v
+--------------------------+                                      +--------------------------+
| lendflow-auth (OAuth/JWT)|                                      | lendflow-ingestion (RBI) |
+--------------------------+                                      +-------------+------------+
                                                                                |
             +--------------------+---------------------+-----------------------+
             |                    |                     |
             v                    v                     v
+--------------------------+ +--------------------+ +--------------------------+
| lendflow-credit-scoring  | |lendflow-doc-verify | | lendflow-underwriting    |
| (ML Risk - 3 Multi-AZ)   | |(OCR/KYC Engine)    | | (Automated Decisioning)  |
+--------------------------+ +--------------------+ +--------------------------+
             |                                                  |
             +--------------------+-----------------------------+
                                  |
                                  v
+------------------------------------------------------------------------------------+
|  Isolated PCI DSS Zone (Dedicated VPC Subnet & Security Groups, Tokenized Data)    |
|  --> lendflow-payments (Min 3 Multi-AZ, zero public egress, tokenized vault)       |
+---------------------------------+--------------------------------------------------+
                                  |
                                  v
+--------------------------+ +--------------------+ +--------------------------+
| lendflow-ledger (ACID)   | |lendflow-notif      | | lendflow-collections     |
| (Aurora PostgreSQL)      | |(EventBridge/SNS)   | | (Delinquency Workflows)  |
+--------------------------+ +--------------------+ +--------------------------+
             |
             v
+--------------------------+ +-------------------------------------------------+
| lendflow-audit (SOC 2)   | | lendflow-analytics (BI Lakehouse, S3 Parquet)   |
| (S3 WORM Object Lock)    | | (Scheduled Graviton3 spot instances)            |
+--------------------------+ +-------------------------------------------------+
```

---

## Financial Baseline & Savings Waterfall

### Monthly AWS Baseline: $180,000

| Service Category | Baseline Monthly Cost | Target Optimization Strategy | Post-Opt Cost |
| :--- | :---: | :--- | :---: |
| **EC2 & EKS Compute** | $75,000 | Graviton3 (c7g/m7g), Karpenter Spot, non-prod shutdown | $32,450 |
| **RDS & Aurora PostgreSQL** | $45,000 | Aurora I/O-Optimized, right-sizing dev DBs, Multi-AZ audit | $22,800 |
| **NAT Gateways & Cross-AZ Transfer**| $18,000 | S3 VPC Gateway Endpoint (Free), intra-AZ affinity | $3,600 |
| **S3 Storage & EBS Volumes** | $15,000 | gp2 &rarr; gp3 migration, S3 Intelligent-Tiering, unattached cleanup | $6,875 |
| **ElastiCache Redis & MemoryDB**| $12,000 | Reserved cache nodes, cluster auto-failover rightsizing | $5,400 |
| **Other (CloudWatch, WAF, KMS)**| $15,000 | Log retention lifecycle, metric stream filtering | $6,400 |
| **TOTAL** | **$180,000 / mo** | **Net Run-Rate Savings: $102,475 / month (56.9% reduction)** | **$77,525 / mo** |

### Zero Double-Counting Mathematical Contract
To eliminate inflated or overlapping savings claims in executive reporting:
1. **Step 1: Eliminate Idle & Orphaned Waste** &mdash; Calculated against the raw **$180,000** baseline (*Non-prod off-hours shutdown, unattached gp2 volumes, idle ELBs*).
2. **Step 2: Right-Size Active Capacity** &mdash; Calculated strictly on the **post-Step-1 baseline** (*Graviton3 ARM migration, gp2 &rarr; gp3 EBS, Aurora rightsizing*).
3. **Step 3: Commitments & Spot Optimization** &mdash; Calculated strictly on the **post-Step-2 baseline** (*1-Year Savings Plans, Karpenter spot node pools for analytics*).

$$\text{Final Monthly Spend} = \text{Baseline} - (\text{Step}_1 + \text{Step}_2 + \text{Step}_3) \le \$120,000$$

---

## Technical Features & Stack

* **FastAPI Calculation Engine (`app/backend`)**: High-performance asynchronous REST API computing real-time Z-score anomaly outliers, tag governance compliance, and scenario simulation.
* **React 18 & TypeScript SPA (`app/frontend`)**: Dark-themed modern dashboard with Recharts, interactive anomaly triage, and interactive scenario simulator:
  1. *Executive Summary*: Real-time financial waterfall, margin recovery, and unit economics ($0.36 &rarr; $0.155/loan).
  2. *Cost Explorer*: Multi-dimensional slicing by service, team, AZ, environment, and tag.
  3. *Compute & Database Optimization*: Graviton3 migration matrix and idle database audits.
  4. *Storage Optimization*: S3 wrong-tier lifecycle candidates and gp2-to-gp3 migration tracker.
  5. *Data Transfer Analytics*: Inter-AZ and NAT Gateway traffic heatmaps.
  6. *Tag Governance & Dark Spend*: Audit of untagged resources causing attribution blindness.
  7. *Anomaly Detection Centre*: Z-score statistical outlier detection with Slack alert dispatching.
  8. *Scenario Simulator*: Real-time toggling of 18 recommendations with instant waterfall recalculation.
  9. *FinOps War Room*: Emergency cost incident response triage and simulated team actions.
  10. *Governance & Compliance*: Verification matrix for PCI DSS, RBI IT, and SOC 2.
* **Cost-Aware IaC (`infrastructure/main.tf`)**:
  * S3 Gateway VPC Endpoints eliminating NAT Gateway cross-AZ data fees.
  * Graviton3 ARM64 EKS node groups (`c7g.xlarge`, `m7g.xlarge`).
* **Policy as Code (`policies/`)**:
  * **Open Policy Agent (OPA) Rego**: Guardrails enforcing mandatory tags, Graviton node pools, and PCI DSS minimum instance counts.
  * **AWS SCPs**: Deny unapproved regions, restrict expensive GPU instances, enforce tag policies.
  * **Kubernetes Auto-Scaling**: Karpenter spot/graviton provisioners, HPA, and VPA configurations.
* **100% Automated Pytest Verification (`tests/`)**: 117 automated unit and integration tests verifying datasets, API contracts, compliance constraints, and math models.

---

## Quick Start

### Option 1: Docker Compose (Recommended - 1 Command)

```bash
docker compose up --build
```
* **Frontend Dashboard**: Open `http://localhost:5173`
* **FastAPI Backend & Interactive Swagger Docs**: Open `http://localhost:8000/docs`

---

### Option 2: Local Development Setup

#### Prerequisites
* Python 3.11+
* Node.js 18+ & npm 9+

#### 1. Backend Setup
```bash
# Navigate to backend directory
cd app/backend

# Create and activate virtual environment
python -m venv .venv

# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd app/frontend

# Install packages
npm install

# Start Vite dev server
npm run dev
```

Dashboard is live at `http://localhost:5173`.

---

## Automated Test Suite

Run the full verification test suite (117 tests):

```bash
pytest -v
```

Output:
```text
======================= 117 passed in 4.01s ========================
- TestSchemas (8 passed)
- TestRowCounts (8 passed)
- TestDataRanges (10 passed)
- TestWastePatterns (8 passed)
- TestComplianceTags (6 passed)
- TestWaterfallMath (12 passed)
- TestRecommendations (6 passed)
- TestCrossDatasetConsistency (5 passed)
- TestAWSSCPPolicies (5 passed)
- TestOPAPoliciesAndTerraform (3 passed)
- TestAutoScalingConfigs (2 passed)
- TestExcelDeliverables (2 passed)
- TestPresentationDeliverable (1 passed)
- TestDocumentationSuite (4 passed)
- TestPowerShellScripts (1 passed)
- TestBackendAPI (36 passed)
```

---

## Project Structure

```
lendflow-finops-framework/
|-- .github/workflows/ci.yml       # Automated CI/CD test & build pipeline
|-- analysis/                      # Excel financial models & audit scripts
|   |-- billing-analysis.xlsx      # 7-tab audit model (Pareto, MoM, Dark spend)
|   |-- savings-model.xlsx         # 6-tab live formula waterfall model
|   `-- scripts/run_analysis.py    # Python CLI baseline audit engine
|-- app/
|   |-- backend/                   # FastAPI FinOps calculation engine
|   |   |-- routers/               # 8 FinOps domain routers
|   |   |-- data_loader.py         # CSV & memory dataset manager
|   |   |-- schemas.py             # Pydantic schemas for all payloads
|   |   `-- main.py                # FastAPI entrypoint
|   `-- frontend/                  # React 18 + TypeScript + Vite + Tailwind CSS
|       `-- src/views/             # 10 full-featured FinOps operational views
|-- data/                          # 8 Synthetic fintech billing datasets (19,152 rows)
|-- docs/                          # Comprehensive architecture and runbooks
|   |-- architecture.md            # 12-microservice 3-tier AWS design
|   |-- requirements-traceability.md # RTM mapping specifications & tests
|   |-- 90-day-roadmap.md          # Phased FinOps adoption plan
|   `-- runbook.md                 # Operational FinOps runbook
|-- infrastructure/                # Terraform modules (Graviton3, VPC Endpoints)
|-- policies/                      # Policy as Code guardrails
|   |-- aws/                       # AWS SCPs & Config rules JSON
|   |-- opa/                       # OPA Rego compliance policies
|   `-- autoscaling/               # Karpenter, HPA & VPA configurations
|-- presentation/                  # CFO executive presentation deck (.pptx)
|-- scripts/                       # Automation, build, and test scripts
|-- tests/                         # Pytest test suite (117 test cases)
|-- docker-compose.yml             # Container orchestration config
`-- requirements.txt               # Top-level Python requirements
```

---

## License

This project is licensed under the [MIT License](LICENSE).
