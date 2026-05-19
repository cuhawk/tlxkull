---
source: bughunters
source_url: https://bughunters.google.com/blog/new-patch-rewards-program-for-osv-scalibr
title: "New Patch Rewards Program for OSV-SCALIBR - Google Bug Hunters"
description: "Check out our new Patch Rewards Program for OSV-SCALIBR, offering financial incentives for providing novel OSV-SCALIBR plugins for inventory, vulnerability, or secret detection."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/new-patch-rewards-program-for-osv-scalibr#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# New Patch Rewards Program for OSV-SCALIBR

![](https://storage.googleapis.com/bughunters-article-images/blogs/erikvarga.jpg)

Erik Varga

Software Engineer

Published: Aug 7, 2025

Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# New Patch Rewards Program for OSV-SCALIBR

Earlier this year we published
[OSV-SCALIBR](https://security.googleblog.com/2025/01/osv-scalibr-library-for-software.html),
Google's open source tool for finding vulnerabilities in software dependencies.
In the months since, we've added various new detection capabilities to enhance
the scope of vulns our scanner can find in- and outside of Google, including
many new
[software inventory types](https://github.com/google/osv-scalibr/blob/main/docs/supported_inventory_types.md),
and
[Secret Scanning](https://opensource.googleblog.com/2025/07/stop-leaked-credentials-in-their-tracks-with-veles-our-new-open-source-secret-scanner.html).

Today, we are announcing a new
[Patch Rewards Program for OSV-SCALIBR](https://bughunters.google.com/about/rules/open-source/6436351477940224).
Participants in the program will be eligible to receive a financial reward for
providing novel OSV-SCALIBR plugins for inventory, vulnerability, or secret
detection. This program will allow us to quickly extend the capabilities of the
scanner to better benefit our users and uncover more vulnerabilities in their
infrastructure and code repos.

In detail, this program is scoped to the following types of contributions:

- **Vulnerability detection plugins:** OSV-SCALIBR has a number of detectors
for efficiently finding specific high-severity vulnerabilities with a low
false positive rate. We encourage everyone who is interested in making
contributions to this project to add new vulnerability detection plugins.
- **Secret detection plugins:** We recently added capabilities for detecting
and validating the presence of exposed secrets such as service account keys
on a filesystem or codebase. We invite you to help us make this feature even
more useful by adding new secret types for it to detect and validate.
- **Inventory extraction plugins:** OSV-SCALIBR's software extraction
capability is what allows it to find hundreds of different CVEs in
out-of-date software dependencies at scale. We welcome contributions to
improve our coverage by introducing extraction plugins for new software
inventory types.

All plugin contributions will be reviewed by our panel members in Google's
Vulnerability Management team and the reward amount will be determined by
factors such as the severity and time sensitivity of the vulnerability, as well
as the precision and accuracy of the detection method.

As with other Security Reward Programs, rewards can be donated to charity—and
we'll double your donation if you choose to do so. We'll run this program in
iterations so that everyone interested has the opportunity to participate.

To learn more about this program, please check out our
[official rules and guidelines](https://bughunters.google.com/about/rules/open-source/6436351477940224). If
you have any questions or suggestions regarding this program, feel free to
contact us at [osv-scalibr-patch-rewards@google.com](mailto:osv-scalibr-patch-rewards@google.com).

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab