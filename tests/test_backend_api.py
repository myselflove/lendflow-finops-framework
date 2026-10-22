"""
tests/test_backend_api.py — LendFlow FinOps Backend API Test Suite
LendFlow FinOps Platform Group

Validates all 8 endpoints, compliance isolation blocks, and simulator zero double-counting math.
Uses pytest and FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from app.backend.main import app

client = TestClient(app)


# ==============================================================================
# 1. Health & Root Endpoints
# ==============================================================================

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"
    assert "endpoints" in data
    assert data["endpoints"]["summary"] == "/api/summary"
    assert data["endpoints"]["simulator"] == "/api/simulator"
    assert data["endpoints"]["war_room"] == "/api/war-room"


def test_health_endpoints():
    for path in ["/health", "/api/health"]:
        res = client.get(path)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "HEALTHY"
        assert data["region"] == "ap-south-1"


# ==============================================================================
# 2. Executive Summary (/api/summary)
# ==============================================================================

def test_summary_kpis():
    res = client.get("/api/summary")
    assert res.status_code == 200
    data = res.json()
    kpis = data["kpis"]

    assert kpis["baseline_monthly_spend_usd"] == 180_000.0
    assert kpis["total_monthly_savings_usd"] >= 60_000.0
    assert kpis["projected_monthly_spend_usd"] <= 120_000.0
    assert kpis["savings_pct"] >= 33.3
    assert kpis["target_achieved"] is True
    assert kpis["annualized_run_rate_savings_usd"] == round(kpis["total_monthly_savings_usd"] * 12, 2)
    assert kpis["compliance_ring_fenced_usd"] == 16_300.0
    assert kpis["current_gross_margin_pct"] == 55.0
    assert kpis["projected_gross_margin_pct"] > 55.0


def test_summary_unit_economics():
    res = client.get("/api/summary")
    assert res.status_code == 200
    unit = res.json()["unit_economics"]

    assert unit["monthly_loan_applications"] == 500_000
    assert unit["current_cost_per_application_usd"] == 0.36
    assert unit["current_cost_per_1k_loans_usd"] == 360.00
    assert unit["projected_cost_per_1k_loans_usd"] < 200.0
    assert unit["savings_per_1k_loans_usd"] > 100.0


def test_summary_spend_trend():
    res = client.get("/api/summary")
    assert res.status_code == 200
    trend = res.json()["spend_trend"]

    assert len(trend) == 6
    # Month 1 < Month 6
    assert trend[0]["total_cost_usd"] < trend[-1]["total_cost_usd"]
    assert abs(trend[-1]["total_cost_usd"] - 180_000.0) < 500.0


def test_summary_forecast_90_day():
    res = client.get("/api/summary")
    assert res.status_code == 200
    forecast = res.json()["forecast_90_day"]

    assert len(forecast) == 4
    days = [f["day"] for f in forecast]
    assert days == [0, 30, 60, 90]
    # Unmanaged spend increases over time
    assert forecast[0]["unmanaged_spend_usd"] < forecast[-1]["unmanaged_spend_usd"]
    # Optimised spend decreases over time
    assert forecast[0]["optimised_spend_usd"] > forecast[-1]["optimised_spend_usd"]


def test_summary_ri_coverage():
    res = client.get("/api/summary")
    assert res.status_code == 200
    ri = res.json()["ri_coverage"]

    assert ri["current_effective_coverage_pct"] == 0.0
    assert ri["target_coverage_pct"] == 72.0
    assert len(ri["recommended_split"]) >= 3


# ==============================================================================
# 3. Cost Explorer (/api/explorer)
# ==============================================================================

def test_explorer_unfiltered():
    res = client.get("/api/explorer")
    assert res.status_code == 200
    data = res.json()

    assert data["total_records"] == 10_800
    assert data["filtered_records_count"] == 10_800
    assert data["total_spend_usd"] > 0
    assert len(data["grouped_data"]) > 0
    assert len(data["daily_trend"]) == 180
    assert len(data["sample_records"]) > 0


def test_explorer_filter_service():
    res = client.get("/api/explorer?service=lendflow-payments")
    assert res.status_code == 200
    data = res.json()

    assert data["filtered_records_count"] > 0
    assert data["filtered_records_count"] < 10_800
    for rec in data["sample_records"]:
        assert rec["service"] == "lendflow-payments"


def test_explorer_filter_environment():
    res_prod = client.get("/api/explorer?environment=production")
    res_dev = client.get("/api/explorer?environment=development")

    assert res_prod.status_code == 200
    assert res_dev.status_code == 200
    # Prod should cost more than dev
    assert res_prod.json()["total_spend_usd"] > res_dev.json()["total_spend_usd"]


def test_explorer_filter_compliance_scope():
    res = client.get("/api/explorer?compliance_scope=pci-dss")
    assert res.status_code == 200
    data = res.json()

    for rec in data["sample_records"]:
        assert rec["service"] == "lendflow-payments"


def test_explorer_group_by():
    res = client.get("/api/explorer?group_by=environment")
    assert res.status_code == 200
    data = res.json()

    envs = [g["name"] for g in data["grouped_data"]]
    assert "production" in envs
    assert "staging" in envs
    assert "development" in envs


# ==============================================================================
# 4. Optimisations (/api/optimisations)
# ==============================================================================

def test_optimisations_total_count():
    res = client.get("/api/optimisations")
    assert res.status_code == 200
    data = res.json()

    assert data["total_recommendations"] == 18
    assert len(data["recommendations"]) == 18
    assert data["total_estimated_monthly_savings_usd"] > 60_000.0


def test_optimisations_phases_represented():
    res = client.get("/api/optimisations")
    assert res.status_code == 200
    data = res.json()

    phases = data["recommendations_by_phase"]
    assert phases["Step 1 — Eliminate"] == 6
    assert phases["Step 2 — Right-Size"] == 7
    assert phases["Step 3 — Commitments"] == 5


def test_optimisations_compliance_locks():
    res = client.get("/api/optimisations")
    assert res.status_code == 200
    locks = res.json()["compliance_locks"]

    frameworks = [l["framework"] for l in locks]
    assert any("PCI DSS" in f for f in frameworks)
    assert any("SOC 2" in f for f in frameworks)
    assert any("RBI IT" in f for f in frameworks)
    assert any("GDPR" in f for f in frameworks)


def test_optimisations_phase_filter():
    res = client.get("/api/optimisations?phase=Step 1")
    assert res.status_code == 200
    data = res.json()

    assert data["total_recommendations"] == 6
    for r in data["recommendations"]:
        assert "Step 1" in r["phase"]


# ==============================================================================
# 5. Storage & Transfer (/api/storage, /api/transfer)
# ==============================================================================

def test_storage_endpoint():
    res = client.get("/api/storage")
    assert res.status_code == 200
    data = res.json()

    assert data["total_storage_monthly_cost_usd"] > 0
    assert data["total_storage_gb"] > 0
    assert data["total_potential_savings_usd"] > 0
    assert data["s3_wrong_tier_count"] > 0
    assert data["gp2_to_gp3_candidates_count"] > 0
    assert len(data["storage_class_breakdown"]) > 0
    assert len(data["s3_candidates"]) > 0
    assert len(data["ebs_candidates"]) > 0


def test_transfer_endpoint():
    res = client.get("/api/transfer")
    assert res.status_code == 200
    data = res.json()

    assert data["total_transfer_cost_usd"] > 0
    assert data["total_transfer_gb"] > 0
    assert data["cross_az_cost_usd"] > 0
    assert data["cross_az_percentage"] > 25.0
    assert len(data["top_10_costliest_paths"]) == 10
    assert len(data["recommendations"]) >= 3


# ==============================================================================
# 6. Tag Compliance (/api/tags)
# ==============================================================================

def test_tags_endpoint():
    res = client.get("/api/tags")
    assert res.status_code == 200
    data = res.json()

    assert data["total_resources_analyzed"] == 1500
    assert 60.0 <= data["overall_compliance_rate_pct"] <= 90.0
    assert data["dark_spend_monthly_usd"] > 0
    assert len(data["mandatory_tags_metrics"]) == 10
    core_tags = [t["tag_name"] for t in data["mandatory_tags_metrics"] if t["is_core"]]
    assert set(core_tags) == {"CostCenter", "Environment", "Service", "Owner", "ComplianceScope"}
    assert len(data["service_heatmap"]) > 0


# ==============================================================================
# 7. Cost Anomalies (/api/anomalies)
# ==============================================================================

def test_anomalies_endpoint():
    res = client.get("/api/anomalies")
    assert res.status_code == 200
    data = res.json()

    assert data["summary"]["total_anomalies"] > 0
    assert data["summary"]["total_impact_usd"] > 0
    for anom in data["anomalies"]:
        assert anom["sla_tier"] in [
            "P1 (Critical - 1h SLA)",
            "P2 (High - 4h SLA)",
            "P3 (Medium - 24h SLA)",
            "P4 (Low - 72h SLA)"
        ]
        assert "z_score" in anom


def test_anomalies_threshold_filter():
    res_low = client.get("/api/anomalies?threshold_pct=10.0")
    res_high = client.get("/api/anomalies?threshold_pct=100.0")

    assert res_low.status_code == 200
    assert res_high.status_code == 200
    assert res_low.json()["summary"]["total_anomalies"] >= res_high.json()["summary"]["total_anomalies"]


# ==============================================================================
# 8. Interactive Simulator (/api/simulator)
# ==============================================================================

def test_simulator_default_all_enabled():
    res = client.get("/api/simulator")
    assert res.status_code == 200
    data = res.json()

    assert data["initial_baseline_spend_usd"] == 180_000.0
    assert data["total_savings_usd"] >= 60_000.0
    assert data["final_monthly_spend_usd"] <= 120_000.0
    assert data["target_achieved"] is True
    assert data["zero_double_counting_verified"] is True
    assert all(data["verification_checks"].values())


def test_simulator_zero_double_counting_contract():
    res = client.post("/api/simulator", json={"enabled_recommendation_ids": list(range(1, 19))})
    assert res.status_code == 200
    data = res.json()

    # Step 1: baseline = $180,000
    assert data["step1"]["baseline_usd"] == 180_000.0
    s1_post = data["step1"]["post_savings_baseline_usd"]
    assert s1_post == round(180_000.0 - data["step1"]["savings_usd"], 2)

    # Step 2: baseline strictly equals Step 1 post-savings baseline
    assert data["step2"]["baseline_usd"] == s1_post
    s2_post = data["step2"]["post_savings_baseline_usd"]
    assert s2_post == round(s1_post - data["step2"]["savings_usd"], 2)

    # Step 3: baseline strictly equals Step 2 post-savings baseline
    assert data["step3"]["baseline_usd"] == s2_post
    s3_post = data["step3"]["post_savings_baseline_usd"]
    assert s3_post == round(s2_post - data["step3"]["savings_usd"], 2)

    # Final spend matches
    assert data["final_monthly_spend_usd"] == s3_post
    total_savings_sum = round(
        data["step1"]["savings_usd"] + data["step2"]["savings_usd"] + data["step3"]["savings_usd"], 2
    )
    assert data["total_savings_usd"] == total_savings_sum


def test_simulator_partial_enabled():
    # Only enable Step 1 recommendations (IDs 1-6)
    res = client.post("/api/simulator", json={"enabled_recommendation_ids": [1, 2, 3, 4, 5, 6]})
    assert res.status_code == 200
    data = res.json()

    assert data["step1"]["savings_usd"] > 0
    assert data["step2"]["savings_usd"] == 0.0
    assert data["step3"]["savings_usd"] == 0.0
    assert data["total_savings_usd"] == data["step1"]["savings_usd"]
    assert data["zero_double_counting_verified"] is True


def test_simulator_none_enabled():
    res = client.post("/api/simulator", json={"enabled_recommendation_ids": []})
    assert res.status_code == 200
    data = res.json()

    assert data["total_savings_usd"] == 0.0
    assert data["final_monthly_spend_usd"] == 180_000.0
    assert data["target_achieved"] is False
    assert data["target_gap_usd"] == 60_000.0


# ==============================================================================
# 9. FinOps War Room (/api/war-room)
# ==============================================================================

def test_war_room_scenarios():
    res = client.get("/api/war-room")
    assert res.status_code == 200
    data = res.json()

    assert data["total_scenarios"] == 4
    scenario_ids = [s["id"] for s in data["scenarios"]]
    assert "cfo-90-day-ultimatum" in scenario_ids
    assert "engineering-resistance" in scenario_ids
    assert "billing-spike-containment" in scenario_ids
    assert "compliance-audit-mapping" in scenario_ids


def test_war_room_simulate_successful_action():
    # In CFO ultimatum, choose all compliant high-impact actions
    payload = {
        "scenario_id": "cfo-90-day-ultimatum",
        "selected_action_ids": ["act-cfo-1", "act-cfo-2", "act-cfo-3", "act-cfo-4"]
    }
    res = client.post("/api/war-room/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["compliance_passed"] is True
    assert data["total_savings_achieved_usd"] >= 50000.0
    assert "APPROVED" in data["cfo_approval_status"]


def test_war_room_simulate_compliance_breach():
    # Selecting the illegal action (cutting payments single AZ)
    payload = {
        "scenario_id": "cfo-90-day-ultimatum",
        "selected_action_ids": ["act-cfo-5"]
    }
    res = client.post("/api/war-room/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["compliance_passed"] is False
    assert data["risk_score"] == "CRITICAL_COMPLIANCE_BREACH"
    assert "REJECTED" in data["cfo_approval_status"]
