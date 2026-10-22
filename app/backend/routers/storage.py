"""
storage.py — S3 and EBS Storage Inventory & Lifecycle Optimisation API
LendFlow FinOps Platform Group
"""

from typing import List
from fastapi import APIRouter
from app.backend.data_loader import data_loader
from app.backend.schemas import (
    StorageResponse, StorageClassMetric, S3LifecycleItem, EbsCandidateItem
)

router = APIRouter(prefix="/api/storage", tags=["Storage"])


@router.get("", response_model=StorageResponse)
def get_storage_analysis() -> StorageResponse:
    df_s = data_loader.get_df("storage")
    if df_s.empty:
        return StorageResponse(
            total_storage_monthly_cost_usd=0.0,
            total_storage_gb=0.0,
            total_potential_savings_usd=0.0,
            s3_wrong_tier_count=0,
            ebs_over_provisioned_count=0,
            gp2_to_gp3_candidates_count=0,
            storage_class_breakdown=[],
            s3_candidates=[],
            ebs_candidates=[]
        )

    total_cost = round(float(df_s["monthly_cost_usd"].sum()), 2)
    total_gb = round(float(df_s["size_gb"].sum()), 2)

    # 1. Storage class metrics
    class_metrics: List[StorageClassMetric] = []
    grp = df_s.groupby("storage_class").agg(
        cnt=("resource_id", "count"),
        tot_gb=("size_gb", "sum"),
        tot_cost=("monthly_cost_usd", "sum")
    ).reset_index().sort_values(by="tot_cost", ascending=False)

    for _, r in grp.iterrows():
        class_metrics.append(StorageClassMetric(
            storage_class=str(r["storage_class"]),
            resource_count=int(r["cnt"]),
            total_size_gb=round(float(r["tot_gb"]), 1),
            total_monthly_cost_usd=round(float(r["tot_cost"]), 2)
        ))

    # 2. S3 Candidates (STANDARD > 90 days)
    s3_df = df_s[df_s["resource_type"] == "S3_BUCKET"]
    s3_waste = s3_df[s3_df["lifecycle_status"] == "WASTE_WRONG_TIER"]

    s3_candidates: List[S3LifecycleItem] = []
    s3_savings_total = 0.0
    for _, r in s3_waste.iterrows():
        cur_cost = float(r["monthly_cost_usd"])
        # Standard ($0.023) -> Glacier ($0.004) or Standard-IA ($0.0125) => ~55-80% savings
        proj_cost = round(cur_cost * 0.35, 2)
        save = round(cur_cost - proj_cost, 2)
        s3_savings_total += save
        s3_candidates.append(S3LifecycleItem(
            resource_id=str(r["resource_id"]),
            service=str(r["service"]),
            environment=str(r["environment"]),
            size_gb=round(float(r["size_gb"]), 1),
            current_storage_class=str(r["storage_class"]),
            target_storage_class="GLACIER" if int(r.get("days_since_access", 0)) > 180 else "STANDARD_IA",
            days_since_access=int(r.get("days_since_access", 0)),
            current_monthly_cost_usd=cur_cost,
            projected_monthly_cost_usd=proj_cost,
            monthly_savings_usd=save,
            lifecycle_status=str(r["lifecycle_status"])
        ))

    # 3. EBS Candidates (Over-provisioned + gp2->gp3)
    ebs_df = df_s[df_s["resource_type"] == "EBS_VOLUME"]
    ebs_waste = ebs_df[
        (ebs_df["lifecycle_status"] == "WASTE_OVER_PROVISIONED") |
        (ebs_df["storage_class"] == "gp2")
    ]

    ebs_candidates: List[EbsCandidateItem] = []
    ebs_savings_total = 0.0
    for _, r in ebs_waste.head(50).iterrows():
        cur_cost = float(r["monthly_cost_usd"])
        sc = str(r["storage_class"])
        is_over_prov = r["lifecycle_status"] == "WASTE_OVER_PROVISIONED"
        if is_over_prov:
            # Downsize provisioned volume by 50%
            save = round(cur_cost * 0.50, 2)
            rec = "DOWNSIZE_VOLUME_TO_250GB"
        else:
            # gp2 to gp3 is 20% cheaper
            save = round(cur_cost * 0.20, 2)
            rec = "MIGRATE_GP2_TO_GP3"
        ebs_savings_total += save
        ebs_candidates.append(EbsCandidateItem(
            resource_id=str(r["resource_id"]),
            service=str(r["service"]),
            environment=str(r["environment"]),
            size_gb=round(float(r["size_gb"]), 1),
            size_used_gb=round(float(r.get("size_used_gb", 0)), 1),
            wasted_pct=round(float(r.get("wasted_pct", 0)), 1),
            storage_class=sc,
            current_monthly_cost_usd=cur_cost,
            monthly_savings_usd=save,
            recommendation=rec
        ))

    gp2_count = int((ebs_df["storage_class"] == "gp2").sum())
    total_pot_savings = round(s3_savings_total + ebs_savings_total, 2)

    return StorageResponse(
        total_storage_monthly_cost_usd=total_cost,
        total_storage_gb=total_gb,
        total_potential_savings_usd=total_pot_savings,
        s3_wrong_tier_count=len(s3_candidates),
        ebs_over_provisioned_count=int((ebs_df["lifecycle_status"] == "WASTE_OVER_PROVISIONED").sum()),
        gp2_to_gp3_candidates_count=gp2_count,
        storage_class_breakdown=class_metrics,
        s3_candidates=s3_candidates[:30],
        ebs_candidates=ebs_candidates[:30]
    )
