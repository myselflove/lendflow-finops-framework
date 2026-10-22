# LendFlow FinOps Dashboard Specification & User Guide

## 1. Dashboard Architecture

The LendFlow FinOps Platform provides an enterprise-grade React 18 + TypeScript single-page application interfacing with a high-performance FastAPI backend.

### Core Views
1. **Executive / CFO Dashboard**: High-level KPIs ($180k baseline, $77.5k target, $102.5k savings, unit economics, 90-day forecast).
2. **Infrastructure Cost Explorer**: Multi-dimensional filtering by Month, Service, Environment, Team, Region, Cost Centre, Compliance Scope.
3. **Compute & Database Optimisation**: Actionable rightsizing cards with compliance badges and projected savings.
4. **Storage Optimisation**: EBS volume purges, S3 Intelligent-Tiering candidate tables.
5. **Data Transfer Analysis**: Top 10 costliest transfer paths and cross-AZ reduction strategies.
6. **Tag Governance & Dark Spend**: Compliance gauges for 10 mandatory tags, team heatmaps, and dark spend quantification.
7. **Cost Anomaly Centre**: Real-time anomaly alerts with P1-P4 severity badges and interactive Z-score sensitivity sliders.
8. **FinOps Savings Simulator**: Dynamic toggle switches recalculating Step 1, Step 2, and Step 3 non-overlapping waterfalls.
9. **FinOps Policy-as-Code & Compliance**: Live syntax view of AWS SCPs, Config rules, OPA Rego policies, and Infracost specs.
10. **FinOps Live Operations War Room**: Real-time simulated telemetry, burn rate monitor, and active incident tracker.
