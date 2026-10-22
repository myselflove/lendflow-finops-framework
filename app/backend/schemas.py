"""
schemas.py — LendFlow FinOps Framework Pydantic Schemas
LendFlow FinOps Platform Team

Pydantic models for all API request and response payloads.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ==============================================================================
# Summary Schemas
# ==============================================================================

class ExecutiveKpis(BaseModel):
    baseline_monthly_spend_usd: float = Field(..., description="Month 6 baseline spend ($180,000.00)")
    projected_monthly_spend_usd: float = Field(..., description="Post-optimisation monthly spend")
    total_monthly_savings_usd: float = Field(..., description="Total projected monthly savings")
    savings_pct: float = Field(..., description="Savings percentage (target >= 33.3%)")
    target_achieved: bool = Field(..., description="Whether $60,000/month target is met")
    annualized_run_rate_savings_usd: float = Field(..., description="Annualized savings")
    monthly_revenue_usd: float = Field(1_000_000.0, description="Monthly revenue baseline")
    current_gross_margin_pct: float = Field(55.0, description="Current gross margin percentage")
    projected_gross_margin_pct: float = Field(..., description="Projected gross margin after AWS cost reduction")
    compliance_ring_fenced_usd: float = Field(..., description="Protected non-reducible spend ($16,300)")


class SpendTrendItem(BaseModel):
    month: int
    month_name: str
    total_cost_usd: float
    categories: Dict[str, float]


class UnitEconomics(BaseModel):
    monthly_loan_applications: int = Field(500_000, description="Monthly loan applications processed")
    current_cost_per_application_usd: float = Field(..., description="Current cost per loan application")
    projected_cost_per_application_usd: float = Field(..., description="Projected cost per loan application")
    current_cost_per_1k_loans_usd: float = Field(..., description="Current cost per 1,000 loan applications")
    projected_cost_per_1k_loans_usd: float = Field(..., description="Projected cost per 1,000 loan applications")
    savings_per_1k_loans_usd: float = Field(..., description="Savings per 1,000 loan applications")


class Forecast90DayItem(BaseModel):
    day: int
    month_label: str
    unmanaged_spend_usd: float
    optimised_spend_usd: float
    cumulative_savings_usd: float
    active_phase: str


class RiCoverageSummary(BaseModel):
    current_effective_coverage_pct: float = Field(..., description="Current RI/SP coverage (0% baseline)")
    target_coverage_pct: float = Field(72.0, description="Target RI/SP coverage")
    recommended_split: Dict[str, float] = Field(..., description="Recommended commitment mix")
    monthly_commitment_spend_usd: float


class SummaryResponse(BaseModel):
    kpis: ExecutiveKpis
    spend_trend: List[SpendTrendItem]
    unit_economics: UnitEconomics
    forecast_90_day: List[Forecast90DayItem]
    ri_coverage: RiCoverageSummary


# ==============================================================================
# Cost Explorer Schemas
# ==============================================================================

class CostRecord(BaseModel):
    date: str
    service: str
    resource_type: str
    resource_id: str
    cost: float
    environment: str
    region: str
    az: Optional[str] = None
    tags: Optional[str] = None


class GroupedCostItem(BaseModel):
    name: str
    total_cost_usd: float
    percentage: float
    resource_count: int


class DailyCostItem(BaseModel):
    date: str
    total_cost_usd: float


class ExplorerResponse(BaseModel):
    total_spend_usd: float
    total_records: int
    filtered_records_count: int
    group_by: str
    grouped_data: List[GroupedCostItem]
    daily_trend: List[DailyCostItem]
    sample_records: List[CostRecord]


# ==============================================================================
# Optimisations Schemas
# ==============================================================================

class ComplianceLock(BaseModel):
    service: str
    framework: str
    rule: str
    protected_budget_usd: float
    description: str


class OptimisationItem(BaseModel):
    id: int
    rank: int
    phase: str
    appendix_a: str
    category: str
    title: str
    action: str
    estimated_monthly_savings_usd: float
    effort: str
    risk: str
    compliance_impact: str
    compliance_locked: bool
    implementation_days: int
    payback_days: int
    status: str = "RECOMMENDED"


class OptimisationsResponse(BaseModel):
    total_recommendations: int
    total_estimated_monthly_savings_usd: float
    recommendations_by_phase: Dict[str, int]
    recommendations_by_effort: Dict[str, int]
    compliance_locks: List[ComplianceLock]
    recommendations: List[OptimisationItem]


# ==============================================================================
# Storage & Transfer Schemas
# ==============================================================================

class S3LifecycleItem(BaseModel):
    resource_id: str
    service: str
    environment: str
    size_gb: float
    current_storage_class: str
    target_storage_class: str
    days_since_access: int
    current_monthly_cost_usd: float
    projected_monthly_cost_usd: float
    monthly_savings_usd: float
    lifecycle_status: str


class EbsCandidateItem(BaseModel):
    resource_id: str
    service: str
    environment: str
    size_gb: float
    size_used_gb: float
    wasted_pct: float
    storage_class: str
    current_monthly_cost_usd: float
    monthly_savings_usd: float
    recommendation: str


class StorageClassMetric(BaseModel):
    storage_class: str
    resource_count: int
    total_size_gb: float
    total_monthly_cost_usd: float


class StorageResponse(BaseModel):
    total_storage_monthly_cost_usd: float
    total_storage_gb: float
    total_potential_savings_usd: float
    s3_wrong_tier_count: int
    ebs_over_provisioned_count: int
    gp2_to_gp3_candidates_count: int
    storage_class_breakdown: List[StorageClassMetric]
    s3_candidates: List[S3LifecycleItem]
    ebs_candidates: List[EbsCandidateItem]


class TransferPathItem(BaseModel):
    source_service: str
    destination_service: str
    transfer_type: str
    total_gb_transferred: float
    total_cost_usd: float
    is_wasteful: bool
    optimization: str


class TransferTypeMetric(BaseModel):
    transfer_type: str
    total_gb: float
    total_cost_usd: float
    cost_percentage: float


class TransferResponse(BaseModel):
    total_transfer_cost_usd: float
    total_transfer_gb: float
    cross_az_cost_usd: float
    cross_az_percentage: float
    transfer_type_breakdown: List[TransferTypeMetric]
    top_10_costliest_paths: List[TransferPathItem]
    recommendations: List[Dict[str, Any]]


# ==============================================================================
# Tagging Schemas
# ==============================================================================

class TagMetric(BaseModel):
    tag_name: str
    is_core: bool
    compliance_rate_pct: float
    compliant_resources: int
    non_compliant_resources: int


class TeamTagMetric(BaseModel):
    service_or_team: str
    environment: str
    total_resources: int
    compliant_resources: int
    compliance_rate_pct: float
    missing_tags: List[str]


class TagsResponse(BaseModel):
    total_resources_analyzed: int
    overall_compliance_rate_pct: float
    dark_spend_monthly_usd: float
    dark_spend_percentage: float
    mandatory_tags_metrics: List[TagMetric]
    service_heatmap: List[TeamTagMetric]


# ==============================================================================
# Anomalies Schemas
# ==============================================================================

class AnomalyItem(BaseModel):
    date: str
    service: str
    anomaly_type: str
    severity: str
    sla_hours: int
    sla_tier: str
    expected_cost_usd: float
    actual_cost_usd: float
    delta_usd: float
    delta_pct: float
    z_score: float
    root_cause: str
    auto_resolved: bool
    ticket_id: str
    region: str


class AnomalySummary(BaseModel):
    total_anomalies: int
    total_impact_usd: float
    open_count: int
    resolved_count: int
    by_severity: Dict[str, int]
    by_type: Dict[str, int]


class AnomaliesResponse(BaseModel):
    threshold_pct: float
    summary: AnomalySummary
    anomalies: List[AnomalyItem]


# ==============================================================================
# Simulator Schemas
# ==============================================================================

class SimulatorRequest(BaseModel):
    enabled_recommendation_ids: Optional[List[int]] = Field(
        default=None,
        description="List of recommendation IDs (1-18) to enable. Defaults to all 18 if None."
    )


class WaterfallStepDetail(BaseModel):
    step_name: str
    step_number: int
    baseline_usd: float
    savings_usd: float
    post_savings_baseline_usd: float
    savings_breakdown: Dict[str, float]
    active_recommendations_count: int


class SimulatorResponse(BaseModel):
    initial_baseline_spend_usd: float = 180_000.0
    step1: WaterfallStepDetail
    step2: WaterfallStepDetail
    step3: WaterfallStepDetail
    total_savings_usd: float
    savings_pct: float
    final_monthly_spend_usd: float
    target_monthly_savings_usd: float = 60_000.0
    target_achieved: bool
    target_gap_usd: float
    zero_double_counting_verified: bool
    verification_checks: Dict[str, bool]


# ==============================================================================
# War Room Schemas
# ==============================================================================

class WarRoomAction(BaseModel):
    action_id: str
    title: str
    description: str
    immediate_savings_usd: float
    implementation_time_days: int
    risk_level: str
    stakeholder_impact: str
    compliance_approved: bool


class WarRoomScenario(BaseModel):
    id: str
    title: str
    urgency: str
    description: str
    context: str
    primary_challenge: str
    financial_stake_usd: float
    stakeholder_dynamics: str
    available_actions: List[WarRoomAction]
    compliance_guardrail: str


class WarRoomResponse(BaseModel):
    total_scenarios: int
    scenarios: List[WarRoomScenario]


class WarRoomActionRequest(BaseModel):
    scenario_id: str
    selected_action_ids: List[str]


class WarRoomActionResponse(BaseModel):
    scenario_id: str
    total_savings_achieved_usd: float
    implementation_days_total: int
    risk_score: str
    compliance_passed: bool
    cfo_approval_status: str
    outcome_summary: str
