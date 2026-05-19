---
source: detectify
source_url: https://labs.detectify.com/ethical-hacking/should-you-learn-to-code-before-you-learn-to-hack/
title: "Hacking or coding - Should you learn code before hacking? Labs Detectify"
author: "Detectify"
published: 2022-11-30T15:10:50+00:00
description: "Some of the advantages that coding knowledge can give you when you start ethical hacking. Aimed at developers who want to learn hacking."
---

[Home](https://labs.detectify.com/)/ [Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/)/ [Should you learn to code before you learn to hack?](https://labs.detectify.com/ethical-hacking/should-you-learn-to-code-before-you-learn-to-hack/)

[Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/ "Ethical Hacking")

# Should you learn to code before you learn to hack?

**Gunnar Andrews** Nov 30, 2022

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/should-you-learn-to-code-before-you-learn-to-hack/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/should-you-learn-to-code-before-you-learn-to-hack/ "Share on LinkedIn")

![Should you learn to code before you learn to hack?](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2022%2F11%2Fshould-you-learn-how-to-code-before-you-learn-hacking.png&w=3840&q=75)

**You will find a common pattern if you read blog posts or watch interviews with some of today’s [top ethical hackers](https://detectify.com/crowdsource/ethical-hacking-with-crowdsource). When asked if coding knowledge is needed for hacking, the answer is almost always the same: It’s possible to become a great hacker without coding knowledge, but having coding experience makes it a whole lot easier. Knowing how software is built in theory makes it easier to break. This blog post will discuss some of the advantages that coding knowledge can give you when you start hacking.**

## Writing your own tools

Ethical hackers have created many tools for specific purposes to help them with their hacking. You can do the same. By creating your own tools, you know exactly what each tool is doing.

Here’s a simple process I follow when creating my own tools:

**Find a gap in currently available tooling** This could be a tool that might be outdated or deprecated. It could also be an area that requires a solution. Find a spot where your knowledge of the topic and programming skills can shine.

**Create your updated or new tool.**

If you’re updating an existing tool, this may look more like forking a GitHub repo and changing/adding code. If you are creating a brand new tool, this might look like creating your new repository and starting from scratch.

**Test your new tool against local targets.** This is the easiest way to determine if your new tool is working as expected. Spending more time in the testing phase will benefit you in the long run.

**Deploy your tool against real targets.**

Pick some bug bounty targets or something you have permission to hack and deploy your shiny new tool against it.

**Open source it (or don’t!).** This is the easiest way to determine if your new tool is working as expected. Spending more time in the testing phase will benefit you in the long run.

## Insider knowledge

Knowing the internal details of the software you’re hacking is like using cheat codes in video games. It changes the game entirely. An ethical hacker with development experience can make educated guesses about how a feature is implemented in the backend and what vulnerabilities are likely to have been introduced. Without development experience, an ethical hacker spends more time shooting in the dark and relying solely on probe results to determine suspicious behaviors.

> “Knowing the internal details of the software you’re hacking is like using cheat codes in video games.”

For this reason, when approaching a new target as a an ethical hacker with development experience, it is advantageous to focus on assets that use languages, frameworks, and technologies you’re familiar with. This will ensure that you are approaching the target with an advantage. There are many ways to find these targets:

- If you’re hacking on a bug bounty platform, many of them list the technologies used by each target within the bounty brief.
- Use technology fingerprinting tools such as wappalyzer or httpx.
- Use search engines like Google and Shodan

## Source code review

Some of the juiciest bugs are very difficult to uncover from pure black-box testing. Reviewing source code offers more insights and a fresh perspectives on applications that can yield more bugs. Someone with coding experience will always be more adept at uncovering vulnerable code than someone without coding experience. This is especially true if you have experience with the language or framework being used.

There are many ways to find source code to review, including:

- Reviewing open source code (of course!)
- Decompiling Java
- Reviewing containerized software in public registries

Some examples of these methods leading to [high/critical severity CVEs](https://blog.detectify.com/2020/12/30/top-10-critical-cves-added-in-2020/) are CVE-2020-13379 (Found by Justin Gardner) and CVE-2021-22054 (Found by Keiran Sampson, James Hebden, and Shubham Shah). These examples are great to read through to get an idea of the kinds of sources and sinks ethical hackers look for in modern software.

## Automation

Companies and researchers alike are trying to automate as much as possible. In theory, this only makes you more efficient if the menial tasks involved with hacking are automated. As you may have guessed, one of the best new ways to flex your programming skills is to [automate steps of the hacking methodology](https://labs.detectify.com/2022/06/21/hack-with-goodfaith-to-automate-and-scale-ethical-hacking/). This can look very different depending on the task you are trying to automate. I would recommend thinking about it using the following steps:

**What does the input data look like?**

Are you taking info from stdin on a command line or pulling data from a database? What format is the input in? (ex: JSON, text, CSV, etc.)

**How should your automation be ingesting this data to produce results?**

Is it making requests with this data, decoding the data, or maybe using the data for some type of analysis?

**What does the resulting output data look like, and where is it stored?** This looks very similar to step #1. What format is it, and where is it being stored?

**How will you deploy this automation in a way that can scale to handle enough targets?**

(ex: Are you using VPS servers? Will there be one big script or a bunch of smaller ones?)

The language or framework you use is up to you. If you follow the above steps to use your programming knowledge to start automating your tasks, I can promise you that you will see an [improvement in your results!](https://labs.detectify.com/2022/10/28/hacking-supercharged-how-to-gunnar-andrews/)

## Resources to learn more

Whether you have prior programming knowledge and this blog has convinced you to utilize it in your hacking adventures, or you are now convinced it is time to learn some programming, here are some resources to get you started:

- [Sources and Sinks](https://www.youtube.com/watch?v=ZaOtY4i5w_U) video by LiveOverflow
- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/assets/OWASP_Code_Review_Guide_v2.pdf)
- [Writeups by security researchers](https://labs.detectify.com/category/writeups/) (ex: CVE writeups)

If you have the programming knowledge and are ready to use it to your advantage, I recommend you grab some source code from a bug bounty program, an open-source project, or otherwise publicly available software and start hacking. I hope this has encouraged some developers to try flexing those ethical hacker muscles. I think you will find that it can be a very fun transition to try breaking software instead of building it. Many developer-turned-hackers would love to welcome you to the club. Have fun and happy hacking!

* * *

#### **Written by:**  **Gunnar Andrews**

My online alias is G0lden. I am a hacker out of the midwest United States. I came into the hacking world through corporate jobs out of college, and I also do bug bounties. I enjoy finding new ways to hunt bugs and cutting-edge new tools. Making new connections with fellow hackers is the best part of this community for me!

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/should-you-learn-to-code-before-you-learn-to-hack/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/should-you-learn-to-code-before-you-learn-to-hack/ "Share on LinkedIn")

**Gunnar Andrews**

Ethical Hacker

## Check out more content

Why picking targets is so important Many ethical hackers struggle because they are hacking the “wrong” types of targets for them. This is especially true …

December 07, 2022

Docker is an open-source platform that allows you to develop, deploy, and manage multiple applications across one operating system

November 21, 2022

Approaching a target to hack can feel like climbing a mountain. You may face large scopes, confusing applications, complex user hierarchies…the list goes on. The …

October 28, 2022

TL/DR: In this world of rapid digitization, companies are moving from traditional on-premise deployments to cloud service providers for handling their infrastructure. In this article, …

July 25, 2022