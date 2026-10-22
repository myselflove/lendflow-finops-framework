# LendFlow FinOps Platform — Executive Demo Script

**Audience**: CFO, VP of Engineering, Lead FinOps Review Panel  
**Duration**: 15 Minutes  
**Demonstrator**: FinOps Lead Engineer  

---

## 1. Scene 1: The Problem — Unchecked Cloud Expansion (2 Mins)
- **Visual**: Navigate to **Executive / CFO Dashboard** view.
- **Narrative**:
  > "Over the last 6 months, LendFlow grew 10x in loan volume from 50,000 to 500,000 applications. But our cloud spend grew even faster — from $50,000 to $180,000 per month.
  > Notice here: Compute represents 36.7% and Database represents 23.3% of total spend. Our unit cost per application reached $0.36. Our mission was to uncover waste and bring this unit cost down without sacrificing availability."

---

## 2. Scene 2: Waste Breakdown & The Three-Step Waterfall (4 Mins)
- **Visual**: Navigate to **FinOps Savings Simulator** view.
- **Narrative**:
  > "Rather than arbitrary cuts, we engineered a rigorous 3-step non-overlapping savings waterfall:
  > - **Step 1: Hygiene**: Purging 42 unattached EBS volumes, S3 Intelligent-Tiering, and automated non-prod power scheduling saves **$28,320/mo**.
  > - **Step 2: Rightsizing**: Downsizing 48 oversized EC2 nodes, migrating to AWS Graviton3, and Aurora Serverless v2 saves **$38,850/mo**.
  > - **Step 3: Commitments**: 3-Year Compute Savings Plans and Spot instances for async workers saves **$35,305/mo**.
  > Total savings: **$102,475/month**, lowering our monthly bill from $180,000 to $77,525."
- **Interactive Action**: Toggle off one of the recommendations to demonstrate live dynamic recalculation of the waterfall chart and net monthly bill.

---

## 3. Scene 3: Regulatory Compliance Ring-Fence (3 Mins)
- **Visual**: Navigate to **Compute & Database Optimisation** and **Storage Optimisation** views.
- **Narrative**:
  > "Notice these regulatory badges. As a fintech handling credit underwriting and disbursements, we operate under PCI DSS v4.0 and RBI IT mandates.
  > The `lendflow-payments` service is strictly ring-fenced at a minimum of 6 pods across 3 availability zones on On-Demand instances — Spot instances are strictly blocked.
  > In storage, our `lendflow-audit-trail` bucket uses AWS S3 Object Lock with 7-year WORM compliance for SOC 2 Type II audit readiness. Zero deletion is permitted."

---

## 4. Scene 4: Policy-as-Code & Automated Guardrails (3 Mins)
- **Visual**: Navigate to **FinOps Policy-as-Code & Compliance** view.
- **Narrative**:
  > "To ensure waste never returns, we embedded guardrails into code.
  > Here you see our 4 AWS Service Control Policies, our OPA Rego policy, and our Infracost Terraform module. Any deployment missing one of our 10 mandatory tags or requesting unauthorized GPU instances is automatically rejected at the CI/CD gate before spending a single dollar."

---

## 5. Scene 5: Live Operations & Anomaly War Room (2 Mins)
- **Visual**: Navigate to **Cost Anomaly Centre** and **FinOps Live Operations War Room**.
- **Narrative**:
  > "Our automated Z-score anomaly detection flags unexpected spikes in real-time with P1 through P4 SLAs. When a spike exceeds $500/day, PagerDuty automatically alerts the squad lead.
  > Our 90-day roadmap delivers full realization by Day 90, generating an annualized EBITDA contribution of $1,229,700."

---

## 6. Q&A Preparation
- Be prepared to open `analysis/savings-model.xlsx` to show the live Excel formulas and the Spot sensitivity tab (5%, 10%, 20%).
- Refer to `presentation/cfo-review.pptx` for full financial breakdown and appendix details.
