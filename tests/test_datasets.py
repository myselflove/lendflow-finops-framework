"""
tests/test_datasets.py — LendFlow FinOps Framework Dataset Validation Suite
LendFlow FinOps Platform Group

Validates all 8 synthetic CSV datasets for:
  1. File existence
  2. Schema (required column presence)
  3. Row counts (within ±5% of specified target)
  4. Data types and value ranges
  5. Waste pattern embeddings (Section A8.2 patterns present)
  6. Compliance tag presence (pci-dss, soc2, rbi-it, gdpr)
  7. Waterfall savings model non-overlapping math (zero double-counting)
  8. Savings target achievement (>= $60,000/month)

Run:
    cd <workspace-root>
    .\\app\\backend\\.venv\\Scripts\\pytest tests/test_datasets.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# ── Path setup ─────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

# Add analysis/scripts to path so we can import run_analysis
sys.path.insert(0, str(ROOT / "analysis" / "scripts"))
sys.path.insert(0, str(ROOT / "scripts"))

# ── Constants ──────────────────────────────────────────────────────────────────
BASELINE_MONTHLY = 180_000.0
SAVINGS_TARGET   = 60_000.0
ROW_TOLERANCE    = 0.05   # ±5% row count tolerance


# ==============================================================================
# Fixtures — load CSVs once per session
# ==============================================================================

@pytest.fixture(scope="session")
def monthly_df():
    path = DATA_DIR / "monthly_cost_summary.csv"
    assert path.exists(), f"Missing: {path}"
    return pd.read_csv(path)

@pytest.fixture(scope="session")
def daily_df():
    path = DATA_DIR / "daily_cost_detail.csv"
    assert path.exists(), f"Missing: {path}"
    return pd.read_csv(path)

@pytest.fixture(scope="session")
def util_df():
    path = DATA_DIR / "instance_utilisation.csv"
    assert path.exists(), f"Missing: {path}"
    return pd.read_csv(path)

@pytest.fixture(scope="session")
def storage_df():
    path = DATA_DIR / "storage_inventory.csv"
    assert path.exists(), f"Missing: {path}"
    return pd.read_csv(path)

@pytest.fixture(scope="session")
def transfer_df():
    path = DATA_DIR / "data_transfer_log.csv"
    assert path.exists(), f"Missing: {path}"
    return pd.read_csv(path)

@pytest.fixture(scope="session")
def ri_df():
    path = DATA_DIR / "reserved_instance_coverage.csv"
    assert path.exists(), f"Missing: {path}"
    return pd.read_csv(path)

@pytest.fixture(scope="session")
def tag_df():
    path = DATA_DIR / "tag_compliance_report.csv"
    assert path.exists(), f"Missing: {path}"
    return pd.read_csv(path)

@pytest.fixture(scope="session")
def anomaly_df():
    path = DATA_DIR / "cost_anomaly_events.csv"
    assert path.exists(), f"Missing: {path}"
    return pd.read_csv(path)

@pytest.fixture(scope="session")
def analysis_results():
    """Run the full analysis pipeline and return results dict."""
    from run_analysis import run_full_analysis
    return run_full_analysis()


# ==============================================================================
# GROUP 1: File Existence
# ==============================================================================

class TestFileExistence:
    REQUIRED_FILES = [
        "monthly_cost_summary.csv",
        "daily_cost_detail.csv",
        "instance_utilisation.csv",
        "storage_inventory.csv",
        "data_transfer_log.csv",
        "reserved_instance_coverage.csv",
        "tag_compliance_report.csv",
        "cost_anomaly_events.csv",
    ]

    @pytest.mark.parametrize("filename", REQUIRED_FILES)
    def test_file_exists(self, filename):
        path = DATA_DIR / filename
        assert path.exists(), f"Required data file is missing: {path}"
        assert path.stat().st_size > 0, f"File is empty: {path}"


# ==============================================================================
# GROUP 2: Schema Validation
# ==============================================================================

class TestSchemas:
    def test_monthly_cost_summary_schema(self, monthly_df):
        required = {"month", "year_month", "category", "monthly_cost_usd",
                    "pct_of_total", "environment", "optimization_potential",
                    "compliance_ring_fence"}
        assert required.issubset(set(monthly_df.columns)), \
            f"Missing columns: {required - set(monthly_df.columns)}"

    def test_daily_cost_detail_schema(self, daily_df):
        required = {"date", "service", "resource_type", "resource_id",
                    "cost", "tags", "region", "environment", "az"}
        assert required.issubset(set(daily_df.columns)), \
            f"Missing columns: {required - set(daily_df.columns)}"

    def test_instance_utilisation_schema(self, util_df):
        required = {"instance_id", "service", "environment", "instance_type",
                    "region", "avg_cpu_pct", "max_cpu_pct", "avg_mem_pct",
                    "max_mem_pct", "hours_running", "monthly_cost_usd",
                    "rightsizing_flag", "graviton_eligible"}
        assert required.issubset(set(util_df.columns)), \
            f"Missing columns: {required - set(util_df.columns)}"

    def test_storage_inventory_schema(self, storage_df):
        required = {"resource_id", "service", "environment", "resource_type",
                    "size_gb", "size_used_gb", "storage_class", "last_accessed",
                    "monthly_cost_usd", "days_since_access", "lifecycle_status"}
        assert required.issubset(set(storage_df.columns)), \
            f"Missing columns: {required - set(storage_df.columns)}"

    def test_data_transfer_log_schema(self, transfer_df):
        required = {"date", "source_service", "destination_service",
                    "transfer_type", "gb_transferred", "cost_usd",
                    "is_wasteful", "optimization"}
        assert required.issubset(set(transfer_df.columns)), \
            f"Missing columns: {required - set(transfer_df.columns)}"

    def test_ri_coverage_schema(self, ri_df):
        required = {"ri_id", "instance_type", "term", "payment_option",
                    "region", "utilisation_pct", "on_demand_equiv_monthly_usd",
                    "ri_monthly_cost_usd", "monthly_savings_usd",
                    "expiry_date", "days_to_expiry", "status", "recommendation"}
        assert required.issubset(set(ri_df.columns)), \
            f"Missing columns: {required - set(ri_df.columns)}"

    def test_tag_compliance_schema(self, tag_df):
        required = {"resource_id", "service", "environment", "resource_type",
                    "region", "required_tags", "present_tags", "missing_tags",
                    "compliance_status", "compliance_frameworks",
                    "compliance_tag_ok", "remediation_action"}
        assert required.issubset(set(tag_df.columns)), \
            f"Missing columns: {required - set(tag_df.columns)}"

    def test_cost_anomaly_schema(self, anomaly_df):
        required = {"date", "service", "anomaly_type", "severity",
                    "expected_cost_usd", "actual_cost_usd", "delta_pct",
                    "root_cause", "auto_resolved", "ticket_id", "region"}
        assert required.issubset(set(anomaly_df.columns)), \
            f"Missing columns: {required - set(anomaly_df.columns)}"


# ==============================================================================
# GROUP 3: Row Count Validation
# ==============================================================================

class TestRowCounts:
    """Each count must be within ±5% of target."""

    def _check_count(self, actual: int, target: int, name: str):
        low  = int(target * (1 - ROW_TOLERANCE))
        high = int(target * (1 + ROW_TOLERANCE))
        assert low <= actual <= high, \
            f"{name}: expected {target}±5% ({low}–{high}), got {actual}"

    def test_monthly_cost_summary_rows(self, monthly_df):
        # 6 months × 12 categories = 72
        assert len(monthly_df) == 72, \
            f"monthly_cost_summary.csv: expected exactly 72 rows, got {len(monthly_df)}"

    def test_daily_cost_detail_rows(self, daily_df):
        # 180 days × 60 resources = 10,800 exactly
        assert len(daily_df) == 10_800, \
            f"daily_cost_detail.csv: expected exactly 10,800 rows, got {len(daily_df)}"

    def test_instance_utilisation_rows(self, util_df):
        self._check_count(len(util_df), 2_400, "instance_utilisation.csv")

    def test_storage_inventory_rows(self, storage_df):
        self._check_count(len(storage_df), 500, "storage_inventory.csv")

    def test_data_transfer_log_rows(self, transfer_df):
        self._check_count(len(transfer_df), 3_600, "data_transfer_log.csv")

    def test_ri_coverage_rows(self, ri_df):
        self._check_count(len(ri_df), 200, "reserved_instance_coverage.csv")

    def test_tag_compliance_rows(self, tag_df):
        self._check_count(len(tag_df), 1_500, "tag_compliance_report.csv")

    def test_cost_anomaly_rows(self, anomaly_df):
        self._check_count(len(anomaly_df), 80, "cost_anomaly_events.csv")


# ==============================================================================
# GROUP 4: Data Range & Type Validation
# ==============================================================================

class TestDataRanges:
    def test_monthly_costs_positive(self, monthly_df):
        assert (monthly_df["monthly_cost_usd"] > 0).all(), \
            "All monthly costs must be positive"

    def test_month6_total_near_180k(self, monthly_df):
        m6_total = monthly_df[monthly_df["month"] == 6]["monthly_cost_usd"].sum()
        assert abs(m6_total - 180_000) < 1.0, \
            f"Month-6 total must equal $180,000, got ${m6_total:,.2f}"

    def test_monthly_growth_trend(self, monthly_df):
        """Overall spend must grow from month 1 to month 6."""
        totals = monthly_df.groupby("month")["monthly_cost_usd"].sum()
        assert totals.iloc[0] < totals.iloc[-1], \
            "Monthly spend must grow from month 1 to month 6"
        assert totals.iloc[0] < 100_000, \
            f"Month-1 total should be <$100k, got ${totals.iloc[0]:,.2f}"

    def test_daily_costs_positive(self, daily_df):
        assert (daily_df["cost"] > 0).all(), "All daily costs must be positive"

    def test_cpu_range_valid(self, util_df):
        assert (util_df["avg_cpu_pct"] >= 0).all() and (util_df["avg_cpu_pct"] <= 100).all(), \
            "avg_cpu_pct must be in [0, 100]"
        assert (util_df["max_cpu_pct"] >= util_df["avg_cpu_pct"]).all(), \
            "max_cpu_pct must be >= avg_cpu_pct"

    def test_hours_running_valid(self, util_df):
        assert (util_df["hours_running"] <= 744).all(), \
            "hours_running cannot exceed 744 (31 days)"
        assert (util_df["hours_running"] > 0).all(), \
            "hours_running must be positive"

    def test_ri_utilisation_range(self, ri_df):
        assert (ri_df["utilisation_pct"] >= 0).all() and \
               (ri_df["utilisation_pct"] <= 100).all(), \
            "RI utilisation_pct must be in [0, 100]"

    def test_anomaly_actual_vs_expected(self, anomaly_df):
        """SPIKE anomalies must have actual > expected."""
        spikes = anomaly_df[anomaly_df["anomaly_type"] == "SPIKE"]
        assert (spikes["actual_cost_usd"] > spikes["expected_cost_usd"]).all(), \
            "All SPIKE anomalies must have actual_cost > expected_cost"

    def test_storage_class_values_valid(self, storage_df):
        valid_classes = {
            "STANDARD", "STANDARD_IA", "GLACIER", "DEEP_ARCHIVE",
            "INTELLIGENT_TIERING", "gp2", "gp3"
        }
        invalid = set(storage_df["storage_class"].unique()) - valid_classes
        assert not invalid, f"Invalid storage classes found: {invalid}"

    def test_transfer_gb_positive(self, transfer_df):
        assert (transfer_df["gb_transferred"] >= 0).all(), \
            "gb_transferred cannot be negative"


# ==============================================================================
# GROUP 5: Waste Pattern Validation (Section A8.2)
# ==============================================================================

class TestWastePatterns:
    def test_oversized_ec2_instances_present(self, util_df):
        """A8.2: Over-provisioned EC2 with <20% CPU must be present."""
        oversized = util_df[util_df["avg_cpu_pct"] < 20.0]
        pct = len(oversized) / len(util_df) * 100
        assert len(oversized) > 100, \
            f"Expected >100 oversized instances (<20% CPU), found {len(oversized)}"
        assert pct > 30, \
            f"Expected >30% oversized instances, found {pct:.1f}%"

    def test_nonprod_running_24x7(self, util_df):
        """A8.2: Dev/staging instances running 24x7 waste pattern."""
        nonprod = util_df[util_df["environment"].isin(["staging", "development"])]
        running_247 = nonprod[nonprod["hours_running"] >= 700]
        assert len(running_247) > 50, \
            f"Expected >50 non-prod instances running ~24/7, found {len(running_247)}"

    def test_s3_wrong_tier_waste(self, storage_df):
        """A8.2: S3 objects >90 days still in STANDARD tier."""
        s3 = storage_df[storage_df["resource_type"] == "S3_BUCKET"]
        wrong_tier = s3[
            (s3["days_since_access"] > 90) &
            (s3["storage_class"] == "STANDARD")
        ]
        assert len(wrong_tier) > 20, \
            f"Expected >20 S3 buckets in wrong tier, found {len(wrong_tier)}"

    def test_ebs_over_provisioned(self, storage_df):
        """A8.2: 1TB EBS volumes using <100GB."""
        ebs = storage_df[storage_df["resource_type"] == "EBS_VOLUME"]
        over_prov = ebs[
            (ebs["size_gb"] >= 1000) &
            (ebs["size_used_gb"] < 100)
        ]
        assert len(over_prov) > 0, \
            f"Expected over-provisioned EBS (>=1TB, <100GB used), found {len(over_prov)}"

    def test_cross_az_transfer_waste(self, transfer_df):
        """A8.2: Cross-AZ data transfer waste pattern present."""
        cross_az = transfer_df[transfer_df["transfer_type"] == "CROSS_AZ"]
        pct = len(cross_az) / len(transfer_df) * 100
        assert pct > 50, \
            f"Expected >50% cross-AZ transfers (waste), found {pct:.1f}%"
        assert cross_az["cost_usd"].sum() > 0, \
            "Cross-AZ transfers must have positive cost"

    def test_orphaned_resource_anomalies(self, anomaly_df):
        """A8.2: Orphaned resource anomaly events present."""
        orphaned = anomaly_df[anomaly_df["anomaly_type"] == "ORPHANED_RESOURCE"]
        assert len(orphaned) > 0, \
            "Expected ORPHANED_RESOURCE anomaly events"

    def test_ri_under_utilisation_waste(self, ri_df):
        """A8.2: Oversized RDS / under-utilised RIs present."""
        under = ri_df[ri_df["utilisation_pct"] < 50]
        assert len(under) > 50, \
            f"Expected >50 under-utilised RIs (<50%), found {len(under)}"

    def test_gp2_volumes_for_migration(self, storage_df):
        """A8.2: gp2 EBS volumes present (gp3 migration opportunity)."""
        ebs_gp2 = storage_df[storage_df["storage_class"] == "gp2"]
        assert len(ebs_gp2) > 50, \
            f"Expected >50 gp2 volumes for gp3 migration, found {len(ebs_gp2)}"


# ==============================================================================
# GROUP 6: Compliance Tag Validation
# ==============================================================================

class TestComplianceTags:
    def test_pci_dss_tag_present(self, tag_df):
        """lendflow-payments resources must reference pci-dss."""
        payments = tag_df[tag_df["service"] == "lendflow-payments"]
        assert len(payments) > 0, "No records for lendflow-payments"
        pci_tagged = payments[payments["compliance_frameworks"].str.contains(
            "pci-dss", na=False, case=False
        )]
        assert len(pci_tagged) > 0, \
            "lendflow-payments resources must have pci-dss compliance tag"

    def test_soc2_tag_present(self, tag_df):
        """lendflow-audit resources must reference soc2."""
        audit_svc = tag_df[tag_df["service"] == "lendflow-audit"]
        assert len(audit_svc) > 0, "No records for lendflow-audit"
        soc2 = audit_svc[audit_svc["compliance_frameworks"].str.contains(
            "soc2", na=False, case=False
        )]
        assert len(soc2) > 0, \
            "lendflow-audit resources must have soc2 compliance tag"

    def test_rbi_it_tag_present(self, tag_df):
        """lendflow-ingestion and lendflow-credit-scoring must reference rbi-it."""
        for svc in ["lendflow-ingestion", "lendflow-credit-scoring"]:
            svc_rows = tag_df[tag_df["service"] == svc]
            assert len(svc_rows) > 0, f"No records for {svc}"
            rbi = svc_rows[svc_rows["compliance_frameworks"].str.contains(
                "rbi-it", na=False, case=False
            )]
            assert len(rbi) > 0, f"{svc} must have rbi-it compliance tag"

    def test_gdpr_tag_present(self, tag_df):
        """GDPR-scoped services must have gdpr tag."""
        gdpr_services = ["lendflow-auth", "lendflow-notifications",
                         "lendflow-doc-verify", "lendflow-ingestion"]
        for svc in gdpr_services:
            svc_rows = tag_df[tag_df["service"] == svc]
            if len(svc_rows) == 0:
                continue
            gdpr = svc_rows[svc_rows["compliance_frameworks"].str.contains(
                "gdpr", na=False, case=False
            )]
            assert len(gdpr) > 0, f"{svc} must have gdpr compliance tag"

    def test_tag_non_compliance_present(self, tag_df):
        """Some resources must be non-compliant to test governance workflows."""
        non_compliant = tag_df[tag_df["compliance_status"] == "NON_COMPLIANT"]
        assert len(non_compliant) > 0, \
            "Expected some NON_COMPLIANT resources for governance testing"

    def test_five_required_tags_listed(self, tag_df):
        """Required tag column must include all 5 canonical tags."""
        required_tags_set = {"CostCenter", "Environment", "Service", "Owner", "ComplianceScope"}
        for _, row in tag_df.head(10).iterrows():
            row_tags = set(str(row["required_tags"]).split("|"))
            assert required_tags_set.issubset(row_tags), \
                f"Required tags incomplete: {row_tags}"


# ==============================================================================
# GROUP 7: Waterfall Savings Math Validation (Zero Double-Counting)
# ==============================================================================

class TestWaterfallMath:
    def test_waterfall_step1_baseline_equals_180k(self, analysis_results):
        """Step 1 baseline must equal the $180,000 canonical baseline."""
        wf = analysis_results["waterfall"]
        diff = abs(wf["step1_baseline_usd"] - 180_000.0)
        assert diff < 1.0, \
            f"Step1 baseline must equal $180,000, got ${wf['step1_baseline_usd']:,.2f}"

    def test_waterfall_step2_baseline_equals_post_step1(self, analysis_results):
        """Step 2 baseline must equal post-Step-1 spend (zero double-counting)."""
        wf = analysis_results["waterfall"]
        expected = wf["step1_baseline_usd"] - wf["step1_total_savings_usd"]
        actual   = wf["step2_baseline_usd"]
        assert abs(actual - expected) < 0.02, \
            f"Step2 baseline must equal post-Step1 (${expected:,.2f}), got ${actual:,.2f}"

    def test_waterfall_step3_baseline_equals_post_step2(self, analysis_results):
        """Step 3 baseline must equal post-Step-2 spend (zero double-counting)."""
        wf = analysis_results["waterfall"]
        expected = wf["step2_baseline_usd"] - wf["step2_total_savings_usd"]
        actual   = wf["step3_baseline_usd"]
        assert abs(actual - expected) < 0.02, \
            f"Step3 baseline must equal post-Step2 (${expected:,.2f}), got ${actual:,.2f}"

    def test_total_savings_equals_sum_of_steps(self, analysis_results):
        """Total savings must equal the arithmetic sum of Step 1 + 2 + 3 savings."""
        wf = analysis_results["waterfall"]
        expected_total = (
            wf["step1_total_savings_usd"] +
            wf["step2_total_savings_usd"] +
            wf["step3_total_savings_usd"]
        )
        assert abs(wf["total_savings_usd"] - expected_total) < 0.02, \
            f"Total savings ${wf['total_savings_usd']:,.2f} != sum of steps ${expected_total:,.2f}"

    def test_final_spend_equals_baseline_minus_savings(self, analysis_results):
        """Final spend must equal baseline minus total savings."""
        wf = analysis_results["waterfall"]
        expected = 180_000.0 - wf["total_savings_usd"]
        assert abs(wf["final_monthly_spend_usd"] - expected) < 0.02, \
            f"Final spend ${wf['final_monthly_spend_usd']:,.2f} != baseline - savings (${expected:,.2f})"

    def test_step1_savings_positive(self, analysis_results):
        wf = analysis_results["waterfall"]
        assert wf["step1_total_savings_usd"] > 0, "Step 1 savings must be positive"

    def test_step2_savings_positive(self, analysis_results):
        wf = analysis_results["waterfall"]
        assert wf["step2_total_savings_usd"] > 0, "Step 2 savings must be positive"

    def test_step3_savings_positive(self, analysis_results):
        wf = analysis_results["waterfall"]
        assert wf["step3_total_savings_usd"] > 0, "Step 3 savings must be positive"

    def test_no_step_exceeds_its_baseline(self, analysis_results):
        """No step can save more than its own baseline (physically impossible)."""
        wf = analysis_results["waterfall"]
        assert wf["step1_total_savings_usd"] <= wf["step1_baseline_usd"], \
            "Step 1 cannot save more than its baseline"
        assert wf["step2_total_savings_usd"] <= wf["step2_baseline_usd"], \
            "Step 2 cannot save more than its baseline"
        assert wf["step3_total_savings_usd"] <= wf["step3_baseline_usd"], \
            "Step 3 cannot save more than its baseline"

    def test_savings_target_achieved(self, analysis_results):
        """Total savings must meet the $60,000/month target."""
        wf = analysis_results["waterfall"]
        total = wf["total_savings_usd"]
        assert total >= SAVINGS_TARGET, \
            f"Savings ${total:,.2f} must be >= target ${SAVINGS_TARGET:,.2f}/month"

    def test_final_spend_below_120k(self, analysis_results):
        """Final monthly spend must be <= $120,000."""
        wf = analysis_results["waterfall"]
        assert wf["final_monthly_spend_usd"] <= 120_000.0, \
            f"Final spend ${wf['final_monthly_spend_usd']:,.2f} must be <= $120,000"

    def test_zero_dc_flags_all_pass(self, analysis_results):
        """All zero-double-counting verification flags must be True."""
        zdc = analysis_results["waterfall"]["zero_dc_verification"]
        assert zdc["step1_baseline_eq_original"],   "ZDC: Step1 baseline flag failed"
        assert zdc["step2_baseline_eq_post_step1"], "ZDC: Step2 baseline flag failed"
        assert zdc["step3_baseline_eq_post_step2"], "ZDC: Step3 baseline flag failed"
        assert zdc["no_double_counting"],            "ZDC: no_double_counting flag failed"


# ==============================================================================
# GROUP 8: Recommendations Validation
# ==============================================================================

class TestRecommendations:
    def test_exactly_18_recommendations(self, analysis_results):
        recs = analysis_results["recommendations"]
        assert len(recs) == 18, f"Expected 18 recommendations, got {len(recs)}"

    def test_all_recommendations_have_positive_savings(self, analysis_results):
        recs = analysis_results["recommendations"]
        for r in recs:
            assert r["estimated_monthly_savings_usd"] >= 0, \
                f"Rec #{r['rank']} has negative savings: {r['estimated_monthly_savings_usd']}"

    def test_recommendations_cover_all_3_phases(self, analysis_results):
        recs = analysis_results["recommendations"]
        phases = {r["phase"].split("—")[0].strip() for r in recs}
        assert "Step 1" in phases, "Missing Step 1 recommendations"
        assert "Step 2" in phases, "Missing Step 2 recommendations"
        assert "Step 3" in phases, "Missing Step 3 recommendations"

    def test_recommendations_mapped_to_appendix_a(self, analysis_results):
        recs = analysis_results["recommendations"]
        for r in recs:
            assert r.get("appendix_a", "").startswith("A-"), \
                f"Rec #{r['rank']} missing Appendix A reference: {r.get('appendix_a')}"

    def test_recommendations_ranked_sequentially(self, analysis_results):
        recs = analysis_results["recommendations"]
        ranks = [r["rank"] for r in recs]
        assert ranks == list(range(1, 19)), \
            f"Recommendations must be ranked 1-18 sequentially, got: {ranks}"

    def test_compliance_ring_fenced_in_recommendations(self, analysis_results):
        """Graviton3 migration must explicitly exclude PCI DSS payments service."""
        recs = analysis_results["recommendations"]
        graviton_recs = [r for r in recs if "graviton" in r["title"].lower()]
        assert len(graviton_recs) > 0, "No Graviton3 recommendation found"
        for r in graviton_recs:
            action_lower = r["action"].lower()
            # Must mention PCI exclusion or payments exclusion
            assert "pci" in action_lower or "payment" in action_lower, \
                f"Graviton3 rec must mention PCI/payments exclusion: {r['action']}"


# ==============================================================================
# GROUP 9: Cross-Dataset Consistency
# ==============================================================================

class TestCrossDatasetConsistency:
    VALID_SERVICES = {
        "lendflow-gateway", "lendflow-auth", "lendflow-ingestion",
        "lendflow-credit-scoring", "lendflow-underwriting", "lendflow-doc-verify",
        "lendflow-payments", "lendflow-ledger", "lendflow-notifications",
        "lendflow-analytics", "lendflow-audit", "lendflow-collections",
    }

    def test_all_services_in_daily_detail(self, daily_df):
        """All 12 microservices must appear in daily cost detail."""
        found_services = set(daily_df["service"].unique())
        missing = self.VALID_SERVICES - found_services
        assert not missing, f"Missing services in daily_cost_detail: {missing}"

    def test_all_services_in_utilisation(self, util_df):
        """All 12 microservices must appear in instance utilisation."""
        found_services = set(util_df["service"].unique())
        missing = self.VALID_SERVICES - found_services
        assert not missing, f"Missing services in instance_utilisation: {missing}"

    def test_daily_dates_in_valid_range(self, daily_df):
        """All daily cost dates must be within the 6-month window."""
        dates = pd.to_datetime(daily_df["date"])
        assert dates.min() >= pd.Timestamp("2024-07-01"), \
            f"Dates start before 2024-07-01: {dates.min()}"
        assert dates.max() <= pd.Timestamp("2025-01-31"), \
            f"Dates exceed valid window: {dates.max()}"

    def test_regions_valid(self, daily_df):
        """All regions must be known AWS regions."""
        valid_regions = {"ap-south-1", "eu-west-1", "eu-central-1",
                         "us-east-1", "us-west-2"}
        invalid = set(daily_df["region"].unique()) - valid_regions
        assert not invalid, f"Invalid regions found: {invalid}"

    def test_payments_service_in_ap_south_1(self, daily_df):
        """lendflow-payments must only run in ap-south-1 (PCI + RBI)."""
        payments = daily_df[daily_df["service"] == "lendflow-payments"]
        non_india = payments[payments["region"] != "ap-south-1"]
        assert len(non_india) == 0, \
            f"lendflow-payments found outside ap-south-1: {non_india['region'].unique()}"
