---
source: detectify
source_url: https://labs.detectify.com/writeups/undocumented-authentication-bypass-issue-in-aem-package-manager-blog-updated/
title: "Undocumented authentication bypass issue in AEM Package Manager [Blog updated] - Labs Detectify"
author: "Detectify"
published: 2021-06-28T13:56:44+00:00
description: "Detectify Crowdsource ethical hackers found an undocumented authentication bypass in Adobe Experience Manager. Comments from Adobe added."
---

[Home](https://labs.detectify.com/)/ [Writeups](https://labs.detectify.com/category/writeups/)/ [Undocumented authentication bypass issue in AEM Package Manager \[Blog updated\]](https://labs.detectify.com/writeups/undocumented-authentication-bypass-issue-in-aem-package-manager-blog-updated/)

[Writeups](https://labs.detectify.com/category/writeups/ "Writeups")

# Undocumented authentication bypass issue in AEM Package Manager \[Blog updated\]

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F09%2FInk-Detectify-1600x1600-1-300x300-1.png&w=128&q=75)

**Detectify** Jun 28, 2021

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/writeups/undocumented-authentication-bypass-issue-in-aem-package-manager-blog-updated/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/writeups/undocumented-authentication-bypass-issue-in-aem-package-manager-blog-updated/ "Share on LinkedIn")

![Undocumented authentication bypass issue in AEM Package Manager [Blog updated]](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F08%2FScreenshot-2021-06-28-at-15.48.39.png&w=3840&q=75)

_Note: This blog post has been updated to include a response from Adobe for accuracy on July 9, 2021._

**Updated with response from Adobe:**

_We do not have any evidence of public exploitation in the wild that would justify the classification of this issue as a “0-day” vulnerability in Adobe Experience Manager (AEM)._

_For clarification, this issue does not impact AEM Cloud Service customers and only potentially impacts AEM on-premise or AEM as a Managed Service if default security configurations are removed._

_As a result, this does not require a CVE from Adobe because AEM has the necessary security controls enabled by default to help protect customers. This out-of-the-box protection is available on supported versions of AEM._

_Adobe recommends AEM customers review access controls for the CRX package manager path: `/etc/packages`._

* * *

_Note: Detectify previously classified this vulnerability as a 0-day. After discussions with the Adobe PSIRT team, it is now classified as an “undocumented security issue” and the blog has been updated to clarify the specific circumstances under which this security issue may occur._

**TL;DR Security researchers in the [Detectify Crowdsource](https://detectify.com/crowdsource/ethical-hacking-with-crowdsource) community, Ai Ho ( [@j3ssiejjj](https://twitter.com/j3ssiejjj?lang=en)) and Bao Bui ( [@Jok3rDb](https://twitter.com/Jok3rDb)), found an undocumented security issue in Adobe Experience Manager (AEM) that bypassed authentication, and left the application open to information disclosure attacks. If you are a Detectify customer vulnerable to this issue, it will show up as AEM CRX Bypass in your scan results.**

Adobe Experience Manager (AEM) is a widely used content management solution for building digital customer experiences, like websites, mobile apps and forms.

This bug allows attackers to bypass authentication and gain access to Package Manager if the security controls for out-of-box protection are manually removed. Packages enable the importing and exporting of repository content, and the Package Manager can be used for configuring, building, downloading, installing and deleting packages on local AEM installations. This issue allows an unauthorized user to view and download packages.

Security researchers and Detectify Crowdsourcemembers Ai Ho (@j3ssiejjj) and Bao Bui (@Jok3rDb), discovered the issue.

_When a Crowdsource member reports a 0-day, Detectify’s research team works with vendors for responsible disclosure within 45-days of reporting. [Learn more about how Detectify handles this process.](https://blog.detectify.com/2019/10/03/how-detectify-handles-zero-day-submissions/)_

## **How the issue works**

This bug occurs when default security controls are manually turned off on the Package Manager content tree, by default `/etc/packages`.

The Package Manager is accessed by bypassing dispatcher filter rules. The component responsible for this issue used to be exploited before with one special character. This one uses a new approach by exploiting it with a lot of special characters combined.

**Normal request:**

![](https://labsadmin.detectify.com/app/uploads/2021/06/normal-request.png)

**Apply bypass to list the packages the user session has access to:**

![](https://labsadmin.detectify.com/app/uploads/2021/06/apply-bypass-to-list-all-packages.png)

## Mitigation

Adobe recommends to mitigate this information disclosure issue by setting strict permissions on Package Manager content tree, by default /etc/packages.

The researchers found that another effective way is to block public access to the CRX console (blocking all access to endpoints: `/crx/*`)

## **Report timeline for AEM CRX Bypass**

**12/09/2020** – Researchers send a report to an impacted organization.

**03/15/2021 – Researchers report multi subdomains to another impacted organization**.

**03/22/2021**– Researchers report the 0-day to Detectify who validates it.

**03/25/2021**– Detectify informs Adobe about the undocumented issue. The specific installations that were found to be vulnerable were quickly remediated by switching the default security controls back on.

**05/06/2021 – The test module for this security issue goes live for all Detectify customers.**

## **About the researchers**

**Ai Ho** ( [@j3ssiejj)](https://twitter.com/j3ssiejjj) is a passionate security engineer, developer and Detectify Crowdsource member who enjoys automation. He has been into responsible disclosure and bug bounties for the past two years and now builds his own tools to do it. [Check them out on GitHub.](https://github.com/j3ssie)

**Bao Bui** ( [@Jok3rDb)](https://twitter.com/jok3rdb) is a security researcher on the Detectify Crowdsource platform. He is a former CTF player of Meepwn CTF Team and got into bug bounty about a year ago.

## **How Detectify handles undocumented security issues**

When a researcher shares an undocumented security issue with Detectify, including 0-days, the first step is to evaluate that it is valid. Once confirmed, Detectify contacts the affected vendor on behalf of the researcher so they are aware of the issue.

The vendor then has 45 days to fix the issue before Detectify releases the security module that will be tested against customers’ web applications. If the vendor fixes the security vulnerability within these 45 days, Detectify releases the security test as soon as possible after the fix. _[Learn more about how Detectify handles this process.](https://blog.detectify.com/2019/10/03/how-detectify-handles-zero-day-submissions/)_

## Detectify customers will know if they’re vulnerable or not

You can follow the guidance provided by Adobe in this blog to verify your AEM installation. Get certainty whether you’re vulnerable to this issue, or any other known security issues used to exploit AEM by checking your web apps with Detectify.

**_Detectify customers know which vulnerabilities are confirmed as exploitable:_**

![](https://labsadmin.detectify.com/app/uploads/2021/06/Screenshot-2021-09-07-at-16.28.52.png)

_images: this screenshot of the Detectify GUI shows a web app is vulnerable to Routing-based authentication bypass_

[Detectify](https://www.detectify.com/) is a [crowd-based web vulnerability scanner](https://www.detectify.com/crowdsource) that goes beyond version and signature-testing. The testbed is payload-based and checks for actively exploited web vulnerabilities like [Prototype Pollution](https://labs.detectify.com/2021/06/08/what-is-a-prototype-pollution-vulnerability-and-how-does-page-fetch-help/), [OWASP Top 10](https://blog.detectify.com/2016/05/01/owasp/), undocumented vulns, [CORS misconfigurations](https://blog.detectify.com/2018/04/26/cors-misconfigurations-explained/) and more.

**Curious to see what Detectify will find in your web apps? [Sign up for a 2-week free trial today.](https://www.detectify.com/)**

* * *

**Into ethical hacking and want to join Crowdsource?** [Learn more on how you can earn recurring rewards while making the Internet safer with Detectify Crowdsource.](http://detectify-1.hubspotpagebuilder.com/more-hacking-less-busy-work)

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/writeups/undocumented-authentication-bypass-issue-in-aem-package-manager-blog-updated/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/writeups/undocumented-authentication-bypass-issue-in-aem-package-manager-blog-updated/ "Share on LinkedIn")

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F09%2FInk-Detectify-1600x1600-1-300x300-1.png&w=128&q=75)

**Detectify**

Complete External Attack Surface Management for AppSec and ProdSec teams.

## Check out more content

The Detectify AI Agent Alfred fully automates the creation of security tests for new vulnerabilities, from research to a merge request. In its first six …

September 25, 2025

Combining response-type switching, invalid state and redirect-uri quirks using OAuth, with third-party javascript-inclusions has multiple vulnerable scenarios where authorization codes or tokens could leak to …

July 06, 2022

CloudKit, the data storage framework by Apple, has various access controls. These access controls could be misconfigured, even by Apple themselves, which affected Apple’s own apps using CloudKit. This blog post explains in detail three bugs found in iCrowd+, Apple News and Apple Shortcuts with different criticality uncovered by Frans Rosen while hacking Cloudkit. All bugs were reported to and fixed by the Apple Security Bounty program.

September 13, 2021

Here’s how I (@Almroot) bought the domain name used in the NS delegations for the ccTLD of the Democratic Republic of Congo (.cd) and temporarily took over 50% of all DNS traffic for the TLD

January 15, 2021