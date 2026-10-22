# LendFlow FinOps Engineering Runbook

## 1. Step-by-Step Optimization Procedures

### Procedure A: Purging Unattached EBS Volumes
```bash
# 1. List all unattached volumes older than 7 days
aws ec2 describe-volumes --filters Name=status,Values=available --query "Volumes[*].{ID:VolumeId,Size:Size,Created:CreateTime}"

# 2. Take precautionary snapshot before purge
aws ec2 create-snapshot --volume-id vol-0a1b2c3d4e5f6g7h8 --description "Pre-purge backup FinOps"

# 3. Delete volume
aws ec2 delete-volume --volume-id vol-0a1b2c3d4e5f6g7h8
```

### Procedure B: Applying S3 Intelligent-Tiering
```bash
aws s3api put-bucket-lifecycle-configuration --bucket lendflow-document-archive-prod --lifecycle-configuration file://policies/s3-lifecycle.json
```

### Procedure C: Toggling Non-Prod Scheduled State
```bash
# Trigger immediate non-prod pause via Lambda
aws lambda invoke --function-name lendflow-nonprod-power-scheduler --payload '{"action":"stop","environment":"dev"}' response.json
```
