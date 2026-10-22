/**
 * finops.ts — TypeScript interfaces for LendFlow FinOps Platform
 * LendFlow FinOps Platform Group
 */

export type AudienceView = 'executive' | 'engineering-manager' | 'team';

export interface ExecutiveKpis {
  baseline_monthly_spend_usd: number;
  projected_monthly_spend_usd: number;
  total_monthly_savings_usd: number;
  savings_pct: number;
  target_achieved: boolean;
  annualized_run_rate_savings_usd: number;
  monthly_revenue_usd: number;
  current_gross_margin_pct: number;
  projected_gross_margin_pct: number;
  compliance_ring_fenced_usd: number;
}

export interface SpendTrendItem {
  month: number;
  month_name: string;
  total_cost_usd: number;
  categories: Record<string, number>;
}

export interface UnitEconomics {
  monthly_loan_applications: number;
  current_cost_per_application_usd: number;
  projected_cost_per_application_usd: number;
  current_cost_per_1k_loans_usd: number;
  projected_cost_per_1k_loans_usd: number;
  savings_per_1k_loans_usd: number;
}

export interface Forecast90DayItem {
  day: number;
  month_label: string;
  unmanaged_spend_usd: number;
  optimised_spend_usd: number;
  cumulative_savings_usd: number;
  active_phase: string;
}

export interface RiCoverageSummary {
  current_effective_coverage_pct: number;
  target_coverage_pct: number;
  recommended_split: Record<string, number>;
  monthly_commitment_spend_usd: number;
}

export interface SummaryResponse {
  kpis: ExecutiveKpis;
  spend_trend: SpendTrendItem[];
  unit_economics: UnitEconomics;
  forecast_90_day: Forecast90DayItem[];
  ri_coverage: RiCoverageSummary;
}

export interface GroupedCostItem {
  name: string;
  total_cost_usd: number;
  percentage: number;
  resource_count: number;
}

export interface DailyCostItem {
  date: string;
  total_cost_usd: number;
}

export interface CostRecord {
  date: string;
  service: string;
  resource_type: string;
  resource_id: string;
  cost: number;
  environment: string;
  region: string;
  az?: string;
  tags?: string;
}

export interface ExplorerResponse {
  total_spend_usd: number;
  total_records: number;
  filtered_records_count: number;
  group_by: string;
  grouped_data: GroupedCostItem[];
  daily_trend: DailyCostItem[];
  sample_records: CostRecord[];
}

export interface ComplianceLock {
  service: string;
  framework: string;
  rule: string;
  protected_budget_usd: number;
  description: string;
}

export interface OptimisationItem {
  id: number;
  rank: number;
  phase: string;
  appendix_a: string;
  category: string;
  title: string;
  action: string;
  estimated_monthly_savings_usd: number;
  effort: string;
  risk: string;
  compliance_impact: string;
  compliance_locked: boolean;
  implementation_days: number;
  payback_days: number;
  status: string;
}

export interface OptimisationsResponse {
  total_recommendations: number;
  total_estimated_monthly_savings_usd: number;
  recommendations_by_phase: Record<string, number>;
  recommendations_by_effort: Record<string, number>;
  compliance_locks: ComplianceLock[];
  recommendations: OptimisationItem[];
}

export interface S3LifecycleItem {
  resource_id: string;
  service: string;
  environment: string;
  size_gb: number;
  current_storage_class: string;
  target_storage_class: string;
  days_since_access: number;
  current_monthly_cost_usd: number;
  projected_monthly_cost_usd: number;
  monthly_savings_usd: number;
  lifecycle_status: string;
}

export interface EbsCandidateItem {
  resource_id: string;
  service: string;
  environment: string;
  size_gb: number;
  size_used_gb: number;
  wasted_pct: number;
  storage_class: string;
  current_monthly_cost_usd: number;
  monthly_savings_usd: number;
  recommendation: string;
}

export interface StorageClassMetric {
  storage_class: string;
  resource_count: number;
  total_size_gb: number;
  total_monthly_cost_usd: number;
}

export interface StorageResponse {
  total_storage_monthly_cost_usd: number;
  total_storage_gb: number;
  total_potential_savings_usd: number;
  s3_wrong_tier_count: number;
  ebs_over_provisioned_count: number;
  gp2_to_gp3_candidates_count: number;
  storage_class_breakdown: StorageClassMetric[];
  s3_candidates: S3LifecycleItem[];
  ebs_candidates: EbsCandidateItem[];
}

export interface TransferPathItem {
  source_service: string;
  destination_service: string;
  transfer_type: string;
  total_gb_transferred: number;
  total_cost_usd: number;
  is_wasteful: boolean;
  optimization: string;
}

export interface TransferTypeMetric {
  transfer_type: string;
  total_gb: number;
  total_cost_usd: number;
  cost_percentage: number;
}

export interface TransferResponse {
  total_transfer_cost_usd: number;
  total_transfer_gb: number;
  cross_az_cost_usd: number;
  cross_az_percentage: number;
  transfer_type_breakdown: TransferTypeMetric[];
  top_10_costliest_paths: TransferPathItem[];
  recommendations: Array<{
    priority: string;
    title: string;
    impact: string;
    estimated_monthly_savings_usd: number;
    complexity: string;
  }>;
}

export interface TagMetric {
  tag_name: string;
  is_core: boolean;
  compliance_rate_pct: number;
  compliant_resources: number;
  non_compliant_resources: number;
}

export interface TeamTagMetric {
  service_or_team: string;
  environment: string;
  total_resources: number;
  compliant_resources: number;
  compliance_rate_pct: number;
  missing_tags: string[];
}

export interface TagsResponse {
  total_resources_analyzed: number;
  overall_compliance_rate_pct: number;
  dark_spend_monthly_usd: number;
  dark_spend_percentage: number;
  mandatory_tags_metrics: TagMetric[];
  service_heatmap: TeamTagMetric[];
}

export interface AnomalyItem {
  date: string;
  service: string;
  anomaly_type: string;
  severity: string;
  sla_hours: number;
  sla_tier: string;
  expected_cost_usd: number;
  actual_cost_usd: number;
  delta_usd: number;
  delta_pct: number;
  z_score: number;
  root_cause: string;
  auto_resolved: boolean;
  ticket_id: string;
  region: string;
}

export interface AnomalySummary {
  total_anomalies: number;
  total_impact_usd: number;
  open_count: number;
  resolved_count: number;
  by_severity: Record<string, number>;
  by_type: Record<string, number>;
}

export interface AnomaliesResponse {
  threshold_pct: number;
  summary: AnomalySummary;
  anomalies: AnomalyItem[];
}

export interface WaterfallStepDetail {
  step_name: string;
  step_number: number;
  baseline_usd: number;
  savings_usd: number;
  post_savings_baseline_usd: number;
  savings_breakdown: Record<string, number>;
  active_recommendations_count: number;
}

export interface SimulatorResponse {
  initial_baseline_spend_usd: number;
  step1: WaterfallStepDetail;
  step2: WaterfallStepDetail;
  step3: WaterfallStepDetail;
  total_savings_usd: number;
  savings_pct: number;
  final_monthly_spend_usd: number;
  target_monthly_savings_usd: number;
  target_achieved: boolean;
  target_gap_usd: number;
  zero_double_counting_verified: boolean;
  verification_checks: Record<string, boolean>;
}

export interface WarRoomAction {
  action_id: string;
  title: string;
  description: string;
  immediate_savings_usd: number;
  implementation_time_days: number;
  risk_level: string;
  stakeholder_impact: string;
  compliance_approved: boolean;
}

export interface WarRoomScenario {
  id: string;
  title: string;
  urgency: string;
  description: string;
  context: string;
  primary_challenge: string;
  financial_stake_usd: number;
  stakeholder_dynamics: string;
  available_actions: WarRoomAction[];
  compliance_guardrail: string;
}

export interface WarRoomResponse {
  total_scenarios: number;
  scenarios: WarRoomScenario[];
}

export interface WarRoomActionResponse {
  scenario_id: string;
  total_savings_achieved_usd: number;
  implementation_days_total: number;
  risk_score: string;
  compliance_passed: boolean;
  cfo_approval_status: string;
  outcome_summary: string;
}
