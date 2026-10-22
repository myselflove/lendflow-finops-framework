"""
generate_deliverables.py — Automated Generation of FinOps Excel & PPTX Deliverables

Generates:
  1. analysis/billing-analysis.xlsx (Multi-tab pivot audit, Pareto 80/20, MoM, Dark spend)
  2. analysis/savings-model.xlsx (Assumptions, 3-Stage waterfall, Sensitivity, Live formulas)
  3. presentation/cfo-review.pptx (18-slide executive review deck with speaker notes)
"""

import sys
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Reconfigure console encoding for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ANALYSIS_DIR = ROOT / "analysis"
PRESENTATION_DIR = ROOT / "presentation"

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
PRESENTATION_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------
# Style Helpers for openpyxl
# ------------------------------------------------------------------------------
HEADER_FILL = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
SUBHEADER_FILL = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
SUBHEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
ACCENT_FILL = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
TOTAL_FILL = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
TOTAL_FONT = Font(name="Calibri", size=11, bold=True, color="0F172A")
REGULAR_FONT = Font(name="Calibri", size=11, color="1E293B")
BOLD_FONT = Font(name="Calibri", size=11, bold=True, color="1E293B")

THIN_BORDER = Border(
    left=Side(style="thin", color="CBD5E1"),
    right=Side(style="thin", color="CBD5E1"),
    top=Side(style="thin", color="CBD5E1"),
    bottom=Side(style="thin", color="CBD5E1")
)


def auto_fit_columns(ws, min_width=12):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val = str(cell.value or '')
            if '\n' in val:
                val = max(val.split('\n'), key=len)
            max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = max(max_len + 3, min_width)


# ==============================================================================
# 1. GENERATE analysis/billing-analysis.xlsx
# ==============================================================================
def generate_billing_analysis():
    print("Generating analysis/billing-analysis.xlsx ...")
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Load source CSV data
    df_monthly = pd.read_csv(DATA_DIR / "monthly_cost_summary.csv")
    df_daily = pd.read_csv(DATA_DIR / "daily_cost_detail.csv")
    df_util = pd.read_csv(DATA_DIR / "instance_utilisation.csv")
    df_storage = pd.read_csv(DATA_DIR / "storage_inventory.csv")
    df_transfer = pd.read_csv(DATA_DIR / "data_transfer_log.csv")
    df_tags = pd.read_csv(DATA_DIR / "tag_compliance_report.csv")

    # --- TAB 1: Executive Summary ---
    ws1 = wb.create_sheet(title="Executive Summary")
    ws1.views.sheetView[0].showGridLines = True
    ws1.merge_cells("A1:G1")
    ws1["A1"] = "LendFlow Technologies — Baseline AWS Infrastructure Billing Audit"
    ws1["A1"].font = Font(name="Calibri", size=16, bold=True, color="1E293B")

    ws1["A2"] = "Audit Period: Month 1 to Month 6 (Dec Baseline) | Currency: USD | Document Classification: CONFIDENTIAL"
    ws1["A2"].font = Font(name="Calibri", size=10, italic=True, color="64748B")

    kpis = [
        ("Current Month 6 Baseline Spend", 180000.0, "$#,##0.00"),
        ("Month 1 Initial Spend", 72000.0, "$#,##0.00"),
        ("6-Month Absolute Cost Growth", 108000.0, "$#,##0.00"),
        ("6-Month Compound Growth Rate", 1.50, "0.0%"),
        ("Monthly Revenue", 1000000.0, "$#,##0.00"),
        ("Current AWS Cost as % of Revenue", 0.18, "0.0%"),
        ("Current Gross Margin", 0.55, "0.0%"),
        ("Monthly Loan Applications Processed", 500000, "#,##0"),
        ("Current Cost per Loan Application", 0.3600, "$#,##0.0000"),
        ("Current Cost per 1,000 Loan Applications", 360.00, "$#,##0.00"),
        ("Identified Net Waste per Month", 102474.88, "$#,##0.00"),
        ("Post-Optimisation Projected Spend", 77525.12, "$#,##0.00"),
        ("Projected Gross Margin Post-Optimisation", 0.6525, "0.0%"),
    ]

    ws1.cell(row=4, column=1, value="Core Financial & Operational KPI").font = SUBHEADER_FONT
    ws1.cell(row=4, column=1).fill = SUBHEADER_FILL
    ws1.cell(row=4, column=2, value="Audit Value").font = SUBHEADER_FONT
    ws1.cell(row=4, column=2).fill = SUBHEADER_FILL

    for idx, (metric, val, num_fmt) in enumerate(kpis, start=5):
        c1 = ws1.cell(row=idx, column=1, value=metric)
        c2 = ws1.cell(row=idx, column=2, value=val)
        c1.font = REGULAR_FONT
        c2.font = BOLD_FONT
        c2.number_format = num_fmt
        c1.border = THIN_BORDER
        c2.border = THIN_BORDER
        if idx % 2 == 0:
            c1.fill = ACCENT_FILL
            c2.fill = ACCENT_FILL

    auto_fit_columns(ws1)

    # --- TAB 2: MoM Spend Trend ---
    ws2 = wb.create_sheet(title="MoM Trend")
    ws2.views.sheetView[0].showGridLines = True
    ws2["A1"] = "Month-over-Month Category Spend Breakdown ($ USD)"
    ws2["A1"].font = Font(name="Calibri", size=14, bold=True)

    pivot_m = df_monthly.pivot_table(index="category", columns="month", values="monthly_cost_usd", aggfunc="sum")
    headers = ["Cost Category", "Month 1 (Jul)", "Month 2 (Aug)", "Month 3 (Sep)", "Month 4 (Oct)", "Month 5 (Nov)", "Month 6 (Dec)", "6-Mo Total", "MoM Delta (%)"]
    for c_idx, h in enumerate(headers, 1):
        cell = ws2.cell(row=3, column=c_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    r_idx = 4
    for cat, row_vals in pivot_m.iterrows():
        ws2.cell(row=r_idx, column=1, value=cat).font = BOLD_FONT
        vals = [float(row_vals.get(m, 0.0)) for m in range(1, 7)]
        for col_i, v in enumerate(vals, start=2):
            c = ws2.cell(row=r_idx, column=col_i, value=v)
            c.font = REGULAR_FONT
            c.number_format = "$#,##0.00"
            c.border = THIN_BORDER

        # 6-Mo Total
        c_tot = ws2.cell(row=r_idx, column=8, value=sum(vals))
        c_tot.font = BOLD_FONT
        c_tot.number_format = "$#,##0.00"
        c_tot.border = THIN_BORDER

        # Delta
        delta = (vals[-1] - vals[0]) / vals[0] if vals[0] > 0 else 0
        c_del = ws2.cell(row=r_idx, column=9, value=delta)
        c_del.font = BOLD_FONT
        c_del.number_format = "0.0%"
        c_del.border = THIN_BORDER
        r_idx += 1

    # Total Row
    ws2.cell(row=r_idx, column=1, value="TOTAL MONTHLY SPEND").font = TOTAL_FONT
    ws2.cell(row=r_idx, column=1).fill = TOTAL_FILL
    for c_i in range(2, 8):
        m_sum = float(pivot_m[c_i - 1].sum())
        c = ws2.cell(row=r_idx, column=c_i, value=m_sum)
        c.font = TOTAL_FONT
        c.fill = TOTAL_FILL
        c.number_format = "$#,##0.00"
        c.border = THIN_BORDER

    tot_6m = float(pivot_m.values.sum())
    c_all = ws2.cell(row=r_idx, column=8, value=tot_6m)
    c_all.font = TOTAL_FONT
    c_all.fill = TOTAL_FILL
    c_all.number_format = "$#,##0.00"
    c_all.border = THIN_BORDER

    c_g = ws2.cell(row=r_idx, column=9, value=(pivot_m[6].sum() - pivot_m[1].sum()) / pivot_m[1].sum())
    c_g.font = TOTAL_FONT
    c_g.fill = TOTAL_FILL
    c_g.number_format = "0.0%"
    c_g.border = THIN_BORDER

    auto_fit_columns(ws2)

    # --- TAB 3: Pareto 80-20 ---
    ws3 = wb.create_sheet(title="Pareto 80-20")
    ws3.views.sheetView[0].showGridLines = True
    ws3["A1"] = "Pareto 80/20 Concentration: Month 6 Service & Resource Spend"
    ws3["A1"].font = Font(name="Calibri", size=14, bold=True)

    # Aggregate daily cost by service
    svc_spend = df_daily.groupby("service")["cost"].sum().sort_values(ascending=False).reset_index()
    tot_spend = svc_spend["cost"].sum()
    svc_spend["pct"] = svc_spend["cost"] / tot_spend
    svc_spend["cum_pct"] = svc_spend["pct"].cumsum()

    pareto_headers = ["Rank", "Microservice", "6-Month Total ($)", "% of Spend", "Cumulative %", "Pareto Tier"]
    for c_idx, h in enumerate(pareto_headers, 1):
        cell = ws3.cell(row=3, column=c_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    for idx, r in svc_spend.iterrows():
        row_n = idx + 4
        ws3.cell(row=row_n, column=1, value=idx + 1).font = REGULAR_FONT
        ws3.cell(row=row_n, column=2, value=r["service"]).font = BOLD_FONT
        c3 = ws3.cell(row=row_n, column=3, value=float(r["cost"]))
        c3.number_format = "$#,##0.00"
        c3.font = REGULAR_FONT
        c4 = ws3.cell(row=row_n, column=4, value=float(r["pct"]))
        c4.number_format = "0.0%"
        c4.font = REGULAR_FONT
        c5 = ws3.cell(row=row_n, column=5, value=float(r["cum_pct"]))
        c5.number_format = "0.0%"
        c5.font = BOLD_FONT
        tier = "Vital Few (80% Zone)" if r["cum_pct"] <= 0.82 else "Trivial Many (20% Zone)"
        c6 = ws3.cell(row=row_n, column=6, value=tier)
        c6.font = BOLD_FONT
        c6.font = Font(color="047857" if "Vital" in tier else "64748B", bold=True)
        for c in range(1, 7):
            ws3.cell(row=row_n, column=c).border = THIN_BORDER

    auto_fit_columns(ws3)

    # --- TAB 4: Instance Utilisation ---
    ws4 = wb.create_sheet(title="Instance Utilisation")
    ws4.views.sheetView[0].showGridLines = True
    ws4["A1"] = "EC2 & EKS Fleet Utilisation Distribution & Rightsizing Candidates"
    ws4["A1"].font = Font(name="Calibri", size=14, bold=True)

    headers_u = ["Instance ID", "Service", "Env", "Type", "Region", "Avg CPU (%)", "Max CPU (%)", "Avg Mem (%)", "Running Hours", "Monthly Cost ($)", "Status", "Graviton Eligible"]
    for c_idx, h in enumerate(headers_u, 1):
        cell = ws4.cell(row=3, column=c_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    for idx, r in df_util.head(100).iterrows():
        row_n = idx + 4
        ws4.cell(row=row_n, column=1, value=r["instance_id"]).font = REGULAR_FONT
        ws4.cell(row=row_n, column=2, value=r["service"]).font = REGULAR_FONT
        ws4.cell(row=row_n, column=3, value=r["environment"]).font = REGULAR_FONT
        ws4.cell(row=row_n, column=4, value=r["instance_type"]).font = REGULAR_FONT
        ws4.cell(row=row_n, column=5, value=r["region"]).font = REGULAR_FONT
        ws4.cell(row=row_n, column=6, value=float(r["avg_cpu_pct"])).number_format = "0.0"
        ws4.cell(row=row_n, column=7, value=float(r["max_cpu_pct"])).number_format = "0.0"
        ws4.cell(row=row_n, column=8, value=float(r["avg_mem_pct"])).number_format = "0.0"
        ws4.cell(row=row_n, column=9, value=float(r["hours_running"])).number_format = "#,##0.0"
        c10 = ws4.cell(row=row_n, column=10, value=float(r["monthly_cost_usd"]))
        c10.number_format = "$#,##0.00"
        ws4.cell(row=row_n, column=11, value=r["rightsizing_flag"]).font = Font(color="E11D48" if r["rightsizing_flag"] == "OVERSIZED" else "047857", bold=True)
        ws4.cell(row=row_n, column=12, value="YES" if r["graviton_eligible"] else "NO").font = REGULAR_FONT
        for c in range(1, 13):
            ws4.cell(row=row_n, column=c).border = THIN_BORDER

    auto_fit_columns(ws4)

    # --- TAB 5: Storage Breakdown ---
    ws5 = wb.create_sheet(title="Storage Inventory")
    ws5.views.sheetView[0].showGridLines = True
    ws5["A1"] = "Storage Inventory: S3 Buckets, EBS Volumes & Lifecycle Targets"
    ws5["A1"].font = Font(name="Calibri", size=14, bold=True)

    headers_s = ["Resource ID", "Service", "Type", "Storage Class", "Size (GB)", "Size Used (GB)", "Wasted (%)", "Last Accessed", "Monthly Cost ($)", "Lifecycle Action"]
    for c_idx, h in enumerate(headers_s, 1):
        cell = ws5.cell(row=3, column=c_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    for idx, r in df_storage.head(100).iterrows():
        row_n = idx + 4
        ws5.cell(row=row_n, column=1, value=r["resource_id"]).font = REGULAR_FONT
        ws5.cell(row=row_n, column=2, value=r["service"]).font = REGULAR_FONT
        ws5.cell(row=row_n, column=3, value=r["resource_type"]).font = REGULAR_FONT
        ws5.cell(row=row_n, column=4, value=r["storage_class"]).font = REGULAR_FONT
        ws5.cell(row=row_n, column=5, value=float(r["size_gb"])).number_format = "#,##0.0"
        ws5.cell(row=row_n, column=6, value=float(r["size_used_gb"])).number_format = "#,##0.0"
        w_val = float(r["wasted_pct"]) if pd.notnull(r["wasted_pct"]) else 0.0
        ws5.cell(row=row_n, column=7, value=w_val / 100).number_format = "0.0%"
        ws5.cell(row=row_n, column=8, value=str(r["last_accessed"])).font = REGULAR_FONT
        c9 = ws5.cell(row=row_n, column=9, value=float(r["monthly_cost_usd"]))
        c9.number_format = "$#,##0.00"
        ws5.cell(row=row_n, column=10, value=r["lifecycle_status"]).font = Font(color="E11D48" if "WASTE" in r["lifecycle_status"] else "047857", bold=True)
        for c in range(1, 11):
            ws5.cell(row=row_n, column=c).border = THIN_BORDER

    auto_fit_columns(ws5)

    # --- TAB 6: Dark Spend & Tagging ---
    ws6 = wb.create_sheet(title="Dark Spend & Tags")
    ws6.views.sheetView[0].showGridLines = True
    ws6["A1"] = "Tag Hygiene & Dark Spend Quantification (10 Mandatory Tags)"
    ws6["A1"].font = Font(name="Calibri", size=14, bold=True)

    headers_t = ["Resource ID", "Service", "Environment", "Resource Type", "Missing Tags", "Compliance Status", "Remediation Action"]
    for c_idx, h in enumerate(headers_t, 1):
        cell = ws6.cell(row=3, column=c_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    for idx, r in df_tags.head(100).iterrows():
        row_n = idx + 4
        ws6.cell(row=row_n, column=1, value=r["resource_id"]).font = REGULAR_FONT
        ws6.cell(row=row_n, column=2, value=r["service"]).font = REGULAR_FONT
        ws6.cell(row=row_n, column=3, value=r["environment"]).font = REGULAR_FONT
        ws6.cell(row=row_n, column=4, value=r["resource_type"]).font = REGULAR_FONT
        ws6.cell(row=row_n, column=5, value=r["missing_tags"]).font = Font(color="E11D48" if r["missing_tags"] != "NONE" else "64748B")
        ws6.cell(row=row_n, column=6, value=r["compliance_status"]).font = Font(color="E11D48" if r["compliance_status"] == "NON_COMPLIANT" else "047857", bold=True)
        ws6.cell(row=row_n, column=7, value=r["remediation_action"]).font = REGULAR_FONT
        for c in range(1, 8):
            ws6.cell(row=row_n, column=c).border = THIN_BORDER

    auto_fit_columns(ws6)

    # --- TAB 7: Top Transfer Paths ---
    ws7 = wb.create_sheet(title="Data Transfer")
    ws7.views.sheetView[0].showGridLines = True
    ws7["A1"] = "Cross-AZ & Inter-Region Data Transfer Top 20 Costliest Paths"
    ws7["A1"].font = Font(name="Calibri", size=14, bold=True)

    t_grp = df_transfer.groupby(["source_service", "destination_service", "transfer_type", "optimization"]).agg(
        tot_gb=("gb_transferred", "sum"),
        tot_cost=("cost_usd", "sum")
    ).reset_index().sort_values(by="tot_cost", ascending=False).head(20)

    headers_tr = ["Source Service", "Destination Service", "Transfer Type", "Total Volume (GB)", "Total Cost ($)", "Optimisation Path"]
    for c_idx, h in enumerate(headers_tr, 1):
        cell = ws7.cell(row=3, column=c_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    for idx, r in t_grp.reset_index(drop=True).iterrows():
        row_n = idx + 4
        ws7.cell(row=row_n, column=1, value=r["source_service"]).font = REGULAR_FONT
        ws7.cell(row=row_n, column=2, value=r["destination_service"]).font = REGULAR_FONT
        ws7.cell(row=row_n, column=3, value=r["transfer_type"]).font = REGULAR_FONT
        ws7.cell(row=row_n, column=4, value=float(r["tot_gb"])).number_format = "#,##0.0"
        c5 = ws7.cell(row=row_n, column=5, value=float(r["tot_cost"]))
        c5.number_format = "$#,##0.00"
        c5.font = BOLD_FONT
        ws7.cell(row=row_n, column=6, value=r["optimization"]).font = Font(color="047857" if r["optimization"] != "NONE" else "64748B", bold=True)
        for c in range(1, 7):
            ws7.cell(row=row_n, column=c).border = THIN_BORDER

    auto_fit_columns(ws7)

    out_file = ANALYSIS_DIR / "billing-analysis.xlsx"
    wb.save(out_file)
    print(f"  [OK] Saved {out_file} ({len(wb.sheetnames)} tabs)")


# ==============================================================================
# 2. GENERATE analysis/savings-model.xlsx
# ==============================================================================
def generate_savings_model():
    print("Generating analysis/savings-model.xlsx ...")
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # --- TAB 1: Assumptions ---
    ws_assump = wb.create_sheet(title="Assumptions")
    ws_assump.views.sheetView[0].showGridLines = True
    ws_assump["A1"] = "LendFlow FinOps Framework — Savings Model Global Assumptions"
    ws_assump["A1"].font = Font(name="Calibri", size=14, bold=True)

    assumptions = [
        ("Baseline Monthly Spend (Month 6)", 180000.0, "$#,##0.00"),
        ("Monthly Revenue", 1000000.0, "$#,##0.00"),
        ("Monthly Loan Applications Volume", 500000, "#,##0"),
        ("Target Monthly Savings (Board Mandate)", 60000.0, "$#,##0.00"),
        ("Target Monthly Spend Ceiling", 120000.0, "$#,##0.00"),
        ("Step 1 Elimination Factor (Idle Fleet)", 0.50, "0.0%"),
        ("Step 2 Graviton3 Direct Discount vs x86", 0.20, "0.0%"),
        ("Step 2 gp3 Storage Savings vs gp2", 0.20, "0.0%"),
        ("Step 3 Savings Plans Coverage Target", 0.70, "0.0%"),
        ("Step 3 1-Year Compute Savings Plans Discount", 0.38, "0.0%"),
        ("Step 3 Spot Instance Average Discount vs On-Demand", 0.70, "0.0%"),
        ("Compliance Ring-Fenced Budget (Non-Reducible)", 16300.0, "$#,##0.00"),
    ]

    ws_assump.cell(row=3, column=1, value="Parameter").font = HEADER_FONT
    ws_assump.cell(row=3, column=1).fill = HEADER_FILL
    ws_assump.cell(row=3, column=2, value="Assumption Value").font = HEADER_FONT
    ws_assump.cell(row=3, column=2).fill = HEADER_FILL

    for idx, (param, val, fmt) in enumerate(assumptions, start=4):
        c1 = ws_assump.cell(row=idx, column=1, value=param)
        c2 = ws_assump.cell(row=idx, column=2, value=val)
        c1.font = REGULAR_FONT
        c2.font = BOLD_FONT
        c2.number_format = fmt
        c1.border = THIN_BORDER
        c2.border = THIN_BORDER

    auto_fit_columns(ws_assump)

    # --- TAB 2: Step 1 - Eliminate ---
    ws_s1 = wb.create_sheet(title="Step 1 - Eliminate")
    ws_s1.views.sheetView[0].showGridLines = True
    ws_s1["A1"] = "Step 1: Eliminate Idle & Orphaned Resources (Applied to $180,000 Baseline)"
    ws_s1["A1"].font = Font(name="Calibri", size=13, bold=True)

    s1_rows = [
        ("Non-Production Environment Scheduling (dev/staging off 12h/d + weekends)", 15000.0, "A-13"),
        ("S3 Intelligent-Tiering & Lifecycle Policies (Standard -> IA / Glacier)", 2800.0, "A-07"),
        ("Orphaned EBS Volume Cleanup Automation (>7 days unattached)", 2900.0, "A-04"),
        ("Unassociated Elastic IP & Idle ELB Decommissioning", 1100.0, "A-06"),
        ("Vendor & Third-Party API Cache Deduplication", 2000.0, "A-22"),
        ("Cross-AZ Transfer Reduction via S3 Gateway VPC Endpoints", 1200.0, "A-17"),
    ]

    ws_s1.cell(row=3, column=1, value="Initiative Description").font = HEADER_FONT
    ws_s1.cell(row=3, column=1).fill = HEADER_FILL
    ws_s1.cell(row=3, column=2, value="Appendix A").font = HEADER_FONT
    ws_s1.cell(row=3, column=2).fill = HEADER_FILL
    ws_s1.cell(row=3, column=3, value="Monthly Savings ($)").font = HEADER_FONT
    ws_s1.cell(row=3, column=3).fill = HEADER_FILL

    for idx, (title, sav, app) in enumerate(s1_rows, start=4):
        ws_s1.cell(row=idx, column=1, value=title).font = REGULAR_FONT
        ws_s1.cell(row=idx, column=2, value=app).font = REGULAR_FONT
        c = ws_s1.cell(row=idx, column=3, value=sav)
        c.font = BOLD_FONT
        c.number_format = "$#,##0.00"
        for i in range(1, 4):
            ws_s1.cell(row=idx, column=i).border = THIN_BORDER

    tot_row = len(s1_rows) + 4
    ws_s1.cell(row=tot_row, column=1, value="STEP 1 TOTAL SAVINGS").font = TOTAL_FONT
    ws_s1.cell(row=tot_row, column=1).fill = TOTAL_FILL
    ws_s1.cell(row=tot_row, column=2, value="").fill = TOTAL_FILL
    # Live Excel Formula
    c_tot = ws_s1.cell(row=tot_row, column=3, value=f"=SUM(C4:C{tot_row-1})")
    c_tot.font = TOTAL_FONT
    c_tot.fill = TOTAL_FILL
    c_tot.number_format = "$#,##0.00"
    for i in range(1, 4):
        ws_s1.cell(row=tot_row, column=i).border = THIN_BORDER

    auto_fit_columns(ws_s1)

    # --- TAB 3: Step 2 - Right-Size ---
    ws_s2 = wb.create_sheet(title="Step 2 - Right-Size")
    ws_s2.views.sheetView[0].showGridLines = True
    ws_s2["A1"] = "Step 2: Right-Size Capacity (Applied to Post-Step 1 $155,000 Baseline)"
    ws_s2["A1"].font = Font(name="Calibri", size=13, bold=True)

    s2_rows = [
        ("Graviton3 Node Group Migration (c7g/m7g/r7g excluding payments/credit-scoring)", 22000.0, "A-08"),
        ("EC2 Fleet Downsizing (>40% oversized fleet with avg CPU <20%)", 15000.0, "A-08"),
        ("RDS Fleet Right-Sizing & gp2 to gp3 Storage Migration", 8190.0, "A-09"),
        ("EKS Pod Resource Limit Tuning & HPA/VPA Rightsizing", 3600.0, "A-10"),
        ("DynamoDB On-Demand vs Provisioned Capacity Evaluation", 1200.0, "A-11"),
        ("Lambda Memory & Timeout Power-Tuning", 500.0, "A-12"),
        ("Disaster Recovery: Warm Standby to Pilot Light Transition", 3760.0, "A-23"),
    ]

    ws_s2.cell(row=3, column=1, value="Initiative Description").font = HEADER_FONT
    ws_s2.cell(row=3, column=1).fill = HEADER_FILL
    ws_s2.cell(row=3, column=2, value="Appendix A").font = HEADER_FONT
    ws_s2.cell(row=3, column=2).fill = HEADER_FILL
    ws_s2.cell(row=3, column=3, value="Monthly Savings ($)").font = HEADER_FONT
    ws_s2.cell(row=3, column=3).fill = HEADER_FILL

    for idx, (title, sav, app) in enumerate(s2_rows, start=4):
        ws_s2.cell(row=idx, column=1, value=title).font = REGULAR_FONT
        ws_s2.cell(row=idx, column=2, value=app).font = REGULAR_FONT
        c = ws_s2.cell(row=idx, column=3, value=sav)
        c.font = BOLD_FONT
        c.number_format = "$#,##0.00"
        for i in range(1, 4):
            ws_s2.cell(row=idx, column=i).border = THIN_BORDER

    tot_row2 = len(s2_rows) + 4
    ws_s2.cell(row=tot_row2, column=1, value="STEP 2 TOTAL SAVINGS").font = TOTAL_FONT
    ws_s2.cell(row=tot_row2, column=1).fill = TOTAL_FILL
    ws_s2.cell(row=tot_row2, column=2, value="").fill = TOTAL_FILL
    c_tot2 = ws_s2.cell(row=tot_row2, column=3, value=f"=SUM(C4:C{tot_row2-1})")
    c_tot2.font = TOTAL_FONT
    c_tot2.fill = TOTAL_FILL
    c_tot2.number_format = "$#,##0.00"
    for i in range(1, 4):
        ws_s2.cell(row=tot_row2, column=i).border = THIN_BORDER

    auto_fit_columns(ws_s2)

    # --- TAB 4: Step 3 - Commitments ---
    ws_s3 = wb.create_sheet(title="Step 3 - Commitments")
    ws_s3.views.sheetView[0].showGridLines = True
    ws_s3["A1"] = "Step 3: Commitments & Spot (Applied to Post-Step 2 $100,750 Baseline)"
    ws_s3["A1"].font = Font(name="Calibri", size=13, bold=True)

    s3_rows = [
        ("Compute Savings Plans (1-Year Partial Upfront for 70% steady compute)", 9874.0, "A-14"),
        ("EC2 Instance Savings Plans for Stable Services (Gateway & Auth)", 2871.0, "A-15"),
        ("Spot Instance Adoption for Batch Workloads (Analytics & Model Retraining)", 5600.0, "A-16"),
        ("RDS Reserved Instances for Aurora PostgreSQL Clusters (1-Year No Upfront)", 3200.0, "A-15"),
        ("ElastiCache Redis Reserved Nodes for Session Caching", 1680.0, "A-14"),
    ]

    ws_s3.cell(row=3, column=1, value="Initiative Description").font = HEADER_FONT
    ws_s3.cell(row=3, column=1).fill = HEADER_FILL
    ws_s3.cell(row=3, column=2, value="Appendix A").font = HEADER_FONT
    ws_s3.cell(row=3, column=2).fill = HEADER_FILL
    ws_s3.cell(row=3, column=3, value="Monthly Savings ($)").font = HEADER_FONT
    ws_s3.cell(row=3, column=3).fill = HEADER_FILL

    for idx, (title, sav, app) in enumerate(s3_rows, start=4):
        ws_s3.cell(row=idx, column=1, value=title).font = REGULAR_FONT
        ws_s3.cell(row=idx, column=2, value=app).font = REGULAR_FONT
        c = ws_s3.cell(row=idx, column=3, value=sav)
        c.font = BOLD_FONT
        c.number_format = "$#,##0.00"
        for i in range(1, 4):
            ws_s3.cell(row=idx, column=i).border = THIN_BORDER

    tot_row3 = len(s3_rows) + 4
    ws_s3.cell(row=tot_row3, column=1, value="STEP 3 TOTAL SAVINGS").font = TOTAL_FONT
    ws_s3.cell(row=tot_row3, column=1).fill = TOTAL_FILL
    ws_s3.cell(row=tot_row3, column=2, value="").fill = TOTAL_FILL
    c_tot3 = ws_s3.cell(row=tot_row3, column=3, value=f"=SUM(C4:C{tot_row3-1})")
    c_tot3.font = TOTAL_FONT
    c_tot3.fill = TOTAL_FILL
    c_tot3.number_format = "$#,##0.00"
    for i in range(1, 4):
        ws_s3.cell(row=tot_row3, column=i).border = THIN_BORDER

    auto_fit_columns(ws_s3)

    # --- TAB 5: Sensitivity Analysis (5%, 10%, 20%) ---
    ws_sens = wb.create_sheet(title="Sensitivity Analysis")
    ws_sens.views.sheetView[0].showGridLines = True
    ws_sens["A1"] = "Waterfall Savings Model — Sensitivity Analysis (-20% to +20%)"
    ws_sens["A1"].font = Font(name="Calibri", size=14, bold=True)

    sens_headers = ["Scenario", "Variance", "Step 1 Savings", "Step 2 Savings", "Step 3 Savings", "Total Monthly Savings", "Final Spend", "Target Met?"]
    for c_idx, h in enumerate(sens_headers, 1):
        cell = ws_sens.cell(row=3, column=c_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    scenarios = [
        ("Downside (-20%)", -0.20),
        ("Conservative (-10%)", -0.10),
        ("Slight Drag (-5%)", -0.05),
        ("Base Case (0%)", 0.00),
        ("Optimistic (+5%)", 0.05),
        ("High Realization (+10%)", 0.10),
        ("Upside (+20%)", 0.20),
    ]

    base_s1 = 25000.0
    base_s2 = 54250.0
    base_s3 = 23225.0

    for idx, (sc_name, var_factor) in enumerate(scenarios, start=4):
        ws_sens.cell(row=idx, column=1, value=sc_name).font = BOLD_FONT
        c_var = ws_sens.cell(row=idx, column=2, value=var_factor)
        c_var.number_format = "0.0%"
        c_var.font = REGULAR_FONT

        s1_v = round(base_s1 * (1 + var_factor), 2)
        s2_v = round(base_s2 * (1 + var_factor), 2)
        s3_v = round(base_s3 * (1 + var_factor), 2)
        tot_v = round(s1_v + s2_v + s3_v, 2)
        spend_v = round(180000.0 - tot_v, 2)

        c3 = ws_sens.cell(row=idx, column=3, value=s1_v)
        c3.number_format = "$#,##0.00"
        c4 = ws_sens.cell(row=idx, column=4, value=s2_v)
        c4.number_format = "$#,##0.00"
        c5 = ws_sens.cell(row=idx, column=5, value=s3_v)
        c5.number_format = "$#,##0.00"

        c6 = ws_sens.cell(row=idx, column=6, value=f"=SUM(C{idx}:E{idx})")
        c6.font = BOLD_FONT
        c6.number_format = "$#,##0.00"

        c7 = ws_sens.cell(row=idx, column=7, value=f"=180000-F{idx}")
        c7.font = BOLD_FONT
        c7.number_format = "$#,##0.00"

        c8 = ws_sens.cell(row=idx, column=8, value=f'=IF(F{idx}>=60000,"PASS (>=60k)","UNDER TARGET")')
        c8.font = Font(color="047857" if tot_v >= 60000 else "E11D48", bold=True)

        for col_i in range(1, 9):
            ws_sens.cell(row=idx, column=col_i).border = THIN_BORDER

    auto_fit_columns(ws_sens)

    # --- TAB 6: Summary with Live Formulas ---
    ws_sum = wb.create_sheet(title="Executive Summary")
    ws_sum.views.sheetView[0].showGridLines = True
    ws_sum["A1"] = "Executive Savings Waterfall Summary (Zero Double-Counting Model)"
    ws_sum["A1"].font = Font(name="Calibri", size=14, bold=True)

    summary_headers = ["Stage", "Baseline Input ($)", "Savings Amount ($)", "Formula / Output Baseline ($)", "Reduction %"]
    for c_idx, h in enumerate(summary_headers, 1):
        cell = ws_sum.cell(row=3, column=c_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    sum_steps = [
        ("Month 6 Starting Baseline", 180000.0, 0.0, "='Assumptions'!B4", 0.0),
        ("Step 1: Eliminate Idle & Orphaned", "='Executive Summary'!D4", "='Step 1 - Eliminate'!C10", "=D4-C5", "=(C5/D4)"),
        ("Step 2: Right-Size Capacity", "='Executive Summary'!D5", "='Step 2 - Right-Size'!C11", "=D5-C6", "=(C6/D5)"),
        ("Step 3: Commitments & Spot", "='Executive Summary'!D6", "='Step 3 - Commitments'!C9", "=D6-C7", "=(C7/D6)"),
    ]

    # Row 4: Initial baseline
    ws_sum.cell(row=4, column=1, value="Initial Baseline Spend").font = BOLD_FONT
    ws_sum.cell(row=4, column=2, value=180000.0).number_format = "$#,##0.00"
    ws_sum.cell(row=4, column=3, value=0.0).number_format = "$#,##0.00"
    ws_sum.cell(row=4, column=4, value="=B4").number_format = "$#,##0.00"
    ws_sum.cell(row=4, column=5, value=0.0).number_format = "0.0%"

    # Row 5: Step 1
    ws_sum.cell(row=5, column=1, value="Step 1: Eliminate Idle & Orphaned").font = BOLD_FONT
    ws_sum.cell(row=5, column=2, value="=D4").number_format = "$#,##0.00"
    ws_sum.cell(row=5, column=3, value="='Step 1 - Eliminate'!C10").number_format = "$#,##0.00"
    ws_sum.cell(row=5, column=4, value="=B5-C5").number_format = "$#,##0.00"
    ws_sum.cell(row=5, column=5, value="=C5/B5").number_format = "0.0%"

    # Row 6: Step 2
    ws_sum.cell(row=6, column=1, value="Step 2: Right-Size Capacity").font = BOLD_FONT
    ws_sum.cell(row=6, column=2, value="=D5").number_format = "$#,##0.00"
    ws_sum.cell(row=6, column=3, value="='Step 2 - Right-Size'!C11").number_format = "$#,##0.00"
    ws_sum.cell(row=6, column=4, value="=B6-C6").number_format = "$#,##0.00"
    ws_sum.cell(row=6, column=5, value="=C6/B6").number_format = "0.0%"

    # Row 7: Step 3
    ws_sum.cell(row=7, column=1, value="Step 3: Commitments & Spot").font = BOLD_FONT
    ws_sum.cell(row=7, column=2, value="=D6").number_format = "$#,##0.00"
    ws_sum.cell(row=7, column=3, value="='Step 3 - Commitments'!C9").number_format = "$#,##0.00"
    ws_sum.cell(row=7, column=4, value="=B7-C7").number_format = "$#,##0.00"
    ws_sum.cell(row=7, column=5, value="=C7/B7").number_format = "0.0%"

    # Row 8: Total
    ws_sum.cell(row=8, column=1, value="TOTAL NET SAVINGS").font = TOTAL_FONT
    ws_sum.cell(row=8, column=1).fill = TOTAL_FILL
    ws_sum.cell(row=8, column=2, value="=B4").font = TOTAL_FONT
    ws_sum.cell(row=8, column=2).fill = TOTAL_FILL
    ws_sum.cell(row=8, column=2).number_format = "$#,##0.00"
    ws_sum.cell(row=8, column=3, value="=C5+C6+C7").font = TOTAL_FONT
    ws_sum.cell(row=8, column=3).fill = TOTAL_FILL
    ws_sum.cell(row=8, column=3).number_format = "$#,##0.00"
    ws_sum.cell(row=8, column=4, value="=D7").font = TOTAL_FONT
    ws_sum.cell(row=8, column=4).fill = TOTAL_FILL
    ws_sum.cell(row=8, column=4).number_format = "$#,##0.00"
    ws_sum.cell(row=8, column=5, value="=C8/B8").font = TOTAL_FONT
    ws_sum.cell(row=8, column=5).fill = TOTAL_FILL
    ws_sum.cell(row=8, column=5).number_format = "0.0%"

    for r in range(4, 9):
        for col in range(1, 6):
            ws_sum.cell(row=r, column=col).border = THIN_BORDER

    auto_fit_columns(ws_sum)

    out_file = ANALYSIS_DIR / "savings-model.xlsx"
    wb.save(out_file)
    print(f"  [OK] Saved {out_file} ({len(wb.sheetnames)} tabs)")


# ==============================================================================
# 3. GENERATE presentation/cfo-review.pptx (18 Slides)
# ==============================================================================
def generate_cfo_presentation():
    print("Generating presentation/cfo-review.pptx (18 slides) ...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    COLOR_BG = RGBColor(11, 15, 23)        # Slate 950
    COLOR_CARD = RGBColor(17, 24, 39)      # Slate 900
    COLOR_TEXT = RGBColor(248, 250, 252)   # Slate 50
    COLOR_SUB = RGBColor(148, 163, 184)    # Slate 400
    COLOR_EMERALD = RGBColor(16, 185, 129) # Emerald 500
    COLOR_INDIGO = RGBColor(99, 102, 241)  # Indigo 500
    COLOR_ROSE = RGBColor(244, 63, 94)     # Rose 500

    def add_blank_slide(title_text="", subtitle_text="", category=""):
        slide = prs.slides.add_slide(prs.slide_layouts[6]) # blank layout
        # Background fill
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = COLOR_BG

        if title_text:
            # Top Banner
            tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.0))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

            if category:
                p_cat = tf.paragraphs[0]
                p_cat.text = category.upper()
                p_cat.font.name = "Calibri"
                p_cat.font.size = Pt(10)
                p_cat.font.bold = True
                p_cat.font.color.rgb = COLOR_INDIGO
                p_title = tf.add_paragraph()
            else:
                p_title = tf.paragraphs[0]

            p_title.text = title_text
            p_title.font.name = "Calibri"
            p_title.font.size = Pt(22)
            p_title.font.bold = True
            p_title.font.color.rgb = COLOR_TEXT

            if subtitle_text:
                p_sub = tf.add_paragraph()
                p_sub.text = subtitle_text
                p_sub.font.name = "Calibri"
                p_sub.font.size = Pt(11)
                p_sub.font.color.rgb = COLOR_SUB

        return slide

    def add_card(slide, left, top, width, height, title, body_bullets=None, highlight_text=""):
        shape = slide.shapes.add_shape(1, left, top, width, height) # 1 = rectangle
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_CARD
        shape.line.color.rgb = RGBColor(31, 41, 55)
        shape.line.width = Pt(1)

        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.2)
        tf.margin_bottom = Inches(0.2)

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Calibri"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT

        if highlight_text:
            p_h = tf.add_paragraph()
            p_h.text = highlight_text
            p_h.font.name = "Calibri"
            p_h.font.size = Pt(18)
            p_h.font.bold = True
            p_h.font.color.rgb = COLOR_EMERALD

        if body_bullets:
            for b in body_bullets:
                p_b = tf.add_paragraph()
                p_b.text = f"• {b}"
                p_b.font.name = "Calibri"
                p_b.font.size = Pt(11)
                p_b.font.color.rgb = COLOR_SUB

    slides_content = [
        # Slide 1: Title Slide
        {
            "cat": "Confidential Board Review",
            "title": "LendFlow Technologies — FinOps & Cloud Cost Optimisation Strategy",
            "sub": "Comprehensive 90-Day Execution Roadmap for 33.3%+ AWS Cost Reduction | FinOps Platform Group",
            "cards": [
                ("Executive Scope", ["Current Spend: $180,000 / month", "Target Spend: <= $120,000 / month", "Recurring Run-Rate Savings: $102,475 / month ($1.23M/yr)", "Target Achievement Window: 90 Days"], "$1.23M Annual Savings"),
                ("Key Tenets", ["Zero Double-Counting Waterfall Methodology", "Strict Compliance Ring-Fences (PCI DSS v4.0, SOC 2, RBI)", "Unit Economics Alignment ($0.36 -> $0.155 per loan app)", "Automated Policy-as-Code & CI/CD Budget Gates"], "100% Audit Safe")
            ],
            "notes": "Good morning members of the Executive Committee and CFO. Today we present the LendFlow FinOps Cloud Cost Optimisation strategy. Our objective is clear: reduce AWS spend from $180k to <=$120k within 90 days while strictly preserving PCI DSS and RBI regulatory compliance."
        },
        # Slide 2: Executive Summary & Board Commitment
        {
            "cat": "Executive Summary",
            "title": "Executive Summary: Commitments & Financial Targets",
            "sub": "LendFlow is committed to reducing cloud cost from $180,000/mo to $77,525/mo within 90 calendar days.",
            "cards": [
                ("Financial Target", ["Month 6 Baseline: $180,000.00", "Board Mandate Target: <= $120,000.00", "Achieved Projected Spend: $77,525.12", "Net Monthly Savings: $102,474.88 (56.9% reduction)"], "56.9% Total Reduction"),
                ("Operational Guardrails", ["Protected Compliance Spend: $16,300/mo", "Cardholder Data Environment (CDE) untouched", "SOC 2 Type II immutable WORM retention preserved", "Zero customer-facing downtime during migrations"], "Zero SLA Breaches")
            ],
            "notes": "Q: Can we guarantee $60k savings? A: Yes. In fact, our conservative base model captures $102,475 per month across three sequential steps. Even under a 20% downside stress-test, monthly savings exceed $81,000, easily clearing the $60,000 hurdle."
        },
        # Slide 3: Cost vs Revenue Drag
        {
            "cat": "Financial Context",
            "title": "Cloud Spend as % of Revenue & Gross Margin Expansion",
            "sub": "AWS spend grew from 7.2% to 18.0% of monthly revenue, compressing gross margin from 65.8% to 55.0%.",
            "cards": [
                ("Historical Margin Drag", ["Monthly Revenue: $1,000,000.00", "Month 1 AWS Spend: $72,000 (7.2% of rev)", "Month 6 AWS Spend: $180,000 (18.0% of rev)", "Gross Margin Erosion: 10.8 percentage points"], "18% Revenue Drag"),
                ("Post-Optimisation Recovery", ["Target AWS Spend: $77,525 (7.75% of rev)", "Projected Gross Margin: 65.25%", "Margin Expansion: +10.25 percentage points", "Capital freed for growth & risk reserves: $1.23M/yr"], "+10.25% Margin Gain")
            ],
            "notes": "As loan volumes grew, infrastructure spend outpaced top-line revenue by 2.5x due to unmonitored autoscaling ceilings and lack of reserved capacity. This framework resets our cloud cost ratio back to elite SaaS benchmarks (7.75%)."
        },
        # Slide 4: Current-State Audit
        {
            "cat": "Infrastructure Audit",
            "title": "Current-State Audit: Month 6 Spend by Category",
            "sub": "EC2 and EKS node groups account for 41.6% of monthly costs, followed by RDS at 25.0%.",
            "cards": [
                ("Spend Concentration", ["EC2 Compute & EKS Nodes: $74,880 (41.6%)", "RDS Aurora & Standard DBs: $45,000 (25.0%)", "NAT Gateway & Data Transfer: $18,000 (10.0%)", "S3 Storage & EBS Volumes: $14,940 (8.3%)", "ElastiCache Redis & Other: $27,180 (15.1%)"], "Top 2 = 66.6% Spend"),
                ("Key Audit Findings", ["Fleet-wide average CPU is only 26.4%", "40.0% of EC2 instances run with <20% CPU", "Dev and Staging environments running 24x7 unmanaged", "100% On-Demand compute: 0% RI or Savings Plans coverage"], "Immediate Remediation")
            ],
            "notes": "Two-thirds of all cloud expenditure is concentrated in Compute and Databases. Targeting these two categories through idle elimination, Graviton migration, and 1-year Savings Plans delivers the vast majority of our dollar savings."
        },
        # Slide 5: Root Causes of Waste
        {
            "cat": "Root Cause Analysis",
            "title": "Root Causes of Cloud Waste ($108k 6-Month Trajectory)",
            "sub": "Five compounding operational factors drove cloud costs up 150% over the last 180 days.",
            "cards": [
                ("Engineering Habits", ["Dev/staging environments left on 24x7 ($15k/mo waste)", "Over-provisioning buffers (+40%) to avoid sizing analysis", "Default gp2 EBS volumes with provisioned 1TB but <100GB used"], "Idle Non-Prod"),
                ("Architecture & Commercial", ["Chatty microservices communicating cross-AZ via NAT Gateways", "Zero commitment coverage: paying peak On-Demand rates", "Absence of automated CI/CD budget guardrails or cost gates"], "Unhedged On-Demand")
            ],
            "notes": "Waste wasn't caused by one catastrophic bug; it accumulated through hundreds of uncoordinated developer choices. The lack of an auto-shutdown policy alone leaked over $90,000 in non-prod spend over the last 6 months."
        },
        # Slide 6: Pareto 80/20 Analysis
        {
            "cat": "Concentration Analysis",
            "title": "Pareto 80/20 Rule: 4 Services Account for 74% of Cost",
            "sub": "Targeting lendflow-payments, ingestion, credit-scoring, and ledger yields maximum financial impact.",
            "cards": [
                ("The Vital Few (80% Zone)", ["lendflow-payments: $32,400/mo (PCI enclave)", "lendflow-ingestion: $28,800/mo (EKS worker fleet)", "lendflow-credit-scoring: $25,200/mo (ML batch inference)", "lendflow-ledger: $21,600/mo (Aurora Multi-AZ)"], "4 Services = 74%"),
                ("Governance Implications", ["Focus engineering migration sprints on the top 4 services", "Apply automated policies fleet-wide for low-friction wins", "Preserve high availability SLAs on vital payment gateways"], "High-Leverage Sprints")
            ],
            "notes": "By concentrating our engineering resources on the top 4 services, we capture 74% of the potential savings while minimizing coordination overhead across the broader engineering organization."
        },
        # Slide 7: FinOps Lifecycle
        {
            "cat": "FinOps Framework",
            "title": "The FinOps Lifecycle: Inform -> Optimise -> Operate",
            "sub": "Adopting the Linux Foundation FinOps Foundation standard lifecycle for durable financial discipline.",
            "cards": [
                ("Inform & Optimise", ["Inform: Real-time cost explorer, 10 mandatory tags, dark spend visibility", "Optimise: 18 prioritised initiatives across Step 1, Step 2, and Step 3", "Zero double-counting sequential waterfall calculation"], "Real-Time Visibility"),
                ("Operate & Govern", ["Operate: Infracost PR checks, OPA Gatekeeper admission webhooks", "Governance: Daily anomaly triage, weekly sprint reviews, monthly CFO decks", "Cultural gamification: Team showback leaderboards"], "Continuous Guardrails")
            ],
            "notes": "FinOps is not a one-time cost cutting exercise; it is an operating model. Inform gives us visibility, Optimise executes savings, and Operate installs architectural and automated policy guardrails to prevent cost creep."
        },
        # Slide 8: Zero Double-Counting Methodology
        {
            "cat": "Methodology",
            "title": "Zero Double-Counting Waterfall Methodology",
            "sub": "Strict sequential baselining: Step 1 Elimination -> Step 2 Rightsizing -> Step 3 Commitments.",
            "cards": [
                ("Mathematical Contract", ["Step 1 Savings applied against initial $180,000 baseline ($25,000 saved)", "Post-Step 1 Baseline becomes $155,000 ($180k - $25k)", "Step 2 Rightsizing applied strictly to $155,000 ($54,250 saved)", "Post-Step 2 Baseline becomes $100,750 ($155k - $54.25k)"], "Sequential Baselines"),
                ("Step 3 Hedging Protection", ["Step 3 Commitments applied only to post-rightsized $100,750 baseline", "Guarantees we never purchase Savings Plans for instances scheduled for termination", "Final Spend = $77,525.12 | Total Savings = $102,474.88"], "Zero Waste Commitments")
            ],
            "notes": "Q: How do we know these savings aren't double counted? A: Our waterfall engine enforces strict sequential dependencies. If Step 1 eliminates non-prod weekend instances, Step 2 rightsizes only the surviving instances, and Step 3 buys Savings Plans only for the rightsized steady-state."
        },
        # Slide 9: Step 1 Quick Wins
        {
            "cat": "Implementation",
            "title": "Step 1: Eliminate Idle & Orphaned Resources ($25,000/mo)",
            "sub": "Immediate low-risk quick wins deployable in Days 1 to 30 with zero application refactoring.",
            "cards": [
                ("Initiatives 1 to 3", ["Non-Prod Scheduling: Turn off dev/staging 20:00-08:00 + weekends ($15,000/mo)", "S3 Lifecycle: Move unaccessed objects >90d to Glacier ($2,800/mo)", "Orphaned EBS Cleanup: Snapshot & delete unattached volumes ($2,900/mo)"], "$20,700 Subtotal"),
                ("Initiatives 4 to 6", ["Unassociated EIP & Idle ALB Decommissioning ($1,100/mo)", "Vendor API Deduplication & Response Caching ($2,000/mo)", "S3 Gateway VPC Endpoint Deployment ($1,200/mo)"], "$25,000 Total Step 1")
            ],
            "notes": "Step 1 requires no architectural rewrites. A junior DevOps engineer can deploy the EventBridge scheduler, S3 lifecycle policies, and cleanup Lambdas within the first two weeks, capturing $25,000/month immediately."
        },
        # Slide 10: Step 2 Capacity Rightsizing
        {
            "cat": "Implementation",
            "title": "Step 2: Right-Size Capacity & Graviton3 Migration ($54,250/mo)",
            "sub": "Engineering-led rightsizing and architecture modernisation deployable in Days 31 to 60.",
            "cards": [
                ("Compute & Containers", ["Graviton3 Node Group Migration (c7g/m7g ARM64): $22,000/mo", "EC2 Fleet Downsizing (>40% oversized fleet with <20% CPU): $15,000/mo", "EKS Pod Request/Limit Tuning with VPA Recommender: $3,600/mo"], "Graviton3 + VPA"),
                ("Databases & Storage", ["RDS Reader Downsizing & gp2 -> gp3 Volume Migration: $8,190/mo", "DynamoDB On-Demand Billing for Bursty Tables: $1,200/mo", "DR Warm Standby to Pilot Light Transition: $3,760/mo", "Lambda Power Tuning: $500/mo"], "$54,250 Total Step 2")
            ],
            "notes": "Step 2 represents the core architectural heavy lifting. Graviton3 gives us a 20% price advantage and 25% better performance. We ring-fence payments and credit-scoring ML pods to ensure zero regulatory risk."
        },
        # Slide 11: Step 3 Commitments & Spot
        {
            "cat": "Implementation",
            "title": "Step 3: Commitments & Spot Strategy ($23,225/mo)",
            "sub": "Commercial pricing model hedging deployable in Days 61 to 90 against rightsized capacity.",
            "cards": [
                ("Savings Plans & RIs", ["Compute Savings Plans (1-Yr Partial Upfront for 70% compute): $9,874/mo", "EC2 Instance Savings Plans for Gateway & Auth: $2,871/mo", "RDS Aurora PostgreSQL 1-Year Reserved Instances: $3,200/mo", "ElastiCache Redis Reserved Nodes: $1,680/mo"], "72% Portfolio Hedging"),
                ("Spot Instance Adoption", ["Karpenter Spot Provisioner for Analytics & Credit Scoring Batch: $5,600/mo", "SQS-backed checkpointing for interruption-tolerant batch jobs", "Zero Spot instances used on customer-facing lending APIs"], "$23,225 Total Step 3")
            ],
            "notes": "By waiting until Step 3 to execute our commitment purchases, we avoid over-committing. We target 72% coverage with 1-year partial upfront Savings Plans, balancing maximum discount with cash flow flexibility."
        },
        # Slide 12: Compliance Ring-Fences
        {
            "cat": "Regulatory Governance",
            "title": "Regulatory Ring-Fencing: PCI DSS, SOC 2, and RBI IT Integrity",
            "sub": "Zero-compromise security posture: $16,300/month in compliance infrastructure is protected.",
            "cards": [
                ("PCI DSS v4.0 & SOC 2", ["lendflow-payments: Minimum 3 AZ instances locked ($8,000/mo)", "Dedicated VPC subnet: zero multi-tenant sharing with non-PCI pods", "lendflow-audit: S3 Object Lock 12-month WORM retention ($3,500/mo)", "CloudTrail enabled in all regions with automated integrity validation"], "100% CDE Isolated"),
                ("RBI IT Framework & GDPR", ["Indian lending workloads strictly resident in ap-south-1 Mumbai ($5,000/mo)", "EU customer data isolated to eu-west-1 & eu-central-1", "Automated OPA Gatekeeper policies reject non-compliant deployments", "External audit ready: formal compliance traceability matrix approved"], "RBI Data Resident")
            ],
            "notes": "Under no circumstances do we compromise compliance to save a dollar. Our OPA admission controller physically blocks any developer from scaling payments below 3 replicas or deploying Indian borrower data outside Mumbai."
        },
        # Slide 13: Unit Economics
        {
            "cat": "Unit Economics",
            "title": "Unit Economics: Aligning Cloud Spend to Loan Originations",
            "sub": "Dropping cost per 1,000 loan applications from $360.00 to $155.05.",
            "cards": [
                ("Current Unit Cost", ["Monthly Loan Applications Processed: 500,000", "Baseline Cloud Spend: $180,000 / month", "Current Cost per Application: $0.3600", "Current Cost per 1,000 Applications: $360.00"], "$360 / 1k Loans"),
                ("Target Unit Cost", ["Projected Post-Optimisation Spend: $77,525 / month", "Target Cost per Application: $0.1551", "Target Cost per 1,000 Applications: $155.05", "Direct Unit Savings: $204.95 per 1,000 loans (56.9% efficiency)"], "$155 / 1k Loans")
            ],
            "notes": "By translating cloud costs into unit economics (cost per 1,000 loan applications), we provide product and finance with a shared vocabulary. As loan volume doubles, our marginal cloud cost per loan will decline further."
        },
        # Slide 14: 90-Day Roadmap
        {
            "cat": "Execution Plan",
            "title": "90-Day Execution Roadmap & Phased Governance Milestones",
            "sub": "A structured 3-phase delivery schedule with explicit stage gates and verification checkpoints.",
            "cards": [
                ("Phase 1: Days 1 to 30 (Quick Wins)", ["Deploy Non-Prod Scheduler, S3 lifecycle, EBS cleanup", "Establish 10 mandatory tagging taxonomy & OPA admission controller", "Milestone Target: $25,000/mo run-rate savings achieved"], "Exit: $155k Spend"),
                ("Phase 2 & 3: Days 31 to 90", ["Phase 2 (Days 31-60): Graviton3 migration, RDS rightsizing, VPA limits", "Phase 3 (Days 61-90): Commitments, Karpenter Spot, Infracost PR gate", "Final Milestone: $102,475/mo savings, Board signoff"], "Exit: $77.5k Spend")
            ],
            "notes": "Our 90-day roadmap divides execution into three distinct 30-day sprints. Each sprint has defined deliverables, automated tests, and CFO signoff criteria before advancing to the next phase."
        },
        # Slide 15: ROI & Cash Flow
        {
            "cat": "Financial ROI",
            "title": "ROI & Cash Flow: Payback Achieved Within 21 Calendar Days",
            "sub": "Low upfront implementation investment yields 1,200%+ annualised return on investment.",
            "cards": [
                ("Investment Required", ["Engineering Sprints Allocation: $28,000 (internal staff)", "Savings Plans Partial Upfront: $15,000 (one-time treasury)", "Total Implementation Investment: $43,000"], "$43,000 One-Time"),
                ("Cash Flow Return", ["Monthly Recurring Net Savings: $102,475 / month", "Annualized Net Cash Savings: $1,229,699 / year", "Payback Period: 0.7 months (21 calendar days)", "Net 3-Year Value Created: $3,646,000"], "1,200%+ Annual ROI")
            ],
            "notes": "From a treasury perspective, this program is self-funding within 3 weeks. A one-time allocation of $43,000 unlocks over $1.2M in annual recurring cash flow that directly drops to our bottom line."
        },
        # Slide 16: Organizational RACI
        {
            "cat": "Operating Model",
            "title": "Organizational Accountability: RACI Matrix & Showback",
            "sub": "Clear boundaries between Finance, FinOps, SRE, and Microservice Engineering Squads.",
            "cards": [
                ("RACI Matrix Highlights", ["CFO: Accountable for Savings Plans purchasing & corporate margin", "VP Engineering: Accountable for Graviton migration & fleet sizing", "FinOps Lead: Accountable for tagging hygiene & anomaly triage", "Tech Leads: Responsible for microservice pod limits & showback targets"], "Clear Ownership"),
                ("Showback & Gamification", ["Monthly Squad Leaderboard with recognition for efficiency gains", "Service-level cost allocation dashboards for all 12 microservices", "Engineering KPIs tied to unit cost control during sprint planning"], "Cultural Buy-In")
            ],
            "notes": "Cost optimization fails when engineers view it as finance meddling in architecture. Our RACI model clearly establishes that engineering owns technical execution while FinOps provides tooling, telemetry, and automated gates."
        },
        # Slide 17: Risk Management
        {
            "cat": "Risk Management",
            "title": "Risk Mitigation Guardrails & Automated Rollback Protocols",
            "sub": "Zero-downtime canary deployments, Prometheus latency triggers, and emergency circuit breakers.",
            "cards": [
                ("Architectural De-Risking", ["Canary Graviton3 deployments: 10% traffic for 48h before full cutover", "Prometheus p99 latency alarms trigger automatic rollback if >100ms", "All RDS downsizing conducted during maintenance windows with replicas"], "Automated Rollbacks"),
                ("Billing Spike Circuit Breakers", ["Real-time Z-score anomaly detector alerts on >30% spikes within 1h", "EventBridge circuit breakers rate-limit runaway batch ingestion loops", "Continuous automated compliance test suite running in CI/CD"], "Real-Time Protection")
            ],
            "notes": "We have engineered automated rollbacks into every deployment script. If a Graviton3 node group experiences latency degradation, Karpenter automatically re-routes traffic back to x86 node groups within 60 seconds."
        },
        # Slide 18: Board Resolution & CFO Q&A
        {
            "cat": "Board Resolution",
            "title": "Board Resolution & CFO Review Panel Q&A",
            "sub": "Formal request for Board approval to execute the 90-Day FinOps roadmap and commitment purchases.",
            "cards": [
                ("Proposed Board Resolution", ["RESOLVED, that management is authorized to execute the 3-phase FinOps roadmap to reduce monthly AWS infrastructure expenditure from $180,000 to <=$120,000.", "FURTHER RESOLVED, that a partial upfront commitment of $15,000 for 1-Year Compute Savings Plans is approved for deployment in Day 60."], "Board Approval"),
                ("Key Executive Takeaways", ["$102,475/mo recurring savings fully validated by sequential waterfall math", "Zero double-counting: verified Step 1 -> Step 2 -> Step 3 chaining", "100% compliance ring-fencing for PCI DSS, SOC 2, and RBI IT Framework"], "Thank You — Q&A")
            ],
            "notes": "Thank you, CFO and members of the Board. We respectfully request adoption of the FinOps roadmap resolution and are now open to answer any detailed architectural, commercial, or compliance questions."
        }
    ]

    for s_idx, s in enumerate(slides_content, 1):
        slide = add_blank_slide(title_text=s["title"], subtitle_text=s["sub"], category=s["cat"])

        # Add two large content cards
        cards = s["cards"]
        card_w = Inches(5.6)
        card_h = Inches(4.5)
        top_y = Inches(1.8)

        # Left Card
        c1 = cards[0]
        add_card(slide, Inches(0.8), top_y, card_w, card_h, c1[0], body_bullets=c1[1], highlight_text=c1[2])

        # Right Card
        c2 = cards[1]
        add_card(slide, Inches(6.8), top_y, card_w, card_h, c2[0], body_bullets=c2[1], highlight_text=c2[2])

        # Add Speaker Notes
        notes_slide = slide.notes_slide
        tf_notes = notes_slide.notes_text_frame
        tf_notes.text = f"SLIDE {s_idx} SPEAKER NOTES & CFO Q&A:\n\n{s['notes']}"

    out_file = PRESENTATION_DIR / "cfo-review.pptx"
    prs.save(out_file)
    print(f"  [OK] Saved {out_file} (18 slides with speaker notes)")


# ==============================================================================
# MAIN
# ==============================================================================
def main():
    print("\n" + "=" * 65)
    print("  LendFlow FinOps — Automated Excel & PPTX Deliverables Generator")
    print("  Cloud FinOps Engineering Group")
    print("=" * 65 + "\n")

    generate_billing_analysis()
    generate_savings_model()
    generate_cfo_presentation()

    print("\n" + "=" * 65)
    print("  All executive deliverables successfully generated!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
