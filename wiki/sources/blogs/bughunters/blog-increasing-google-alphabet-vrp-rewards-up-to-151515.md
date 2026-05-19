---
source: bughunters
source_url: https://bughunters.google.com/blog/increasing-google-alphabet-vrp-rewards-up-to-151515
title: "Increasing Google & Alphabet VRP rewards up to $151,515 - Google Bug Hunters"
description: "The reward amounts on offer by the Google VRP have undergone a major overhaul: We're increasing reward amounts by up to 5x (with maximum rewards of up to $151,515)!"
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/increasing-google-alphabet-vrp-rewards-up-to-151515#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Increasing Google & Alphabet VRP rewards up to $151,515

![](https://storage.googleapis.com/bughunters-article-images/blogs/serb.jpg)

Sam Erb

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/koto.jpg)

Krzysztof Kotowicz

Information Security Engineer

Published: Jul 11, 2024

Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# Increasing Google & Alphabet VRP rewards up to $151,515

TL;DR: Since the
[creation of the Google VRP in 2010](https://security.googleblog.com/2010/11/rewarding-web-application-security.html),
we have been rewarding bugs found in Google systems & applications. As our
systems have become more secure over time, we know it is taking much longer to
find bugs – with that in mind, we are very excited to announce that **we are**
**updating our reward amounts by up to 5x, with a maximum reward of $151,515 USD**
**($101,010 for an RCE in our most sensitive products, with a 1.5x modifier**
**applied for exceptional report quality = $151,515).**

Want to know more about the changes we've made to our reward amounts and
structure? Read on or refer to the updated
[Reward Amounts](https://bughunters.google.com/about/rules/google-friends/6625378258649088/google-and-alphabet-vulnerability-reward-program-vrp-rules#reward-amounts-for-security-vulnerabilities)
section of the Google VRP rules.

## Examples of Reward Increases

In addition to the RCE example highlighted above, we want to highlight the
reward increases we're introducing with a few additional examples, where reports
are of exceptional quality (1.5x multiplier applied):

| Example Vulnerability | New Reward | Old Reward |
| --- | --- | --- |
| A logic flaw leading to an accounts.google.com @gmail.com account takeover | ($50,000 \* 1.5) = **$75,000** | $13,337 |
| XSS on idx.google.com | ($10,000 \* 1.5) = **$15,000** | $3,133.7 |
| A logic flaw disclosing PII on home.nest.com (a [tier 1 acquisition domain](https://github.com/google/bughunters/blob/main/domain-tiers/external_domains_acquisitions.asciipb)) | ($2,500 \* 1.5) = **$3,750** | $500 |

## Rewarding Exceptional Reports

Following the lead of the
[Mobile VRP](https://bughunters.google.com/blog/5792192022577152/one-year-of-mobile-vrp-reward-increases-and-lessons-learned#quality-based-reward-modifiers),
the
[Chrome VRP](https://security.googleblog.com/2019/07/bigger-rewards-for-security-bugs.html),
and the
[Android VRP](https://security.googleblog.com/2023/05/new-android-google-device-VRP.html),
we are adding quality-based reward modifiers to our program. These modifiers
have the potential to substantially impact your reward amount and are intended
to encourage higher quality reports that clearly demonstrate the impact of the
finding.

Going forward, we will apply one of the following three multipliers to each
reward:

- Exceptional quality (1.5x reward amount)
- Good quality (1x reward amount)
- Low quality (0.5x reward amount)

For details, see the
[Report Quality](https://bughunters.google.com/about/rules/google-friends/6625378258649088/google-and-alphabet-vulnerability-reward-program-vrp-rules#report-quality)
section of the Google VRP rules.

## Increased Reward Transparency

In the past, we have applied unpublished reward modifiers which could increase
or decrease your total reward, generally based on the impact and exploitability
of the vulnerability you reported. We are now publishing the criteria for those
downgrades and upgrades, as well as some common precedents we refer to when
determining awards (see the
[Common Precedents / Upgrades and Downgrades](https://bughunters.google.com/about/rules/google-friends/6625378258649088/google-and-alphabet-vulnerability-reward-program-vrp-rules#common-precedents-upgrades-and-downgrades)
section of the Google VRP rules).

In addition, we are sharing detailed examples of bugs and the reward amounts
that go with them so that you will be able to see how we compute reward amounts
(see the
[Examples](https://bughunters.google.com/about/rules/google-friends/6625378258649088/google-and-alphabet-vulnerability-reward-program-vrp-rules#examples)
section of the Google VRP rules).

We hope this increase in transparency will help you better understand how the
panel thinks about submissions and decides on rewards for reports.

### Application Tier Updates

We are slightly redefining our application tiers, using our
[domain tiers](https://bughunters.google.com/blog/4562175388155904/externalizing-the-google-domain-tiers-concept)
data
[published online](https://github.com/google/bughunters/tree/main/domain-tiers)
as a basis. We are adopting this approach as it allows us to better define what
matters most to us and reward it accordingly.

In this context, we are also introducing a new reward tier for acquisitions.
This will allow us to reward higher amounts for more impactful reports
concerning our most critical acquisition subdomains.

You can find these tiers in the first row of the table in the
[Reward Amounts](https://bughunters.google.com/about/rules/google-friends/6625378258649088/google-and-alphabet-vulnerability-reward-program-vrp-rules#reward-amounts-for-security-vulnerabilities)
section of the Google VRP rules.

### Vulnerability Category Updates

We are splitting the “Logic flaw bugs leaking or bypassing significant security
controls” category into 3 categories based on impact (SPII, PII/confidential
information, and other). The old category was too broad and, when matched with
the “Normal Google Applications” tier, accounted for 36% of all rewards in the
past year. This change will allow us to reward higher amounts for logic bugs
with more significant impact.

You can find these categories in the “Category” column of the table in the
[Reward amounts](https://bughunters.google.com/about/rules/google-friends/6625378258649088/google-and-alphabet-vulnerability-reward-program-vrp-rules#reward-amounts-for-security-vulnerabilities)
section of the Google VRP rules.

## Conclusion

We hope the changes announced in this post underscore our commitment to
supporting and rewarding bug hunters appropriately for their efforts in finding
flaws and vulnerabilities in Google's products. And just in case you missed it:
besides offering higher rewards, we also recently expanded our payment options
by introducing the possibility to
[receive payments through Bugcrowd](https://bughunters.google.com/blog/6483936851394560/announcing-bugcrowd-as-a-new-bughunters-google-com-payment-option).

Let's join forces to make Google and the internet a safer place.

Happy hunting and keep those bugs coming!

## FAQ

**Why $101,010?**

We're fans of the number
[42](https://www.google.com/search?q=the+answer+to+the+ultimate+question+of+life%2C+the+universe%2C+and+everything).

**What's an example of the largest reward possible with the new table?**

An RCE on a
[tier 0 domain](https://github.com/google/bughunters/blob/main/domain-tiers/external_domains_google.asciipb),
with exceptional report quality will receive $101,010 \* 1.5 = $151,515.

**Will my old report get an additional reward?**

Only vulnerability reports submitted from today (July 11, 2024 00:00 UTC)
forward will be eligible to use the new rewards table.

**What did the old reward table look like?**

For your reference, here's what the "Reward amounts" table looked like before
the changes we announced in this post:

| Category | Examples | Applications that permit taking over a Google account \[1\] | Other highly sensitive applications \[2\] | Normal Google applications \[3\] | Non-integrated acquisitions and other sandboxed or lower priority applications \[4\]\[5\] |
| --- | --- | --- | --- | --- | --- |
| Vulnerabilities giving direct access to Google servers |
| Remote code execution | Command injection, deserialization bugs, sandbox escapes | $31,337 | $31,337 | $31,337 | $1,337 - $5,000 |
| Unrestricted file system or database access | Unsandboxed XXE, SQL injection | $13,337 | $13,337 | $13,337 | $1,337 - $5,000 |
| Logic flaw bugs leaking or bypassing significant security controls | Direct object reference, remote user impersonation | $13,337 | $7,500 | $5,000 | $500 |
| Vulnerabilities giving access to client or authenticated session of the logged-in<br> victim |
| Execute code on the client | Web: Cross-site scripting<br>Mobile / Hardware: Code execution | $7,500 | $5,000 | $3,133.7 | $100 |
| Other valid security vulnerabilities | Web: CSRF, Clickjacking<br>Mobile / Hardware: Information leak, privilege<br> escalation | $500 - $7,500 | $500 - $5,000 | $500 - $3,133.7 | $100 |

\[1\] For example, for web properties this includes some vulnerabilities in Google
Accounts (https://accounts.google.com) and for Android in Google Play services (com.google.android.gms).

\[2\] This category includes products such as Google Search (https://www.google.com and
https://encrypted.google.com), Google Pay (https://pay.google.com), Gmail
(https://mail.google.com), Chromium Bug Tracker (https://bugs.chromium.org),
Chrome Web Store (https://chrome.google.com), Google App Engine (https://appengine.google.com),
Admin Console (https://admin.google.com), Google Cloud Console
(https://console.cloud.google.com) and Google Play (https://play.google.com).

\[3\] \*.google.com applications will be considered at least "Normal Google applications".

\[4\] Note that acquisitions qualify for a reward only after the initial six-month
blackout period has elapsed.

\[5\] "Non-integrated acquisitions" refers to any domain or application acquired
through the acquisition process with the exception of youtube.com, blogger.com and admob.com.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab