---
source: detectify
source_url: https://labs.detectify.com/ethical-hacking/discovering-the-origin-host-to-bypass-waf/
title: "New tool release: Discovering the origin host to bypass web application firewalls - Labs Detectify"
author: "Detectify"
published: 2022-05-09T08:29:06+00:00
description: "TL/DR: Crowdsource hacker Luke “hakluke” Stephens documents a tool for discovering the origin host behind a reverse proxy which is useful for bypassing WAFs and other ..."
---

[Home](https://labs.detectify.com/)/ [Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/)/ [New tool release: Discovering the origin host to bypass web application firewalls](https://labs.detectify.com/ethical-hacking/discovering-the-origin-host-to-bypass-waf/)

[Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/ "Ethical Hacking")

# New tool release: Discovering the origin host to bypass web application firewalls

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F09%2FInk-Detectify-1600x1600-1-300x300-1.png&w=128&q=75)

**Detectify** May 09, 2022

[hakluke](https://labs.detectify.com/tag/hakluke/ "hakluke")

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/discovering-the-origin-host-to-bypass-waf/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/discovering-the-origin-host-to-bypass-waf/ "Share on LinkedIn")

![New tool release: Discovering the origin host to bypass web application firewalls](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2015%2F06%2FGeneral-pattern-starlink.png&w=3840&q=75)

#### TL/DR: **Crowdsource hacker Luke “ [hakluke](https://www.twitter.com/hakluke)” Stephens documents** a tool for discovering the origin host behind a reverse proxy which is useful for bypassing [WAFs](https://blog.detectify.com/2020/11/25/continuously-hack-yourself-because-waf-security-is-not-enough/) and other reverse proxies.

We’ve all been there; you settle down into your lovely comfy office chair with a perfectly warm coffee, ready to start hacking a new web application. You instinctively throw ‘”><img src=x onerror=alert()> into the search bar, and are immediately greeted with this familiar page.

![](https://labsadmin.detectify.com/app/uploads/2022/05/Screenshot-2022-05-06-at-09.42.48.png)

_You have been blocked by a Web Application Firewall (WAF). In this case, Akamai. What now? Do you quit? No! Hackers don’t quit, they hack!_

## **Common WAF Implementation**

The most common WAF implementation that I see is simply implementing the WAF as a reverse proxy, as shown in the diagram below:

![](https://labsadmin.detectify.com/app/uploads/2022/05/Screenshot-2022-05-06-at-09.43.29.png)

The redirection of traffic through the WAF is usually achieved using DNS. The hostname will typically be a CNAME or A record that points to the WAF, and then the WAF can determine which origin (web server) to send the request to based on the Host header.

## **The problem**

Here’s the problem, if the WAF needs to access the web server, then it needs to be accessible over the internet by the WAF. Oftentimes, when an origin web server is set up, it can be accessed directly by _anyone_ on the internet, not just the WAF. In this case, all we need to bypass the WAF is the direct IP address of the origin web server, then the traffic flow would look something like this:

![](https://labsadmin.detectify.com/app/uploads/2022/05/Screenshot-2022-05-06-at-09.44.05.png)

## **Finding the IP address**

There are a bunch of different ways to potentially find the origin IP address including:

- Scouring historical DNS records from a service such as SecurityTrails
- Abusing a SSRF in the web application
- Information disclosure (for example, in error messages)

In this blog post, we’ll be exploring a different method. For this example, we will be using tesla.com as the target – but I will not be revealing any sensitive information. A quick dig of the target reveals a few IP addresses.

hakluke$ dig tesla.com +short

23.201.26.71

104.86.104.55

104.89.119.127

2.20.92.122

184.30.18.203

184.50.204.169

Passing these IP addresses to IPInfo reveals that the IP addresses are owned by, you guessed it, Akamai.

![](https://labsadmin.detectify.com/app/uploads/2022/05/Screenshot-2022-05-06-at-09.45.27.png)

If I was looking to find the origin IP address of the tesla.com web server, the first thing I would do is get a list of IP addresses associated with the organization. Again, there are many ways to do this, but one such way is to look up the ASN details of the organization. For demonstration purposes, I used the HackerTarget ASN lookup tool at [https://hackertarget.com/as-ip-lookup/](https://hackertarget.com/as-ip-lookup/). There are a few different organizations with “Tesla” in the name, but “Tesla, US” is the one we are after.

The results reveal a series of IP addresses associated with Tesla.

199.120.52.0/24

213.19.141.0/24

199.120.53.0/24

199.43.255.0/24

199.66.10.0/24

199.120.48.0/24

8.47.24.0/24

8.244.131.0/24

62.67.197.0/24

2620:137:d000:1::/64

199.120.50.0/24

8.45.124.0/24

8.244.67.0/24

205.234.11.0/24

199.120.51.0/24

8.21.14.0/24

213.244.145.0/24

199.66.11.0/24

199.120.56.0/24

199.66.9.0/24

209.133.79.0/24

199.120.49.0/24

Great! Now we have a list of IP addresses, one of which might be the origin server of tesla.com! The next step is to systematically check all of these IP addresses to see if they return the tesla.com website. Unfortunately, there are a few things that make this difficult to do, namely:

1. Navigating to the IP address directly may not actually return the correct website because many web servers employ [virtual hosts](https://httpd.apache.org/docs/2.4/vhosts/).
2. There are thousands of IP addresses to sort through, it would take too long to do this manually.
3. We can’t directly compare the original response with the IP response because many pages will return slightly different responses on every load (for example, nonces).

Fortunately, there are solutions to all of these problems!

1. We can add the Host header to every request containing the original hostname, which should return the correct website, even if we are accessing the IP address directly.
2. We can write a tool to do this for us over thousands of hosts (I already have!)
3. Instead of comparing responses byte-for-byte, we can use the Levenshtein algorithm to determine similarity!

## **Hakoriginfinder**

Hakoriginfinder is a golang tool for discovering the origin host behind a reverse proxy, it is useful for bypassing WAFs and other reverse proxies. You supply it with a list of IP addresses (via stdin) along with a hostname, and it will make HTTP and HTTPS requests to every IP address, attempting to find the origin host by comparing the responses with the response of the real website, and finding similar responses by using the Levenshtein algorithm.

You can see the tool here: [https://github.com/hakluke/hakoriginfinder](https://github.com/hakluke/hakoriginfinder)

## **Remediation**

The best remediation to this type of WAF bypass is to whitelist the IP addresses of your WAF provider on the web server. The origin server should not be accessible from anywhere except the WAF, which forces everyone to use the application through the WAF even if they know the origin server’s IP address.

WAF providers will usually list the IP addresses that need to be whitelisted in their documentation. For reference, here are the relevant links for [Akamai](https://techdocs.akamai.com/property-mgr/docs/origin-ip-access-control), [Imperva](https://docs.imperva.com/howto/c85245b7) and [CloudFlare](https://www.cloudflare.com/ips/).

**Written by:**

Luke Stephens a.ka. [hakluke](https://www.twitter.com/hakluke). Currently living on the Sunshine Coast, in Australia, I recently resigned from my role as the Manager of Training and Quality Assurance for Bugcrowd to start my own consultancy, [Haksec](https://haksec.io/). I do a lot of penetration testing and bug bounties and create content for hackers. **[Check out my Youtube channel.](https://www.youtube.com/hakluke)**

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/discovering-the-origin-host-to-bypass-waf/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/discovering-the-origin-host-to-bypass-waf/ "Share on LinkedIn")

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F09%2FInk-Detectify-1600x1600-1-300x300-1.png&w=128&q=75)

**Detectify**

Complete External Attack Surface Management for AppSec and ProdSec teams.

## Check out more content

Why picking targets is so important Many ethical hackers struggle because they are hacking the “wrong” types of targets for them. This is especially true …

December 07, 2022

You will find a common pattern if you read blog posts or watch interviews with some of today’s top ethical hackers. When asked if coding …

November 30, 2022

Docker is an open-source platform that allows you to develop, deploy, and manage multiple applications across one operating system

November 21, 2022

Approaching a target to hack can feel like climbing a mountain. You may face large scopes, confusing applications, complex user hierarchies…the list goes on. The …

October 28, 2022