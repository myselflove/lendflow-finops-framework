output "s3_gateway_endpoint_id" {
  value       = aws_vpc_endpoint.s3_gateway.id
  description = "VPC Endpoint ID for S3 Gateway"
}

output "graviton3_node_group_arn" {
  value       = aws_eks_node_group.graviton3_pool.arn
  description = "ARN of the Graviton3 optimized node group"
}

output "pci_enclave_node_group_arn" {
  value       = aws_eks_node_group.pci_enclave.arn
  description = "ARN of the isolated PCI DSS node group"
}

output "audit_logs_bucket_arn" {
  value       = aws_s3_bucket.audit_logs.arn
  description = "ARN of the immutable WORM audit logs bucket"
}
