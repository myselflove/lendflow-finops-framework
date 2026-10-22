"""
generate_data.py — LendFlow FinOps Framework Synthetic Dataset Generator
LendFlow FinOps Platform Group

Generates 8 realistic CSV files under data/ with embedded waste patterns from
Section A8.2 of the project specification. Uses RANDOM_SEED = 42 for full
reproducibility.

Run from workspace root:
    python scripts/generate_data.py

Output: data/*.csv
"""

import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── Seed for 100% reproducibility ─────────────────────────────────────────────
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── Constants mirroring the PDF baseline ──────────────────────────────────────
BASELINE_MONTHLY = 180_000.0   # Month 6 (current)
MONTH_0_SPEND    = 50_000.0    # 12 months ago start
NUM_MONTHS       = 6           # rows of summary (months 1-6 for conciseness)
SERVICES = [
    "lendflow-gateway",
    "lendflow-auth",
    "lendflow-ingestion",
    "lendflow-credit-scoring",
    "lendflow-underwriting",
    "lendflow-doc-verify",
    "lendflow-payments",
    "lendflow-ledger",
    "lendflow-notifications",
    "lendflow-analytics",
    "lendflow-audit",
    "lendflow-collections",
]
RESOURCE_TYPES = [
    "EC2", "EKS_NODE", "RDS", "AURORA", "ELASTICACHE",
    "S3", "EBS", "NAT_GATEWAY", "ALB", "LAMBDA", "CLOUDWATCH", "KMS",
]
AWS_REGIONS = ["ap-south-1", "ap-south-1", "ap-south-1", "eu-west-1", "eu-central-1"]
ENVIRONMENTS = ["production", "production", "staging", "development"]
INSTANCE_TYPES_COMPUTE = [
    "m5.xlarge", "m5.2xlarge", "m5.4xlarge",
    "c5.xlarge", "c5.2xlarge",
    "r5.xlarge", "r5.2xlarge",
    "m5.large", "c5.large",
]
INSTANCE_TYPES_RDS = [
    "db.r6g.xlarge", "db.r6g.2xlarge", "db.r5.xlarge",
    "db.r5.2xlarge", "db.t3.medium", "db.t3.large",
]
STORAGE_CLASSES = ["STANDARD", "STANDARD_IA", "GLACIER", "DEEP_ARCHIVE", "INTELLIGENT_TIERING"]
COMPLIANCE_TAGS = {
    "lendflow-payments": ["pci-dss"],
    "lendflow-audit":    ["soc2"],
    "lendflow-ingestion": ["rbi-it", "gdpr"],
    "lendflow-credit-scoring": ["rbi-it"],
    "lendflow-underwriting": ["rbi-it"],
    "lendflow-ledger": ["rbi-it", "soc2"],
    "lendflow-gateway": [],
    "lendflow-auth": ["soc2", "gdpr"],
    "lendflow-doc-verify": ["gdpr", "rbi-it"],
    "lendflow-notifications": ["gdpr"],
    "lendflow-analytics": ["soc2"],
    "lendflow-collections": ["rbi-it"],
}
COST_SPLIT = {
    "EC2_EKS":     0.416,
    "RDS":         0.250,
    "NAT_DT":      0.100,
    "S3_EBS":      0.083,
    "ELASTICACHE": 0.067,
    "OTHER":       0.084,
}

# ── Helper utilities ──────────────────────────────────────────────────────────

def rng_choice(lst, size=1, replace=True):
    idx = np.random.randint(0, len(lst), size=size)
    result = [lst[i] for i in idx]
    return result if size > 1 else result[0]

def tag_str(service, env):
    base = {
        "CostCenter":      "engineering",
        "Environment":     env,
        "Service":         service,
        "Owner":           "platform-team",
        "ComplianceScope": "|".join(COMPLIANCE_TAGS.get(service, ["none"])),
    }
    return str(base)

def missing_tags_for(service, env):
    """Simulate tag compliance gaps — 30% of non-prod resources missing Owner."""
    required = ["CostCenter", "Environment", "Service", "Owner", "ComplianceScope"]
    missing = []
    if env in ("staging", "development") and random.random() < 0.30:
        missing.append("Owner")
    if random.random() < 0.10:
        missing.append("CostCenter")
    comp_tags = COMPLIANCE_TAGS.get(service, [])
    if comp_tags and random.random() < 0.05:
        missing.append("ComplianceScope")
    return missing


# ==============================================================================
# 1. monthly_cost_summary.csv
#    72 rows: 6 months x 12 categories
#    Month 6 total = $180,000; Month 1 total ≈ $72,000 (trajectory from $50k)
# ==============================================================================
def generate_monthly_cost_summary() -> pd.DataFrame:
    print("  Generating monthly_cost_summary.csv ...")
    # Monthly totals: roughly linear growth from ~$72k (month 1) to $180k (month 6)
    monthly_totals = np.linspace(72_000, 180_000, NUM_MONTHS)

    rows = []
    categories = [
        ("EC2_Compute",           0.250),
        ("EKS_NodeGroups",        0.166),
        ("RDS_Aurora",            0.200),
        ("RDS_Standard",          0.050),
        ("NAT_Gateway",           0.060),
        ("InterAZ_DataTransfer",  0.040),
        ("S3_Storage",            0.040),
        ("EBS_Volumes",           0.043),
        ("ElastiCache_Redis",     0.067),
        ("Lambda_CloudWatch",     0.030),
        ("KMS_WAF_Shield",        0.029),
        ("Other_Services",        0.025),
    ]
    # Verify proportions sum to 1.0
    assert abs(sum(p for _, p in categories) - 1.0) < 1e-6

    for month_idx, total in enumerate(monthly_totals, start=1):
        for cat_name, proportion in categories:
            # Add ±5% noise per category per month
            noise = np.random.uniform(0.95, 1.05)
            cost = round(total * proportion * noise, 2)
            rows.append({
                "month":           month_idx,
                "year_month":      f"2024-{month_idx + 6:02d}",   # 2024-07 to 2024-12
                "category":        cat_name,
                "monthly_cost_usd": cost,
                "pct_of_total":    round(proportion * 100, 1),
                "environment":     "all",
                "optimization_potential": _opt_potential(cat_name),
                "compliance_ring_fence": _is_ring_fenced(cat_name),
            })

    df = pd.DataFrame(rows)
    # Normalize month-6 total to exactly $180,000 (canonical baseline)
    m6_total = df[df["month"] == 6]["monthly_cost_usd"].sum()
    scale = 180_000.0 / m6_total
    df.loc[df["month"] == 6, "monthly_cost_usd"] = (
        df.loc[df["month"] == 6, "monthly_cost_usd"] * scale
    ).round(2)
    assert len(df) == NUM_MONTHS * 12  # 72 rows
    return df

def _opt_potential(cat):
    high = {"EC2_Compute", "EKS_NodeGroups", "RDS_Standard", "NAT_Gateway",
            "S3_Storage", "EBS_Volumes", "InterAZ_DataTransfer"}
    return "HIGH" if cat in high else "MEDIUM"

def _is_ring_fenced(cat):
    return cat in {"RDS_Aurora", "ElastiCache_Redis", "KMS_WAF_Shield"}


# ==============================================================================
# 2. daily_cost_detail.csv
#    10,800 rows: 180 days x 60 resource entries per day
#    Columns: date, service, resource_type, resource_id, cost, tags, region
# ==============================================================================
def generate_daily_cost_detail() -> pd.DataFrame:
    print("  Generating daily_cost_detail.csv (~10,800 rows) ...")
    days = pd.date_range("2024-07-01", periods=180, freq="D")
    rows = []

    # Pre-allocate service-resource pairs (60 total) to keep them stable
    resource_pool = []
    for svc in SERVICES:
        n = 5  # 5 resources per service = 60 total
        for i in range(n):
            env = rng_choice(ENVIRONMENTS)
            region = "ap-south-1" if svc in (
                "lendflow-payments", "lendflow-audit", "lendflow-credit-scoring"
            ) else rng_choice(AWS_REGIONS)
            rtype = _service_rtype(svc, i)
            rid = f"{svc[:8]}-{rtype.lower()}-{i:03d}-{np.random.randint(1000,9999)}"
            base_cost = _base_daily_cost(svc, rtype, env)
            resource_pool.append((svc, rtype, rid, env, region, base_cost))

    for day in days:
        is_weekend = day.weekday() >= 5
        for svc, rtype, rid, env, region, base_cost in resource_pool:
            # Weekend discount for non-prod (but NOT if prod)
            weekend_factor = 1.0
            if is_weekend and env in ("staging", "development"):
                # Waste pattern: these SHOULD be off — they're NOT (cost is still there)
                weekend_factor = 0.95  # slight dip only — real waste is running at all
            # Growth trend: costs grow over 180 days
            day_idx = (day - days[0]).days
            trend = 1.0 + (day_idx / 180) * 0.35  # +35% over 6 months
            noise = np.random.uniform(0.90, 1.10)
            cost = round(base_cost * trend * weekend_factor * noise, 4)
            rows.append({
                "date":          day.strftime("%Y-%m-%d"),
                "service":       svc,
                "resource_type": rtype,
                "resource_id":   rid,
                "cost":          cost,
                "tags":          tag_str(svc, env),
                "region":        region,
                "environment":   env,
                "az":            _pick_az(region),
            })

    df = pd.DataFrame(rows)
    assert len(df) == 10_800
    return df

def _service_rtype(svc, idx):
    mapping = {
        "lendflow-gateway":        ["ALB", "EC2", "EC2", "CLOUDWATCH", "WAF"],
        "lendflow-auth":           ["EC2", "EKS_NODE", "RDS", "ELASTICACHE", "EC2"],
        "lendflow-ingestion":      ["EKS_NODE", "EC2", "RDS", "S3", "EBS"],
        "lendflow-credit-scoring": ["EC2", "EKS_NODE", "EC2", "RDS", "EBS"],
        "lendflow-underwriting":   ["EKS_NODE", "EC2", "RDS", "S3", "LAMBDA"],
        "lendflow-doc-verify":     ["EC2", "S3", "LAMBDA", "EBS", "EC2"],
        "lendflow-payments":       ["EC2", "EKS_NODE", "RDS", "EC2", "EC2"],  # PCI: 3+ AZ
        "lendflow-ledger":         ["RDS", "EC2", "AURORA", "EBS", "ELASTICACHE"],
        "lendflow-notifications":  ["LAMBDA", "EC2", "SQS", "S3", "CLOUDWATCH"],
        "lendflow-analytics":      ["EC2", "S3", "EBS", "LAMBDA", "EC2"],
        "lendflow-audit":          ["EC2", "S3", "EBS", "CLOUDWATCH", "KMS"],
        "lendflow-collections":    ["EC2", "RDS", "LAMBDA", "S3", "EC2"],
    }
    types = mapping.get(svc, ["EC2"] * 5)
    return types[idx % len(types)]

def _base_daily_cost(svc, rtype, env):
    base_map = {
        "EC2": 45.0, "EKS_NODE": 55.0, "RDS": 62.0, "AURORA": 75.0,
        "ELASTICACHE": 40.0, "S3": 8.0, "EBS": 15.0,
        "NAT_GATEWAY": 30.0, "ALB": 12.0, "LAMBDA": 3.0,
        "CLOUDWATCH": 5.0, "KMS": 2.0, "WAF": 8.0, "SQS": 2.0,
    }
    cost = base_map.get(rtype, 10.0)
    # Production costs more (more replicas)
    if env == "production":
        cost *= 2.5
    elif env == "staging":
        cost *= 1.0  # Waste pattern: staging costs ≈ full prod
    else:
        cost *= 0.6  # dev still running 24/7 (waste)
    # Payments service is over-provisioned for PCI compliance
    if svc == "lendflow-payments":
        cost *= 1.4
    return cost

def _pick_az(region):
    azs = {
        "ap-south-1":  ["ap-south-1a", "ap-south-1b", "ap-south-1c"],
        "eu-west-1":   ["eu-west-1a",  "eu-west-1b",  "eu-west-1c"],
        "eu-central-1":["eu-central-1a","eu-central-1b"],
    }
    choices = azs.get(region, ["ap-south-1a"])
    return rng_choice(choices)


# ==============================================================================
# 3. instance_utilisation.csv
#    2,400 rows: instance-level CPU/RAM utilisation
#    Waste pattern: many instances <20% CPU (over-provisioned)
# ==============================================================================
def generate_instance_utilisation() -> pd.DataFrame:
    print("  Generating instance_utilisation.csv (~2,400 rows) ...")
    rows = []
    for i in range(2400):
        svc = rng_choice(SERVICES)
        env = rng_choice(ENVIRONMENTS)
        itype = rng_choice(INSTANCE_TYPES_COMPUTE)
        # Waste pattern: 40% of instances are over-provisioned (avg CPU < 20%)
        if i % 5 < 2:  # 40%
            avg_cpu = round(np.random.uniform(3.0, 19.9), 1)   # WASTE: <20%
            avg_mem = round(np.random.uniform(10.0, 35.0), 1)
        elif i % 5 == 2:  # 20% moderate
            avg_cpu = round(np.random.uniform(20.0, 45.0), 1)
            avg_mem = round(np.random.uniform(35.0, 60.0), 1)
        else:  # 40% well-utilised
            avg_cpu = round(np.random.uniform(45.0, 85.0), 1)
            avg_mem = round(np.random.uniform(55.0, 85.0), 1)

        max_cpu = min(100.0, round(avg_cpu * np.random.uniform(1.5, 2.5), 1))
        max_mem = min(100.0, round(avg_mem * np.random.uniform(1.2, 1.8), 1))

        # Dev/staging: running 24/7 — real waste
        if env in ("staging", "development"):
            hours_running = round(np.random.uniform(700, 744), 1)  # essentially 24/7
        else:
            hours_running = round(np.random.uniform(690, 744), 1)

        monthly_cost = round(_base_daily_cost(svc, "EC2", env) * 30, 2)

        rows.append({
            "instance_id":     f"i-{random.randint(10**11, 10**12 - 1):012d}",
            "service":         svc,
            "environment":     env,
            "instance_type":   itype,
            "region":          rng_choice(AWS_REGIONS),
            "avg_cpu_pct":     avg_cpu,
            "max_cpu_pct":     max_cpu,
            "avg_mem_pct":     avg_mem,
            "max_mem_pct":     max_mem,
            "hours_running":   hours_running,
            "monthly_cost_usd": monthly_cost,
            "rightsizing_flag": "OVERSIZED" if avg_cpu < 20.0 else (
                "CANDIDATE" if avg_cpu < 40.0 else "OPTIMAL"
            ),
            "graviton_eligible": itype.startswith(("m5", "c5", "r5")),
        })
    return pd.DataFrame(rows)


# ==============================================================================
# 4. storage_inventory.csv
#    500 rows: S3 + EBS storage
#    Waste patterns: S3 >90 days in STANDARD, EBS with <100GB used
# ==============================================================================
def generate_storage_inventory() -> pd.DataFrame:
    print("  Generating storage_inventory.csv (~500 rows) ...")
    rows = []
    for i in range(500):
        svc  = rng_choice(SERVICES)
        env  = rng_choice(ENVIRONMENTS)
        is_s3 = i < 300  # 300 S3 buckets, 200 EBS volumes

        if is_s3:
            size_gb = round(np.random.choice(
                np.concatenate([
                    np.random.uniform(10, 200, 150),     # small
                    np.random.uniform(200, 2000, 100),   # large (including 1TB waste)
                    np.random.uniform(2000, 10000, 50),  # very large audit logs
                ])
            ), 1)
            # Waste pattern: 35% still in STANDARD after >90 days
            days_since = int(np.random.uniform(1, 400))
            if days_since > 90 and random.random() < 0.35:
                sc = "STANDARD"  # WASTE — should be IA or Glacier
            elif days_since > 90:
                sc = rng_choice(["STANDARD_IA", "GLACIER", "INTELLIGENT_TIERING"])
            else:
                sc = "STANDARD"

            last_accessed = pd.Timestamp("2024-12-31") - pd.Timedelta(days=days_since)
            rtype = "S3_BUCKET"
            monthly_cost = round(size_gb * 0.023, 2) if sc == "STANDARD" else round(
                size_gb * (0.0125 if sc == "STANDARD_IA" else 0.004), 2
            )
            size_used_gb  = size_gb  # S3 — no separate used concept
            wasted_pct    = None
        else:
            # EBS volumes
            size_gb = round(rng_choice([
                500, 500, 1000, 1000, 2000, 100, 200, 300, 750
            ], size=1))
            # Waste pattern: EBS provisioned 1TB, using <100GB
            if size_gb >= 1000 and random.random() < 0.50:
                size_used_gb = round(np.random.uniform(10, 95), 1)  # WASTE
            else:
                size_used_gb = round(size_gb * np.random.uniform(0.40, 0.92), 1)
            last_accessed = pd.Timestamp("2024-12-31") - pd.Timedelta(
                days=int(np.random.uniform(0, 365))
            )
            sc = "gp2" if random.random() < 0.60 else "gp3"  # gp2→gp3 migration opportunity
            rtype = "EBS_VOLUME"
            monthly_cost  = round(size_gb * (0.10 if sc == "gp2" else 0.08), 2)
            wasted_pct    = round((1 - size_used_gb / size_gb) * 100, 1)

        rows.append({
            "resource_id":      f"{svc[:8]}-{rtype.lower()[:3]}-{i:04d}",
            "service":          svc,
            "environment":      env,
            "resource_type":    rtype,
            "size_gb":          size_gb,
            "size_used_gb":     size_used_gb if not is_s3 else size_gb,
            "storage_class":    sc,
            "last_accessed":    last_accessed.strftime("%Y-%m-%d"),
            "monthly_cost_usd": monthly_cost,
            "days_since_access": int((pd.Timestamp("2024-12-31") - last_accessed).days),
            "lifecycle_status": (
                "WASTE_WRONG_TIER" if (is_s3 and sc == "STANDARD" and
                    int((pd.Timestamp("2024-12-31") - last_accessed).days) > 90)
                else "WASTE_OVER_PROVISIONED" if (not is_s3 and wasted_pct and wasted_pct > 80)
                else "OPTIMAL"
            ),
            "wasted_pct":       wasted_pct,
        })
    return pd.DataFrame(rows)


# ==============================================================================
# 5. data_transfer_log.csv
#    3,600 rows
#    Waste: cross-AZ transfers (expensive), same-region S3 → EC2
# ==============================================================================
def generate_data_transfer_log() -> pd.DataFrame:
    print("  Generating data_transfer_log.csv (~3,600 rows) ...")
    rows = []
    dates = pd.date_range("2024-07-01", periods=180, freq="D")
    TRANSFER_TYPES = [
        "CROSS_AZ",           # $0.01/GB — most common waste
        "SAME_AZ",            # $0.00/GB — free
        "INTER_REGION",       # $0.09/GB — expensive
        "INTERNET_EGRESS",    # $0.09/GB — expensive
        "S3_TO_EC2_SAME_REGION",  # $0.00 if via endpoint, else $0.01
        "CLOUDFRONT_ORIGIN",  # $0.01/GB
    ]
    COST_PER_GB = {
        "CROSS_AZ": 0.01,
        "SAME_AZ": 0.00,
        "INTER_REGION": 0.09,
        "INTERNET_EGRESS": 0.09,
        "S3_TO_EC2_SAME_REGION": 0.01,
        "CLOUDFRONT_ORIGIN": 0.01,
    }

    for i in range(3600):
        svc_src = rng_choice(SERVICES)
        svc_dst = rng_choice(SERVICES)
        ttype   = rng_choice(TRANSFER_TYPES)
        # Waste pattern: Cross-AZ accounts for 60% of NAT/transfer costs
        if i % 10 < 6:
            ttype = "CROSS_AZ"

        gb = round(np.random.exponential(scale=50.0), 2)  # heavy-tail distribution
        cost = round(gb * COST_PER_GB[ttype], 4)
        day  = dates[i % len(dates)]

        rows.append({
            "date":            day.strftime("%Y-%m-%d"),
            "source_service":  svc_src,
            "destination_service": svc_dst,
            "source_az":       _pick_az("ap-south-1"),
            "dest_az":         _pick_az("ap-south-1"),
            "transfer_type":   ttype,
            "gb_transferred":  gb,
            "cost_usd":        cost,
            "is_wasteful":     ttype in ("CROSS_AZ", "INTER_REGION") and cost > 0,
            "optimization":    "USE_VPC_ENDPOINT" if ttype == "S3_TO_EC2_SAME_REGION"
                               else "SAME_AZ_PLACEMENT" if ttype == "CROSS_AZ"
                               else "NONE",
        })
    return pd.DataFrame(rows)


# ==============================================================================
# 6. reserved_instance_coverage.csv
#    200 rows: RI portfolio — currently 0% coverage (waste = 100% On-Demand)
# ==============================================================================
def generate_reserved_instance_coverage() -> pd.DataFrame:
    print("  Generating reserved_instance_coverage.csv (~200 rows) ...")
    rows = []
    RI_TERMS    = ["1yr", "3yr"]
    RI_PAYMENTS = ["No Upfront", "Partial Upfront", "All Upfront"]

    for i in range(200):
        itype    = rng_choice(INSTANCE_TYPES_COMPUTE + INSTANCE_TYPES_RDS)
        term     = rng_choice(RI_TERMS)
        payment  = rng_choice(RI_PAYMENTS)
        # Waste pattern: most existing RIs are under-utilised (legacy over-purchase)
        # OR expiring soon (no renewal planned)
        if i < 60:
            utilisation = round(np.random.uniform(5.0, 45.0), 1)  # WASTE: low utilisation
            expiry_offset = int(np.random.randint(1, 45))          # expiring soon
        elif i < 120:
            utilisation = round(np.random.uniform(55.0, 85.0), 1)  # moderate
            expiry_offset = int(np.random.randint(45, 365))
        else:
            utilisation = round(np.random.uniform(85.0, 100.0), 1)  # optimal
            expiry_offset = int(np.random.randint(180, 730))

        expiry = (pd.Timestamp("2024-12-31") + pd.Timedelta(days=expiry_offset))
        od_cost    = round(np.random.uniform(500, 3000), 2)
        ri_cost    = round(od_cost * (0.60 if term == "1yr" else 0.45), 2)
        savings    = round(od_cost - ri_cost, 2)

        rows.append({
            "ri_id":           f"ri-{i:04d}-{np.random.randint(10000,99999)}",
            "instance_type":   itype,
            "term":            term,
            "payment_option":  payment,
            "region":          "ap-south-1",
            "utilisation_pct": utilisation,
            "on_demand_equiv_monthly_usd": od_cost,
            "ri_monthly_cost_usd":         ri_cost,
            "monthly_savings_usd":         savings,
            "expiry_date":     expiry.strftime("%Y-%m-%d"),
            "days_to_expiry":  expiry_offset,
            "status":          (
                "EXPIRING_SOON" if expiry_offset < 45
                else "UNDER_UTILISED" if utilisation < 50
                else "ACTIVE"
            ),
            "recommendation":  (
                "SELL_OR_MODIFY" if utilisation < 30
                else "MONITOR" if utilisation < 50
                else "RENEW" if expiry_offset < 90
                else "HOLD"
            ),
        })
    return pd.DataFrame(rows)


# ==============================================================================
# 7. tag_compliance_report.csv
#    1,500 rows
#    Compliance tags: pci-dss, soc2, rbi-it, gdpr
# ==============================================================================
def generate_tag_compliance_report() -> pd.DataFrame:
    print("  Generating tag_compliance_report.csv (~1,500 rows) ...")
    rows = []
    REQUIRED_TAGS = ["CostCenter", "Environment", "Service", "Owner", "ComplianceScope"]

    for i in range(1500):
        svc  = rng_choice(SERVICES)
        env  = rng_choice(ENVIRONMENTS)
        rtype = rng_choice(RESOURCE_TYPES)
        comp_tags = COMPLIANCE_TAGS.get(svc, [])
        missing = missing_tags_for(svc, env)
        present = [t for t in REQUIRED_TAGS if t not in missing]

        # Compliance tag check
        comp_ok = (len(comp_tags) == 0 or "ComplianceScope" in present)

        rows.append({
            "resource_id":        f"{svc[:8]}-{rtype.lower()[:5]}-{i:05d}",
            "service":            svc,
            "environment":        env,
            "resource_type":      rtype,
            "region":             rng_choice(AWS_REGIONS),
            "required_tags":      "|".join(REQUIRED_TAGS),
            "present_tags":       "|".join(present),
            "missing_tags":       "|".join(missing) if missing else "NONE",
            "compliance_status":  "NON_COMPLIANT" if missing else "COMPLIANT",
            "compliance_frameworks": "|".join(comp_tags) if comp_tags else "NONE",
            "compliance_tag_ok":  comp_ok,
            "remediation_action": (
                "ADD_MISSING_TAGS" if missing else "NO_ACTION"
            ),
        })

    return pd.DataFrame(rows)


# ==============================================================================
# 8. cost_anomaly_events.csv
#    80 rows
#    Anomaly types: SPIKE, SUSTAINED_INCREASE, IDLE_WASTE, ORPHANED_RESOURCE
# ==============================================================================
def generate_cost_anomaly_events() -> pd.DataFrame:
    print("  Generating cost_anomaly_events.csv (~80 rows) ...")
    ANOMALY_TYPES = ["SPIKE", "SUSTAINED_INCREASE", "IDLE_WASTE", "ORPHANED_RESOURCE"]
    ROOT_CAUSES = {
        "SPIKE":               [
            "Unscheduled load test in dev",
            "NAT Gateway data transfer spike",
            "Runaway Lambda recursion",
            "Missing S3 lifecycle policy",
        ],
        "SUSTAINED_INCREASE":  [
            "New feature deployment without rightsizing review",
            "Autoscaling ceiling too high",
            "Staging env cloned from prod, never scaled down",
        ],
        "IDLE_WASTE":          [
            "Dev environment running all weekend",
            "RDS snapshot left from deleted cluster",
            "EBS volumes unattached after EC2 termination",
        ],
        "ORPHANED_RESOURCE":   [
            "Elastic IP not associated after instance stop",
            "Idle ALB with no registered targets",
            "S3 bucket not cleaned after pipeline deletion",
        ],
    }

    rows = []
    dates = pd.date_range("2024-07-01", periods=180, freq="D")
    # Anomaly frequency increases over time (as spend grows)
    anomaly_dates = np.random.choice(dates, size=80, replace=False)
    anomaly_dates.sort()

    for i, date in enumerate(anomaly_dates):
        svc    = rng_choice(SERVICES)
        atype  = rng_choice(ANOMALY_TYPES)
        causes = ROOT_CAUSES[atype]
        cause  = rng_choice(causes)

        expected = round(np.random.uniform(500, 5000), 2)
        if atype == "SPIKE":
            actual = round(expected * np.random.uniform(2.0, 5.0), 2)
        elif atype == "SUSTAINED_INCREASE":
            actual = round(expected * np.random.uniform(1.3, 2.0), 2)
        else:
            actual = round(expected * np.random.uniform(0.8, 1.2), 2)  # idle: similar cost

        delta_pct = round((actual - expected) / expected * 100, 1)

        rows.append({
            "date":              pd.Timestamp(date).strftime("%Y-%m-%d"),
            "service":           svc,
            "anomaly_type":      atype,
            "severity":          "CRITICAL" if delta_pct > 100 else "HIGH" if delta_pct > 50 else "MEDIUM",
            "expected_cost_usd": expected,
            "actual_cost_usd":   actual,
            "delta_pct":         delta_pct,
            "root_cause":        cause,
            "auto_resolved":     random.random() < 0.25,
            "ticket_id":         f"LF-FINOPS-{2000 + i:04d}",
            "region":            "ap-south-1",
        })

    return pd.DataFrame(rows)


# ==============================================================================
# MAIN — write all CSVs
# ==============================================================================
def main():
    print("\n" + "=" * 65)
    print("  LendFlow FinOps — Synthetic Dataset Generator")
    print("  RANDOM_SEED =", RANDOM_SEED)
    print("  Output directory:", DATA_DIR)
    print("=" * 65 + "\n")

    generators = {
        "monthly_cost_summary.csv":      generate_monthly_cost_summary,
        "daily_cost_detail.csv":         generate_daily_cost_detail,
        "instance_utilisation.csv":      generate_instance_utilisation,
        "storage_inventory.csv":         generate_storage_inventory,
        "data_transfer_log.csv":         generate_data_transfer_log,
        "reserved_instance_coverage.csv": generate_reserved_instance_coverage,
        "tag_compliance_report.csv":     generate_tag_compliance_report,
        "cost_anomaly_events.csv":       generate_cost_anomaly_events,
    }

    totals = {}
    for filename, generator_fn in generators.items():
        df = generator_fn()
        out_path = DATA_DIR / filename
        df.to_csv(out_path, index=False)
        totals[filename] = len(df)
        print(f"  [OK] {filename}: {len(df):,} rows -> {out_path}")

    print("\n" + "=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    total_rows = sum(totals.values())
    for fn, rows in totals.items():
        print(f"  {fn:<45} {rows:>7,} rows")
    print(f"  {'TOTAL':<45} {total_rows:>7,} rows")
    print("=" * 65)
    print("\n  All datasets generated successfully.\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
