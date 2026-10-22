# LendFlow Cost Anomaly Detection & Incident Response Runbook

## 1. Detection Engine Architecture

The LendFlow FinOps Platform runs an automated hourly and daily cost anomaly detection engine utilizing:
1. **Dynamic Rolling Z-Score**:
   $$	ext{Z-Score} = rac{	ext{Current Daily Spend} - \mu_{30	ext{-day}}}{\sigma_{30	ext{-day}}}$$
   Anomalies are flagged when $|Z| \ge 2.5$.
2. **Absolute Spend Deviation**: Any single service jumping by $> \$500$ in a 24-hour window regardless of historical variance.
3. **Unattached Resource Spikes**: Hourly polling for unattached EBS volumes, unassociated Elastic IPs, and idle NAT Gateways.

---

## 2. Incident Classification & SLAs

| Severity | Threshold Criteria | Incident Response SLA | Root Cause Analysis (RCA) Due |
|---|---|---|---|
| **P1 - Critical** | Impact $> \$2,000$ / day or $> 100\%$ spike in single service | 1 Hour | 24 Hours |
| **P2 - High** | Impact $\$500 - \$2,000$ / day or unmanaged EKS node surge | 4 Hours | 48 Hours |
| **P3 - Medium** | Impact $\$100 - \$500$ / day or unattached volumes $> 10$ | 24 Hours | 5 Business Days |
| **P4 - Low** | Minor tagging violations or storage growth deviation | 72 Hours | Next Sprint |
