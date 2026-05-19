---
source: bughunters
source_url: https://bughunters.google.com/blog/standardizing-rewards-in-google-vrp
title: "Standardizing Rewards in Google VRP: Introducing Information Tiers and Action Criticality - Google Bug Hunters"
description: "We are evolving our reward model to reflect the changing security landscape by introducing two new dimensions to our model: Information Tiers and Action Criticality."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/standardizing-rewards-in-google-vrp#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Standardizing Rewards in Google VRP: Introducing Information Tiers and Action Criticality

![](https://storage.googleapis.com/bughunters-article-images/blogs/schcamille.jpg)

Camille Schneider

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/jangora.jpg)

Jan Gora

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/serb.jpg)

Sam Erb

Information Security Engineer

Published: Apr 8, 2026

Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# Standardizing Rewards in Google VRP: Introducing Information Tiers and Action Criticality

> **TL;DR:** Since the inception of the Google VRP, we have continuously evolved
> our reward model to reflect the changing security landscape. Today, we are
> introducing two new dimensions to our model: **Information Tiers** and
> **Action Criticality**. These changes should **not affect reward amounts**
> **significantly**, but aim to **standardize reward payouts** by focusing on the
> actual impact of a vulnerability and the sensitivity of the data involved,
> rather than relying primarily on
> [Domain Tiers](https://bughunters.google.com/blog/externalizing-the-google-domain-tiers-concept). In
> particular, this will be helpful as it provides more consistency and
> predictability for researchers when it comes to our
> [C1 category of vulnerabilities](https://bughunters.google.com/about/rules/google-friends/google-and-alphabet-vulnerability-reward-program-vrp-rules#reward-table).

* * *

## From Domain Tiers to Impact-Based Rewards

Historically, our reward model has been highly influenced by Domain Tiers, which
didn't always accurately reflect the true impact of a vulnerability. For
example, a minor data leak on a Tier 0 domain might have received a higher base
reward than a more sensitive leak on a Tier 1 domain, leading to inconsistencies
that required manual adjustments.

In particular, our category “Other valid security vulnerabilities (C1)” had a
very large base range, from $5,000 to $15,000 for Domain Tier0 and Tier1, which
made the reward decision sometimes inconsistent, and led to confusion from
researchers. With this new reward system, we aim at making the reward amounts
more predictable and less arbitrary, especially for the C1 category.

## Understanding Information Tiers (IT)

We are adopting a three-tier categorization for data sensitivity to ensure that
leaks of highly sensitive information are rewarded appropriately:

- **IT0 (Credentials & Internal Systems):** Information that could be used to
compromise a user’s Google Account, Google’s infrastructure, or other
unauthorized access across multiple Google systems and applications.
- **IT1 (High Security Impact User Data):** User data such as Drive documents,
photos, or fine-grained location data, as well as sensitive internal data
that doesn't directly compromise a large part of our infrastructure,
systems, and applications.
- **IT2 (Metadata & Other Lower Security Impact User Data):** Metadata or user
data we consider to have less security impact or less sensitivity than IT1
data, such as file ownership information or email addresses.

You can find more information and examples in our
[rule page](https://bughunters.google.com/about/rules/google-friends/google-and-alphabet-vulnerability-reward-program-vrp-rules#information-tiers-it-).

## Measuring Action Criticality (AC)

For state-changing vulnerabilities, we are introducing **Action Criticality,**
which acts as an extension to the Information Tiers for cases where the impact
is not strictly an information leak:

- **Critical Actions (CA):** Actions that directly affect credentials or lead
to account takeover (e.g., changing a user's password or adding an SSH key).
- **Impactful Actions (IA):** Actions affecting sensitive user data, such as
deleting photos or sharing private documents.
- **Moderate Actions (MA):** Actions with limited scope or affecting less
sensitive metadata, such as changing a profile picture or a user’s display
name.

You can find more information and examples in our
[rule page](https://bughunters.google.com/about/rules/google-friends/google-and-alphabet-vulnerability-reward-program-vrp-rules#action-criticality-ac-).

## The New Reward Model

These new metrics have been integrated into our reward table, specifically
expanding or refining the **C1** and **S2** categories into subcategories ( **a,**
**b, and c**) based on the Information Tier or Action Criticality.

You can find more information and examples in the new
[reward table](https://bughunters.google.com/about/rules/google-friends/google-and-alphabet-vulnerability-reward-program-vrp-rules#reward-table).

## Incentivizing High-Impact Research

By scaling down rewards for client-side non-XSS vulnerabilities that have lower
impact, we want to further incentivize researchers to focus on discovering
critical vulnerabilities like XSS, which can often cause significantly more
damage.

In addition, a further goal we worked towards was evening out the rewards for
Tier0 and Tier1 domains in cases where Information Tier or Action Criticality is
impacted, as we think that in practice, those types of vulnerabilities have very
similar impact.

### Example Changes

Overall, we don't expect this update to drastically change the reward amounts.
To give you an idea of how this looks in practice, here are a few examples from
our recent dry runs
( [downgrades](https://bughunters.google.com/about/rules/google-friends/google-and-alphabet-vulnerability-reward-program-vrp-rules#downgrades)
and bonuses have been omitted for clarity):

| Vulnerability | Old Reward | New Reward |
| --- | --- | --- |
| Vulnerability leading to deanonymizing a user who visits a 3p webpage (or interacts with a 3p mobile app) | $1,337- $10,000 (or higher range depending on domain tier, usually met with many downgrades, sometimes leading to $500 rewards or lower) | **$1,337** |
| XS-Leak (Cross-site leak) in our Issue Tracker system leaking content of reported vulnerabilities (which is Information Tier 0) | $13,337 without downgrades (the C1 category base value was often changed at the panel’s discretion, in the range of $5,000 - $15,000) | **$15,000** (as base, without downgrade) |
| Authorization bypass in a T1 domain proxying YouTube Issue Tracker bugs, leading to a leak of a significant amount of sensitive issues | $20,000 (affecting a T1 domain) | **$31,337** (aligns to Tier0 and Tier1 rewards for S2b) |
| Clickjacking or XS-Leaks leaking the content of a document in Drive | The C1 category base value was often changed at the panel’s discretion, in the range of $5,000 - $15,000, leading to different reward amounts, sometimes doubled or more, for reports with similar impact | **$5,000** (as base, without downgrade, C1b category) |

## Conclusion

We believe these changes will lead to a fairer and more transparent reward
process for our community of security researchers. By focusing on the
sensitivity of information and the criticality of actions, we can ensure that
our rewards accurately reflect the real-world security impact of your
vulnerability findings.

Happy bug hunting!

## FAQ

What did the old reward table look like?

**Expand to view the old reward table**

For your reference, here's what the "Reward amounts" table looked like before
the changes we announced in this post:

| Category | Examples | Google applications on [Tier 0](https://github.com/google/bughunters/blob/main/domain-tiers/external_domains_google.asciipb) domains \[0\], or global impact \[1\] (T0) | Google applications on [Tier 1](https://github.com/google/bughunters/blob/main/domain-tiers/external_domains_google.asciipb) domains \[2\] (T1) | Normal Google Applications (T2)<br> Examples include: \*.google.com, \*.youtube.com, \*.blogger.com, \*.admob.com | Applications on acquisition [Tier 0, Tier 1](https://github.com/google/bughunters/blob/main/domain-tiers/external_domains_acquisitions.asciipb) domains \[3\]\[4\] (T3a) | Other acquisitions, other sandboxed or lower priority applications \[4\] (T3b)<br> Examples include: \*.withgoogle.com, \*.withyoutube.com |
| --- | --- | --- | --- | --- | --- | --- |
| Vulnerabilities giving direct access to Google servers |
| Remote code execution (S0) | Command injection, deserialization bugs, sandbox escapes | $101,010 | $101,010 | $75,000 | $10,000 | $1,337 - $5,000 |
| Unrestricted file system or database access (S1) | Unsandboxed XXE, SQL injection | $75,000 | $75,000 | $50,000 | $10,000 | $1,337 - $5,000 |
| Logic flaw bugs leaking or bypassing significant security controls impacting SPII \[5\] (S2a) | SPII – Direct object reference, remote user impersonation | $50,000 | $50,000 | $31,337 | $5,000 | $500 |
| Logic flaw bugs leaking or bypassing significant security controls impacting PII or other user confidential information (S2b) | PII or other user confidential information – Direct object reference, remote user impersonation | $31,337 | $20,000 | $13,337 | $2,500 | $500 |
| Logic flaw bugs leaking or bypassing significant security controls impacting other data/systems (S2c) | Other – Direct object reference, remote user impersonation | $13,337 | $10,000 | $5,000 | $1,337 | $500 |
| Vulnerabilities giving access to client or authenticated session of the logged-in<br> victim |
| Execute code on the client (C0) | Web: Cross-site scripting<br>Mobile / Hardware: Code execution | $20,000 | $15,000 | $10,000 | $500 | $200 |
| Other valid security vulnerabilities (C1) | Web: CSRF, Clickjacking, [XSLeaks](https://bughunters.google.com/learn/invalid-reports/web-platform/xsleaks/5022006283862016/xsleaks-and-xs-search)<br>Mobile / Hardware: Information leak, privilege<br> escalation | $5,000 - $15,000 | $5,000 - $15,000 | $1,337- $10,000 | $500 | $200 |

\[0\] Tier 0 domains are defined as domains where a critical vulnerability (e.g.
XSS or authorization bypass) could lead to a compromise of a user's account or
execution of code on their system.

\[1\] “Global impact” refers to any vulnerability that impacts a significant
portion of the Internet, through integration with a product in Google VRP scope.
For example, an XSS in Google Analytics embedded JavaScript.

\[2\] Tier 1 domains are defined as domains where a vulnerability could disclose
particularly sensitive user data.

\[3\] Tier 0 and tier 1 acquisition domains are defined as domains where a
compromise may lead to access of highly-sensitive information.

\[4\] Note that acquisitions qualify for a reward only after the initial six-month
blackout period has elapsed.

\[5\] SPII is defined
[here](https://developers.google.com/standard-payments/reference/glossary#spii).

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab