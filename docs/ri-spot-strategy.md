# LendFlow Reserved Instance & Spot Strategy

## 1. Portfolio Allocation Model

To achieve optimal balance between cost efficiency, financial risk, and application availability, LendFlow infrastructure compute capacity is structured into three distinct tiers:

```
[Total Compute Capacity: 100%]
   │
   ├── Tier 1: Core Baseline (70% Allocation)
   │     - Covered by 3-Year Compute Savings Plans (CSP) & 1-Year RDS RIs
   │     - Workloads: Core API, Payment Gateway, Production Aurora Primary
   │     - Discount Rate: 52% - 68% off On-Demand rates
   │
   ├── Tier 2: Elastic Daytime Demand (18% Allocation)
   │     - Covered by 1-Year Flexible Savings Plans & On-Demand buffer
   │     - Workloads: Underwriting business-hour spikes, Reporting ETL
   │     - Discount Rate: 28% - 38% off On-Demand
   │
   └── Tier 3: Fault-Tolerant & Asynchronous Batch (12% Allocation)
         - Covered by AWS Spot Instances (Karpenter provisioned)
         - Workloads: Document OCR processing, Risk simulation batch, Dev/Test EKS
         - Discount Rate: 70% - 82% off On-Demand
```

---

## 2. Spot Instance Interruption Resilience Architecture

1. **Spot Instance Diversification**: Karpenter configured with at least 8 eligible instance types across 2 generations (`c6g.xlarge`, `c7g.xlarge`, `m6g.xlarge`, `m7g.xlarge`, `c6i.xlarge`, `m6i.xlarge`, `c5.2xlarge`, `m5.2xlarge`).
2. **AWS Node Termination Handler (NTH)**: Captures 2-minute Spot termination notices via EventBridge, cordons the node, and initiates graceful pod draining to alternative nodes before termination.
3. **Strict Workload Ring-Fence**:
   - `lendflow-payments` $ightarrow$ **FORBIDDEN ON SPOT** (PCI DSS).
   - `lendflow-core-db` $ightarrow$ **FORBIDDEN ON SPOT**.
   - `lendflow-doc-processor` $ightarrow$ **APPROVED FOR 100% SPOT**.
   - `lendflow-batch-etl` $ightarrow$ **APPROVED FOR 100% SPOT**.
