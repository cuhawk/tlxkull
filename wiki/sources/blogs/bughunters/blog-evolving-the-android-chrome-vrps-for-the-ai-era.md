---
source: bughunters
source_url: https://bughunters.google.com/blog/evolving-the-android-chrome-vrps-for-the-ai-era
title: "Evolving the Android & Chrome VRPs for the AI Era - Google Bug Hunters"
description: "We are announcing changes to the Chrome & Android Vulnerability Reward Programs (VRP) which take effect immediately and are focused on adjusting our reward amounts and bonuses to reflect the types of reports and bug categories that provide the most value to security today."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/evolving-the-android-chrome-vrps-for-the-ai-era#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Evolving the Android & Chrome VRPs for the AI Era

![](https://storage.googleapis.com/bughunters-article-images/blogs/ajgo.jpg)

Alex Gough

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/shaileshs.jpg)

Shailesh Saini

Director, Android

![](https://storage.googleapis.com/bughunters-article-images/blogs/tony.jpg)

Tony Mendez

Technical Program Manager

Published: Apr 30, 2026

Vulnerability Reward Program  Chrome  Android

[RSS Feed](https://bughunters.google.com/feed/en)

# Evolving the Android & Chrome VRPs for the AI Era

The primary goal of the Android & Google Devices and Chrome Vulnerability Reward
Programs (VRPs) has been to partner with the external security researcher
community to analyze areas lacking coverage, helping us discover vulnerabilities
that historically have been hard to find. In today’s shifting security research
landscape, we want to continue to reward researchers for their expertise and
creativity in finding the most challenging and impactful vulnerabilities in our
products.

Over the past few years, AI and automation have accelerated the pace of
vulnerability discovery, and our teams are moving at an unprecedented rate –
remediating risks more effectively than ever before. The latest advancements in
AI from Google and the broader industry have made it significantly easier to
take a test case and explain the root cause, propose a suitable fix, and to find
variants of known problems. And to keep pace with vulnerability discovery, we’ve
been continuing to implement structural improvements in our products to make it
increasingly difficult to achieve full chain exploits. For example, Android
recently introduced Advanced Protection Mode and continues to drive adoption of
[memory safe languages](https://security.googleblog.com/2025/11/rust-in-android-move-fast-fix-things.html).
Chrome has driven structural improvements to the V8 sandbox, container
hardening, and in-browser memory quarantining. By pairing automated tools like
[Big Sleep](https://blog.google/innovation-and-ai/technology/safety-security/cybersecurity-updates-summer-2025/),
[CodeMender](https://deepmind.google/blog/introducing-codemender-an-ai-agent-for-code-security/),
and [OSS-Fuzz service](https://bughunters.google.com/open-source-security/oss-fuzz) with the human expertise
from teams like [Project Zero](https://projectzero.google/),
[Bug Hunters](https://bughunters.google.com/), dedicated product security teams,
and the
[Google Threat Intelligence Group](https://cloud.google.com/blog/topics/threat-intelligence),
we have a multi-layered approach to addressing security issues across Google
products and other non-Google platforms to keep users safe online.

As the security research landscape evolves with AI, we're making changes in our
programs to ensure we're rewarding the most challenging and impactful
vulnerabilities in our products. This focus provides the most value to our
security teams and helps keep users safe today, all while making sure security
researchers continue to be rewarded for their efforts.

## Top-Tier Rewards for Hard Problems

We know that certain particularly impactful exploits remain incredibly difficult
to achieve and we’ve greatly appreciated collaborating with the researcher
community to discover and unearth them. We want to build on this partnership by
continuing to emphasize the highest tiers of rewards across both Android and
Chrome.

Android:

- Up to **$1,500,000** for a zero-click full chain Pixel Titan M2 compromise
with persistence.
- Up to **$750,000** for a zero-click full chain Pixel Titan M2 compromise.

Chrome:

- Up to **$250,000** for full chain browser process exploits on the latest
operating systems and hardware.
- Up to **$250,128** bonus for a report that successfully exploits an
allocation we believe to be protected by MiraclePtr.

## Key Changes to the Android & Google Devices VRP

**Focusing On Issues With the Highest User Impact:** We are revising our program
scope to emphasize categories that represent the highest risk to our users. We
are also prioritizing categories that remain more challenging for automated AI
tooling to find to ensure we reward researchers for their unique skills and
talents.

**Incentivizing Actionable Reports:** We are shifting our program focus on Linux
kernel vulnerabilities to Google-maintained components unless there is concrete
proof of exploitability on Android or our devices. For most vulnerabilities we
will also be strongly incentivizing reports to contain proposed patches for
addressing the underlying issue.

**Enhanced Reporting Support:** We will be investigating options for our
reporting process to provide researchers with simpler methods to clearly
demonstrate the impact of their reports, enabling a more streamlined process
from start to finish. More details will be shared later this year.

For full details, please see the
[Android and Google devices security reward program rules](https://bughunters.google.com/about/rules/android-friends/android-and-google-devices-security-reward-program-rules).

## Key Changes to the Chrome VRP

**Incentivizing Actionable Reports:** While AI has made it effortless to produce
lengthy, detailed write-ups, our internal tooling has also evolved to help us
automatically explain and suggest fixes for bugs. Moving forward, we are
shifting our program's focus to prioritize concrete proof that a bug exists. We
now consider the most effective reports to be concise, containing only a
reproducer and the necessary artifacts to help us validate and route the issue.

**Phasing Out RCE and Renderer Arbitrary R/W Bonuses:** Last year, we noticed a
scarcity of reports demonstrating renderer code execution (RCE), so we
introduced an enhanced reward for arbitrary read/write (R/W) and RCE
vulnerabilities. This successfully encouraged a wave of new
submissions—validating that these exploits were still possible and motivating
our ongoing work to apply an in-process sandbox to V8. Today, AI has made
demonstrating these techniques almost routine, allowing us to focus on more
complex, novel escalation methods. As a result, we are retiring these specific
special bonuses.

**Upgrading Intake & Reproduction Infrastructure:** Following the success of
V8’s sandbox escape mode for d8, we are overhauling our intake and reproduction
infrastructure. In the coming weeks, we will release special configurations of
Chrome designed specifically for researchers to provide evidence of arbitrary
R/W in privileged processes and controlled browser memory leaks. Details on how
to use these builds will be added to the
[VRP FAQ](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/security/vrp-faq.md)
shortly.

For full details, please see the
[Chrome VRP rules & guidelines](https://bughunters.google.com/about/rules/chrome-friends/chrome-vulnerability-reward-program-rules).

## Looking Ahead

Along with these changes, we will be reducing some of our reward amounts and
bonuses across Android and Chrome. While these adjustments may reduce the payout
for a _single_ bug report, we continue to prioritize our VRPs and the total
aggregate rewards paid out in 2026 is expected to increase.

The new values and reward categories are now live on our
[Android](https://bughunters.google.com/about/rules/android-friends/android-and-google-devices-security-reward-program-rules)
and
[Chrome](https://bughunters.google.com/about/rules/chrome-friends/chrome-vulnerability-reward-program-rules)
rules pages. We'll continue to evaluate and refine our VRPs to ensure they
remain the industry standard for security research.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab