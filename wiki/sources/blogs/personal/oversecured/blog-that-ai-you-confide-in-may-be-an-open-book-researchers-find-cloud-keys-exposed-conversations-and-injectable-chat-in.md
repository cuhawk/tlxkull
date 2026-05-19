---
source: oversecured
source_url: https://oversecured.com/blog/that-ai-you-confide-in-may-be-an-open-book-researchers-find-cloud-keys-exposed-conversations-and-injectable-chat-in-companion-apps
title: "That AI You Confide in May Be an Open Book: Researchers Find Cloud Keys, Exposed Conversations, and Injectable Chat in Companion Apps | Oversecured Blog"
author: "HubSpot, Inc."
description: "Oversecured identifies hardcoded cloud credentials and a cross-site scripting flaw in popular AI companion apps, exposing backend infrastructure and allowing code injection into private conversations"
---

Dast is live!

Run a new scan to see dynamic findings in your reports

[Learn more →](https://oversecured.com/dast)

One app ships with the developer’s OpenAI token and Google Cloud private key in its code. Another lets any app on the phone inject scripts into what users experience as a private conversation.

Oversecured, a mobile application security company, has identified security vulnerabilities in several popular AI companion and chatbot apps on Google Play. The category includes virtual friends, romantic partners, coaching assistants, and general-purpose AI wrappers. AI companion apps are one of the fastest-growing categories on Google Play — downloads surged after the launch of ChatGPT, and new apps appear weekly. The security audit focused not on major platforms like OpenAI or Google, but on the wave of independent apps that millions of users are actually installing. The most severe findings: hardcoded cloud credentials that give anyone who decompiles the app access to the developer’s backend, and a cross-site scripting flaw that allows code injection into a conversation interface.

The affected apps include:

- A productivity AI chatbot with OpenAI and Google Cloud credentials exposed in its code

- A multi-voice AI companion with cross-site scripting in its conversation WebView

- A metaverse-oriented AI companion with hardcoded authentication tokens

- Multiple chatbots with host validation errors that could redirect users to attacker-controlled sites


Users tell AI companions about relationships, sexual preferences, loneliness, financial stress, and family conflicts. Unlike clinical mental health apps, AI companions operate in a regulatory gap — there is no equivalent of HIPAA for a conversation with a virtual partner.

# A chatbot ships with cloud keys in its code

A productivity AI chatbot contains a hardcoded OpenAI API token and a Google Cloud service account private key. Anyone who downloads the APK and runs a standard decompiler can extract both. The OpenAI token allows API calls at the developer’s expense. The Google key provides access to a project called “invoice\_maker” — the developer’s invoicing and billing infrastructure.

In practice: the private key is a direct path to the developer’s invoice and payment data. If the same Google Cloud project also handles user data — as is common when developers run multiple services under one account — the exposure could extend to conversation histories and personal information as well.

# Script injection into a private conversation

A multi-voice AI companion has an exported activity that accepts raw HTML and loads it into a WebView with JavaScript enabled. A malicious app can inject arbitrary code that executes within the companion’s interface, under its base URL origin.

In practice: an attacker could read the user’s conversation history, inject fake messages into the chat, or present a phishing screen requesting personal data — all inside what the user sees as a trusted conversation with their AI companion.

# The wrapper problem

Many AI companion apps are “wrappers” — they connect to a third-party API (OpenAI, Google, or an open-source model) and add an interface, a personality, and a payment model. The API provider handles the AI. The wrapper developer handles authentication, data storage, and Android security.

Every vulnerability in this audit sits in the wrapper layer. Users trust the AI brand. The failures happen in the layer between the user and the model.

‘One app includes both its OpenAI token and its Google Cloud private key in the code — the Cloud key belongs to the developer’s invoicing system. With those two credentials, you can reach the AI backend and the billing infrastructure. The AI companion category handles a different but equally sensitive type of data as therapy apps — personal confessions, relationship details, sexual content. These apps grew so fast that basic security was never part of the process,’ says Sergey Toshin, founder of Oversecured.

The researchers have not disclosed specific app names or technical details as the vulnerabilities remain unpatched.

Please find technical report on our findings [here](https://drive.google.com/file/d/1LdRbXFr3MKEgESmv68QoU3R4Ca2FCk97/view?usp=sharing).

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

2026 © Oversecured

follow us

### [LinkedIn](https://www.linkedin.com/company/oversecured/)

### [Twitter (X)](https://x.com/oversecuredinc)

[Privacy Policy](https://oversecured.com/privacy)

[Terms of use](https://oversecured.com/terms)

[go up ↑](https://oversecured.com/blog/that-ai-you-confide-in-may-be-an-open-book-researchers-find-cloud-keys-exposed-conversations-and-injectable-chat-in-companion-apps#header)

Chat Widget