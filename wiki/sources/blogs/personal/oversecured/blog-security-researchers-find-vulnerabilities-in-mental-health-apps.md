---
source: oversecured
source_url: https://oversecured.com/blog/security-researchers-find-vulnerabilities-in-mental-health-apps
title: "Security Researchers Find Vulnerabilities in Mental Health Apps; One With Millions of Users May Leak Therapy Notes | Oversecured Blog"
author: "HubSpot, Inc."
description: "Find and fix Android and iOS app vulnerabilities with automated SAST and DAST, CI/CD integration, proof-of-concept reports, and expert support."
---

Dast is live!

Run a new scan to see dynamic findings in your reports

[Learn more →](https://oversecured.com/dast)

Your AI therapist’s notes may be worth more than your credit card number on the dark web. Security analysis reveals a potential new frontier for cyber espionage.

Oversecured, a mobile application security company, has identified vulnerabilities in several of the most popular mental health apps available on Google Play. The affected apps have a combined download count exceeding tens of millions. The flaws could turn these apps into unintended data sources for surveillance, including users’ personal conversations with the therapist - a new vector that security experts warn may become as valuable to attackers as financial credentials.

One of the apps with confirmed security flaws reports millions of users and ranks among the most engaging AI therapy solutions according to peer-reviewed clinical publications. The vulnerabilities could allow other applications on the same device to intercept sensitive user data, including conversation history with AI therapists and mood tracking records.

Other apps on the list included:

- Apps with FDA Breakthrough Device designations for treating depression

- Apps deployed in state healthcare programs in Europe, with six-figure patient counts and major clinical trials funded by leading research institutions

- Apps backed by major venture funding from prominent technology investors

- Products with multiple randomized controlled trials and peer-reviewed studies in JMIR

- Apps used by major employers, insurers, and government health agencies


Combined, these tested apps have tens of millions of downloads and have facilitated hundreds of millions of conversations about anxiety, depression, trauma, and addiction.

## How the attack works

Android apps communicate through ‘intents,’ a messaging system between app components. A secure app sends data to a specific recipient. The vulnerable apps broadcast data without specifying who should receive it. Any other app on the phone can register as a listener and capture this information.

## A realistic scenario

A user downloads an app, usually a free one, such as a flashlight or a calculator app. The app looks harmless but contains hidden code. When the user opens their therapy app and types ‘I have been having panic attacks,’ the malicious app intercepts the message in the background. The data goes to the attacker’s server. The user notices nothing unusual.

In 2020, hackers breached Vastaamo, a Finnish psychotherapy clinic, and stole session notes from 33,000 patients. They contacted victims individually and demanded ransom to keep their secrets private. Several victims took their own lives.

‘Mental health data carries unique risks. On the dark web, therapy records sell for $1,000 or more per record, far more than credit card numbers,’ says Sergey Toshin, founder of Oversecured and mobile security researcher with over 15 years of experience. ‘We analyzed the most popular mental health apps, and several had security vulnerabilities, including critical ones. These are apps with millions of downloads and professional development teams. Smaller apps with fewer resources are likely to have even more issues, which means the real scale of the problem is much larger.’

The findings come as the mental health app market reaches $10-12 billion in 2025, with annual growth rates of 18-20%. According to the WHO, one in eight people globally (approximately one billion) suffers from mental health disorders. In the US, 56% of adults with mental illness receive no treatment. AI chatbots have become the first point of mental health support for millions.

The researchers have not disclosed specific technical details as the vulnerabilities remain unpatched.

This is not the first time mental health apps have faced security scrutiny. Mozilla Foundation’s ‘Privacy Not Included’ project has flagged the category as a ‘privacy nightmare.’ In 2023, a major teletherapy platform paid millions to settle FTC charges over sharing user data with advertisers.

Mental health apps are typically not covered by HIPAA regulations that protect traditional healthcare data.

Ready to strengthen your mobile security? [Start your free trial of Oversecured today](https://ovsc.framer.website/)

##### Keep reading

[View all](https://oversecured.com/blog)

[![](https://framerusercontent.com/images/OnN0UKCOhnnXin2eBts9J3SaUQ.png?width=5592&height=3259)\\
\\
20 Security Issues Found in Xiaomi Devices\\
\\
Oversecured found and resolved significant mobile security vulnerabilities in Xiaomi devices. Our team discovered 20 dangerous vulnerabilities across various applications and system components that pose a threat to all Xiaomi users. The vulnerabilities\\
\\
Case Study\\
\\
May 2, 2024\\
\\
15\\
\\
min read\\
\\
TOp article](https://oversecured.com/blog/20-security-issues-found-in-xiaomi-devices)

[![](https://framerusercontent.com/images/W9Wn9vbZPPJFNH7MN7Zx6QXches.png?width=2048&height=1194)\\
\\
Android deep link vulnerabilities: how intent filters lead to account takeover\\
\\
A technical guide to Android deep link security. Learn how intent filter misconfigurations lead to account takeover, and how mobile application security testing with SAST and DAST finds these vulnerability chains.\\
\\
Android Security\\
\\
Apr 27, 2026\\
\\
8\\
\\
min read](https://oversecured.com/blog/android-deep-link-vulnerabilities)

[![](https://framerusercontent.com/images/xSiSLs1y7y6Mzr4lWYWCpFoYmM4.png?width=2848&height=1656)\\
\\
Android security checklist: theft of arbitrary files\\
\\
Developers for Android do a lot of work with files and exchange them with other apps, for example, to get photos, images, or user data. \\
\\
Android Security\\
\\
May 20, 2022\\
\\
11\\
\\
min read\\
\\
TOp article](https://oversecured.com/blog/android-security-checklist-theft-of-arbitrary-files)

Book a personalized demo

During the demo with our cybersecurity experts you will get:

A free trial scan of your app

An analysis of your SAST and DAST findings

Practical insights on mobile security of your app

First name

Business email

How did you hear about us?

Book a demo

[Blog](https://oversecured.com/blog)

[Partner](https://oversecured.com/partner)

[Wall of fame](https://oversecured.com/cve)

2026 © Oversecured

follow us

### [LinkedIn](https://www.linkedin.com/company/oversecured/)

### [Twitter (X)](https://x.com/oversecuredinc)

[Privacy Policy](https://oversecured.com/privacy)

[Terms of use](https://oversecured.com/terms)

[go up ↑](https://oversecured.com/blog/security-researchers-find-vulnerabilities-in-mental-health-apps#header)

Chat Widget