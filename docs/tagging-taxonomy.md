# LendFlow Cloud Tagging Taxonomy & Enforcement Standard

## 1. Mandatory Tag Schema

Every cloud resource provisioned in LendFlow AWS accounts must possess the following 10 mandatory tags:

| Tag Key | Type | Allowed Values / Format | Purpose |
|---|---|---|---|
| `Environment` | Enum | `prod`, `staging`, `dev`, `qa`, `sandbox` | Environment isolation & SLA definition |
| `Team` | Enum | `platform`, `underwriting`, `payments`, `analytics`, `security` | Team cost attribution |
| `Owner` | String | Valid Corporate Email (`name@lendflow.com`) | Operational and billing accountability |
| `CostCentre` | Enum | `CC-101` (Core), `CC-202` (Underwriting), `CC-303` (Payments), `CC-404` (BI), `CC-505` (Shared Infra) | Financial ledger reconciliation |
| `Project` | String | `lendflow-origination`, `lendflow-servicing`, `shared-platform` | Project accounting |
| `ComplianceScope` | Enum | `PCI-DSS`, `SOC2`, `RBI-IT`, `GDPR`, `Standard`, `None` | Regulatory ring-fencing |
| `DataClassification`| Enum | `Public`, `Internal`, `Confidential`, `Restricted-PII` | Data security & lifecycle tiering |
| `ApplicationID` | String | Format: `APP-[0-9]{4}` (e.g. `APP-1001`) | CMDB inventory tracking |
| `CreatedDate` | Date | ISO 8601 UTC (`YYYY-MM-DD`) | Age tracking & orphan resource audits |
| `AutoStopExclude` | Boolean| `true`, `false` | Power scheduler bypass validation |

---

## 2. Enforcement Architecture

Tag compliance is enforced across three distinct pipeline checkpoints:
1. **Pre-Deployment (Terraform & CI/CD)**: Infracost and OPA Rego policies (`finops_guardrails.rego`) reject `terraform plan` if any of the 10 mandatory tags are missing.
2. **Account Boundary (AWS Service Control Policies)**: SCP `mandatory-tags.json` blocks `ec2:RunInstances`, `rds:CreateDBInstance`, and `s3:CreateBucket` without tags.
3. **Continuous Audit (AWS Config)**: AWS Config Rule `REQUIRED_TAGS` flags untagged resources within 5 minutes. Resources remaining non-compliant for >48 hours in non-production are automatically stopped.
