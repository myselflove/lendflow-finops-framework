# LendFlow FinOps Methodology & Financial Assumptions

## 1. Modeling Principles

1. **Non-Overlapping Savings Waterfall**: To eliminate double-counting, savings are calculated sequentially:
   - **Step 1 (Hygiene)** operates on raw Month 6 baseline ($180,000).
   - **Step 2 (Rightsizing & Modernization)** operates on the remaining un-eliminated resources.
   - **Step 3 (Commitments & Rates)** calculates RI and Savings Plan discounts strictly on the rightsized post-Step 2 footprint.
2. **Conservative Realization Factor**: A 10% contingency buffer is factored into all human-dependent engineering migrations.
3. **Currency & Cost Basis**: All figures are represented in USD ($). AWS list prices and verified enterprise discount schedule rates applied.
4. **Loan Application Scale**: 500,000 monthly applications modeled as the ongoing baseline volume for unit economics calculation ($180,000 / 500,000 = $0.36 baseline; $77,525 / 500,000 = $0.155 target).
