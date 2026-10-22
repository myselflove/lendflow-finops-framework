"""
explorer.py — Filterable Cost Explorer API
LendFlow FinOps Platform Group

Supports filtering by month, service, environment, team, region, cost_centre, compliance_scope.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
import pandas as pd
from app.backend.data_loader import data_loader
from app.backend.schemas import (
    ExplorerResponse, GroupedCostItem, DailyCostItem, CostRecord
)

router = APIRouter(prefix="/api/explorer", tags=["Explorer"])

# Compliance scope mapping to services
COMPLIANCE_SERVICE_MAP = {
    "pci-dss": ["lendflow-payments"],
    "soc2": ["lendflow-audit", "lendflow-ledger", "lendflow-auth", "lendflow-analytics"],
    "rbi-it": ["lendflow-ingestion", "lendflow-credit-scoring", "lendflow-underwriting",
               "lendflow-ledger", "lendflow-doc-verify", "lendflow-collections"],
    "gdpr": ["lendflow-ingestion", "lendflow-auth", "lendflow-doc-verify", "lendflow-notifications"],
}

# Team mapping by service
SERVICE_TEAM_MAP = {
    "lendflow-gateway": "Core Infrastructure",
    "lendflow-auth": "Security & Identity",
    "lendflow-ingestion": "Data Platform",
    "lendflow-credit-scoring": "Data Science & Risk",
    "lendflow-underwriting": "Lending Operations",
    "lendflow-doc-verify": "Identity & KYC",
    "lendflow-payments": "Payments Engineering",
    "lendflow-ledger": "Core Financials",
    "lendflow-notifications": "Customer Engagement",
    "lendflow-analytics": "BI & Analytics",
    "lendflow-audit": "Governance & Compliance",
    "lendflow-collections": "Servicing & Recovery",
}


@router.get("", response_model=ExplorerResponse)
def query_cost_explorer(
    month: Optional[int] = Query(None, description="Month number 1 to 6"),
    service: Optional[str] = Query(None, description="Filter by service name"),
    environment: Optional[str] = Query(None, description="production, staging, development"),
    team: Optional[str] = Query(None, description="Filter by owning team"),
    region: Optional[str] = Query(None, description="AWS Region (ap-south-1, eu-west-1, eu-central-1)"),
    cost_centre: Optional[str] = Query(None, description="Cost center filter"),
    compliance_scope: Optional[str] = Query(None, description="pci-dss, soc2, rbi-it, gdpr"),
    resource_type: Optional[str] = Query(None, description="EC2, RDS, EKS_NODE, S3, EBS, etc."),
    group_by: str = Query("service", description="Field to aggregate by (service, environment, region, resource_type, month)"),
    limit: int = Query(50, ge=1, le=500, description="Max sample records to return")
) -> ExplorerResponse:
    df = data_loader.get_df("daily").copy()
    if df.empty:
        return ExplorerResponse(
            total_spend_usd=0.0,
            total_records=0,
            filtered_records_count=0,
            group_by=group_by,
            grouped_data=[],
            daily_trend=[],
            sample_records=[]
        )

    total_records = len(df)

    # 1. Parse date for month filtering
    df["date_dt"] = pd.to_datetime(df["date"])
    # July = Month 1, Dec = Month 6
    df["month_num"] = df["date_dt"].dt.month.map({
        7: 1, 8: 2, 9: 3, 10: 4, 11: 5, 12: 6
    }).fillna(1).astype(int)

    # 2. Add Team column
    df["team"] = df["service"].map(SERVICE_TEAM_MAP).fillna("Engineering")

    # 3. Apply Filters
    if month is not None:
        df = df[df["month_num"] == month]
    if service is not None:
        df = df[df["service"].str.lower() == service.lower()]
    if environment is not None:
        df = df[df["environment"].str.lower() == environment.lower()]
    if team is not None:
        df = df[df["team"].str.lower() == team.lower()]
    if region is not None:
        df = df[df["region"].str.lower() == region.lower()]
    if resource_type is not None:
        df = df[df["resource_type"].str.upper() == resource_type.upper()]
    if compliance_scope is not None:
        target_services = COMPLIANCE_SERVICE_MAP.get(compliance_scope.lower(), [])
        df = df[df["service"].isin(target_services)]
    if cost_centre is not None:
        # Check in tags string or default
        df = df[df["tags"].str.contains(cost_centre, case=False, na=False)]

    filtered_count = len(df)
    total_spend = round(float(df["cost"].sum()), 2)

    # 4. Grouped Aggregation
    agg_field = group_by if group_by in df.columns else "service"
    grouped_rows: List[GroupedCostItem] = []
    if not df.empty:
        grp = df.groupby(agg_field).agg(
            total_cost=("cost", "sum"),
            res_count=("resource_id", "nunique")
        ).reset_index().sort_values(by="total_cost", ascending=False)

        for _, row in grp.iterrows():
            c_val = round(float(row["total_cost"]), 2)
            pct = round((c_val / total_spend) * 100, 1) if total_spend > 0 else 0.0
            grouped_rows.append(GroupedCostItem(
                name=str(row[agg_field]),
                total_cost_usd=c_val,
                percentage=pct,
                resource_count=int(row["res_count"])
            ))

    # 5. Daily Trend
    daily_trend: List[DailyCostItem] = []
    if not df.empty:
        d_grp = df.groupby("date")["cost"].sum().reset_index().sort_values(by="date")
        for _, r in d_grp.iterrows():
            daily_trend.append(DailyCostItem(
                date=str(r["date"]),
                total_cost_usd=round(float(r["cost"]), 2)
            ))

    # 6. Sample Records
    sample_records: List[CostRecord] = []
    for _, r in df.head(limit).iterrows():
        sample_records.append(CostRecord(
            date=str(r["date"]),
            service=str(r["service"]),
            resource_type=str(r["resource_type"]),
            resource_id=str(r["resource_id"]),
            cost=round(float(r["cost"]), 4),
            environment=str(r["environment"]),
            region=str(r["region"]),
            az=str(r.get("az", "")),
            tags=str(r.get("tags", ""))
        ))

    return ExplorerResponse(
        total_spend_usd=total_spend,
        total_records=total_records,
        filtered_records_count=filtered_count,
        group_by=agg_field,
        grouped_data=grouped_rows,
        daily_trend=daily_trend,
        sample_records=sample_records
    )
