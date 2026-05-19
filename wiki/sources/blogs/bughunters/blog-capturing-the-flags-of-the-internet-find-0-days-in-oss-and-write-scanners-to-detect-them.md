---
source: bughunters
source_url: https://bughunters.google.com/blog/capturing-the-flags-of-the-internet-find-0-days-in-oss-and-write-scanners-to-detect-them
title: "Capturing the Flags of the Internet: Find 0-days in OSS and write scanners to detect them - Google Bug Hunters"
description: "The InternetCTF offers a total reward of up to $10,000 to bug hunters who not only discover novel code execution vulnerabilities in Open Source Software, but also provide Tsunami plugin patches for them!"
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/capturing-the-flags-of-the-internet-find-0-days-in-oss-and-write-scanners-to-detect-them#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Capturing the Flags of the Internet: Find 0-days in OSS and write scanners to detect them

![](https://storage.googleapis.com/bughunters-article-images/blogs/anniemao.jpg)

Annie Mao

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/hlynur.jpg)

Hlynur Óskar Guðmundsson

Information Security Engineer

Published: Jan 8, 2025

Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# Capturing the Flags of the Internet: Find 0-days in OSS and write scanners to detect them

Today, we are happy to announce the official launch of our new patch reward
program:
[InternetCTF](https://bughunters.google.com/about/rules/open-source/5067456626688000/tsunami-patch-rewards-program-rules#-new-from-vulnerability-disclosure-to-vulnerability-detection-via-internetctf).
We would love to live in a world where we don't have remote code execution
vulnerabilities in widely-used software, and for this reason, we've decided to
incentivize security researchers to search for vulnerabilities and support
others in detecting them – to help defenders find their vulnerable assets faster
than the bad guys can.

InternetCTF builds on our existing
[Tsunami Patch Reward Program](https://bughunters.google.com/about/rules/open-source/5067456626688000/tsunami-patch-rewards-program-rules)
and takes it to the next level: we are offering a total reward of up to $10,000
to bug hunters who not only discover novel code execution vulnerabilities in
Open Source Software, _but also_ provide Tsunami plugin patches for them
(vulnerabilities without a plugin patch are not eligible for InternetCTF
rewards).

If you like:

- Searching for vulnerabilities in securely configured OSS instances we're
making available explicitly for this purpose

AND

- Providing
[Tsunami plugin](https://github.com/google/tsunami-security-scanner-plugins)
patches to enable the community to detect these vulnerabilities at scale

...then this is for you!

## What's in the name?

**Internet**

We want to use InternetCTF as a platform for discovering critical
vulnerabilities on the internet. At the same time, we want to give early warning
signals to the wider internet community about any vulnerabilities that exist in
securely configured versions of open source software. The intention is to ensure
that the security community can be better prepared for the next log4j-style
event, by putting defenses in place before such large-scale compromises can
occur. This is the reason why we open sourced the configurations of various Open
Source Software (OSS) at [https://github.com/google/security-testbeds](https://github.com/google/security-testbeds), which in
turn powers the live applications hosted on the
[InternetCTF platform](https://capturetheflag.withgoogle.com/internet).

**CTF**

What is a better way to verify the existence of a code execution vulnerability
than stealing a root flag from a securely configured instance of an OSS? We have
set up a firing range at [https://capturetheflag.withgoogle.com/internet](https://capturetheflag.withgoogle.com/internet), where a
list of sandboxed versions of popular OSS are hosted. They are split into 2
categories:

- Software with known vulnerabilities – Used for education purposes, to
showcase how easy it is to gain code execution if an application is
misconfigured (either using a vulnerable version or lacking access control).
- Securely configured software – Enables all bug hunters on the internet to
start looking for 0-day vulns in this OSS, and kick-start the InternetCTF
process by stealing the root flag in them (look out for the “Secure” tag).

## What's the scope?

The list of in-scope OSS for InternetCTF can be found at
[https://capturetheflag.withgoogle.com/internet](https://capturetheflag.withgoogle.com/internet). These are commonly used services
reachable on the public internet, including lots of AI-relevant software. Note
that only services with the **"Secure"** tag qualify for InternetCTF; in other
words, you should only hunt for 0-day vulnerabilities (and exfiltrate flags) in
these services.

> Tip: If you are interested in OSS that is currently not hosted on our
> platform, feel free to contact us with your request by creating an issue at
> [https://github.com/google/tsunami-security-scanner-plugins/issues](https://github.com/google/tsunami-security-scanner-plugins/issues).

## How can I get started?

Nothing easier than that: Pick a target from the
[in scope OSS](https://capturetheflag.withgoogle.com/internet) (all OSS with the
"Secure" tag is eligible), and start searching for a vulnerability that allows
you to exfiltrate the root flag!

> Important! Please don't share any details about 0-day vulns in the InternetCTF
> submission form or on the Tsunami public GitHub repository before they are
> publicly disclosed.

After finding a vulnerability, follow the detailed InternetCTF steps in our
[official rules](https://bughunters.google.com/about/rules/open-source/5067456626688000/tsunami-patch-rewards-program-rules#internetctf-patch-reward-process)
document.

## More bang for your bugs!

You can get paid up to 3 times for a single vulnerability! Sounds too good to be
true? This is how receiving multiple rewards for one vulnerability works:

1. [InternetCTF](https://bughunters.google.com/about/rules/open-source/5067456626688000/tsunami-patch-rewards-program-rules#-new-from-vulnerability-disclosure-to-vulnerability-detection-via-internetctf)
– For discovering a 0-day vulnerability and writing a Tsunami plugin patch
to detect it
2. [Patch Rewards Program](https://bughunters.google.com/about/rules/open-source/4928084514701312/patch-rewards-program-rules)
– For writing a patch for the vulnerability itself
3. [Other VRPs](https://bughunters.google.com/about/rules/6744710187712512) –
For reporting the vulnerability to us with a clear demonstration of the
vulnerability's security impact. Examples: An issue in TensorFlow could be
reported to the
[OSS VRP](https://bughunters.google.com/about/rules/open-source/6521337925468160/google-open-source-software-vulnerability-reward-program-rules),
a 0-day affecting `*.google.com` to the
[Google VRP](https://bughunters.google.com/about/rules/google-friends/6625378258649088/google-and-alphabet-vulnerability-reward-program-vrp-rules).

Thanks for joining us in the endeavor to make the internet safer and take OSS
security to the next level, to the benefit of the global community of users!

Happy bug hunting and Tsunami plugin writing!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab