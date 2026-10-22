# 💸 LendFlow FinOps Framework
### Cloud-Native Infrastructure Cost Optimisation & FinOps Governance Platform

[![CI/CD Pipeline](https://github.com/myselflove/lendflow-finops-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/myselflove/lendflow-finops-framework/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Terraform](https://img.shields.io/badge/Terraform-1.5+-844FBA.svg?logo=terraform&logoColor=white)](https://www.terraform.io)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Tests Passing](https://img.shields.io/badge/Tests-117%20Passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 At a Glance

* **The Problem:** Cloud spend skyrocketed from **$50,000 to $180,000/mo** across **12 microservices** as loan volume scaled to **500,000+/mo**, slashing gross operating margin from **75% to 55%**.
* **The Solution:** A 90-day **Zero Double-Counting FinOps Framework** cutting AWS spend to **$77,525/mo** (**$102,475/mo savings &bull; 56.9% reduction**).
* **The Guarantee:** Zero double-counting math, 100% audit-safe, with zero compromise on **PCI DSS v4.0**, **RBI IT**, or **SOC 2** SLAs.

---

## 💰 Financial Waterfall & Savings

| ☁️ AWS Service Category | 📉 Baseline / mo | 🛠️ Optimization Levers | 💵 Post-Opt / mo | 💸 Net Monthly Savings |
| :--- | :---: | :--- | :---: | :---: |
| **Compute (EC2 & EKS)** | $75,000 | Graviton3 (c7g/m7g), Karpenter Spot, off-hours shutdown | $32,450 | **+$42,550** |
| **Databases (RDS & Aurora)** | $45,000 | Aurora I/O-Optimized, right-sizing non-prod DBs | $22,800 | **+$22,200** |
| **NAT Gateways & Transfer** | $18,000 | S3 VPC Gateway Endpoints (Free), intra-AZ routing | $3,600 | **+$14,400** |
| **Storage (EBS & S3)** | $15,000 | gp2 &rarr; gp3 migration, S3 Intelligent-Tiering | $6,875 | **+$8,125** |
| **ElastiCache & Redis** | $12,000 | Reserved cache nodes, cluster right-sizing | $5,400 | **+$6,600** |
| **Other (CloudWatch, KMS)** | $15,000 | Log lifecycle policies, metric stream pruning | $6,400 | **+$8,600** |
| **TOTAL** | **$180,000** | **Phased 3-Stage Waterfall Execution** | **$77,525** | **+$102,475 / mo** |

> 📊 **Unit Economics Impact:** Cost per 1,000 loan applications reduced from **$360 &rarr; $155** (**56.9% efficiency gain**).

---

## 🏗️ Architecture & 12 Microservices

```
                                  [Internet Traffic]
                                          │
                                 [AWS WAF / Shield]
                                          ▼
                               ┌──────────────────────┐
                               │   lendflow-gateway   │
                               └──────────┬───────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
       ┌──────────────────────┐                       ┌──────────────────────┐
       │    lendflow-auth     │                       │  lendflow-ingestion  │
       └──────────────────────┘                       └───────────┬──────────┘
                                                                  │
              ┌───────────────────────────┬───────────────────────┘
              ▼                           ▼
   ┌──────────────────────┐    ┌──────────────────────┐
   │ lendflow-credit-risk │    │ lendflow-doc-verify  │
   │  (ML • 3 Multi-AZ)   │    │     (OCR / KYC)      │
   └──────────┬───────────┘    └──────────┬───────────┘
              └─────────────┬─────────────┘
                            ▼
   ┌────────────────────────────────────────────────────────┐
   │ 🔒 Isolated PCI DSS Subnet                             │
   │    └── lendflow-payments (Min 3 Multi-AZ, zero egress) │
   └────────────────────────┬───────────────────────────────┘
                            ▼
   ┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
   │   lendflow-ledger    │    │  lendflow-analytics  │    │   lendflow-audit     │
   │  (Aurora Multi-AZ)   │    │  (Graviton3 Spot)    │    │  (S3 WORM Lock)      │
   └──────────────────────┘    └──────────────────────┘    └──────────────────────┘
```

---

## ✨ Key Features & Stack

* ⚡ **FastAPI Calculation Engine:** REST API with Z-score anomaly detection, tag compliance, and recommendation simulator.
* 🖥️ **React 18 & TypeScript Dashboard:** 10 views (Executive Waterfall, Cost Explorer, War Room, Storage, Compute, Anomaly Alerts).
* 🚨 **Real-Time On-Call Alerting:** One-click anomaly alert dispatcher integrated with Slack/Discord webhooks.
* 🛡️ **Policy-as-Code Guardrails:** Open Policy Agent (OPA) Rego rules, AWS SCPs, and Karpenter autoscaling configs.
* ☁️ **Terraform IaC:** Graviton3 node pools and NAT-free S3 Gateway VPC endpoints.
* ✅ **117 Pytest Tests:** 100% automated test coverage across billing math, schemas, and compliance constraints.

---

## 💻 Step-by-Step Setup Guide

### 🚀 Method 1: 1-Click Docker (Easiest)

Run both the FastAPI backend and React frontend with one command:

```bash
docker compose up --build
```
* 🌐 **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
* 📖 **Backend API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### ⚙️ Method 2: Manual Local Setup (Step-by-Step)

#### Step 1: Clone Repository
```bash
git clone https://github.com/myselflove/lendflow-finops-framework.git
cd lendflow-finops-framework
```

#### Step 2: Start Backend (Terminal 1)
```powershell
# Navigate to backend directory
cd app\backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --port 8000
```
> 💡 *Backend will be live at `http://localhost:8000` (API docs at `/docs`).*

#### Step 3: Start Frontend (Terminal 2)
```powershell
# Open a new terminal and navigate to frontend directory
cd app\frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
> 💡 *Dashboard will open at `http://localhost:5173`.*

---

## 🧪 Running Automated Tests

Run the full suite of **117 tests**:

```powershell
# From project root
pytest -v
```

```text
======================= 117 passed in 3.50s =======================
```

---

## 📁 Clean Repository Structure

```text
lendflow-finops-framework/
├── .github/workflows/ci.yml       # 🤖 GitHub Actions automated CI/CD pipeline
├── analysis/                      # 📊 Excel financial models & audit scripts
├── app/
│   ├── backend/                   # ⚡ FastAPI calculation engine & routers
│   └── frontend/                  # 🖥️ React 18 + TypeScript + Recharts SPA
├── data/                          # 📁 8 Synthetic fintech billing datasets
├── docs/                          # 📚 Architecture, RTM & FinOps runbooks
├── infrastructure/                # ☁️ Terraform modules (Graviton3, VPC Endpoints)
├── policies/                      # 🛡️ OPA Rego policies, SCPs & Karpenter configs
├── presentation/                  # 📈 CFO executive presentation deck (.pptx)
├── scripts/                       # 🔧 Automation & test scripts
├── tests/                         # ✅ Pytest test suite (117 test cases)
├── docker-compose.yml             # 🐳 Docker container orchestration
├── vercel.json                    # 🌐 1-Click Vercel cloud deployment config
└── requirements.txt               # 🐍 Python dependencies
```

---

## 📜 License

Distributed under the [MIT License](LICENSE).
