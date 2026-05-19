---
source: bughunters
source_url: https://bughunters.google.com/blog/hardening-google-cloud-insights-from-the-latest-cloud-vrp-bugswat
title: "Hardening Google Cloud: Insights from the latest Cloud VRP bugSWAT - Google Bug Hunters"
description: "Check out this blog post for more on the inaugural Cloud-focused bugSWAT, hosted by the Cloud VRP, and how events like this help boost Google's security posture in close collaboration with external researchers."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/hardening-google-cloud-insights-from-the-latest-cloud-vrp-bugswat#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Hardening Google Cloud: Insights from the latest Cloud VRP bugSWAT

![](https://storage.googleapis.com/bughunters-article-images/blogs/darbyhopkins.jpg)

Darby Hopkins

Cloud Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/mcote.png)

Michael Cote

Technical Program Manager

Published: Sep 10, 2025

Vulnerability Reward Program  Google Cloud

[RSS Feed](https://bughunters.google.com/feed/en)

# Hardening Google Cloud: Insights from the latest Cloud VRP bugSWAT

> If you're new to Google's bugSWAT events, we encourage you to check out our
> previous blog post on the
> [AI bugSWAT in Tokyo & 2025 Hacker Roadshow](https://bughunters.google.com/blog/5753079171252224/ai-bugswat-in-tokyo-2025-hacker-roadshow)
> which provides a great overview of these live hacking events. This blog post
> focuses specifically on the latest Cloud-specific bugSWAT and its unique
> outcomes.

Google Cloud’s Vulnerability Reward Program’s (VRP) inaugural Cloud-focused
bugSWAT proved to not only be a remarkable, but also a record-breaking event,
receiving the largest volume of reports for any bugSWAT Google has ever hosted.
We brought together 20 of the world's top cloud security researchers for an
intensive, multi-day event. Their deep expertise uncovered subtle and complex
vulnerabilities that are inherently challenging to detect, complementing the
continuous efforts of our internal Google security engineering teams. The
collaboration between these external experts and our internal teams reiterated
the crucial role the Cloud VRP plays in stress-testing our platform from diverse
perspectives.

The true success of these types of events is in the security enhancements and
mitigations implemented as a direct result. Overall, we received 130 reports at
this bugSWAT, resulting in 91 identified vulnerabilities. These reports provided
invaluable, actionable insights, allowing our engineering teams to implement
targeted mitigations, enhance security controls, and further harden the Google
Cloud platform. Researcher participation in ongoing events like this one enable
us to proactively address potential issues and further strengthen our platform.

This collaborative effort resulted in the Cloud VRP awarding ~$1.6 million for
the security findings from this event alone (which includes a 100% bonus added
to each reward). Combined with our ongoing VRP reports, this bugSWAT has pushed
our total Cloud VRP rewards to ~$2.5M in 2025, reflecting Google Cloud’s
commitment to rewarding high-impact security research.

## Impactful reports

We want to emphasize that the Google Cloud VRP’s rewards are some of the highest
in the bug bounty industry. Here's a summary of bugSWAT vulnerability report
counts broken down by severity:

- **Critical:** 0 reports – Represents the most serious vulnerabilities. These
are typically issues like Remote Code Execution (RCE) on a production
system, or flaws that allow widespread, unauthorized access to user data or
system controls. Exploitation is often straightforward.
- **High**: 46 reports, $24,000 average reward per report – Flaws that could
lead to significant data compromise, privilege escalation, or bypass of key
security controls. Exploitation often requires the attacker to have some
form of presence or role within the target's cloud environment or
organization (a pre-existing relationship). Example: Impersonation of
service accounts.
- **Medium**: 35 reports, $12,000 average reward per report – Vulnerabilities
posing a risk, but with a more limited scope or requiring more specific
conditions to exploit than High.
- **Low**: 10 reports, $1,100 average reward per report – Vulnerabilities that
are difficult to exploit or have minimal impact on overall security.
Examples: Issues requiring significant user interaction, theoretical
weaknesses with no clear attack path.

Two reports, in particular, highlighted impactful findings and were among the
highest rewarded during the event. Both issues have been fixed as of this blog’s
publishing. Here are summaries of these impactful findings:

**Network Egress Filter Bypass**

A high-severity vulnerability was discovered that allowed attackers to
circumvent network safeguards intended to block access to restricted internal
addresses within a customer's Google Cloud project. Exploiting this flaw enabled
Server-Side Request Forgery (SSRF) attacks. A successful SSRF attack could
expose sensitive instance service account credentials, most notably from the
cloud instance metadata service. With these credentials, an attacker could
potentially escalate privileges and move laterally, gaining broader unauthorized
access to other resources and data within the victim's GCP environment.

**SQL Injection in Database Connector**

A high-severity class of vulnerabilities was discovered that allowed attackers
with only view access to a report to execute arbitrary SQL queries against the
underlying data source. The queries ran with the report owner's credentials,
meaning an attacker could potentially bypass the report's intended scope to
read, modify, or delete data within the datasets the owner could access.

### And the winners of the bugSWAT were:

- **Most Valuable Hacker:** [Sivanesh Ashok](https://x.com/sivaneshashok) &
[Sreeram KL](https://x.com/kl_sree) – for an impressive number of individual
reports, uncovering highly impactful issues and identifying widespread
vulnerability classes across a variety of our products. What set them apart
was the amazing quality of their reports, which enabled our teams to quickly
test, assess, and _mitigate_ the impact of their findings, making our
platforms significantly safer.
- **2nd Most Valuable Hacker:** [Liv Matan](https://x.com/terminatorLM) – for
an impressive number of reports, uncovering highly impactful issues, and
identifying widespread vulnerability classes.
- **Most Surprising/Creative Report:** [Jakub Domeracki](https://x.com/j_domeracki) – for his report on service
account impersonation. Multiple bugSWAT researchers reported the same issue
but it was only Jakub’s report that was able to demonstrate impact. His
creativity and skill proved this issue is highly impactful and resulted in
multiple researchers being rewarded.
- **Best “Explain it Like I’m 5” Report Title:** [Kat Traxler](https://x.com/NightmareJS) – Kat’s report was so engaging that
any 5-year-old would have been engrossed.

## Targeted product inclusion

Because Google Cloud encompasses hundreds of products, we narrowed the scope of
targets our bugSWAT researchers could hack on. Out of the 9 targets we chose, we
included certain enterprise products in the bugSWAT scope that our independent
researchers do not have easy access to. To enable research on these products
during the bugSWAT event, we provided them with their own instances for these
enterprise products. This led to a large number of vulnerabilities being
identified and mitigated, further securing these products.

## Why this matters

This bugSWAT event highlights the immense value of Vulnerability Reward Programs
(VRPs) and collaborative security research. Bug bounty programs like the Cloud
VRP are essential because they bring a diversity of skills and perspectives.
External researchers often think like potential attackers, exploring novel
pathways and uncovering issues that might be missed otherwise.

Events like bugSWAT focus external expertise on specific areas, accelerating the
discovery and _mitigation_ of potential vulnerabilities. By partnering with the
security research community, we can:

- **Identify and Fix Bugs Faster:** The focused effort leads to quicker
identification and remediation of issues.
- **Enhance Platform Resilience:** Addressing the findings from this event
directly strengthens the security posture of Google Cloud.
- **Stay Ahead of Threats:** Proactive security research helps us anticipate
and defend against emerging attack techniques.

Ultimately, the Cloud VRP and events like this bugSWAT are crucial components of
our defense-in-depth strategy, making Google Cloud a more secure and trusted
platform for all our users. We're incredibly proud of the results of this
bugSWAT and the commitment of everyone involved.

## I'd love to join future hacking events, how do I get invited?

Google typically considers the performance of individual researchers from the
past year of Cloud VRP reports as well as previous bugSWAT event performance
when deciding who to invite.

Remember, this is about quality, not quantity – the higher the impact of your
reports, the more you'll be rewarded, and the higher you'll move up in the
ranking of impactful researchers, increasing your chances of receiving an
invitation to bugSWAT.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab