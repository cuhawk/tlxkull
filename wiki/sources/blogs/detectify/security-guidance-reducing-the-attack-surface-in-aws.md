---
source: detectify
source_url: https://labs.detectify.com/security-guidance/reducing-the-attack-surface-in-aws/
title: "Reducing the attack surface using AWS SCPs - Labs Detectify"
author: "Detectify"
published: 2024-03-26T11:17:55+00:00
description: "Explore how Detectify leverages AWS Service Control Policies (SCPs) to minimize their attack surface and streamline security."
---

[Home](https://labs.detectify.com/)/ [Security guidance](https://labs.detectify.com/category/security-guidance/)/ [Reducing the attack surface in AWS](https://labs.detectify.com/security-guidance/reducing-the-attack-surface-in-aws/)

[Security guidance](https://labs.detectify.com/category/security-guidance/ "Security guidance")

# Reducing the attack surface in AWS

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2024%2F03%2Fjohan-edholm-detectify.png&w=128&q=75)

**Johan Edholm** Mar 26, 2024

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/security-guidance/reducing-the-attack-surface-in-aws/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/security-guidance/reducing-the-attack-surface-in-aws/ "Share on LinkedIn")

![Purple patterned image with the words 'Reducing AWS attack surface', alongside an image of Detectify co-founder, Johan Edholm](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2024%2F03%2FReducing-AWS-Attack-Surface.png&w=3840&q=75)

**“Anything that can go wrong will go wrong” – Murphy’s Law. We want to reduce what can go wrong. The smaller our attack surface, the fewer things we need to worry about. An excellent way of reducing the attack surface (and our cognitive load) is using AWS Service Control Policies (SCPs.) In this post, I’ll describe how we approached it.**

## **What are SCPs?**

SCPs are policies to control what can and cannot be done in one or more AWS accounts, regardless of what an IAM policy might say (even if you’re root.) SCPs can be applied to accounts or organizational units (OUs). By default, everything is allowed, and it’s up to us to deny what we don’t need. SCPs are always a defense in depth and will never trigger if IAM permissions are properly configured, but relying on perfect IAM configuration is not a luxury we can afford to count on. For more information about SCPs, see the [official AWS documentation on SCPs](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html).

## **What do we want to allow or deny?**

Preferably, we would deny any action we’re not using, but that’s most likely an administrative hell, and we’ll end up blocking developers daily, so we decided against even trying it. At Detectify, we’ve gone for a more pragmatic approach:

- Only allow AWS _services_ we use (rather than _actions_)
- Only allow regions we use
- Disallow dangerous actions

This has been a good balance between reducing things we need to worry about and keeping developers productive.

## **Only allow services we use**

The easiest way to find which services you use is by generating an [Organization activity](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_access-advisor-view-data-orgs.html) report (aka. organizations access report.) This report shows when services were last used, if at all.

The report can be generated based on an OU or a specific account. In our case, we started with generating a report for our Production OU. To generate such a report, we can use AWS CLI:

```
aws iam generate-organizations-access-report \
  --entity-path "o-XXXXXXXXXX/r-XXXX/ou-XXXX-XXXXXXXX"
```

Where the `entity-path` is the [AWS Organizations entity path](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_access-advisor-view-data-orgs.html#access_policies_access-advisor-viewing-orgs-entity-path) to our Production OU.

Once the report is generated we can get the list of used services with:

```
aws iam get-organizations-access-report \
  --job-id "JobId-goes-here" \
  --max-items 1000 \
  --query 'AccessDetails[?TotalAuthenticatedEntities > `0`].[ServiceName,ServiceNamespace,LastAuthenticatedTime]'
```

This gives a list of all services that have been used in the [tracking period](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_access-advisor.html?icmpid=docs_iam_console#access_policies_access-advisor-know). It shows the service name, the IAM namespace, and when it was last accessed.

We manually went through this list and filtered out obvious entries that were most likely just someone browsing a specific service in the AWS web console and very old activity.

With the list of used services, we created a policy that denied anything not on the list:

```
data "aws_iam_policy_document" "allow_only_used_services" {
  statement {
    sid       = "AllowOnlyUsedServices"
    effect    = "Deny"
    resources = ["*"]

    not_actions = [\
      <LIST OF NAMESPACES OF USED SERVICES>\
    ]
  }
}
```

This policy denies access to any service not listed in the `not_actions`. We seldom adopt new AWS services so this method rarely blocks development but allows us to ensure a proper process for evaluating new services.

## **Only allow regions we use**

We only use a few AWS regions, and there is no reason to allow usage of any region outside of that. At first glance, it might seem obvious how one can use SCP to block unused regions, but because some services are global, you cannot fully restrict access to only certain regions.

As described in [Detectify’s journey to an AWS multi-account strategy](https://blog.detectify.com/2023/04/13/aws-multi-account-strategy/), we use Control Tower. In Control Tower you can [configure which regions to allow or deny](https://docs.aws.amazon.com/controltower/latest/userguide/region-deny.html), which is what we did.

## **Disallow known dangerous actions**

While only allowing specific actions would be too much work, blocking the risky ones is a lot easier.

Exactly which SCPs to apply depends on the organization but they tend to be far more general than IAM policies, which means they can be shared between organizations. Some places to find SCPs:

- [AWS Service Control Policy examples repository](https://github.com/aws-samples/service-control-policy-examples)
- [AWS IAM Permissions Guardrails](https://aws-samples.github.io/aws-iam-permissions-guardrails/guardrails/scp-guardrails.html)
- [AWS – Example service control policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps_examples.html)
- [Summit Route – AWS SCP Best Practices](https://summitroute.com/blog/2020/03/25/aws_scp_best_practices/)

There are lots of good resources out there. If you search for `aws scp site:github.com` you’ll find plenty of examples. We went through many different SCPs for inspiration and picked the (for us) most relevant and least error-prone parts we could find.

### **Expensive actions**

Some actions can be _very_ expensive. We have opted to block the most expensive ones we know of. Ian Mckay has a [gist with some expensive actions](https://gist.github.com/iann0036/b473bbb3097c5f4c656ed3d07b4d2222) you might want to block to avoid costly mistakes:

```
data "aws_iam_policy_document" "deny_costly_actions" {
  statement {
    sid       = "DenyCostlyActions"
    effect    = "Deny"
    resources = ["*"]

    actions = [\
      "acm-pca:CreateCertificateAuthority",\
      "aws-marketplace:AcceptAgreementApprovalRequest",\
      "aws-marketplace:Subscribe",\
      "backup:PutBackupVaultLockConfiguration",\
      "bedrock:CreateProvisionedModelThroughput",\
      "bedrock:UpdateProvisionedModelThroughput",\
      "dynamodb:PurchaseReservedCapacityOfferings",\
      "ec2:ModifyReservedInstances",\
      "ec2:PurchaseHostReservation",\
      "ec2:PurchaseReservedInstancesOffering",\
      "ec2:PurchaseScheduledInstances",\
      "elasticache:PurchaseReservedCacheNodesOffering",\
      "es:PurchaseReservedElasticsearchInstanceOffering",\
      "es:PurchaseReservedInstanceOffering",\
      "glacier:CompleteVaultLock",\
      "glacier:InitiateVaultLock",\
      "outposts:CreateOutpost",\
      "rds:PurchaseReservedDBInstancesOffering",\
      "redshift:PurchaseReservedNodeOffering",\
      "route53domains:RegisterDomain",\
      "route53domains:RenewDomain",\
      "route53domains:TransferDomain",\
      "s3-object-lambda:PutObjectLegalHold",\
      "s3-object-lambda:PutObjectRetention",\
      "s3:BypassGovernanceRetention",\
      "s3:PutBucketObjectLockConfiguration",\
      "s3:PutObjectLegalHold",\
      "s3:PutObjectRetention",\
      "savingsplans:CreateSavingsPlan",\
      "shield:CreateSubscription",\
      "snowball:CreateCluster",\
    ]
  }
}
```

Some of these actions you might want to be careful with. For example, denying `route53domains:RenewDomain` could cause problems if it’s applied to the OU or account that manages domains.

### **SCPs via Control Tower controls**

If you are, like us, using Control Tower there are a few dozen SCPs you can enable and let Control Tower manage. In Control Tower you can filter the view to only show SCPs:

![](https://labsadmin.detectify.com/app/uploads/2024/03/filter-view-SCPs.png)

Some of the listed SCPs are enabled by default, but plenty of opt-ins exist.

## **SCP size limits and workarounds**

SCPs can be a maximum 5120 bytes, _including_ white-space. We ran into this issue because `aws_iam_policy_document` does not generate minimized JSON by default.

There are a few ways to work around this:

- Use multiple policies (max 5 per OU)
- Apply the policy to a parent OU (if you’ve reached the max 5 limit per OU)
- Minimize the JSON

We went with the last option. There is no built-in function to minimize JSON in Terraform, but you can minimize it by running `jsonencode(jsondecode())`, so something like:

```
resource "aws_organizations_policy" "example" {
  name    = "example"
  type    = "SERVICE_CONTROL_POLICY"
  content = jsonencode(jsondecode(data.aws_iam_policy_document.example.json))
}
```

This allows us to have our policies written in Terraform (which is more readable, allows comments, gives linting, etc) and still minimize the number of bytes used. If you browse the SCP via AWS console, it won’t be minimized so it’s still readable there too.

## **Testing SCPs before production**

There is no dry-run for SCPs which makes any change to them a bit scary since you cannot know if something will break or not.

To reduce the risk of us breaking anything important, we first apply our SCPs to our Staging OU. By having the SCPs applied in staging for a while one can see if it passes the [scream test](https://www.v-wiki.net/the-scream-test/). One can also [query CloudTrail via Athena](https://docs.aws.amazon.com/athena/latest/ug/cloudtrail-logs.html) to see if there are any relevant SCP errors with for example:

```
SELECT * FROM cloudtrail_logs WHERE errorcode='AccessDenied' AND errormessage LIKE '%service control%';
```

So far we’ve been lucky enough to never encounter any issues and the SCPs have since long been applied to production successfully!

## Conclusion

SCPs allowed us to vastly reduce our attack surface and improve our defense in depth. Even though there is no dry run everything went smoothly and we now have much fewer things to keep in mind and worry about!

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/security-guidance/reducing-the-attack-surface-in-aws/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/security-guidance/reducing-the-attack-surface-in-aws/ "Share on LinkedIn")

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2024%2F03%2Fjohan-edholm-detectify.png&w=128&q=75)

**Johan Edholm**

Security Engineer & Co-Founder, Detectify

## Check out more content

It’s no secret that cloud architectures have several characteristics that make SSRF attacks challenging to defend against. While SSRFs are not a new threat vector, …

September 23, 2022

TL/DR: AWS QuickSight makes it easy to build visualizations, perform ad-hoc analysis, and quickly get business insights from their data, anytime, on any device. Hacker …

May 30, 2022

TL/DR: On December 2, open-source analytics solution Grafana released an emergency security patch for critical zero-day Path Traversal vulnerability CVE-2021-43798, after proof-of-concept code to exploit …

December 15, 2021

Crowdsource hackers Hakluke and Farah Hawa share the top web vulnerabilities that are often missed during security testing. When hunting for bugs, especially on competitive bug bounty …

September 30, 2021