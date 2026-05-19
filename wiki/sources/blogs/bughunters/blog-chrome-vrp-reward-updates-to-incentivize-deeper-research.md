---
source: bughunters
source_url: https://bughunters.google.com/blog/chrome-vrp-reward-updates-to-incentivize-deeper-research
title: "Chrome VRP Reward Updates to Incentivize Deeper Research - Google Bug Hunters"
description: "The Chrome VRP is increasing reward amounts and their structure to incentivize high-quality reporting and deeper research of Chrome vulnerabilities, see this post for details!"
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/chrome-vrp-reward-updates-to-incentivize-deeper-research#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Chrome VRP Reward Updates to Incentivize Deeper Research

![](https://storage.googleapis.com/bughunters-article-images/blogs/amyressler.jpg)

Amy Ressler

Information Security Engineer

Published: Aug 28, 2024

Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# Chrome VRP Reward Updates to Incentivize Deeper Research

Time flies: Believe it or not, Chrome Browser turns 16 this year and, following
closely behind, the Chrome VRP is turning 14! As Chrome has matured over these
years, finding the most impactful and exploitable bugs has become more
challenging. At the same time, new features are frequently introduced into
Chrome that may result in new issues which we also want to encourage being
reported.

Therefore, it is time to evolve the Chrome VRP rewards and amounts to provide an
improved structure and clearer expectations for security researchers reporting
bugs to us and to incentivize high-quality reporting and deeper research of
Chrome vulnerabilities, exploring them to their full impact and exploitability
potential.

In this blog post, we'll explain how we have moved away from a single table of
reward amounts for non-mitigated bugs, and separated out memory corruption
issues from other classes of vulnerabilities. This will allow us to better
incentivize more impactful research in each area, and also reward for higher
quality and more impactful reporting.

## Memory Corruption Bugs

We have remodeled our reward structure for memory corruption vulnerabilities
into the following categories:

- **High-quality report with demonstration of RCE:** Report clearly
demonstrates remote code execution, such as through a functional exploit.
- **High-quality report demonstrating controlled write**: Report clearly
demonstrates attacker controlled write of arbitrary locations in memory.
- **High-quality report of memory corruption**: Report of demonstrated memory
corruption in Chrome that consists of all the characteristics of a
high-quality report.
- **Baseline**: A report consisting of a stack trace and PoC displaying
evidence that memory corruption is triggerable and reachable in Chrome.

While the reward amounts for baseline reports of memory corruption will remain
consistent, we have increased reward amounts in the other categories with the
goal of incentivizing deeper research into the full consequences of a given
issue. The highest potential reward amount for a single issue is now $250,000
for demonstrated RCE in a non-sandboxed process. If the RCE in a non-sandboxed
process can be achieved without a renderer compromise, it is eligible for an
even higher reward, to include the renderer RCE reward.

|  | High-quality report with demonstration of RCE | High-quality report demonstrating controlled write | High-quality report of demonstrated memory corruption | Baseline |
| --- | --- | --- | --- | --- |
| Sandbox escape / Memory corruption / RCE in a non-sandboxed process \[1\], \[2\] | Up to $250,000 | Up to $90,000 | Up to $35,000 | Up to $25,000 |
| Memory Corruption / RCE in a highly privileged process (e.g. GPU or network processes) \[2\] | Up to $85,000 | Up to $70,000 | Up to $15,000 | Up to $10,000 |
| Renderer RCE / memory corruption in a sandboxed process | Up to $55,000 | Up to $50,000 | Up to $10,000 | Up to $7,000 \[3\] |

\[1\] Also includes the GPU process on Android. RCE in the Android GPU process is
considered a sandbox escape since the GPU process is not sandboxed on the
Android platform.

\[2\] Amounts are based on the precondition of a compromised renderer, otherwise
the equivalent renderer reward will also be added.

\[3\] Reports of renderer OOB reads or DCHECK / SEGV / etc. bugs in V8, without
demonstration of write or RCE, are only eligible for baseline reward amounts.

## Other Vulnerability Classes

Memory corruption bugs are not the only type of vulnerabilities in Chrome, of
course. For other classes of vulnerabilities, we want to ensure more
deterministic reward decisions based on report quality, impact, and the
potential harm for people using Chrome:

- **Lower impact**: Low potential for exploitability, significant
preconditions to exploit, low attacker control, low risk / potential for
user harm
- **Moderate impact**: Moderate preconditions to exploit, fair degree of
attacker control
- **High impact**: Straight-forward path to exploitability, demonstrable and
significant user harm, remote exploitability, low preconditions to exploit

We have included [examples](https://g.co/chrome/vrp#other-vulnerability-classes)
of each category of report in our Chrome VRP policies page.

|  | High Quality && High Impact \[1\] | High Quality && Moderate Impact \[1\] | Baseline \|\| Lower Impact |
| --- | --- | --- | --- |
| UXSS \|\| Site isolation bypass | Up to $30,000 | Up to $20,000 | Up to $10,000 |
| Security UI spoofing | Up to $10,000 | Up to $5,000 | Up to $3,000 |
| User information disclosure | Up to $25,000 | Up to $10,000 | Up to $2,000 |
| Local privilege escalation \[2\] | Up to $15,000 | Up to $5,000 | Up to $2,000 |
| Web platform privilege escalation | Up to $7,000 | Up to $4,000 | Up to $1,000 |
| Exploitation mitigation bypass | Up to $5,000 | Up to $4,000 | Up to $1,000 |

\[1\] Reports of a vulnerability in any of these classes _must_ consist of a
functional demonstration of the bug reported and a PoC to be considered a high
quality report.

\[2\] Valid reports of LPE vulnerabilities should demonstrate exploitability that
breaks an OS security boundary using a Chrome component and is otherwise within
Chrome's threat model.

## Update to MiraclePtr Bypass Reward

When MiraclePtr was enabled on active release channels of Chrome last year,
MiraclePtr-protected bugs in non-renderer processes were then considered highly
mitigated security bugs. In tandem, we launched the
[MiraclePtr Bypass Reward](https://g.co/chrome/vrp#miracleptr-bypass-reward) of
$100,115.

As of Chrome 128, MiraclePtr-protected bugs in non-renderer processes are no
longer considered security bugs. As such, MiraclePtr is considered a declarative
security boundary and a valid
[submission of a MiraclePtr bypass](https://g.co/chrome/vrp##miracleptr-bypass-reward)
is now eligible for a reward of $250,128.

## As Things Change, Some Things Stay The Same

All reports are still eligible for
[bonus rewards](https://g.co/chrome/vrp#additional-chrome-rewards) when they
include the applicable characteristics. We will continue exploring more
experimental reward opportunities, similar to the previous
[Full Chain Exploit Reward](https://security.googleblog.com/2023/06/announcing-chrome-browser-full-chain.html),
and evolving our program in ways to better serve the security community.

Reports that don't demonstrate security impact or the potential for user harm,
or are purely reports of theoretical or speculative issues are unlikely to be
eligible for a VRP reward.

As always, we'll continue to be transparent and communicative about your
security bug reports and the reward decisions for them.

## Good Hunting

We hope the changes we described in this blog post are helpful and inspiring to
browser vulnerability researchers. We also hope the increased reward amounts
demonstrate our acknowledgement of the challenges faced finding the most complex
bugs in Chrome and the skills needed for demonstrating exploitability. We
appreciate your efforts to help make Chrome more secure for all users.

|
|

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab