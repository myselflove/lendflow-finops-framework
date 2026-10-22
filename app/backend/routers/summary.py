"""
summary.py — Executive KPIs, spend trends, unit economics, 90-day forecast, and RI coverage
LendFlow FinOps Platform Group
"""

from fastapi import APIRouter
from app.backend.data_loader import data_loader
from app.backend.schemas import (
    SummaryResponse, ExecutiveKpis, SpendTrendItem,
    UnitEconomics, Forecast90DayItem, RiCoverageSummary
)

router = APIRouter(prefix="/api/summary", tags=["Summary"])


@router.get("", response_model=SummaryResponse)
def get_executive_summary() -> SummaryResponse:
    # 1. Compute Waterfall Savings
    wf = data_loader.calculate_waterfall()
    baseline = wf["initial_baseline_spend_usd"]
    total_savings = wf["total_savings_usd"]
    final_spend = wf["final_monthly_spend_usd"]
    savings_pct = wf["savings_pct"]
    target_achieved = wf["target_achieved"]
    annualized_savings = round(total_savings * 12, 2)

    # Gross margin calculation
    monthly_rev = 1_000_000.0
    current_aws_margin_drag = (baseline / monthly_rev) * 100  # 18.0%
    post_aws_margin_drag = (final_spend / monthly_rev) * 100     # 7.75%
    margin_expansion = current_aws_margin_drag - post_aws_margin_drag
    projected_gross_margin = round(55.0 + margin_expansion, 2)

    kpis = ExecutiveKpis(
        baseline_monthly_spend_usd=baseline,
        projected_monthly_spend_usd=final_spend,
        total_monthly_savings_usd=total_savings,
        savings_pct=savings_pct,
        target_achieved=target_achieved,
        annualized_run_rate_savings_usd=annualized_savings,
        monthly_revenue_usd=monthly_rev,
        current_gross_margin_pct=55.0,
        projected_gross_margin_pct=projected_gross_margin,
        compliance_ring_fenced_usd=16_300.0,
    )

    # 2. Spend trend (6 months from monthly_cost_summary.csv)
    df_m = data_loader.get_df("monthly")
    trend_items = []
    month_names = {
        1: "Month 1 (Jul)", 2: "Month 2 (Aug)", 3: "Month 3 (Sep)",
        4: "Month 4 (Oct)", 5: "Month 5 (Nov)", 6: "Month 6 (Dec Baseline)"
    }
    if not df_m.empty:
        for m in sorted(df_m["month"].unique()):
            sub = df_m[df_m["month"] == m]
            tot = round(float(sub["monthly_cost_usd"].sum()), 2)
            cats = sub.groupby("category")["monthly_cost_usd"].sum().round(2).to_dict()
            trend_items.append(SpendTrendItem(
                month=int(m),
                month_name=month_names.get(int(m), f"Month {m}"),
                total_cost_usd=tot,
                categories=cats
            ))

    # 3. Unit economics for 500,000 loan applications
    volume = 500_000
    curr_cost_per_app = round(baseline / volume, 4)
    proj_cost_per_app = round(final_spend / volume, 4)
    curr_per_1k = round(curr_cost_per_app * 1000, 2)
    proj_per_1k = round(proj_cost_per_app * 1000, 2)
    savings_per_1k = round(curr_per_1k - proj_per_1k, 2)

    unit_econ = UnitEconomics(
        monthly_loan_applications=volume,
        current_cost_per_application_usd=curr_cost_per_app,
        projected_cost_per_application_usd=proj_cost_per_app,
        current_cost_per_1k_loans_usd=curr_per_1k,
        projected_cost_per_1k_loans_usd=proj_per_1k,
        savings_per_1k_loans_usd=savings_per_1k
    )

    # 4. 90-day forecast trajectory
    forecast = [
        Forecast90DayItem(
            day=0,
            month_label="Day 0 (Baseline Start)",
            unmanaged_spend_usd=180000.0,
            optimised_spend_usd=180000.0,
            cumulative_savings_usd=0.0,
            active_phase="Audit & Assessment"
        ),
        Forecast90DayItem(
            day=30,
            month_label="Day 30 (Step 1 Complete)",
            unmanaged_spend_usd=195000.0,
            optimised_spend_usd=wf["step1"]["post_savings_baseline_usd"],
            cumulative_savings_usd=wf["step1"]["savings_usd"],
            active_phase="Step 1: Eliminate Idle & Orphaned"
        ),
        Forecast90DayItem(
            day=60,
            month_label="Day 60 (Step 2 Complete)",
            unmanaged_spend_usd=210000.0,
            optimised_spend_usd=wf["step2"]["post_savings_baseline_usd"],
            cumulative_savings_usd=round(wf["step1"]["savings_usd"] + wf["step2"]["savings_usd"], 2),
            active_phase="Step 2: Right-Size Capacity"
        ),
        Forecast90DayItem(
            day=90,
            month_label="Day 90 (Step 3 Complete - Target)",
            unmanaged_spend_usd=225000.0,
            optimised_spend_usd=wf["final_monthly_spend_usd"],
            cumulative_savings_usd=total_savings,
            active_phase="Step 3: Commitments & Spot"
        ),
    ]

    # 5. RI Coverage Summary
    ri_coverage = RiCoverageSummary(
        current_effective_coverage_pct=0.0,
        target_coverage_pct=72.0,
        recommended_split={
            "Compute Savings Plans (1-Year Partial Upfront)": 40.0,
            "EC2 Instance Savings Plans (Predictable Baseline)": 12.0,
            "RDS Aurora Reserved Instances": 15.0,
            "ElastiCache Redis Reserved Nodes": 5.0
        },
        monthly_commitment_spend_usd=round(final_spend * 0.72, 2)
    )

    return SummaryResponse(
        kpis=kpis,
        spend_trend=trend_items,
        unit_economics=unit_econ,
        forecast_90_day=forecast,
        ri_coverage=ri_coverage
    )
