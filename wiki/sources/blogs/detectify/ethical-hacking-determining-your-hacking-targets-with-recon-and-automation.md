---
source: detectify
source_url: https://labs.detectify.com/ethical-hacking/determining-your-hacking-targets-with-recon-and-automation/
title: "Determining hacking targets with recon and automation - Labs Detectify"
author: "Detectify"
published: 2022-12-07T09:50:35+00:00
description: "Finding hacking targets can be a challenge. Gunnar Andrews talks through how recon and automation can be powerful tools for ethical hackers."
---

[Home](https://labs.detectify.com/)/ [Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/)/ [Determining your hacking targets with recon and automation](https://labs.detectify.com/ethical-hacking/determining-your-hacking-targets-with-recon-and-automation/)

[Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/ "Ethical Hacking")

# Determining your hacking targets with recon and automation

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F09%2FInk-Detectify-1600x1600-1-300x300-1.png&w=128&q=75)

**Detectify** Dec 07, 2022

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/determining-your-hacking-targets-with-recon-and-automation/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/determining-your-hacking-targets-with-recon-and-automation/ "Share on LinkedIn")

![Determining your hacking targets with recon and automation](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F08%2Fdetermining-hacking-targets-with-recon-and-automation.png&w=3840&q=75)

## **Why picking targets is so important**

Many [ethical hackers](https://blog.detectify.com/2021/10/19/external-attack-surface-management/) struggle because they are hacking the “wrong” types of targets for them. This is especially true for independent researchers or bug bounty hunters. These endeavors only pay for results and findings, not the time invested. Ethical hackers with a good return on their time ensure that their efforts are focused on hacking targets they are comfortable with. A target that is right for you as an ethical hacker could be any of the following:

- A target using technology or framework you are an expert in.
- A website or asset that appears old or deprecated.
- Older versions of a released product that are still deployed.
- Web applications that accept a large amount of user input.
- Hacking targets that have had vulnerabilities in the past that you are an expert in.

This list can go on even beyond this. But the idea is that you should always try hacking targets you already have an advantage on. But, how do you find these targets and recognize them from a massive list of targets? The answer is recon and automation!

## **When recon and automation are an advantage for hacking targets**

[Recon](https://blog.detectify.com/2020/01/07/guest-blog-streaak-my-recon-techniques-from-2019/) and automation can be powerful tools for ethical hackers. Recon is the step in which asset discovery takes place. The better you perform your recon, the better the results of your hacking are likely to be. There are many ways that recon can be an advantage, such as:

- Finding hacking targets other ethical hackers missed.
- Creating a database of assets that can continuously be hacked or scanned.
- Fingerprinting assets to find technology/frameworks you know.
- Creating a system to learn about new assets that get deployed.

Using recon to find any of the things above will increase the chances you have success when you hack. Using some of these tricks, you can use recon to take your hacking to the next level and ensure you are only hacking the targets that are best for you.

## **When recon is a disadvantage for hacking targets**

A word of warning when it comes to recon and automation. While it is true that finding more lucrative assets is a good thing, it’s not the end game. Ethical hackers often get stuck doing so much recon work that they never actually hack the targets. Like all things, there is a balance between reconnaissance and hands-on hacking. If you find yourself struggling with this balance, here are some tips:

- Only use recon to find the information you actively use in your hands-on hacking.
- Automate more of your recon tasks.
- Minimize the targets you are hacking at one time.

Utilizing recon correctly can exponentially increase the returns of your hacking efforts, but getting stuck in the recon phase or getting hit with information overload, can actually hold you back. Balance is key!

## **Digging for gold where others aren’t**

Using recon to find juicy hacking targets is like digging for gold. To find gold, you have to dig where others are not. For example, many bug bounty hunters use the same subdomain enumeration tools, sources, and techniques as everyone else. There are a few that dig much deeper than this. To go one step further, you can for example, try fuzzing, brute forcing, generating permutations. The deeper you go, the more likely you are to uncover assets that are untouched by others.

> “Bug hunters can find more gold while digging by performing recon continuously.”

Another way other bug hunters can find more gold while digging is by performing recon _continuously_. Almost every ethical hacker will perform recon once when they first engage the target. Once they have completed gathering information through recon, it is never done again. But imagine a target deploys a new domain the very next day. You would never know the domain exists without continuous recon. This is a perfect use case for automation. Writing some scripts that continuously do recon on your target and report new findings is relatively easy. And the benefits are well worth the work. Any new domains found are always worth a look at if you are confident you stumbled across them first. It is like digging for gold in an untouched cave!

## **More gold to dig**

So far, we have talked mostly about subdomain recon, but it doesn’t end there. Recon can be used to find things that other ethical hackers have yet to find, allowing you the chance to test them first. Some of these things are:

- Hidden endpoints (ex: unlinked endpoints, older versions of APIs, etc.)
- Hidden parameters (ex: admin=true, debug=true, etc.)
- Comments from developers
- Virtual hosts
- Secrets (ex: API keys)

There are many things that recon can uncover. And thankfully, many ethical hackers have already made tools to help look for all of these things. Here are some examples:

- [FFUF](https://github.com/ffuf/ffuf) (finding hidden endpoints)
- [Arjun](https://github.com/s0md3v/Arjun) (finding hidden parameters)
- [Gobuster](https://github.com/OJ/gobuster) (searching for virtual hosts)
- [Trufflehog](https://github.com/trufflesecurity/trufflehog) (Secrets finder!)

## **Examples of using recon automation to uncover hacking targets**

### **Finding technologies with Shodan**

Shodan can be used to find all kinds of good targets with technology that you like or enjoy hacking on. There are a lot of repositories on GitHub for Shodan dorks if you want to check them out. A really simple example is looking for Jenkins server dashboards that are publicly available:

1. Browse to [shodan.io](https://www.shodan.io/)
2. For finding Jenkins dashboards, we will try the query: x-jenkins 200

Note: If you have a Shodan subscription you can use other filters or tags to narrow down results even further.

![](https://labsadmin.detectify.com/app/uploads/2022/12/shodan-filter.png)

1. From here, you can poke around the results and check the domains/IPs against known bug bounty targets (Solid list of all public targets [HERE](https://github.com/arkadiyt/bounty-targets-data))
2. If you find one in scope for a program, hack away!

This is a very small example of how Shodan could be used to find hacking targets that would be good for you. Also, I showed the search engine in the browser in the above example. This could be automated with the [shodan cli](https://cli.shodan.io/)!

### **Finding web hacking targets with httpx**

[Httpx](https://github.com/projectdiscovery/httpx) is a HTTP toolkit created by Project Discovery. Part of this toolkit is the ability to run technology detection using known fingerprints. In fact, right in the readme file in the repository is an example using their [subfinder](https://github.com/projectdiscovery/subfinder) tool and httpx to quickly enumerate subdomains for a target, then grab their status codes, HTTP title, and run technology detection:

subfinder -d detectify.com -silent\| httpx -title -tech-detect -status-code

This example is very basic, yet surprisingly quick and effective to quickly generate a list of a target’s domains and some good information about them. Look at the titles, status codes, and technology feedback. And from there, you should be able to discern which domains are best for you.

### **Using Arjun to find parameters**

Arjun can be used to find all available parameters on a page. This can be useful in many situations. This example is going to show a purposely vulnerable page.

1. Browse to [http://testphp.vulnweb.com/listproducts.php](http://testphp.vulnweb.com/listproducts.php)
2. You will notice a SQL error immediately. This is an obvious signal that an SQL injection could be possible
3. Point Arjun at the page ![](https://labsadmin.detectify.com/app/uploads/2022/12/arjun.png)
4. Here you can see that the tool found three possible parameters
5. Try the artist parameter ( [http://testphp.vulnweb.com/listproducts.php?artist=test](http://testphp.vulnweb.com/listproducts.php?artist=test)). You will notice the SQL error message changes based on what you put in the artist parameter. We are getting closer.
6. From here feel free to exploit the SQL injection by hand or use [sqlmap](https://sqlmap.org/) for help.

This is a small example showing the power of enumerating parameters. Finding all the parameters available to you will open up your attack surface as much as possible. Also, as with the other examples, this can be automated. Below would be a small tool chain using Subfinder, [hakrawler](https://github.com/hakluke/hakrawler), httpx, and Arjun:

subfinder -d detectify.com -silent \| httpx -silent \| hakrawler -u \| grep “detectify.com” \> targets.txt && arjun -i targets.txt -oJ data.json

The above tool chain will find subdomains of a target. Use httpx to find which domains have open web ports that are browsable, then spider those domains with hakrawler to find all the pages, and finally run Arjun on each page to find all the parameters for each page. When this stops running, you should have a good list of the pages on a web application, as well as all of the parameters for each page. If you want to take this even further with automation, I would recommend trying to filter your parameters using something like [GF](https://github.com/tomnomnom/gf) and some [patterns](https://github.com/1ndianl33t/Gf-Patterns).

## **Conclusion**

Recon can be one of the strongest tools in a hacker’s tool belt and is a great way to discover hacking targets. I hope something in this post helps you realize there might be a gap in your recon you can fill or that it may be time to automate some of your recon methodologies. I hope you can take something from this and use it to glean more findings. You can easily keep up with new techniques to find hidden assets and hacking targets by following the hacker community on Twitter, Slack, and other communication platforms.

* * *

#### **Written by:**  **Gunnar Andrews**

My online alias is [G0lden](https://mobile.twitter.com/g0lden_infosec). I am a hacker out of the midwest United States. I came into the hacking world through corporate jobs out of college, and I also do bug bounties. I enjoy finding new ways to hunt bugs and cutting-edge new tools. Making new connections with fellow hackers is the best part of this community for me!

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/determining-your-hacking-targets-with-recon-and-automation/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/determining-your-hacking-targets-with-recon-and-automation/ "Share on LinkedIn")

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F09%2FInk-Detectify-1600x1600-1-300x300-1.png&w=128&q=75)

**Detectify**

Complete External Attack Surface Management for AppSec and ProdSec teams.

## Check out more content

You will find a common pattern if you read blog posts or watch interviews with some of today’s top ethical hackers. When asked if coding …

November 30, 2022

Docker is an open-source platform that allows you to develop, deploy, and manage multiple applications across one operating system

November 21, 2022

Approaching a target to hack can feel like climbing a mountain. You may face large scopes, confusing applications, complex user hierarchies…the list goes on. The …

October 28, 2022

TL/DR: In this world of rapid digitization, companies are moving from traditional on-premise deployments to cloud service providers for handling their infrastructure. In this article, …

July 25, 2022