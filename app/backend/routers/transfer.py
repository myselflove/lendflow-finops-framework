"""
transfer.py — Data Transfer Log & Cross-AZ Waste Analysis API
LendFlow FinOps Platform Group
"""

from typing import List
from fastapi import APIRouter
from app.backend.data_loader import data_loader
from app.backend.schemas import (
    TransferResponse, TransferTypeMetric, TransferPathItem
)

router = APIRouter(prefix="/api/transfer", tags=["Transfer"])


@router.get("", response_model=TransferResponse)
def get_transfer_analysis() -> TransferResponse:
    df_t = data_loader.get_df("transfer")
    if df_t.empty:
        return TransferResponse(
            total_transfer_cost_usd=0.0,
            total_transfer_gb=0.0,
            cross_az_cost_usd=0.0,
            cross_az_percentage=0.0,
            transfer_type_breakdown=[],
            top_10_costliest_paths=[],
            recommendations=[]
        )

    total_cost = round(float(df_t["cost_usd"].sum()), 2)
    total_gb = round(float(df_t["gb_transferred"].sum()), 2)

    # 1. Transfer type breakdown
    type_metrics: List[TransferTypeMetric] = []
    t_grp = df_t.groupby("transfer_type").agg(
        tot_gb=("gb_transferred", "sum"),
        tot_cost=("cost_usd", "sum")
    ).reset_index().sort_values(by="tot_cost", ascending=False)

    cross_az_cost = 0.0
    for _, r in t_grp.iterrows():
        c_val = round(float(r["tot_cost"]), 2)
        pct = round((c_val / total_cost) * 100, 1) if total_cost > 0 else 0.0
        ttype = str(r["transfer_type"])
        if ttype == "CROSS_AZ":
            cross_az_cost = c_val
        type_metrics.append(TransferTypeMetric(
            transfer_type=ttype,
            total_gb=round(float(r["tot_gb"]), 1),
            total_cost_usd=c_val,
            cost_percentage=pct
        ))

    cross_az_pct = round((cross_az_cost / total_cost) * 100, 1) if total_cost > 0 else 0.0

    # 2. Top 10 costliest paths (grouped by source and destination)
    path_grp = df_t.groupby(["source_service", "destination_service", "transfer_type", "optimization", "is_wasteful"]).agg(
        tot_gb=("gb_transferred", "sum"),
        tot_cost=("cost_usd", "sum")
    ).reset_index().sort_values(by="tot_cost", ascending=False).head(10)

    top_paths: List[TransferPathItem] = []
    for _, r in path_grp.iterrows():
        top_paths.append(TransferPathItem(
            source_service=str(r["source_service"]),
            destination_service=str(r["destination_service"]),
            transfer_type=str(r["transfer_type"]),
            total_gb_transferred=round(float(r["tot_gb"]), 2),
            total_cost_usd=round(float(r["tot_cost"]), 2),
            is_wasteful=bool(r["is_wasteful"]),
            optimization=str(r["optimization"])
        ))

    # 3. Actionable recommendations
    recommendations = [
        {
            "priority": "HIGH",
            "title": "Enable S3 Gateway VPC Endpoint",
            "impact": "Eliminate 100% of NAT data processing charges for S3 traffic from EKS worker nodes",
            "estimated_monthly_savings_usd": 1200.0,
            "complexity": "LOW"
        },
        {
            "priority": "HIGH",
            "title": "Same-AZ Colocation for High-Throughput Microservice Pairs",
            "impact": "Re-route lendflow-ingestion -> lendflow-credit-scoring traffic within same AZ to reduce cross-AZ transfer charges",
            "estimated_monthly_savings_usd": 850.0,
            "complexity": "MEDIUM"
        },
        {
            "priority": "MEDIUM",
            "title": "CloudFront Origin Shield for Static Asset Ingestion",
            "impact": "Reduce direct S3 internet egress costs by caching API schemas and document verification tokens at edge",
            "estimated_monthly_savings_usd": 400.0,
            "complexity": "LOW"
        }
    ]

    return TransferResponse(
        total_transfer_cost_usd=total_cost,
        total_transfer_gb=total_gb,
        cross_az_cost_usd=cross_az_cost,
        cross_az_percentage=cross_az_pct,
        transfer_type_breakdown=type_metrics,
        top_10_costliest_paths=top_paths,
        recommendations=recommendations
    )
