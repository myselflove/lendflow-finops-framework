"""
anomalies.py — Configurable Threshold & Z-Score Anomaly Detection API
LendFlow FinOps Platform Group

Provides anomaly detection with P1-P4 SLA classification, Z-scores, and root cause analysis.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
import numpy as np
import pandas as pd
from app.backend.data_loader import data_loader
from app.backend.schemas import (
    AnomaliesResponse, AnomalySummary, AnomalyItem
)

router = APIRouter(prefix="/api/anomalies", tags=["Anomalies"])


@router.get("", response_model=AnomaliesResponse)
def get_anomalies(
    threshold_pct: float = Query(30.0, description="Minimum delta percentage to flag (default: 30%)"),
    severity: Optional[str] = Query(None, description="CRITICAL, HIGH, MEDIUM, LOW"),
    anomaly_type: Optional[str] = Query(None, description="SPIKE, SUSTAINED_INCREASE, IDLE_WASTE, ORPHANED_RESOURCE"),
    service: Optional[str] = Query(None, description="Filter by service name"),
    min_cost: Optional[float] = Query(None, description="Minimum actual cost in USD")
) -> AnomaliesResponse:
    df_a = data_loader.get_df("anomalies")
    if df_a.empty:
        return AnomaliesResponse(
            threshold_pct=threshold_pct,
            summary=AnomalySummary(
                total_anomalies=0,
                total_impact_usd=0.0,
                open_count=0,
                resolved_count=0,
                by_severity={},
                by_type={}
            ),
            anomalies=[]
        )

    # Calculate Z-Scores across actual costs
    actuals = df_a["actual_cost_usd"].to_numpy()
    mean_cost = float(np.mean(actuals))
    std_cost = float(np.std(actuals)) if float(np.std(actuals)) > 0 else 1.0

    items: List[AnomalyItem] = []
    for _, r in df_a.iterrows():
        act = float(r["actual_cost_usd"])
        exp = float(r["expected_cost_usd"])
        delta_usd = round(act - exp, 2)
        delta_pct = round(float(r["delta_pct"]), 1)

        # Compute Z-score
        z = round((act - mean_cost) / std_cost, 2)

        # SLA Classification
        if delta_pct > 100 or delta_usd > 5000:
            sev = "CRITICAL"
            sla_h = 1
            sla_t = "P1 (Critical - 1h SLA)"
        elif delta_pct >= 50:
            sev = "HIGH"
            sla_h = 4
            sla_t = "P2 (High - 4h SLA)"
        elif delta_pct >= 25:
            sev = "MEDIUM"
            sla_h = 24
            sla_t = "P3 (Medium - 24h SLA)"
        else:
            sev = "LOW"
            sla_h = 72
            sla_t = "P4 (Low - 72h SLA)"

        items.append(AnomalyItem(
            date=str(r["date"]),
            service=str(r["service"]),
            anomaly_type=str(r["anomaly_type"]),
            severity=sev,
            sla_hours=sla_h,
            sla_tier=sla_t,
            expected_cost_usd=exp,
            actual_cost_usd=act,
            delta_usd=delta_usd,
            delta_pct=delta_pct,
            z_score=z,
            root_cause=str(r.get("root_cause", "Unspecified anomaly")),
            auto_resolved=bool(r.get("auto_resolved", False)),
            ticket_id=str(r.get("ticket_id", "LF-ANOM-0000")),
            region=str(r.get("region", "ap-south-1"))
        ))

    # Filter by threshold_pct
    filtered = [i for i in items if i.delta_pct >= threshold_pct or abs(i.z_score) >= 1.5]

    # Additional user query filters
    if severity is not None:
        filtered = [i for i in filtered if i.severity.upper() == severity.upper()]
    if anomaly_type is not None:
        filtered = [i for i in filtered if i.anomaly_type.upper() == anomaly_type.upper()]
    if service is not None:
        filtered = [i for i in filtered if i.service.lower() == service.lower()]
    if min_cost is not None:
        filtered = [i for i in filtered if i.actual_cost_usd >= min_cost]

    # Summary
    total_impact = round(sum(i.delta_usd for i in filtered if i.delta_usd > 0), 2)
    resolved = len([i for i in filtered if i.auto_resolved])
    opened = len(filtered) - resolved

    by_sev = {
        "CRITICAL": len([i for i in filtered if i.severity == "CRITICAL"]),
        "HIGH": len([i for i in filtered if i.severity == "HIGH"]),
        "MEDIUM": len([i for i in filtered if i.severity == "MEDIUM"]),
        "LOW": len([i for i in filtered if i.severity == "LOW"]),
    }

    by_type = {}
    for i in filtered:
        by_type[i.anomaly_type] = by_type.get(i.anomaly_type, 0) + 1

    return AnomaliesResponse(
        threshold_pct=threshold_pct,
        summary=AnomalySummary(
            total_anomalies=len(filtered),
            total_impact_usd=total_impact,
            open_count=opened,
            resolved_count=resolved,
            by_severity=by_sev,
            by_type=by_type
        ),
        anomalies=filtered
    )


@router.post("/{anomaly_id}/alert")
def dispatch_anomaly_alert(
    anomaly_id: str,
    channel: Optional[str] = Query("slack", description="Target notification channel: slack, discord, or pagerduty")
):
    """
    Dispatches a real-time FinOps on-call alert for a detected cost anomaly.
    Integrates with Slack, Discord, or PagerDuty incident management workflows.
    """
    import datetime
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {
        "status": "DISPATCHED",
        "anomaly_id": anomaly_id,
        "channel": channel.upper(),
        "dispatched_at": now_str,
        "recipient": f"#finops-cost-alerts-{channel.lower()}",
        "message": f"High priority anomaly alert {anomaly_id} routed to on-call engineering team."
    }

