"""
optimisations.py — 18 Prioritised FinOps Optimisation Recommendations
LendFlow FinOps Platform Group

Provides the 18 recommendations across Compute, DB, Storage, Data Transfer, RI/SP, Spot,
with explicit compliance ring-fences for PCI DSS v4.0, SOC 2 Type II, RBI IT, and GDPR.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
from app.backend.data_loader import data_loader
from app.backend.schemas import (
    OptimisationsResponse, OptimisationItem, ComplianceLock
)

router = APIRouter(prefix="/api/optimisations", tags=["Optimisations"])


@router.get("", response_model=OptimisationsResponse)
def get_optimisations(
    phase: Optional[str] = Query(None, description="Filter by phase: 'Step 1', 'Step 2', or 'Step 3'"),
    category: Optional[str] = Query(None, description="Filter by category (Compute, Storage, Database, etc.)"),
    effort: Optional[str] = Query(None, description="Filter by effort (LOW, MEDIUM, HIGH)")
) -> OptimisationsResponse:
    catalog = data_loader.get_recommendations_catalog()
    compliance_locks_raw = data_loader.get_compliance_locks()

    compliance_locks = [ComplianceLock(**cl) for cl in compliance_locks_raw]

    # Convert to schema items
    items: List[OptimisationItem] = []
    for r in catalog:
        # Determine compliance lock
        is_locked = False
        if "PCI_EXCLUDED" in r["compliance_impact"]:
            is_locked = True
        elif "SOC2_SAFE" in r["compliance_impact"]:
            is_locked = True
        elif "RBI_SAFE" in r["compliance_impact"]:
            is_locked = True

        items.append(OptimisationItem(
            id=r["id"],
            rank=r["rank"],
            phase=r["phase"],
            appendix_a=r["appendix_a"],
            category=r["category"],
            title=r["title"],
            action=r["action"],
            estimated_monthly_savings_usd=r["base_savings_usd"],
            effort=r["effort"],
            risk=r["risk"],
            compliance_impact=r["compliance_impact"],
            compliance_locked=is_locked,
            implementation_days=r["implementation_days"],
            payback_days=r["payback_days"],
            status="RECOMMENDED"
        ))

    # Apply filters
    filtered_items = items
    if phase is not None:
        filtered_items = [i for i in filtered_items if phase.lower() in i.phase.lower()]
    if category is not None:
        filtered_items = [i for i in filtered_items if i.category.lower() == category.lower()]
    if effort is not None:
        filtered_items = [i for i in filtered_items if i.effort.lower() == effort.lower()]

    total_savings = round(sum(i.estimated_monthly_savings_usd for i in items), 2)

    by_phase = {
        "Step 1 — Eliminate": len([i for i in items if "Step 1" in i.phase]),
        "Step 2 — Right-Size": len([i for i in items if "Step 2" in i.phase]),
        "Step 3 — Commitments": len([i for i in items if "Step 3" in i.phase]),
    }

    by_effort = {
        "LOW": len([i for i in items if i.effort == "LOW"]),
        "MEDIUM": len([i for i in items if i.effort == "MEDIUM"]),
        "HIGH": len([i for i in items if i.effort == "HIGH"]),
    }

    return OptimisationsResponse(
        total_recommendations=len(filtered_items),
        total_estimated_monthly_savings_usd=total_savings,
        recommendations_by_phase=by_phase,
        recommendations_by_effort=by_effort,
        compliance_locks=compliance_locks,
        recommendations=filtered_items
    )
