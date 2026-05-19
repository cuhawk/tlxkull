---
source: portswigger-research
source_url: https://portswigger.net/research/top-10-web-hacking-techniques-of-2017
title: "Top 10 Web Hacking Techniques of 2017 | PortSwigger Research"
published: 2018-10-11T14:40:39
description: "The verdict is in! Following 37 nominations whittled down to a shortlist of 15 by a community vote, our panel of experts has conferred and selected the top 10 web hacking techniques of 2017 (and 2016)"
---

# Top 10 Web Hacking Techniques of 2017

![James Kettle](https://portswigger.net/content/images/profiles/callout_james_kettle_112px.png)

### [James Kettle](https://portswigger.net/research/james-kettle)

Director of Research

[@albinowax](https://twitter.com/albinowax)

- **Published:** Thursday, 11 October 2018 at 14:40 UTC

- **Updated:** Tuesday, 5 January 2021 at 14:10 UTC


![](https://portswigger.net/cms/images/66/6a/cd49472a0c43-article-top-10-hacking-techniques-winners-article2.png)

The verdict is in! Following [37 nominations](https://portswigger.net/blog/top-10-web-hacking-techniques-of-2017-nominations-open) whittled down to a shortlist of 15 by a community vote, our panel of experts has conferred and selected the top 10 web hacking techniques of 2017 (and 2016).

The panel consisted of [myself](https://twitter.com/albinowax), and distinguished researchers [Gareth Heyes](https://twitter.com/garethheyes), [Nicolas Grégoire](https://twitter.com/Agarri_FR), [Frans Rosén](https://twitter.com/fransrosen), and [Soroush Dalili](https://twitter.com/irsdl). Our objective is to spread awareness of the techniques, and also help prevent them from being forgotten in coming years. As such, we’ve evaluated the 15 nominees by how innovative, widespread and impactful the findings are, and how long they will continue to be relevant. The top three results in particular are unanimously regarded as must-read articles by the entire panel.

We initially decided to prevent conflicts of interest by excluding PortSwigger research, but after we decided to have a broad voting panel it become clear we needed a better system. We eventually settled on disallowing panelists from voting on research they’re affiliated with, and adjusting the final scores to compensate. Of course by then it was too late to reintroduce PortSwigger research, so we’ll never know what the likes of [Cracking the Lens](https://portswigger.net/blog/cracking-the-lens-targeting-https-hidden-attack-surface) and [XSS without HTML](https://portswigger.net/blog/xss-without-html-client-side-template-injection-with-angularjs) would have scored ;)

We’ll run through the results starting at 10th place and building towards the best research of the year:

### 10\. Binary Webshell Through OPcache in PHP 7

In this [blog post](https://gosecure.net/2016/04/27/binary-webshell-through-opcache-in-php-7/) from 2016, [Ian Bouchard](https://twitter.com/corb3nik) unveils a novel technique to bypass hardening and successfully obtain RCE via file write vulnerabilities on systems running PHP 7.

### 9\. Cure53 Browser Security Whitepaper

In this [enormous whitepaper](https://github.com/cure53/browser-sec-whitepaper/raw/master/browser-security-whitepaper.pdf) commissioned by Google, [Cure53](https://twitter.com/cure53berlin) take an in depth look at the security of Internet Explorer, Edge and Chrome. Chapters 3-5 in particular contain some interesting web security lore.

### 8\. Request Encoding to bypass web application firewalls

In which [Soroush Dalili](https://twitter.com/irsdl) does some crazy stuff with encoding and malformed HTTP requests to dance around numerous WAFs. Unfortunately a recording of the presentation isn't available, but it can be pieced together from [two](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2017/august/request-encoding-to-bypass-web-application-firewalls/) blog [posts](https://soroush.secproject.com/blog/2017/09/additional-notes-on-a-forgotten-http-invisibility-cloak-talk/) and the updated [slides](https://www.slideshare.net/SoroushDalili/waf-bypass-techniques-using-http-standard-and-web-servers-behaviour).

### 7\. A deep dive into AWS S3 access controls

In [A deep dive into AWS S3 access controls](https://labs.detectify.com/2017/07/13/a-deep-dive-into-aws-s3-access-controls-taking-full-control-over-your-assets/), [Frans Rosén](https://twitter.com/fransrosen) examines the inner workings of S3 buckets from both an attacker's and defender's perspective. It covers numerous common pitfalls including the amazing and hilarious 'AuthenticatedUsers' gotcha.

### 6\. Advanced Flash Vulnerabilities

This [series of blog posts](https://opnsec.com/category/flash/) by [Enguerran Gillier](https://twitter.com/opnsec) uses a series of vulnerabilities in YouTube to introduce and illustrate several advanced Flash exploitation techniques. He's combined numerous often overlooked techniques with artistic flair in these exceedingly well explained posts.

### 5\. Cloudbleed

This slightly off-beat entry by [Tavis Ormandy](https://twitter.com/taviso) flouts common conceptions of what research should look like - it was discovered by accident, only affects one vendor, and barely requires active exploitation. Nevertheless, it clearly had a huge impact, and is going to leave many people keeping an eye open for memory disclosure for the foreseeable future.

In addition to the original bug report, it’s also worth reading [Cloudflare’s post-mortem](https://blog.cloudflare.com/incident-report-on-memory-leak-caused-by-cloudflare-parser-bug/), although beware that as Taviso warns it “severely downplays the risk to customers”.

### 4\. Friday The 13th JSON Attacks

Following on from the Java [Deserialization](https://portswigger.net/web-security/deserialization) Apocalypse in 2016, [Alvaro Muñoz](https://twitter.com/pwntester) & Oleksandr Mirosh performed a comprehensive analysis of numerous JSON (de)serialization libraries for Java and .NET, providing an ongoing supply of RCEs for the rest of us. It's available both as a [presentation](https://www.youtube.com/watch?v=oUAeWhW5b8c) and [whitepaper](https://www.blackhat.com/docs/us-17/thursday/us-17-Munoz-Friday-The-13th-JSON-Attacks-wp.pdf).

### **3\. Ticket Trick**

[Ticket Trick](https://medium.com/intigriti/how-i-hacked-hundreds-of-companies-through-their-helpdesk-b7680ddc2d4c) is an inventive technique by [Inti De Ceukelaire](https://twitter.com/intidc) abuses issue trackers and support centers to break into systems that implicitly trust all email addresses ending in a certain domain. It’s a beautiful example of how independent systems can be completely secure in isolation but fall apart when combined, and we expect this to be an effective technique for years to come.

It’s also the only entry in the top 3 with a logo, although I’m not sure it deserves any credit for that.

### **2\. Web Cache Deception**

Hackers have been poisoning web caches with malicious content for years, but [Omer Gil](https://twitter.com/omer_gil) took this technique and flipped it on its head, finding a way to manipulate web caches into saving other user’s sensitive data, and demonstrating it on Paypal. Available as both a [presentation](https://www.youtube.com/watch?v=mroq9eHFOIU) and [whitepaper](https://www.blackhat.com/docs/us-17/wednesday/us-17-Gil-Web-Cache-Deception-Attack-wp.pdf), [Web Cache Deception](https://portswigger.net/web-security/web-cache-deception) is a powerful and imaginative technique that still works on multiple major caches, and I suspect will provide a platform for further research in years to come.

Finding genuinely new techniques is getting more difficult as [application security](https://portswigger.net/burp/application-security-testing) matures, so it’s refreshing to see people prove year after year it’s still possible.

### **1\. A New Era of SSRF**

[A New Era of SSRF](https://www.youtube.com/watch?v=D1S-G8rJrEk) by [Orange Tsai](https://twitter.com/orange_8361) advances the state of the art of [SSRF](https://portswigger.net/web-security/ssrf) exploitation with an iceberg of inventive techniques for bypassing SSRF defences and maximising the resulting impact. Described as “impactful and innovative” by Agarri who [knows a bit about SSRF](https://www.youtube.com/watch?v=8t5-A4ASTIU) himself, [the slides](https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf) are squeezed with exploits making it well worth a second or third read-through.

It also features one of the best exploit chains I’ve ever seen, and is enough to put anyone off fetching user-supplied URLs forever. A well deserved number one.

We've since built a [Web Security Academy lab](https://portswigger.net/web-security/ssrf#ssrf-with-whitelist-based-input-filters) where you can try applying this research for yourself.

### Runners up

A few runners up that didn’t quite make it into the top 10 deserve an honourable mention. The [X41 Browser Security whitepaper](https://github.com/x41sec/browser-security-whitepaper-2017/blob/master/X41-Browser-Security-White-Paper.pdf) is a solid resource but light on web research, and [$10k host header](https://sites.google.com/site/testsitehacking/10k-host-header) is shiny but more of an elegant application of a known technique than fresh research. I really like [Hiding Wookies in HTTP](https://www.youtube.com/watch?v=dVU9i5PsMPY) but completely forgot to nominate it, and [Don’t trust the DOM](https://youtu.be/p07acPBi-qw) might have scored quite highly from the panel, but didn’t quite survive the community vote.

### What next?

This year was a bit experimental but it’s gone well and we have numerous ideas on how to improve the process for next year. There were some suspicious voting patterns that made us glad we enforced Google sign-in, and we plan to build a custom voting platform next year to further mitigate this and make voting easier. We’ll also be able to avoid excluding any research, and initiate the process immediately in January 2019 when the research is still fresh in people’s minds. In fact we've already [opened for nominations](https://docs.google.com/forms/d/e/1FAIpQLSfsznl4oLZlHaOU2IjkyH-dVFVpq610t8Ig97KKVdJg7aexsw/viewform?usp=sf_link) for 2018. If you're wondering how to invent a technique that will land you in next year's list, I've published a [guide on how to become a web security researcher](https://portswigger.net/blog/so-you-want-to-become-a-web-security-researcher).

Many thanks to the panellists for contributing their time and expertise, [Matt Johansen](https://twitter.com/mattjay) and [Jeremiah Grossman](https://twitter.com/jeremiahg) for their support with the transition, and the wider community for the many nominations and votes.

Update: the [Top 10 Web Hacking Techniques of 2019](https://portswigger.net/research/top-10-web-hacking-techniques-of-2019) is now out.

[top-10-techniques](https://portswigger.net/research/top-10-techniques) [Top 10 Hacking Techniques](https://portswigger.net/research/top-10-web-hacking-techniques)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[05 February 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) [06 January 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025-nominations-open) [04 February 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024) [08 January 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024-nominations-open)