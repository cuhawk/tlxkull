---
source: bughunters
source_url: https://bughunters.google.com/blog/ossvrp-rule-updates-2026
title: "Streamlining Google’s OSS VRP: Key Rule Updates - Google Bug Hunters"
description: "Read about our updates to the OSS VRP rules which are designed to help us filter out low-quality reports and focus on real-world impact."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/ossvrp-rule-updates-2026#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Streamlining Google’s OSS VRP: Key Rule Updates

![](https://storage.googleapis.com/bughunters-article-images/blogs/schcamille.jpg)

Camille Schneider

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/zjessica.jpg)

Jessica Zhang

Technical Program Manager

![](https://storage.googleapis.com/bughunters-article-images/blogs/hblauzvern.jpg)

Hayden Blauzvern

Software Engineer

Published: Mar 19, 2026

Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# Streamlining Google’s OSS VRP: Key Rule Updates

Since we launched the Google Open Source Software Vulnerability Reward Program
in 2022, your contributions have been vital in securing the software that the
entire world relies on. However, the security landscape is shifting rapidly.
Over the past few weeks, we’ve seen a massive surge in AI-generated reports.

The following modifications apply to all submissions made via
[bughunters.google.com](http://bughunters.google.com/) subsequent to the
publication of this post; the
[OSS VRP rules](https://bughunters.google.com/about/rules/open-source/google-open-source-software-vulnerability-reward-program-rules)
have been updated accordingly.

> TL;DR: To ensure our triage teams can focus on the most critical threats, we
> are updating our requirements for certain types of report. We will now require
> higher-quality proof (like OSS-Fuzz reproduction or a merged patch) for
> certain tiers to filter out low-quality reports and allow us to focus on
> real-world impact.

## April 2026 Update

We have further updated the rules for OSS VRP after the initial publication
of this blog post.

For lower tiers (OT2 and OT3), we are no longer providing
monetary rewards or credit for "Product Vulnerabilities" or "Other Security
Issues". We have also lowered the maximum reward for "Supply Chain Compromises"
for OT2.

## Why we are making these changes

While AI is a powerful tool for security research that can streamline the
discovery of a large number of potential vulnerabilities, like all
research-assisting tools, its outputs need to be validated as you're conducting
the research. Recently, we have observed a significant surge in the volume of
low-quality and invalid reports submitted to OSS VRP. We are increasingly
seeing:

- AI-generated reports that contain incorrect information or "hallucinations"
about how a vulnerability might be triggered.
- A flood of reports that, while technically valid in pointing to a coding
error like a buffer overflow, have negligible security impact given the
project's security model or are not in reachable codepaths.

By redirecting focus from triaging ambiguous reports to rewarding researchers
for actionable, high-impact fixes, we are establishing a more efficient and
sustainable model for the future.

## Introducing Project Tiers (OT0 - OT3)

We are formalizing how we categorize Google OSS projects to indicate their
sensitivity and criticality.

- OT0 (Flagship): The most critical projects (e.g., Bazel, Angular, Golang)
with the highest rewards.
- OT1 (Important): High-impact projects with significant community footprints.
- OT2 (Standard): Active, stable projects, often published in major package
managers.
- OT3 (Low-Priority): Small, experimental, or sample projects.

You can find the full list of OT0 and OT1 repositories in our
["bughunters" GitHub repo](https://github.com/google/bughunters/blob/main/oss-repository-tier/external_repositories.txtpb).
Note that there currently is no published list of OT2 repositories and that the
final tiering decision is made when rewarding a report, at the discretion of the
reward panel.

## New Acceptance Criteria for Product Vulnerabilities

To ensure we are rewarding true security impact, we are updating the
requirements for "Product Vulnerability" reports:

- For OT0 & OT1 projects: Memory corruption reports now require exact
[OSS-Fuzz reproduction steps](https://google.github.io/oss-fuzz/advanced-topics/reproducing/#reproducing-bugs)
(using an existing fuzz target) or a merged patch. We believe that
integrating with OSS-Fuzz provides a more robust defense than triaging
individual reports, and we want to prioritize researchers who contribute to
this model.
- For OT2 & OT3 projects: These projects are no longer eligible for monetary
rewards or credit for "Product Vulnerabilities". See below for additional
changes to these tiers.

## Reward Updates to OT2 & OT3

To focus on rewarding high-impact vulnerabilities, we are making the following
changes to OT2 & OT3 tiers:

- As stated above, these projects are no longer eligible for rewards or credit
for "Product Vulnerabilities". The Google security team will not triage
these reports.
- Additionally, these projects are no longer eligible for rewards or credit
for "Other Security Issues".
- For OT2 projects: The maximum reward for "Supply Chain Compromises" has been
lowered to $3,133.70.

## What Stays the Same

We remain fully committed to rewarding the most critical classes of
vulnerabilities across all Google OSS repositories:

- Supply Chain Compromises: We continue to prioritize vulnerabilities that
could compromise build integrity or source code across every project tier.
- Credential Leaks: Disclosure of sensitive write-access credentials or
package manager keys remains a top priority.

## Conclusion

We want to reward the "wheat," not the "chaff”. By shifting our focus toward
actionable reports and verifiable reproduction steps, we can ensure the OSS VRP
remains sustainable and continues to provide top-tier rewards for high-quality
research. The
[OSS VRP rules](https://bughunters.google.com/about/rules/open-source/google-open-source-software-vulnerability-reward-program-rules)
have been updated according to the changes announced in this post.

Happy bug hunting, and thank you for helping us keep Open Source secure!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab