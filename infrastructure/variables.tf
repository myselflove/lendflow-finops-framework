variable "aws_region" {
  type        = string
  default     = "ap-south-1"
  description = "Primary AWS region for LendFlow operations"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Target deployment environment (production, staging, development)"
}

variable "cost_center" {
  type        = string
  default     = "engineering"
  description = "FinOps cost center attribution"
}

variable "vpc_id" {
  type        = string
  default     = "vpc-0123456789abcdef0"
  description = "Target VPC ID"
}

variable "eks_cluster_name" {
  type        = string
  default     = "lendflow-eks-production"
  description = "EKS Cluster Name"
}

variable "node_role_arn" {
  type        = string
  default     = "arn:aws:iam::123456789012:role/lendflow-eks-node-role"
  description = "IAM Role ARN for EKS Node Groups"
}

variable "private_subnet_ids" {
  type        = list(string)
  default     = ["subnet-0a1b2c3d", "subnet-0e1f2a3b", "subnet-0c1d2e3f"]
  description = "List of 3 AZ private application subnets"
}

variable "pci_subnet_ids" {
  type        = list(string)
  default     = ["subnet-pci-1a", "subnet-pci-1b", "subnet-pci-1c"]
  description = "List of 3 AZ isolated PCI subnets"
}

variable "private_route_table_ids" {
  type        = list(string)
  default     = ["rtb-0123456789abcdef0"]
  description = "Route tables to attach S3 Gateway VPC Endpoint"
}
