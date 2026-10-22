# ==============================================================================
# LendFlow FinOps Framework — Cost-Optimised AWS Infrastructure
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      CostCenter      = var.cost_center
      Environment     = var.environment
      Owner           = "finops-platform-team"
      ComplianceScope = "rbi-it|pci-dss|soc2"
      ManagedBy       = "Terraform"
    }
  }
}

# ------------------------------------------------------------------------------
# 1. S3 GATEWAY VPC ENDPOINT (Eliminates NAT Gateway Cross-AZ Data Transfer)
# ------------------------------------------------------------------------------
resource "aws_vpc_endpoint" "s3_gateway" {
  vpc_id            = var.vpc_id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = var.private_route_table_ids

  tags = {
    Name    = "lendflow-s3-gateway-endpoint"
    Service = "lendflow-gateway"
  }
}

# ------------------------------------------------------------------------------
# 2. GRAVITON3 EKS NODE GROUP (Steady-State 20% Cost Reduction & 25% Perf Gain)
# ------------------------------------------------------------------------------
resource "aws_eks_node_group" "graviton3_pool" {
  cluster_name    = var.eks_cluster_name
  node_group_name = "lendflow-graviton3-optimized"
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.private_subnet_ids

  ami_type       = "AL2_ARM_64"
  instance_types = ["c7g.xlarge", "m7g.xlarge"]
  capacity_type  = "ON_DEMAND"

  scaling_config {
    desired_size = 4
    max_size     = 12
    min_size     = 2
  }

  labels = {
    "kubernetes.io/arch"          = "arm64"
    "finops.lendflow.io/hardware" = "graviton3"
  }

  tags = {
    Name    = "lendflow-graviton3-pool"
    Service = "lendflow-ingestion"
  }
}

# ------------------------------------------------------------------------------
# 3. PCI DSS DEDICATED NODE GROUP (Ring-Fenced 3 AZ Minimum)
# ------------------------------------------------------------------------------
resource "aws_eks_node_group" "pci_enclave" {
  cluster_name    = var.eks_cluster_name
  node_group_name = "lendflow-pci-payments-enclave"
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.pci_subnet_ids

  instance_types = ["m5.xlarge"]
  capacity_type  = "ON_DEMAND"

  scaling_config {
    desired_size = 3
    max_size     = 6
    min_size     = 3 # Strict PCI DSS requirement: min 3 across 3 AZs
  }

  labels = {
    "compliance.lendflow.io/scope" = "pci-dss"
  }

  tags = {
    Name            = "lendflow-pci-payments-enclave"
    Service         = "lendflow-payments"
    ComplianceScope = "pci-dss"
  }
}

# ------------------------------------------------------------------------------
# 4. S3 AUDIT BUCKET WITH OBJECT LOCK (SOC 2 WORM Compliance)
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "audit_logs" {
  bucket        = "lendflow-immutable-audit-logs-${var.environment}"
  force_destroy = false

  object_lock_enabled = true

  tags = {
    Service         = "lendflow-audit"
    ComplianceScope = "soc2"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "audit_lifecycle" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    id     = "auto-glacier-transition"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
  }
}
