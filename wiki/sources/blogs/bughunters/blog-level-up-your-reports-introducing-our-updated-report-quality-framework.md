---
source: bughunters
source_url: https://bughunters.google.com/blog/level-up-your-reports-introducing-our-updated-report-quality-framework
title: "Level Up Your Reports: Introducing Our Updated Report Quality Framework - Google Bug Hunters"
description: "We're announcing an update to how we evaluate report quality across the Google, Cloud, AI, and Abuse Vulnerability Reward Programs (VRPs) to ensure more consistent reward outcomes, and make it straightforward to qualify for the exceptional reward bonus."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/level-up-your-reports-introducing-our-updated-report-quality-framework#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Level Up Your Reports: Introducing Our Updated Report Quality Framework

![](https://storage.googleapis.com/bughunters-article-images/blogs/darbyhopkins.jpg)

Darby Hopkins

Cloud Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/mcote.png)

Michael Cote

Technical Program Manager

![](https://storage.googleapis.com/bughunters-article-images/blogs/serb.jpg)

Sam Erb

Information Security Engineer

Published: Sep 22, 2025

Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# Level Up Your Reports: Introducing Our Updated Report Quality Framework

We're excited to announce an update to how we evaluate report quality across the
Google, Cloud, AI, and Abuse Vulnerability Reward Programs (VRPs). This new
framework is designed to provide clearer guidelines, ensure more consistent
reward outcomes, and make it straightforward to qualify for the exceptional
reward bonus. While the bonus is going down, we believe that more reports will
now be able to qualify for the reward and thus more researchers will be rewarded
with this change. Our goal is to foster an even stronger partnership with the
security research community, ultimately making Google products safer for
everyone.

## Why the Change?

We've heard your feedback. Our previous system for assessing report quality was
not always as specific as it could have been or obtainable for server-side
vulnerabilities, which sometimes led to a lack of clarity on how reward amounts
were determined. To address this, we've developed a more granular,
dimension-based framework. This new framework aims to bring more transparency
and consistency to our reward process and to enable more reports to qualify for
the exceptional reward bonus.

## What's New?

The updated framework, detailed in our VRP rules, evaluates reports across
several key dimensions:

- **Vulnerability Description:** Clarity and completeness of the issue
explanation.
- **Attack Preconditions:** What's needed for the attack to be possible.
- **Impact Analysis:** Realistic and demonstrated security impact.
- **Reproduction Steps / PoC:** Clear, accurate, and easy-to-follow steps to
reproduce the vulnerability. Providing an automated Proof of Concept, where
feasible, is highly encouraged. (See our guide on
[creating exceptional automated PoCs](https://bughunters.google.com/learn/improving-your-reports/how-to-report/5585762221359104/create-an-exceptional-automated-poc)).
- **Target/Product Information:** Specifics like versions, URLs, etc.
- **Reproduction Output:** Supporting evidence like videos, logs, or HTTP
responses.
- **Researcher Responsiveness:** Timeliness and quality of communication.

Based on these dimensions, reports will be assessed as Low, Good, or Exceptional
quality. See the full rules, linked below, for additional details.

## New Reward Multipliers

To align with this new framework, we're adjusting the reward multipliers. The
final reward amount will be influenced by the report quality rating as follows:

- **Low Quality:** 0.8x
- **Good Quality:** 1.0x
- **Exceptional Quality:** 1.2x

We are starting with a “low quality” multiplier of 0.8x to allow the community
to adapt to the new, more detailed criteria but will move the "low quality"
reports to 0.5x in the future. This range is a change from our previous
multipliers \[0.5x, 1x, 1.5x\].

## Rewarding Innovation: The New Novelty Bonus

Beyond report quality, we want to explicitly recognize truly unique or
innovative research. To this end, we're introducing a **Novelty Bonus**, ranging
from +$1,000 to +$5,000. This discretionary bonus will be awarded for reports
that cause our security teams to think differently about a problem or uncover
entirely new vulnerability classes.

## Benefits for Researchers

**Clearer Expectations:** The detailed dimensions show you exactly what we look
for in an exceptional-quality report.

**More Consistent Rewards:** A structured framework leads to more predictable
and fair reward outcomes.

**Recognition for Effort:** Reports that save us time and are easier to
reproduce will lead to rewards being issued more quickly and qualify for the
exceptional reward bonus.

### Benefits for Google Security

**Faster Triage:** High-quality reports are quicker to understand and reproduce.

**Effective Remediation:** Clear impact analysis and PoCs help our product teams
fix issues faster.

**Stronger Security Posture:** By incentivizing detailed and actionable reports,
we can address vulnerabilities more efficiently.

## Learning from Success: The Android VRP Example

We're confident in this approach, partly due to the success of a similar
framework within the Android VRP. Since implementing their detailed report
quality guidelines, the Android VRP has seen a significant improvement in the
quality and actionability of submissions, helping to keep the Android ecosystem
safer.

## When Will This Take Effect?

These changes to the Report Quality framework went live on September 16th.
Reports submitted on or after this date will be evaluated using the new
criteria.

## Where to Find the Full Details

The complete Report Quality dimensions and multiplier information are now part
of the official rules for each VRP:

- [Google VRP Rules](https://bughunters.google.com/about/rules/google-friends/6625378258649088/google-and-alphabet-vulnerability-reward-program-vrp-rules#report-quality)
- [Cloud VRP Rules](https://bughunters.google.com/about/rules/google-friends/4849867320328192/cloud-vulnerability-reward-program-rules#report-quality)
- [Abuse VRP Rules](https://bughunters.google.com/about/rules/google-friends/5238081279623168/abuse-vulnerability-reward-program-rules#report-quality)

Happy bug hunting!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab