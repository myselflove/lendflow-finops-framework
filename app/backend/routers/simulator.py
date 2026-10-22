"""
simulator.py — Interactive Non-Overlapping Waterfall Savings Calculator API
LendFlow FinOps Platform Group

Enables dynamic toggle of recommendations while strictly adhering to the
Stage 1 -> Stage 2 -> Stage 3 sequential baseline recalculation (zero double-counting).
"""

from typing import Optional
from fastapi import APIRouter
from app.backend.data_loader import data_loader
from app.backend.schemas import (
    SimulatorRequest, SimulatorResponse, WaterfallStepDetail
)

router = APIRouter(prefix="/api/simulator", tags=["Simulator"])


def _build_simulator_response(wf: dict) -> SimulatorResponse:
    s1 = WaterfallStepDetail(**wf["step1"])
    s2 = WaterfallStepDetail(**wf["step2"])
    s3 = WaterfallStepDetail(**wf["step3"])

    return SimulatorResponse(
        initial_baseline_spend_usd=wf["initial_baseline_spend_usd"],
        step1=s1,
        step2=s2,
        step3=s3,
        total_savings_usd=wf["total_savings_usd"],
        savings_pct=wf["savings_pct"],
        final_monthly_spend_usd=wf["final_monthly_spend_usd"],
        target_monthly_savings_usd=wf["target_monthly_savings_usd"],
        target_achieved=wf["target_achieved"],
        target_gap_usd=wf["target_gap_usd"],
        zero_double_counting_verified=wf["zero_double_counting_verified"],
        verification_checks=wf["verification_checks"]
    )


@router.get("", response_model=SimulatorResponse)
def get_default_simulator_state() -> SimulatorResponse:
    """Returns baseline simulator state with all 18 recommendations enabled."""
    wf = data_loader.calculate_waterfall(enabled_ids=None)
    return _build_simulator_response(wf)


@router.post("", response_model=SimulatorResponse)
def simulate_savings(payload: SimulatorRequest) -> SimulatorResponse:
    """
    Recalculates the waterfall based on custom active recommendation IDs.
    Guarantees sequential Step 1 -> Step 2 -> Step 3 baselining without double-counting.
    """
    wf = data_loader.calculate_waterfall(enabled_ids=payload.enabled_recommendation_ids)
    return _build_simulator_response(wf)
