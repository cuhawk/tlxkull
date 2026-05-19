---
source: detectify
source_url: https://labs.detectify.com/how-to/advanced-subdomain-reconnaissance-how-to-enhance-an-ethical-hackers-easm/
title: "Subdomain reconnaissance: enhancing a hacker's EASM - Labs Detectify"
author: "Detectify"
published: 2023-01-13T13:48:35+00:00
description: "This blog provides a few advanced subdomain reconnaissance techniques to enhance an ethical hacker’s EASM techniques."
---

[Home](https://labs.detectify.com/)/ [How to](https://labs.detectify.com/category/how-to/)/ [Advanced subdomain reconnaissance: How to enhance an ethical hacker’s EASM](https://labs.detectify.com/how-to/advanced-subdomain-reconnaissance-how-to-enhance-an-ethical-hackers-easm/)

[How to](https://labs.detectify.com/category/how-to/ "How to")

# Advanced subdomain reconnaissance: How to enhance an ethical hacker’s EASM

**Gunnar Andrews** Jan 13, 2023

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/advanced-subdomain-reconnaissance-how-to-enhance-an-ethical-hackers-easm/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/advanced-subdomain-reconnaissance-how-to-enhance-an-ethical-hackers-easm/ "Share on LinkedIn")

![Advanced subdomain reconnaissance: How to enhance an ethical hacker’s EASM](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F01%2FHow-to-enhance-an-ethical-hackers-EASM-with-advanced-subdomain-reconnaissance.png&w=3840&q=75)

**[External Attack Surface Management (EASM)](https://detectify.com/external-attack-surface-management) is the continuous discovery, analysis, and monitoring of an organization’s public facing assets. A substantial part of EASM is the discovery of subdomains. Basic techniques to enumerate subdomains could leave domains unmanaged and vulnerable. Quality EASM provides sufficient visibility of assets and is achieved by finding and monitoring as many subdomains as possible. This blog aims to provide a few advanced subdomain reconnaissance techniques to enhance an [ethical hacker’s EASM techniques](https://blog.detectify.com/2023/01/04/ethical-hackers-perspective-on-easm/).**

## **Enhancing the effectiveness of their subdomain enumeration**

Many EASM programs limit the effectiveness of subdomain enumeration by relying solely on pre-made tools. The following techniques show how ethical hackers can expand their EASM program beyond the basics and build the [best possible subdomain asset inventory](https://detectify.com/solutions/prevent-subdomain-takeover).

### **Discovering root domains**

Subdomain enumeration is commonplace, but root domain enumeration is often ignored. Root domain enumeration can be performed in many ways, including:

- Acquisitions
- Crawling
- Google dorking
- Checking ASNs and IP ranges
- Reverse Whois

#### **Acquisitions**

Searching for acquisitions can help discover assets previously owned by an acquired company. You can search for acquisitions by visiting Crunchbase, searching for an organization, and scrolling down to “Acquisitions.” Here’s an example of Tesla’s [acquisitions](https://www.crunchbase.com/organization/tesla-motors/company_financials):

![](https://labsadmin.detectify.com/app/uploads/2023/01/tesla_aqcuistions.png)

#### **Crawling**

Going to known in-scope domains and using a web crawler can lead you to new subdomains and root domains owned by the same company. Just remember to confirm that the new domain is in scope.

Using a tool like [katana](https://github.com/projectdiscovery/katana) on a target’s seed domain can help you find new subdomains. For example, running katana -u https://tesla.com will find auth.tesla.com, ir.tesla.com, shop.tesla.com, and more.

![](https://labsadmin.detectify.com/app/uploads/2023/01/new_tesla_domain.png)

![](https://labsadmin.detectify.com/app/uploads/2023/01/new_tesla_domain_2.png)

#### **Google dorking**

Using the power of Google can lead to a variety of findings. Try dorking for the company’s copyright using “© \[COMPANY\]. All rights reserved.” or using the allintext, allintitle, and allinurl tags such as allintitle:”Yahoo”.

![](https://labsadmin.detectify.com/app/uploads/2023/01/yahoo_g_dorking.png)

#### **Checking ASNs and IP ranges**

If the organization has an ASN or their own IP range, there are tools such as Shodan and [dnsx](https://github.com/projectdiscovery/dnsx) that can check these for domains. You can search an organization’s ASN details with the Hurricane Electric BGP [toolkit](https://bgp.he.net/) to find ASNs and IP ranges that can be scanned to discover new assets. Here’s just a few of the results from searching “Tesla”:

![](https://labsadmin.detectify.com/app/uploads/2023/01/tesla_asn.png)

#### **Reverse Whois**

WHOIS is a protocol that is mostly used for storing ownership information of domains. Normally, you provide a domain name and a WHOIS server will respond with the domain owner’s details, but there are services that allow you to do a _reverse_ WHOIS lookup, where you provide an organization name or email address, and it will return all of the associated domains.

This information has a very low false positive rate and can yield thousands of domains for larger companies. Some of the more well-known reverse whois services are [Whoxy](https://www.whoxy.com/), [ViewDNS](https://viewdns.info/reversewhois/), and [WhoisXMLAPI](https://whois.whoisxmlapi.com/lookup). They all offer APIs that will make it easy to automate the process.

### **Certificate transparency**

Certificate transparency logs are a great way to find more subdomains that other methods may not discover. Here’s how it’s done:

1. Go to the organization’s main site and find the certificate organization name

![](https://labsadmin.detectify.com/app/uploads/2023/01/org_name.png)

2\. Take the organization name and query crt.sh for that organization

![](https://labsadmin.detectify.com/app/uploads/2023/01/tesla_services.png)

3\. Take all common names found for that organization, and query those too. I used \*.dev.ap.tesla.services here as an example.

![](https://labsadmin.detectify.com/app/uploads/2023/01/more_subdomains-1.png)

This process discovered pages of subdomains that other methods could’ve missed. If you want to see a walkthrough of this method, check out Nahamsec’s [video](https://www.youtube.com/watch?v=siELBLVW5cU).

### **Permutations**

Finding subdomains with permutations is a strategy that has gained a lot of traction recently and is something I have had a lot of success with. The basic idea is that we take subdomains we know to exist and then use them as seeds to generate permutations. For example, if app.example.com exists, we could test for the following:

- app-staging.example.com
- app-dev.example.com
- App2.example.com

There are many tools for automating asset discovery through subdomain permutations, such as [altdns](https://github.com/infosec-au/altdns), [ripgen](https://github.com/resyncgg/ripgen) and [regulator](https://github.com/cramppet/regulator). I recommend testing all the tools and seeing which one suits you.

## **Continuous Monitoring**

Continuous monitoring is essential because external attack surfaces are constantly changing. The key to effective EASM is that you are monitoring changes in as close to real-time as possible. Use automation to routinely check for:

- New subdomains from passive sources
- Bruteforcing new subdomains
- New root domains
- Extended updated information about subdomains (which ones resolve, open web ports, etc)

## **Summarizing advanced subdomain reconnaissance**

This blog  has offered helpful techniques for advanced subdomain reconnaissance that you can add to your EASM toolbelt. There are many data sources to evaluate when assessing an organization’s attack surface. As an ethical hacker, the more data sources you can include, the more effective your EASM will be. As I have mentioned in previous articles, organizations themselves should start thinking like us ethical hackers when it comes to assessing their internet-facing assets and continuously monitoring their growing attack surface. As this blog discusses, root domain enumeration can be performed in many ways, including:

- Acquisitions
- Crawling
- Google dorking
- Checking ASNs and IP ranges
- Reverse Whois

Why not give it a try?

### **Additional reading**

[DNS Hijacking – Taking Over Top-Level Domains and Subdomains](https://blog.detectify.com/2021/01/19/dns-hijacking-taking-over-top-level-domains-and-subdomains/)

[Determining your hacking targets with recon and automation](https://labs.detectify.com/2022/12/07/determining-your-hacking-targets-with-recon-and-automation/)

[\[New research\] Subdomain takeovers are on the rise and are getting harder to monitor](https://blog.detectify.com/2022/03/22/subdomain-takeover-on-the-rise-detectify-research/)

* * *

#### **Written by:**  **Gunnar Andrews**

My online alias is [G0lden](https://mobile.twitter.com/g0lden_infosec). I am a hacker out of the midwest United States. I came into the hacking world through corporate jobs out of college, and I also do bug bounties. I enjoy finding new ways to hunt bugs and cutting-edge new tools. Making new connections with fellow hackers is the best part of this community for me!

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/advanced-subdomain-reconnaissance-how-to-enhance-an-ethical-hackers-easm/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/advanced-subdomain-reconnaissance-how-to-enhance-an-ethical-hackers-easm/ "Share on LinkedIn")

**Gunnar Andrews**

Ethical Hacker

## Check out more content

TL/DR: Web applications have both authentication and authorization as key concepts and if bypassed by an attacker, it can compromise sensitive data. With threats such …

August 05, 2022

TL/DR: It’s becoming increasingly easy to compromise sensitive information for attackers to take advantage of. In this post, Detectify security researcher Alfred Berg wrote about …

June 16, 2022

TL/DR: Web applications can be exploited to gain unauthorized access to sensitive data and web servers. Threats include SQL Injection, Code Injection, XSS, Defacement, and …

May 16, 2022

If you don’t know about HTTP/2 request smuggling then what are you hacking? Alfred Berg, Security Researcher at Detectify, shows you how to set up …

August 26, 2021