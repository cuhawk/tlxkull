---
source: bughunters
source_url: https://bughunters.google.com/blog/think-outside-the-perimeter-bug-hunting-in-google-clouds-vpc-service-controls
title: "Think Outside the Perimeter: Bug Hunting in Google Cloud's VPC Service Controls - Google Bug Hunters"
description: "Read this blog post to understand VPC-SC product details, how to set up an environment, and what vulnerability criteria to consider when bug hunting on this product."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/think-outside-the-perimeter-bug-hunting-in-google-clouds-vpc-service-controls#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Think Outside the Perimeter: Bug Hunting in Google Cloud's VPC Service Controls

![](https://storage.googleapis.com/bughunters-article-images/blogs/vwin.jpg)

Vincent Winstead

Technical Program Manager

Published: Nov 12, 2024

Vulnerability Reward Program  Google Cloud

[RSS Feed](https://bughunters.google.com/feed/en)

# Think Outside the Perimeter: Bug Hunting in Google Cloud's VPC Service Controls

In October 2024, we launched the
[Google Cloud Vulnerability Reward Program (VRP)](https://cloud.google.com/blog/products/identity-security/google-cloud-launches-new-vulnerability-rewards-program)
to incentivize external researchers to hunt for security vulnerabilities in
products and services that are part of Google Cloud. Today, we wanted to give a
special callout to
[VPC Service Controls](https://cloud.google.com/security/vpc-service-controls?e=48754805&hl=en)(VPC-SC),
which is one of the products in scope of this program. Yes, you read that right.
You can get rewarded for finding vulnerabilities in a product that helps prevent
data exfiltration.

## What is VPC Service Controls?

VPC-SC allows you to create isolation perimeters around your cloud environment
and forms a shield around your most valuable cloud resources. You can create
secure perimeters around your
[Google Cloud services](https://cloud.google.com/vpc-service-controls/docs/supported-products)
like Cloud Storage, BigQuery, and more, preventing unauthorized access and data
leakage. Think of it as a bouncer for your cloud data, but instead of checking
IDs, it's checking API calls.

![](https://storage.googleapis.com/bughunters-article-images/blogs/perimeter.png)

_Fig. 1. VPC Service Controls: Perimeter Diagram_

## Getting Started

VPC-SC is a
[Tier-1 service](https://github.com/google/bughunters/blob/main/cloud-tiers/cloud-tiers.text)
in Google Cloud VRP. This is your chance to put VPC-SC to the ultimate test to
uncover potential vulnerabilities. Hunting VPC-SC perimeter bugs is
straightforward, all you need to do is:

- **Set up your environment**: You'll need a Google Cloud organization and a
project to begin with. Don't worry, you can do quite a lot with the
[free trial](https://cloud.google.com/free) without accruing any charges.
Check out our
[documentation](https://cloud.google.com/vpc-service-controls/docs/overview)
to learn all about configuring a VPC-SC. This will also provide you with
valuable details about VPC-SC product design and architecture to assist you
in the hunt. You can also explore one of our new codelabs for a hands-on
guided experience to quickly deploy and test VPC-SC:
  - [VPC Service Controls Basic Tutorial I](https://codelabs.developers.google.com/codelabs/vpc-sc-beginnerlab-1#0)
  - [VPC Service Controls Basic Tutorial II](https://codelabs.developers.google.com/codelabs/vpc-sc-beginnerlab-2#0)
- **Understand the scope**: We're particularly interested in vulnerabilities
that could lead to unauthorized access to protected resources. So, focus
your efforts on areas like perimeter security, access control policies, and
data flow restrictions. Hint:
[Over 100 services](https://cloud.google.com/vpc-service-controls/docs/supported-products)
are protected by VPC-SC, so don’t limit yourself to only data storage
services.
- **Report your findings**: Found something interesting? Submit your report
through the [Bug Hunters portal](https://bughunters.google.com/report) (in
the report form, select _Cloud VRP_ in the **Bug Location** step). Be sure
to provide detailed information about the vulnerability, including steps to
reproduce it, the potential impact, and a
[valid attack scenario](https://bughunters.google.com/learn/improving-your-reports/how-to-report/6379261818306560/write-down-the-attack-scenario).
The more details, the better!

## What Kind of Bugs Are We Looking For?

Think you've found a vulnerability? Here are some examples of findings that can
net you rewards:

- **Perimeter escapes**: Can you upload protected resources outside the
perimeter? Maybe you found a secret tunnel, or perhaps you can teleport data
out.
- **Access control bypasses**: Can you access a resource you shouldn't be able
to? Think you can convince VPC-SC you're someone else? Show us your skills!
- **Data exfiltration techniques**: Can you sneak data out of the perimeter?
We're talking about clever tricks like leveraging multiple services to find
something we hadn't thought of. Check out the
[services in scope](https://bughunters.google.com/about/rules/google-friends/4849867320328192/cloud-vulnerability-reward-program-rules#services-in-scope)
and
[qualifying vulnerabilities](https://bughunters.google.com/about/rules/google-friends/4849867320328192/cloud-vulnerability-reward-program-rules#qualifying-vulnerabilities)
to get some ideas.

## Rewards and Recognition

Check out the
[Cloud VRP rules](https://bughunters.google.com/about/rules/google-friends/4849867320328192/cloud-vulnerability-reward-program-rules#reward-amounts)
for more details about the reward structure and criteria. And of course, you can
get the ultimate recognition: on request, we’ll add a shout-out on our
[Public Reports](https://bughunters.google.com/report/reports) page for valid
reports. We are looking for your active participation – set up your environment
now, dive in, and search for vulnerabilities in VPC-SC.

Happy bug hunting, and may the odds be ever in your favor!

### Helpful links

- [VPC-SC Public Documentation](https://cloud.google.com/vpc-service-controls/docs/overview)
- [VPC-SC Supported Services](https://cloud.google.com/vpc-service-controls/docs/supported-products)
- [Google Bug Hunters home page](https://bughunters.google.com/)
- [Introducing Google Cloud’s new Vulnerability Reward Program](https://cloud.google.com/blog/products/identity-security/google-cloud-launches-new-vulnerability-rewards-program)
(blog post)

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab