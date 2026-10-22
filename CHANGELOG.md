# Changelog
## LendFlow FinOps Framework — Cloud-Native Cost Optimisation Platform
All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] - Production Release

### Added
- **FinOps Calculation Engine**: FastAPI + Pandas zero double-counting waterfall calculation engine.
- **Full-Stack Dashboard**: React 18 + TypeScript + Vite + Tailwind CSS + Recharts with 10 comprehensive operational views.
- **Governance & Policies**: OPA Rego compliance policies, AWS Service Control Policies, AWS Config rules, and Kubernetes Karpenter / HPA / VPA configs.
- **Cost-Aware IaC**: Terraform modules for Graviton3 EKS node groups and S3 Gateway VPC Endpoints.
- **Automated Verification**: Complete Pytest test suite with 117 automated unit and integration tests passing.
- **Docker & CI/CD**: Containerized backend and frontend services with Docker Compose and GitHub Actions CI workflow.

---

## [0.2.0]

### Added
- `docs/requirements-traceability.md` — Full RTM mapping all 26 specification requirements to compliance frameworks and acceptance criteria.
- `docs/architecture.md` — Complete architecture document covering all 12 microservices, 3-tier AWS design, and compliance isolation zones.
- Savings waterfall model (zero-double-counting methodology).

---

## [0.1.0]

### Added
- Complete directory structure and environment configuration.
- Comprehensive `.gitignore` and `.env.example`.
- Synthetic fintech datasets generation engine (Seed 42, 19,152 records).

