package lendflow.finops

import future.keywords.in

default allow = false

# ------------------------------------------------------------------------------
# 1. ALLOW EVALUATION
# ------------------------------------------------------------------------------
allow {
    count(violation) == 0
}

# ------------------------------------------------------------------------------
# 2. MANDATORY TAGGING POLICY (A-01, A-03)
# ------------------------------------------------------------------------------
mandatory_tags := ["CostCenter", "Environment", "Service", "Owner", "ComplianceScope"]

# Evaluates Terraform plan resource changes
violation[msg] {
    some resource in input.resource_changes
    resource.type in ["aws_instance", "aws_eks_node_group", "aws_db_instance", "aws_s3_bucket"]
    resource.change.actions[_] in ["create", "update"]
    tags := object.get(resource.change.after, "tags", {})
    some required in mandatory_tags
    not tags[required]
    msg := sprintf("Resource '%v' (%v) is missing mandatory FinOps tag '%v'", [resource.address, resource.type, required])
}

# ------------------------------------------------------------------------------
# 3. APPROVED REGIONS POLICY (CMP-007, CMP-008)
# ------------------------------------------------------------------------------
approved_regions := ["ap-south-1", "eu-west-1", "eu-central-1"]

violation[msg] {
    some resource in input.resource_changes
    region := object.get(resource.change.after, "region", "unknown")
    region != "unknown"
    not region in approved_regions
    msg := sprintf("Resource '%v' deployed to unapproved region '%v'. Allowed regions: %v", [resource.address, region, approved_regions])
}

# ------------------------------------------------------------------------------
# 4. INSTANCE TYPE & GRAVITON ENFORCEMENT (A-08)
# ------------------------------------------------------------------------------
disallowed_instance_prefixes := ["p3.", "p4.", "p5.", "g4dn.", "g5.", "m5.16xlarge", "c5.18xlarge"]

violation[msg] {
    some resource in input.resource_changes
    resource.type in ["aws_instance", "aws_eks_node_group"]
    itype := object.get(resource.change.after, "instance_type", "")
    some prefix in disallowed_instance_prefixes
    startswith(itype, prefix)
    msg := sprintf("Disallowed or oversized instance type '%v' requested on '%v'", [itype, resource.address])
}

# ------------------------------------------------------------------------------
# 5. PCI DSS v4.0 RING-FENCE (CMP-001)
# ------------------------------------------------------------------------------
violation[msg] {
    some resource in input.resource_changes
    tags := object.get(resource.change.after, "tags", {})
    tags.Service == "lendflow-payments"
    resource.type == "aws_eks_node_group"
    scaling := object.get(resource.change.after, "scaling_config", {})
    min_size := object.get(scaling, "min_size", 0)
    min_size < 3
    msg := sprintf("PCI DSS Violation: 'lendflow-payments' node group '%v' min_size (%v) must be at least 3 across 3 AZs", [resource.address, min_size])
}

# ------------------------------------------------------------------------------
# 6. RBI IT FRAMEWORK DATA RESIDENCY (CMP-007)
# ------------------------------------------------------------------------------
rbi_services := ["lendflow-credit-scoring", "lendflow-underwriting", "lendflow-ledger"]

violation[msg] {
    some resource in input.resource_changes
    tags := object.get(resource.change.after, "tags", {})
    tags.Service in rbi_services
    region := object.get(resource.change.after, "region", "ap-south-1")
    region != "ap-south-1"
    msg := sprintf("RBI Mandate Violation: Regulated Indian lending service '%v' on '%v' must strictly reside in ap-south-1", [tags.Service, resource.address])
}

# ------------------------------------------------------------------------------
# 7. EBS GP3 STORAGE ENFORCEMENT (A-09)
# ------------------------------------------------------------------------------
violation[msg] {
    some resource in input.resource_changes
    resource.type == "aws_ebs_volume"
    resource.change.actions[_] in ["create", "update"]
    vtype := object.get(resource.change.after, "type", "gp2")
    vtype == "gp2"
    msg := sprintf("EBS volume '%v' uses gp2. gp3 is required for 20%% cost reduction and baseline 3,000 IOPS", [resource.address])
}
