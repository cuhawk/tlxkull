---
source: bughunters
source_url: https://bughunters.google.com/blog/one-year-of-mobile-vrp-reward-increases-and-lessons-learned
title: "One Year of Mobile VRP – Reward Increases and Lessons Learned - Google Bug Hunters"
description: "We're celebrating one year of the Google Mobile VRP. See our blog to see what happened in that time and how we are adjusting our rewards structure to be even more attractive for security researchers!"
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/one-year-of-mobile-vrp-reward-increases-and-lessons-learned#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# One Year of Mobile VRP – Reward Increases and Lessons Learned

![](https://storage.googleapis.com/bughunters-article-images/blogs/kblasiak.jpg)

Kristoffer Blasiak

Information Security Engineer

Published: Apr 30, 2024

Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# One Year of Mobile VRP – Reward Increases and Lessons Learned

The
[Mobile VRP](https://bughunters.google.com/about/rules/6618732618186752/google-mobile-vulnerability-reward-program-rules)
launched in May 2023, and after one year, it's time to take a look back at what
we've achieved. Most importantly, we received over 40 valid security bug
reports, nearing $100,000 in rewards paid to security researchers.

A large portion of the vulnerabilities reported to us fell into the following
vulnerability categories:

- Permission Bypasses / Missing Permission Checks
- Intent Redirection
- CreatePackageContext related issues
- Package name squatting related issues

_**PS!**_ _To read more about some of these vulnerability types, click_
_[here](https://developer.android.com/privacy-and-security/risks)._

Some of the most impactful reported vulnerabilities (mainly in
[Tier 1](https://bughunters.google.com/about/rules/6618732618186752/google-mobile-vulnerability-reward-program-rules#tier-1)
and
[Tier 2](https://bughunters.google.com/about/rules/6618732618186752/google-mobile-vulnerability-reward-program-rules#tier-2)
applications) allowed for:

- Local Arbitrary Code Execution (in some cases in SDKs developed by Google)
- Arbitrary Code Execution after following a link
- Data theft of sensitive information

In addition to handling incoming security bug reports, we also attended BugSWAT
to meet our researchers for in-person feedback. Needless to say: it has been an
eventful first year for this new VRP.

The goal was always _“to mitigate vulnerabilities in first-party Android_
_applications, and thus keep users and their data safe”_, and to do so by
_“recognizing the contributions and hard work of researchers who help Google_
_improve the security posture of our first-party Android applications”_.

Judging by these metrics, we are happy to say that the Mobile VRP has been a
thorough success! Nevertheless, after feedback from our top bug hunters, we
decided that the latter part of our goal (concerning recognition) could still be
improved.

In this blog post we will explain the changes we made to the Mobile VRP, how we
expect those adjustments to impact the program going forward, and how these
updates will affect you, as a bug hunter.

## Reward increases and increased focus

The two main changes to our Mobile VRP rules that affect bug hunters are the
updates we made to our rewards tables:

1. We increased reward amounts by up to 10x in some categories (for example
Remote Arbitrary Code Execution in a Tier 1 app went from $30,000 to
$300,000)
2. We increased emphasis on report quality and demonstrated impact (see the
next section of this post for details)

We also took the opportunity to focus the reward increases on categories we want
researchers to pay particular attention to, to make sure we reward the most
impactful reports appropriately.

An example of this is Data theft, where we increased the reward amounts
significantly, but we also made sure to give
[examples](https://bughunters.google.com/about/rules/6618732618186752/google-mobile-vulnerability-reward-program-rules#theft-of-sensitive-data)
of the impact different types of Data theft have; this helps clarify how the
data acquired has an impact on the final reward amount.

Some additional, smaller changes were also made to our rules. For example, the
2x modifier for SDKs is now baked into the regular rewards. This should increase
overall rewards, and will make panel decisions easier.

## Quality-based reward modifiers

One of the things we want to achieve is to encourage bug hunters to spend a
little more time crafting and refining their reports. To incentivize bug hunters
to do so, we established a new reward modifier to reward bug hunters for the
extra time and effort they invest when creating high-quality reports that
clearly demonstrate the impact of their findings.

High-quality reports help the VRP make faster decisions, and make sure that bug
hunters receive appropriate rewards for their research. In other words: Get paid
more, and faster!

From now on, reports will fall into one of three categories:

- Exceptional quality (1.5x reward amount)
- Good quality (1x reward amount)
- Low quality (0.5x reward amount)

For the details on how to make sure your report falls into the Good or
Exceptional category, visit the
[Report Quality section](https://bughunters.google.com/about/rules/6618732618186752/google-mobile-vulnerability-reward-program-rules#report-quality)
of the newly updated
[Mobile VRP rules](https://bughunters.google.com/about/rules/6618732618186752/google-mobile-vulnerability-reward-program-rules).

We're looking forward to receiving your bug reports!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab