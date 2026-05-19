---
source: oversecured
source_url: https://oversecured.com/blog/the-app-you-asked-your-employees-to-install-can-leak-their-bank-account-details-to-hackers
title: "The App You Asked Your Employees to Install Can Leak Their Bank Account Details to Hackers | Oversecured Blog"
author: "HubSpot, Inc."
description: "Find and fix Android and iOS app vulnerabilities with automated SAST and DAST, CI/CD integration, proof-of-concept reports, and expert support."
---

Dast is live!

Run a new scan to see dynamic findings in your reports

[Learn more →](https://oversecured.com/dast)

Security audit of shift scheduling and workforce management apps finds flaws that expose Plaid banking tokens, allow fake messages under the employer’s brand, and let attackers silently delete shift notifications.

Oversecured, a mobile application security company, has identified security vulnerabilities in several widely used shift scheduling and workforce management apps on Google Play. The affected apps serve restaurants, retail chains, healthcare facilities, and logistics companies. The most severe flaw could allow a malicious application to steal Plaid banking tokens — the credentials that connect workers’ bank accounts for direct deposit.

The affected apps include:

- A scheduling platform used by small businesses, with Plaid-based payroll integration

- An all-in-one workforce management platform used across retail and field operations

- Three separate scheduling apps that share the same notification-suppression flaw


For hourly employees, these apps are not optional. They are the primary channel for shift assignments, clock-ins, manager communications, and pay.

# A scheduling app leaks banking tokens

A scheduling platform’s Plaid enrollment activity takes the incoming intent, appends Plaid response data, and returns it to whoever started the activity — without verifying the caller. A malicious app can launch this flow and receive the banking token in return. The same app also lets any other app force it to make arbitrary outbound HTTP requests, because its main activity passes deep-link URLs to a connection handler without host validation.

In practice: a worker who connected their bank for direct deposit could have their financial account data extracted by a malicious app running on the same phone. The attack is invisible — no pop-up, no permission request, no notification.

# Fake messages under the employer’s brand

An all-in-one workforce platform has an exported BroadcastReceiver that builds and displays notifications from any sender’s data. A malicious app can push fake messages — a shift change, an HR notice, a request for credentials — that appear to come from the employee’s company. The same app loads avatar and logo URLs from incoming intents without domain validation, allowing arbitrary images inside its interface.

In practice: an attacker could send a worker a fake “your direct deposit details need updating” notification that looks identical to a real company message, leading to a phishing page.

# Three apps allow silent deletion of shift notifications

Three scheduling apps share the same vulnerability: an exported BroadcastReceiver that cancels notifications without verifying the sender. Any app on the phone can silently dismiss push notifications from these workforce tools.

In practice: a suppressed shift notification could mean a missed shift, a lost day of pay, or disciplinary action. The worker would have no way to know the notification ever existed.

Other findings: a time-tracking app copies user videos to world-readable external storage. Another includes hardcoded basic authentication credentials in its code.

‘When a company deploys a scheduling app, it becomes the nervous system of daily operations. One app lets another application extract Plaid banking tokens. Another lets a third-party app send fake messages under the employer’s name,’ says Sergey Toshin, founder of Oversecured. ‘These are the tools millions of hourly workers depend on every day.’

The researchers have not disclosed specific app names or technical details as the vulnerabilities remain unpatched.

# About Sergey Toshin

[Sergey Toshin](https://www.linkedin.com/in/bagipro/) is the founder of [Oversecured](https://oversecured.com/), a mobile application security company. He has discovered and helped fix over 1,000 mobile vulnerabilities. His research earned the #1 ranking on Google Play’s security researcher leaderboard, top researcher status with Samsung Mobile Security, and a top-3 position on HackerOne. He has collected over $1 million in bug bounties from major technology companies.

# About Oversecured

[Oversecured](https://oversecured.com/) provides automated security scanning for Android and iOS applications. The company has identified vulnerabilities in apps from Google, Samsung, Amazon, PayPal, TikTok, Airbnb, Netflix, and other major technology companies. The scanner covers 175+ vulnerability categories for Android and 85+ for iOS with 99.8% detection accuracy. CNN, TechCrunch, and other media outlets have featured Oversecured’s research.

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

[go up ↑](https://oversecured.com/blog/the-app-you-asked-your-employees-to-install-can-leak-their-bank-account-details-to-hackers#header)

Chat Widget