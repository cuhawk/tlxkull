---
source: detectify
source_url: https://labs.detectify.com/ethical-hacking/hack-with-goodfaith-to-automate-and-scale-ethical-hacking/
title: "Hack with ‘goodfaith’ - A tool to automate and scale good faith hacking - Labs Detectify"
author: "Detectify"
published: 2022-06-21T12:57:12+00:00
description: "Hack with 'Goodfaith' : A new tool that is intended to help hackers avoid generating traffic against out-of-scope targets and stay in scope."
---

[Home](https://labs.detectify.com/)/ [Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/)/ [Hack with ‘goodfaith’ – A tool to automate and scale good faith hacking](https://labs.detectify.com/ethical-hacking/hack-with-goodfaith-to-automate-and-scale-ethical-hacking/)

[Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/ "Ethical Hacking")

# Hack with ‘goodfaith’ – A tool to automate and scale good faith hacking

**Ryan Elkins** Jun 21, 2022

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/hack-with-goodfaith-to-automate-and-scale-ethical-hacking/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/hack-with-goodfaith-to-automate-and-scale-ethical-hacking/ "Share on LinkedIn")

![Hack with ‘goodfaith’ – A tool to automate and scale good faith hacking](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2022%2F06%2Fhacking-with-good-faith.png&w=3840&q=75)

**TL/DR: The tough part about hacking is to stay in scope. Hacker and security researcher Ryan Elkins [(@ryanelkins](https://twitter.com/ryanelkins)) revealed a new tool that is intended to help hackers and security researchers avoid generating traffic against out-of-scope targets.**

## **Importance of good faith hacking**

The term “good faith” has been making headlines lately due to a policy revision by the United States Department of Justice (DOJ) to the Computer Fraud and Abuse Act (CFAA). The [DOJ press release](https://www.justice.gov/opa/pr/department-justice-announces-new-policy-charging-cases-under-computer-fraud-and-abuse-act) explains “that good-faith security research should not be charged. Good faith security research means accessing a computer solely for purposes of good-faith testing, investigation, and/or correction of a security flaw or vulnerability, where such activity is carried out in a manner designed to avoid any harm to individuals or the public”.

This is a victory (and a relief) for security researchers and ethical hackers as it provides more clarity to protect them from federal criminal investigations.

This policy change does not directly protect a researcher from a corporation pursuing charges. At the corporation level, Safe Harbor is an important program-specific component to protect ethical hackers from criminal charges when operating in good faith.

Sample boilerplate Safe Harbor language is available from [disclose.io](https://github.com/disclose/policymaker/blob/main/templates/disclose-io-safe-harbor/en-US.md) and establishes that the researcher is “acting in good faith” when their actions align with the program’s testing/bug bounty policy.

A common policy component across all programs is a listing of in-scope targets and often also includes a list of out-of-scope targets. Common out-of-scope targets include third-party SaaS providers, legacy or fragile systems lacking resiliency, web forms/workflows, or business-critical systems where an outage could be detrimental to the business or its customers.

Anyone that has done penetration testing was likely trained to triple-check that their operations are always within scope.

Complying with scope is an example of a good faith action and is critical to maintaining throughout every step.

## **Scope challenges vs good faith**

In order to develop scalable automation, good faith is a continuous requirement although it poses a constant challenge. Good faith requires manual intervention along the way to ensure that programming, processes, and recursion are not going out of scope of the program.

There are many variations of scope that are defined between programs as well as schema variations across platforms. All of the variations need to be processed and actioned. Example types of defined scopes include:

- Single sites: https://www.brevityinmotion/com/recon
- Partial sites: securitymarker.io/inscope
- Wildcard domains: \*.brevityinmotion.com
- Researcher custom domains: <bughunterdomain>.icicles.io
- CIDR ranges: 192.168.0.1/16
- IP addresses: 192.168.0.2
- Code repositories: https://github.com/brevityinmotion
- Mobile applications: com.application.id
- Unstructured text describing scope: acquisitions, hardware devices, binaries

These scope examples apply to both in-scope and out-of-scope targets. A potential call to action is for bug bounty platforms to normalize a schema, introduce format validation, and add consistency to these fields to better support researchers with their automated workflows.

With the breadth of scope variations, is automated scalability even possible? Without guardrails to handle every scenario, it is difficult to have high confidence that the tooling complies with the expectations of programs. Does this conflict with good faith testing?

## **Solutions to overcome the challenges**

One solution would be to manually interpret the scopes and feed them one by one into the automation workflows. The downside of this is that programs are constantly updating their scope, new programs are being added, and some programs will close or pause. Manual loading may become non-compliant with the program expectations pending any modifications to the scope or overarching program. Do these known gaps keep the researcher within “good faith” hacking?

Continuous automation remains to be the desired outcome although proving difficult to achieve responsibly. Jon Colston (mayonaise) made a comment that stuck with me during one of [Nahamsec’s Live Recon episodes](https://youtu.be/SGLdv_4Iy44?t=1365) – “if it’s not running, you’re not being 100% efficient”. Recently, Luke Stephens ( [@hakluke](https://twitter.com/hakluke)) also described a goal of [continuous program monitoring](https://labs.detectify.com/2021/11/30/hakluke-creating-the-perfect-bug-bounty-automation/) in a prior article.

The only option moving forward for good faith ongoing testing is to develop custom software to process and continuously monitor the scope and avoid accidentally breaking policy. In order to overcome this challenge, I developed a series of disparate Python functions to process the scopes and mostly solve the challenge.

Over time, these scripts became a core component to the success of the [automation framework](https://www.brevityinmotion.com/automated-cloud-based-recon/) that I was building. Seeing this value, it led me to clean up the code and package it for broader community consumption.

## **Introduction to ‘goodfaith’**

![](https://labsadmin.detectify.com/app/uploads/2022/06/image3-1-1.png)

The package will help other researchers automate and hack with ‘ [goodfaith](https://github.com/brevityinmotion/goodfaith)‘.

The usage of goodfaith is intended to help researchers avoid generating traffic against out-of-scope targets that may result in damage to the company through availability impacts or outages, it could result in researcher program/platform bans, lost bounties, or worst case – legal consequences. To reduce the likelihood of testing against out-of-scope targets, a security researcher can now demonstrate proactive intent to hack with [goodfaith](https://github.com/brevityinmotion/goodfaith).

## **Goodfaith: An overview**

The software is available as a Python package and can be installed via:

pip3 install goodfaith

The goodfaith tool can:

- Compare a list of URLs to a program scope file and output the explicitly in-scope targets.
- Be utilized within bug bounty one-liners to process standard input and deliver it to downstream tools via standard output.
- Be imported as a module into a larger project or automation ecosystem.
- Generate statistics for processed URLs, scope status, and unique domains.

![](https://labsadmin.detectify.com/app/uploads/2022/06/image2-1.png)

- Output a graph database visualization displaying relationships between the URLs. This functionality is still in experimental mode as it is slow to process and breaks with too large of a dataset.

![](https://labsadmin.detectify.com/app/uploads/2022/06/image4-1-1532x1536-1.png)

- Lastly, it can quickly generate scope files for the entire public bug bounty space across HackerOne, Bugcrowd, Intigriti, YesWeHack, Federacy, and Hackenproof. To avoid duplication of existing effort, [Arkadiyt Tetelman](https://twitter.com/arkadiyt) has automated the data generation across these platforms through his [bounty-targets-data](https://github.com/arkadiyt/bounty-targets-data) project and is a core dependency for the operational effectiveness of the bulk import functionality.

Goodfaith utilizes two primary inputs: a scope file containing both in-scope and out-of-scope program information and a list of URLs. Typically these URLs would be retrieved via a web crawl using a tool like [hakrawler](https://github.com/hakluke/hakrawler) or a web archive retrieval using [getallurls (gau)](https://github.com/lc/gau) and then piping the standard output into goodfaith.

Example bash one-liner:

cat domains.txt \| hakrawler \| goodfaith -s scopefile.json \| httpx

The [scope input files](https://github.com/brevityinmotion/goodfaith/blob/main/samples/scope.json) follow a standardized schema although the processing will handle the scope variations observed across programs within the context of the schema:

![](https://labsadmin.detectify.com/app/uploads/2022/06/image1-1-1.png)

## **Moving forward**

Additional details are contained within the [goodfaith Readme](https://github.com/brevityinmotion/goodfaith) and the project will have ongoing updates and feature enhancements. Future content will include useful examples within data processing workflows and project imports.

It is important to remember that this software does not by default mean that you are acting in good faith. Scope is just one component as other areas such as researcher intent, permission, disclosure confidentiality, and compliance with anything else within the program policy are important to understand and follow prior to analyzing a target. Feel free to reach out with questions or concerns and let me know if the software has provided value to your workflows.

### **Written by:**

Ryan Elkins [(@ryanelkins](https://twitter.com/ryanelkins)) who has over 15 years of experience leading security architecture and application security programs across multiple industries. Ryan is passionate about software security, cloud automation, sharing knowledge, and supporting other creators. You can learn more at his [blog](https://www.brevityinmotion.com/) or on [GitHub](https://github.com/brevityinmotion).

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/hack-with-goodfaith-to-automate-and-scale-ethical-hacking/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/hack-with-goodfaith-to-automate-and-scale-ethical-hacking/ "Share on LinkedIn")

**Ryan Elkins**

Security Architecture and Application Security Leader

## Check out more content

Why picking targets is so important Many ethical hackers struggle because they are hacking the “wrong” types of targets for them. This is especially true …

December 07, 2022

You will find a common pattern if you read blog posts or watch interviews with some of today’s top ethical hackers. When asked if coding …

November 30, 2022

Docker is an open-source platform that allows you to develop, deploy, and manage multiple applications across one operating system

November 21, 2022

Approaching a target to hack can feel like climbing a mountain. You may face large scopes, confusing applications, complex user hierarchies…the list goes on. The …

October 28, 2022