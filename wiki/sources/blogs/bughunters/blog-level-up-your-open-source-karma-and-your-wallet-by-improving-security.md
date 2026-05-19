---
source: bughunters
source_url: https://bughunters.google.com/blog/level-up-your-open-source-karma-and-your-wallet-by-improving-security
title: "Level Up Your Open Source Karma (And Your Wallet) by Improving Security - Google Bug Hunters"
description: "This blog post takes you through everything you need to know about the Patch Rewards Program, including our newly introduced focus on memory safety (including reward multipliers!), recently increased reward amounts, and lots more!"
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/level-up-your-open-source-karma-and-your-wallet-by-improving-security#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Level Up Your Open Source Karma (And Your Wallet) by Improving Security

![](https://storage.googleapis.com/bughunters-article-images/blogs/serb.jpg)

Sam Erb

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/isler.jpg)

Duygu Isler

Technical Program Manager

![](https://storage.googleapis.com/bughunters-article-images/blogs/arebert.png)

Alex Rebert

Software Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/goedi.jpg)

Dirk Göhmann

Technical Writer

Published: Jan 21, 2025

Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# Level Up Your Open Source Karma (And Your Wallet) by Improving Security

Are you an open source developer/maintainer with a knack for security? Any patch
(typically a merged GitHub pull request) that you can demonstrate to have
improved the security of an
[in-scope project](https://github.com/google/bughunters/blob/main/patch-rewards-program/scope.md)
will be considered for a financial reward by Google’s
[Patch Rewards Program](https://bughunters.google.com/open-source-security/patch-rewards).

Why are we doing this? Google is committed to contributing to a safer open
source space for all users. And one way we're doing that is through our Patch
Rewards Program, which incentivizes developers to make proactive improvements to
security in open source projects, especially those that are important
dependencies for Google and the wider open source community.

In this post, we’ll take you through everything you need to know about the Patch
Rewards Program, including our newly introduced focus on memory safety
(including reward multipliers!), recently increased reward amounts, and lots
more!

## What’s in it for me?

Depending on the complexity and impact of your patch, with our latest changes we
are now offering rewards up to **$45k**. Our standard rewards, as captured in
the table below, range from $100 to $15,000. On top of that, we are offering
additional bonus multipliers for memory safety-related changes (read on for more
information) which can boost your reward up to $45k.

With these changes to reward amounts, we’ve also introduced tiering:

- Tier 1 comprises projects which we are looking to prioritize
( [full list](https://github.com/google/bughunters/blob/main/patch-rewards-program/scope.md))
- Tier 2 represents all
[projects integrated into OSS-Fuzz](https://github.com/google/oss-fuzz/tree/master/projects)

| Category | Tier 1 | Tier 2 |
| --- | --- | --- |
| (S0) Complicated, high-impact improvements that almost certainly prevent major vulnerabilities in the affected code. | $15,000 | $5,000 |
| (S1) Moderately complex patches that offer compelling security benefits. | $7,500 | $1,337 |
| (S2) Submissions of modest complexity, or for ones that offer fairly speculative gains. | $2,000 | $500 |
| (S3) "One-liner special" for smaller improvements that still have merit from a security standpoint. | $500 | $100 |

Not interested in the money? You can opt to donate your reward to a charitable
organization, and we'll double the final reward to boot!

## What kind of submissions are you looking for?

For inspiration, the Patch Reward Program rules provide a list of general
examples of
[qualifying submissions](https://bughunters.google.com/about/rules/open-source/4928084514701312/patch-rewards-program-rules#qualifying-submissions).
To give more flavor to this list, we’re highlighting two recent submissions in
detail which were rewarded under our previous rules:

- **[Implementing an allowlist-based sandbox for OGNL evaluations in the\**\
**Apache Struts web\**\
**framework](https://github.com/google/bughunters/blob/main/patch-rewards-program/rewarded-patches/apache/struts/330511857.md)**

This submission prevents malicious actors from escalating arbitrary
expression injections to remote code execution, thus significantly reducing
the attack surface of applications built upon the Struts framework.

Reward: $10,000

- **[Patching rs/cors to prevent DoS attacks](https://github.com/google/bughunters/blob/main/patch-rewards-program/rewarded-patches/rs/cors/336848281.md)**

This patch prevents DoS attacks via malicious preflight requests with overly
long `Access-Control-Request-Headers` header values.

Reward: $5,000


## Want to contribute to memory safety?

The Patch Rewards Program is explicitly calling for contributions to
[advance memory safety](https://security.googleblog.com/2024/10/safer-with-google-advancing-memory.html).
In line with Google's two-pronged approach, submissions that either mitigate
memory safety risks in OSS or facilitate the adoption of memory-safe languages
will be in scope for additional rewards. In detail, we are looking for
secure-by-design memory safety improvements such as:

- Adopting the
[Safe Buffers Programming Model](https://clang.llvm.org/docs/SafeBuffers.html)
to migrate from C-style buffers to C++ containers, including the use of
`-Wunsafe-buffer-usage` to prevent backsliding
- Replacing C++ dependencies processing potentially untrusted inputs with
equivalent Rust dependencies
- Building the scaffolding to enable writing new components in Rust, and
demonstrating this capability by adding one feature in Rust
- Elimination of error-prone design patterns or library calls
- Rust <> C++ Bindings through the use of manual bindings or interop tooling
such as [bindgen](https://rust-lang.github.io/rust-bindgen/),
[cbindgen](https://github.com/mozilla/cbindgen), and [cxx](https://cxx.rs/);
with accurate safety comments
- Refactoring Rust crates to minimize or eliminate unsafe code
- Improving the auditability and verifiability of Rust crates that use unsafe
code, such as by encapsulating unsafe blocks within self-contained, safe
abstractions

To underscore our commitment to this space and provide extended incentives to
developers, we’re boosting rewards in the area of memory safety until the end of
2025:

- We’ll double the patch reward for secure-by-design memory safety
improvements (example: maximum reward for a complicated, high-impact
improvement on a tier 1 project will be $30k instead of $15k)
- If your improvement affects one of the projects listed as a “Core
infrastructure data parser” in our
[scope list](https://github.com/google/bughunters/blob/main/patch-rewards-program/scope.md),
we’ll take this one step further and triple your patch reward (example:
maximum reward for a complicated, high-impact improvement will be $45k
instead of $15k). \[1\]

## Recent Additional Changes

This month, in addition to the reward increase & memory safety bonus, we
introduced additional changes to the
[Patch Rewards Program rules](https://bughunters.google.com/about/rules/open-source/4928084514701312/patch-rewards-program-rules):

- We added a significant number of projects to our scope and published our
[scope list](https://github.com/google/bughunters/blob/main/patch-rewards-program/scope.md)
on GitHub  - We removed DOS patches from the scope of one-liner patches we will
      reward
- We introduced a maximum of 3 rewards per month for individual submitters to
encourage fewer, but larger rewards
- We introduced a maximum patch age of 12 months to focus the program on
rewarding recent efforts
- We started publishing
[rewarded submissions to GitHub](https://github.com/google/bughunters/tree/main/patch-rewards-program/rewarded-patches)

## This sounds great. How can I apply for a reward?

It’s simple. Just follow these steps to ensure your submission is eligible for a
reward:

1. Implement a patch that improves the security of an
[in-scope project](https://github.com/google/bughunters/blob/main/patch-rewards-program/scope.md).
2. Submit your patch directly to the maintainers of the project.
3. Work with the project maintainers to get your patch accepted into their
repository without reverts for one month.
4. Submit your report via our
[dedicated form](https://bughunters.google.com/report/patch_rewards). Ensure
you include links to all the relevant code locations and diffs, and explain
project-specific benefits offered by your patch.

Note: Submissions made to the Patch Rewards Program _before_ the patch has
been accepted by maintainers (without reverts for one month) will not be
considered for a reward.

## More questions?

Please see the
[Patch Rewards Program Rules](https://bughunters.google.com/about/rules/open-source/4928084514701312/patch-rewards-program-rules)
for more details on patch rewards and frequently asked questions.

We're looking forward to reviewing (and rewarding!) your contributions to
security in open source projects. Let’s work together to make the open source
space safer for everyone!

### Notes

\[1\] Note that this multiplier is not cumulative with the 2x multiplier.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab