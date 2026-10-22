# LendFlow FinOps Regulatory Compliance Matrix

This matrix governs all cost optimization actions to ensure zero compromise on regulatory and statutory requirements.

| Regulatory Standard | Mandate Section | Technical Requirement | FinOps Constraint / Ring-Fence | Optimization Status |
|---|---|---|---|---|
| **PCI DSS v4.0** | Req 10.5.1 | Secure audit trails; Multi-AZ high availability | `lendflow-payments` service must maintain minimum 3 pods across 3 independent AZs; Spot instances prohibited | **STRICTLY LOCKED** ($16,300/mo) |
| **RBI IT Framework** | Section 4.2 | High availability, continuous operations in payment systems | Database reader instances must have automated failover within same region; multi-region data replication active | **COMPLIANT** |
| **SOC 2 Type II** | CC6.1 & CC6.8 | Immutable log retention & access controls | S3 Object Lock in Compliance Mode enabled for `lendflow-audit-trail` (7 years retention); deletion strictly blocked | **PROTECTED** |
| **GDPR** | Article 32 | Security of processing & data minimization | Ephemeral test data in non-prod environments must be purged after 14 days | **AUTOMATED** |
| **ISO 27001** | A.12.1.2 | Change management & capacity planning | Rightsizing operations require blue/green deployment and 48-hour soak testing in Staging | **ENFORCED** |
