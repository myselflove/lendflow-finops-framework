package infracost

import future.keywords.in

default allow = false

# Cost ceiling threshold: Monthly cost increase cannot exceed $500 without FinOps approval
max_monthly_diff = 500.0

allow {
    count(violations) == 0
}

violations[msg] {
    diff := to_number(input.diffTotalMonthlyCost)
    diff > max_monthly_diff
    msg := sprintf("Infracost Budget Gate: Proposed monthly cost increase ($%v) exceeds maximum allowed threshold ($%v). FinOps Lead signoff required.", [diff, max_monthly_diff])
}

violations[msg] {
    some resource in input.projects[_].breakdown.resources
    resource.name == "aws_ebs_volume"
    some cost_component in resource.costComponents
    cost_component.name == "Storage (gp2)"
    msg := sprintf("Infracost Policy Violation: gp2 EBS volume detected on '%v'. Use gp3 for 20%% direct cost reduction.", [resource.name])
}
