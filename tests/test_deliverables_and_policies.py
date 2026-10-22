"""
LendFlow FinOps Framework — Deliverables, Policies & Repository Verification Test Suite
Validates:
- AWS SCP JSON syntax & structure
- AWS Config Rules syntax
- OPA Rego policies & Infracost policies
- Autoscaling YAML/JSON configs
- Terraform infrastructure files
- Excel workbook tabs & formulas
- PPTX presentation slide count & notes
- Core documentation suite & daily logs
- PowerShell automation scripts
"""
import os
import json
import pytest
import openpyxl
from pptx import Presentation

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 1. AWS SCP JSON Policies Tests
class TestAWSSCPPolicies:
    def test_mandatory_tags_scp(self):
        fpath = os.path.join(BASE_DIR, "policies", "aws", "mandatory-tags.json")
        assert os.path.exists(fpath), f"Missing {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("Version") == "2012-10-17"
        assert len(data.get("Statement", [])) >= 1
        stmt = data["Statement"][0]
        assert stmt.get("Effect") == "Deny"

    def test_restrict_gpu_scp(self):
        fpath = os.path.join(BASE_DIR, "policies", "aws", "restrict-gpu.json")
        assert os.path.exists(fpath), f"Missing {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("Version") == "2012-10-17"
        stmt = data["Statement"][0]
        assert stmt.get("Effect") == "Deny"
        # Checks p3, p4, g4, g5 instance conditions
        cond = stmt.get("Condition", {})
        assert "ForAnyValue:StringLike" in cond or "StringLike" in cond

    def test_approved_regions_scp(self):
        fpath = os.path.join(BASE_DIR, "policies", "aws", "approved-regions.json")
        assert os.path.exists(fpath), f"Missing {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("Version") == "2012-10-17"
        stmt = data["Statement"][0]
        assert stmt.get("Effect") == "Deny"
        cond = stmt.get("Condition", {})
        assert "StringNotEquals" in cond

    def test_max_instance_limits_scp(self):
        fpath = os.path.join(BASE_DIR, "policies", "aws", "max-instance-limits.json")
        assert os.path.exists(fpath), f"Missing {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("Version") == "2012-10-17"
        stmt = data["Statement"][0]
        assert stmt.get("Effect") == "Deny"

    def test_config_rules_spec(self):
        fpath = os.path.join(BASE_DIR, "policies", "aws", "config-rules.json")
        assert os.path.exists(fpath), f"Missing {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        rules = data.get("ConfigRules", [])
        assert len(rules) >= 4
        rule_names = [r["ConfigRuleName"] for r in rules]
        assert "lendflow-required-tags-check" in rule_names
        assert "lendflow-ebs-gp3-volume-check" in rule_names


# 2. OPA Rego and Terraform Tests
class TestOPAPoliciesAndTerraform:
    def test_opa_rego_policy(self):
        fpath = os.path.join(BASE_DIR, "policies", "opa", "finops_guardrails.rego")
        assert os.path.exists(fpath), f"Missing {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        assert "package lendflow.finops" in content
        assert "mandatory_tags" in content
        assert "approved_regions" in content
        assert "PCI DSS" in content

    def test_infracost_rego_policy(self):
        fpath = os.path.join(BASE_DIR, "policies", "terraform", "infracost-policy.rego")
        assert os.path.exists(fpath), f"Missing {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        assert "package infracost" in content
        assert "violations" in content or "deny" in content

    def test_terraform_files(self):
        for fname in ["main.tf", "variables.tf", "outputs.tf"]:
            fpath = os.path.join(BASE_DIR, "infrastructure", fname)
            assert os.path.exists(fpath), f"Missing {fpath}"
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            assert len(content.strip()) > 50


# 3. Auto-Scaling Configs Tests
class TestAutoScalingConfigs:
    def test_autoscaling_files_exist(self):
        as_dir = os.path.join(BASE_DIR, "policies", "autoscaling")
        expected_files = [
            "hpa-gateway.yaml",
            "hpa-payments.yaml",
            "vpa-recommender.yaml",
            "karpenter-spot-provisioner.yaml",
            "karpenter-graviton-provisioner.yaml",
            "nonprod-schedule-rule.json"
        ]
        for ef in expected_files:
            fpath = os.path.join(as_dir, ef)
            assert os.path.exists(fpath), f"Missing autoscaling config: {fpath}"

    def test_payments_hpa_pci_compliance(self):
        fpath = os.path.join(BASE_DIR, "policies", "autoscaling", "hpa-payments.yaml")
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        assert "minReplicas: 3" in content
        assert "pci-dss" in content.lower() or "PCI" in content


# 4. Deliverables: Excel Workbooks Tests
class TestExcelDeliverables:
    def test_billing_analysis_excel(self):
        fpath = os.path.join(BASE_DIR, "analysis", "billing-analysis.xlsx")
        assert os.path.exists(fpath), f"Missing {fpath}"
        wb = openpyxl.load_workbook(fpath, read_only=True)
        sheet_names = wb.sheetnames
        assert len(sheet_names) >= 7
        expected_sheets = [
            "Executive Summary",
            "MoM Trend",
            "Pareto 80-20",
            "Instance Utilisation",
            "Storage Inventory",
            "Dark Spend & Tags",
            "Data Transfer"
        ]
        for es in expected_sheets:
            assert es in sheet_names, f"Missing sheet: {es}"
        wb.close()

    def test_savings_model_excel(self):
        fpath = os.path.join(BASE_DIR, "analysis", "savings-model.xlsx")
        assert os.path.exists(fpath), f"Missing {fpath}"
        wb = openpyxl.load_workbook(fpath, data_only=False)
        sheet_names = wb.sheetnames
        assert len(sheet_names) >= 6
        expected_sheets = [
            "Assumptions",
            "Step 1 - Eliminate",
            "Step 2 - Right-Size",
            "Step 3 - Commitments",
            "Sensitivity Analysis",
            "Executive Summary"
        ]
        for es in expected_sheets:
            assert es in sheet_names, f"Missing sheet: {es}"

        # Verify formulas in Executive Summary tab
        ws = wb["Executive Summary"]
        cell_formula = ws["C8"].value
        assert str(cell_formula).startswith("="), f"Expected formula in C8, got {cell_formula}"
        wb.close()


# 5. Deliverables: PowerPoint Presentation Tests
class TestPresentationDeliverable:
    def test_cfo_presentation_deck(self):
        fpath = os.path.join(BASE_DIR, "presentation", "cfo-review.pptx")
        assert os.path.exists(fpath), f"Missing {fpath}"
        prs = Presentation(fpath)
        assert len(prs.slides) == 18, f"Expected 18 slides, found {len(prs.slides)}"

        # Verify speaker notes exist
        slides_with_notes = 0
        for slide in prs.slides:
            if slide.notes_slide and slide.notes_slide.notes_text_frame.text.strip():
                slides_with_notes += 1
        assert slides_with_notes >= 15, f"Expected >=15 slides with notes, got {slides_with_notes}"


# 6. Documentation Suite Tests
class TestDocumentationSuite:
    def test_all_13_core_docs_exist(self):
        expected_docs = [
            "cost-audit-report.md",
            "optimisation-recommendations.md",
            "auto-scaling-policies.md",
            "ri-spot-strategy.md",
            "tagging-taxonomy.md",
            "governance-model.md",
            "anomaly-detection.md",
            "review-process.md",
            "compliance-matrix.md",
            "dashboard-specification.md",
            "methodology-and-assumptions.md",
            "runbook.md",
            "90-day-roadmap.md"
        ]
        for doc in expected_docs:
            fpath = os.path.join(BASE_DIR, "docs", doc)
            assert os.path.exists(fpath), f"Missing doc: {fpath}"
            assert os.path.getsize(fpath) > 200, f"Doc too small: {fpath}"

    def test_all_15_daily_logs_exist(self):
        for day in range(1, 16):
            fname = f"day-{day:02d}.md"
            fpath = os.path.join(BASE_DIR, "daily-logs", fname)
            assert os.path.exists(fpath), f"Missing daily log: {fpath}"
            assert os.path.getsize(fpath) > 100, f"Log too small: {fpath}"

    def test_day_01_has_stakeholder_matrix(self):
        fpath = os.path.join(BASE_DIR, "daily-logs", "day-01.md")
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Stakeholder Matrix" in content
        assert "Sarah Jenkins" in content
        assert "CFO" in content

    def test_demo_assets_exist(self):
        for fname in ["demo-script.md", "submission-checklist.md", "troubleshooting.md"]:
            fpath = os.path.join(BASE_DIR, "demo", fname)
            assert os.path.exists(fpath), f"Missing demo file: {fpath}"


# 7. PowerShell Scripts Tests
class TestPowerShellScripts:
    def test_all_powershell_scripts_exist(self):
        expected_scripts = [
            "setup.ps1",
            "run-dev.ps1",
            "run-tests.ps1",
            "build.ps1",
            "generate-deliverables.ps1"
        ]
        for s in expected_scripts:
            fpath = os.path.join(BASE_DIR, "scripts", s)
            assert os.path.exists(fpath), f"Missing PowerShell script: {fpath}"
            assert os.path.getsize(fpath) > 100, f"Script too small: {fpath}"
