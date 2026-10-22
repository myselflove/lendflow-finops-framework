"""
war_room.py — Interactive 4-Scenario FinOps War Room Simulator API
LendFlow FinOps Platform Group

Scenarios:
  1. CFO 90-Day Ultimatum ($60k/month reduction)
  2. Engineering Resistance (Graviton & downscaling friction)
  3. Billing Spike Containment (runaway NAT/Cross-AZ surge)
  4. Regulatory Compliance Audit Mapping (RBI & PCI DSS ring-fence)
"""

from typing import List
from fastapi import APIRouter, HTTPException
from app.backend.schemas import (
    WarRoomResponse, WarRoomScenario, WarRoomAction,
    WarRoomActionRequest, WarRoomActionResponse
)

router = APIRouter(prefix="/api/war-room", tags=["War Room"])

SCENARIOS: List[WarRoomScenario] = [
    WarRoomScenario(
        id="cfo-90-day-ultimatum",
        title="CFO 90-Day $60k Reduction Ultimatum",
        urgency="CRITICAL",
        description="Runway compression requires an immediate 33.3% cut from $180,000 to <=$120,000/month in 90 days.",
        context="LendFlow Technologies is preparing for Series C. The Board has tied executive bonuses and cloud budget approval to hitting <=$120,000 run-rate without degrading loan ingestion p99 latency.",
        primary_challenge="Deliver $60,000/month recurring savings without triggering customer-facing downtime during peak loan origination hours.",
        financial_stake_usd=60000.0,
        stakeholder_dynamics="CFO demands immediate P&L relief; VP of Eng fears feature roadmaps will be derailed by cloud migrations.",
        compliance_guardrail="Cardholder Data Environment (lendflow-payments) and audit retention cannot be trimmed.",
        available_actions=[
            WarRoomAction(
                action_id="act-cfo-1",
                title="Immediate Dev/Staging 12-Hour Night & Weekend Shutdown",
                description="Deploy EventBridge scheduler to turn off non-prod EKS node groups outside 08:00-20:00 IST weekdays.",
                immediate_savings_usd=15000.0,
                implementation_time_days=3,
                risk_level="LOW",
                stakeholder_impact="Developers must use self-service trigger if working late.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-cfo-2",
                title="Fast-Track Graviton3 Node Migration for Stateless Services",
                description="Convert Gateway, Auth, Notifications, and Analytics EKS node groups to c7g/m7g ARM instances.",
                immediate_savings_usd=22000.0,
                implementation_time_days=21,
                risk_level="MEDIUM",
                stakeholder_impact="Requires multi-arch Docker image builds and canary verification.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-cfo-3",
                title="1-Year Partial Upfront Compute Savings Plans",
                description="Lock in 70% post-rightsized compute baseline for 38% On-Demand discount.",
                immediate_savings_usd=12745.0,
                implementation_time_days=1,
                risk_level="LOW",
                stakeholder_impact="Finance must authorize a one-time partial upfront commitment payment.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-cfo-4",
                title="S3 Lifecycle + Orphaned EBS & EIP Purge",
                description="One-click purge of unattached volumes, idle load balancers, and automate Glacier archiving for old loans.",
                immediate_savings_usd=6800.0,
                implementation_time_days=2,
                risk_level="LOW",
                stakeholder_impact="Zero impact on active workloads.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-cfo-5",
                title="Dangerous: Cut lendflow-payments to Single AZ",
                description="Reduce payment service replicas to save $5,000/mo.",
                immediate_savings_usd=5000.0,
                implementation_time_days=1,
                risk_level="EXTREME",
                stakeholder_impact="Violates PCI DSS v4.0 multi-AZ high availability requirement.",
                compliance_approved=False
            )
        ]
    ),
    WarRoomScenario(
        id="engineering-resistance",
        title="Engineering Pushback on Downscaling & Architecture Changes",
        urgency="HIGH",
        description="Engineering teams resist instance rightsizing and CPU buffer reductions citing potential latency spikes.",
        context="After an initial rightsizing memo was shared, tech leads voiced concerns that lowering CPU buffers below 80% headroom would cause SLA breaches during loan promotion campaigns.",
        primary_challenge="Gain engineering trust and achieve $20,000+ rightsizing savings while establishing objective performance guardrails.",
        financial_stake_usd=23000.0,
        stakeholder_dynamics="Tech Leads defensive of stability; FinOps Lead needs evidence-based rightsizing with safe rollbacks.",
        compliance_guardrail="All critical customer endpoints must maintain <150ms p99 latency SLAs.",
        available_actions=[
            WarRoomAction(
                action_id="act-eng-1",
                title="Deploy Kubernetes Vertical Pod Autoscaler in Recommendation Mode",
                description="Run VPA in audit-only mode for 14 days to provide objective p95 memory and CPU consumption telemetry.",
                immediate_savings_usd=3600.0,
                implementation_time_days=7,
                risk_level="LOW",
                stakeholder_impact="Builds trust with tech leads through empirical data before resizing.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-eng-2",
                title="Automated Canary Deployments with Latency Guardrails",
                description="Rightsize 1 service at a time (e.g. lendflow-gateway) with automated Prometheus canary rollback if latency >100ms.",
                immediate_savings_usd=8500.0,
                implementation_time_days=14,
                risk_level="LOW",
                stakeholder_impact="Removes fear of manual rollbacks.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-eng-3",
                title="FinOps Gamification & Team Showback Dashboards",
                description="Publish monthly cloud efficiency leaderboards with recognition for teams that hit unit cost targets.",
                immediate_savings_usd=4000.0,
                implementation_time_days=5,
                risk_level="LOW",
                stakeholder_impact="Engages engineers through positive competition rather than executive mandates.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-eng-4",
                title="Forced Fleet-Wide CPU Throttling Without Testing",
                description="Arbitrarily reduce all EKS worker node types by 50% overnight.",
                immediate_savings_usd=18000.0,
                implementation_time_days=1,
                risk_level="HIGH",
                stakeholder_impact="High risk of cascading pod evictions and loan submission failures.",
                compliance_approved=False
            )
        ]
    ),
    WarRoomScenario(
        id="billing-spike-containment",
        title="Cross-AZ & NAT Gateway Billing Spike Emergency",
        urgency="HIGH",
        description="A surge in inter-microservice data transfer caused an unexpected $12,000 cost spike over 72 hours.",
        context="A newly released document verification pipeline deployed pods across ap-south-1a, 1b, and 1c without affinity, transmitting uncompressed image payloads across availability zones via NAT Gateway.",
        primary_challenge="Isolate and remediate the runaway network transfer within 4 hours to prevent a $30k budget overrun.",
        financial_stake_usd=12000.0,
        stakeholder_dynamics="DevOps on-call receiving billing alerts; Product team concerned about image upload throughput.",
        compliance_guardrail="All document verification payloads must remain encrypted in transit via TLS 1.3.",
        available_actions=[
            WarRoomAction(
                action_id="act-spk-1",
                title="Provision S3 Gateway VPC Endpoint Immediately",
                description="Re-route all doc-verify S3 uploads through a free VPC Gateway endpoint instead of NAT Gateway ($0.045/GB saved).",
                immediate_savings_usd=4500.0,
                implementation_time_days=1,
                risk_level="LOW",
                stakeholder_impact="Instant fix; 0 application downtime.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-spk-2",
                title="Implement TopologySpreadConstraint & Pod Node Affinity",
                description="Co-locate document processing pods in the same AZ as the ingestion service to eliminate cross-AZ transfer fees.",
                immediate_savings_usd=3800.0,
                implementation_time_days=2,
                risk_level="LOW",
                stakeholder_impact="Improves internal network latency by 40%.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-spk-3",
                title="Client-Side Image Compression Before Upload",
                description="Compress KYC document scans in mobile/web SDK before upload, reducing raw payload size by 65%.",
                immediate_savings_usd=2500.0,
                implementation_time_days=4,
                risk_level="LOW",
                stakeholder_impact="Reduces user mobile data consumption and speeds up processing.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-spk-4",
                title="Circuit Breaker Anomaly Alert Rule in Ingestion Gateway",
                description="Configure rate-limiting circuit breaker if transfer volume from any microservice exceeds 500GB/hour.",
                immediate_savings_usd=1200.0,
                implementation_time_days=1,
                risk_level="LOW",
                stakeholder_impact="Prevents future runaway loops from draining cloud budget.",
                compliance_approved=True
            )
        ]
    ),
    WarRoomScenario(
        id="compliance-audit-mapping",
        title="Regulatory Compliance Audit Mapping (RBI & PCI-DSS v4.0)",
        urgency="CRITICAL",
        description="Annual external compliance audit checks high-availability, data localization, and WORM log immutability.",
        context="Auditors from the Reserve Bank of India (RBI) and PCI Security Standards Council arrive in 14 days. Any cost optimisation that compromised isolation or DR will result in severe regulatory fines and license suspension.",
        primary_challenge="Prove that every single one of the 18 FinOps recommendations maintains 100% compliance with zero violations.",
        financial_stake_usd=16300.0,
        stakeholder_dynamics="Chief Compliance Officer and Head of Legal reviewing every infrastructure change.",
        compliance_guardrail="Zero cardholder data in non-PCI subnets; zero Indian lending data outside ap-south-1.",
        available_actions=[
            WarRoomAction(
                action_id="act-cmp-1",
                title="Verify Ring-Fenced Budget Isolation Policy ($16,300/mo)",
                description="Formally lock minimum 3-AZ configurations for Payments, Credit Scoring, and immutable audit logs.",
                immediate_savings_usd=0.0,
                implementation_time_days=1,
                risk_level="LOW",
                stakeholder_impact="Provides auditors with mathematically proven isolation and immutability guarantees.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-cmp-2",
                title="Automate S3 Object Lock & CloudTrail Continuous Audit Validation",
                description="Deploy AWS Config rule verifying WORM retention >= 12 months for lendflow-audit bucket across all regions.",
                immediate_savings_usd=500.0,
                implementation_time_days=2,
                risk_level="LOW",
                stakeholder_impact="Gives auditors instant green checkmark on SOC 2 and RBI requirements.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-cmp-3",
                title="Tagging Enforcement via OPA Gatekeeper Admission Controller",
                description="Reject any Kubernetes deployment or Terraform plan missing ComplianceScope or CostCenter tags.",
                immediate_savings_usd=1800.0,
                implementation_time_days=3,
                risk_level="LOW",
                stakeholder_impact="Prevents compliance configuration drift permanently.",
                compliance_approved=True
            ),
            WarRoomAction(
                action_id="act-cmp-4",
                title="Illegal Consolidation: Move Indian Loan DB to eu-west-1",
                description="Merge ap-south-1 databases into Frankfurt to save $4,000 on redundant clusters.",
                immediate_savings_usd=4000.0,
                implementation_time_days=1,
                risk_level="EXTREME",
                stakeholder_impact="Severe violation of RBI data residency mandate; triggers catastrophic regulatory revocation.",
                compliance_approved=False
            )
        ]
    )
]


@router.get("", response_model=WarRoomResponse)
def get_war_room_scenarios() -> WarRoomResponse:
    """Returns all 4 interactive FinOps War Room crisis scenarios."""
    return WarRoomResponse(
        total_scenarios=len(SCENARIOS),
        scenarios=SCENARIOS
    )


@router.post("/simulate", response_model=WarRoomActionResponse)
def simulate_war_room_action(payload: WarRoomActionRequest) -> WarRoomActionResponse:
    """Evaluates the user's selected actions for a given scenario."""
    scenario = next((s for s in SCENARIOS if s.id == payload.scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{payload.scenario_id}' not found.")

    selected_actions = [
        a for a in scenario.available_actions if a.action_id in payload.selected_action_ids
    ]

    # Check for compliance violations
    has_violation = any(not a.compliance_approved for a in selected_actions)
    total_savings = round(sum(a.immediate_savings_usd for a in selected_actions), 2)
    total_days = max([a.implementation_time_days for a in selected_actions], default=0)

    # Determine risk score
    if has_violation:
        risk_score = "CRITICAL_COMPLIANCE_BREACH"
        cfo_status = "REJECTED (Regulatory Violation)"
        summary = (
            "CRITICAL WARNING: One or more selected actions violated regulatory requirements "
            "(e.g., PCI DSS isolation or RBI data residency). While on-paper savings appear high, "
            "this plan would trigger severe regulatory audit failure and operational suspension."
        )
    elif total_savings >= scenario.financial_stake_usd:
        risk_score = "LOW_RISK_OPTIMAL"
        cfo_status = "APPROVED — Full Target Achieved"
        summary = (
            f"OUTSTANDING EXECUTION: Selected plan delivers ${total_savings:,.2f}/month in savings, "
            f"exceeding the scenario financial objective (${scenario.financial_stake_usd:,.2f}) within {total_days} days. "
            "All compliance guardrails and latency SLAs remain intact."
        )
    elif total_savings > 0:
        risk_score = "MODERATE_PARTIAL"
        cfo_status = "CONDITIONALLY APPROVED (Under Target)"
        gap = round(scenario.financial_stake_usd - total_savings, 2)
        summary = (
            f"PARTIAL PROGRESS: Selected plan captures ${total_savings:,.2f}/month in safe savings "
            f"in {total_days} days, leaving a ${gap:,.2f}/month gap to the executive objective. "
            "Combine with additional low-risk actions to meet the target."
        )
    else:
        risk_score = "NO_ACTION"
        cfo_status = "PENDING"
        summary = "No valid actions were selected."

    return WarRoomActionResponse(
        scenario_id=payload.scenario_id,
        total_savings_achieved_usd=total_savings,
        implementation_days_total=total_days,
        risk_score=risk_score,
        compliance_passed=not has_violation,
        cfo_approval_status=cfo_status,
        outcome_summary=summary
    )
