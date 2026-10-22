# LendFlow FinOps Governance Model & Operating Framework

## 1. RACI Matrix

| FinOps Activity | FinOps Lead | VP Engineering | CFO / Finance | Lead Architect | DevOps / SRE |
|---|---|---|---|---|---|
| **Monthly Budget Setting** | A | C | R | C | I |
| **Commitment Purchases (RI/SP)** | R | C | A | C | I |
| **Rightsizing Implementation** | A | R | I | C | R |
| **Tag Compliance Audit** | R | I | I | C | A |
| **Anomaly RCA Investigation** | A | R | I | C | R |
| **Architecture Review for Cost**| C | A | I | R | C |

*Legend: R = Responsible, A = Accountable, C = Consulted, I = Informed*

---

## 2. Budget Alerting & Escalation Thresholds

Budgets are configured in AWS Budgets and propagated to Slack `#finops-alerts` and PagerDuty:
- **80% of Monthly Budget Burned**: Automated Slack notification to Engineering Leads.
- **95% of Monthly Budget Burned**: Mandatory review with VP of Engineering.
- **100% Forecast Exceeded**: Automatic P2 ticket created in Jira; architectural hiring/scaling freeze on non-essential services.
- **P1 Cost Anomaly (> $500/day unexpected jump)**: PagerDuty on-call alert triggered with 1-hour SLA.
