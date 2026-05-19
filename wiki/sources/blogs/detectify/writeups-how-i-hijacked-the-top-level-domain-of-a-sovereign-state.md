---
source: detectify
source_url: https://labs.detectify.com/writeups/how-i-hijacked-the-top-level-domain-of-a-sovereign-state/
title: "Hijacking the top-level domain of a sovereign state - Labs Detectify"
author: "Detectify"
published: 2021-01-15T00:00:52+00:00
description: "Here’s how I temporarily took over 50% of all DNS traffic for the TLD of the Democratic Republic of Congo."
---

[Home](https://labs.detectify.com/)/ [Writeups](https://labs.detectify.com/category/writeups/)/ [Hijacking the top-level domain of a sovereign state](https://labs.detectify.com/writeups/how-i-hijacked-the-top-level-domain-of-a-sovereign-state/)

[Writeups](https://labs.detectify.com/category/writeups/ "Writeups")

# Hijacking the top-level domain of a sovereign state

![image of Fredrik Nordberg Almroth on purple background](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2012%2F10%2FFredrik-Nordberg-Almroth.png&w=128&q=75)

**Fredrik Nordberg Almroth** Jan 15, 2021

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/writeups/how-i-hijacked-the-top-level-domain-of-a-sovereign-state/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/writeups/how-i-hijacked-the-top-level-domain-of-a-sovereign-state/ "Share on LinkedIn")

![Fredrik Nordberg Almroth on purple patterned background](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2012%2F10%2FFredrik-Nordberg-Almroth-hero.png&w=3840&q=75)

**Imagine what could happen if the country-code top-level domain (ccTLD) of a sovereign state fell into the wrong hands. Here’s how I ( [@Almroot](https://twitter.com/almroot)) bought the domain name used in the NS delegations for the ccTLD of the Democratic Republic of Congo (.cd) and temporarily took over 50% of all DNS traffic for the TLD that could have been exploited for MITM or other abuse.**

_Note: This issue has been resolved and the .cd ccTLD no longer sends NS delegations to the compromised domain._

## Background

‘Twas the week before Christmas 2020 and I decided to run an analysis of all NS records used by all the TLDs globally. However one thing caught my attention. The domain name “scpt-network.com” had the EPP status code “redemptionPeriod”, which meant that someone had failed to renew their domain (pay their invoice?) in time.

This is quite problematic as the name servers managing `.cd` are the following:

```
almroot@x:~$ dig NS +trace cd | grep "cd."
cd.			172800	IN	NS	ns-root-5.scpt-network.com.
cd.			172800	IN	NS	igubu.saix.net.
cd.			172800	IN	NS	sangoma.saix.net.
cd.			172800	IN	NS	ns-root-2.scpt-network.com.
cd.			172800	IN	NS	sabela.saix.net.
cd.			172800	IN	NS	ns-root-1.scpt-network.com.
```

So I figured I might as well make a bash script to ping me of any EPP status change of the domain.

To my surprise, about a week or so later, I got a ping that the domain had reached status “pendingDelete”.

**I realized the severity of this.** The domain name would soon be available for purchase by anyone on the Internet, meaning that the person who gets hold of that domain name would also get the NS capabilities of `.cd`.

I modified the script, and started probing the registrar on a minute basis for any further status changes.

On the evening of December 30, I got a ping. **I opened my laptop and purchased the domain name to keep it from falling into the wrong hands.**

![](https://labsadmin.detectify.com/app/uploads/2021/01/cd-zone-1536x1495-1.png)

As the three remaining delegations pointing to SAIX ( [the South African Internet eXchange](https://saix.net/)) were still working, the TLD remained operable throughout this time (albeit with a slight performance impact on any domain lookups).

Since I owned `scpt-network.com`, I could configure any subdomain under the zone at will. If I created a new subdomain (like `ns-root-1`) with an A-pointer to IP `1.3.3.7`, then `1.3.3.7` would get legitimate incoming DNS queries meant for `.cd`. **Any DNS response to those queries would be accepted by the caller**.

![](https://labsadmin.detectify.com/app/uploads/2021/01/cd-dns-hijack.png)

To not reply would cause the caller to reach a timeout, and the status code SERVFAIL would be assumed. This is good as a SERVFAIL will force the caller to try reaching any other name server (NS record) for the zone (`.cd`). That is, the caller would eventually hit one of the legitimate SAIX records and be routed appropriately to the correct destination.

## Potential impact

Hijacking the country-code top-level domain of a sovereign state has serious negative implications, especially if the domain were to fall into the hands of cybercriminals or a foreign adversary. The Democratic Republic of Congo (DRC) is not a small country. There are roughly [90 million people](http://data.un.org/en/iso/cd.html), not to mention many international companies and organizations operating with a `.cd` website.

DNS hijacking involving the TLD of an entire country is rare but not unheard of. For example, the ccTLD of the former [Soviet Union (.su)](https://www.theguardian.com/technology/2013/may/31/ussr-cybercriminals-su-domain-space) has been hijacked by cybercriminals in the past, and the Lenovo and Google websites for [Vietnam (.vn)](https://www.pcworld.com/article/2889392/like-google-in-vietnam-lenovo-tripped-up-by-a-dns-attack.html) also fell prey to DNS hijacking in 2015. Redirecting DNS traffic from legitimate `.cd` websites to a phishing site is one clear potential for abuse, but there’s more.

If I had operated with malicious intent, I could have also:

- **Passively intercepted DNS traffic**

**– which could be used for surveillance or data exfiltration**
- **Made new domain names “out of thin air”**

– imagine the capabilities if leveraged for [Fast Fluxing](https://en.wikipedia.org/wiki/Fast_flux)
- **Launched remote code execution (RCE) attacks on local networks**

– and target companies that use WPAD to query public DNS servers
- **Replied to legitimate DNS queries with bogus DNS responses**

– and completely took over targeted apex domains for companies or institutions with a `.cd` website or even launched a DDoS attack.

For example, I could have crafted an exploit that completely hijacked a specific apex domain under `.cd`. Let’s imagine that I always reply with NS `ns-root-1.scpt-network.com` (instead of these four: `[ns1,ns2,n3,ns4].google.com`) for any NS requests to `google.cd`. Now the caller will see this, and then carry out any subsequent DNS requests to `ns-root-1.scpt-network.com` which I control.

This also got me thinking, what if I replied to all NS queries with a reference back to myself. Then for any A question replied with `1.3.3.7`, all domain lookups for any apex or subdomain would eventually hit my manipulated A pointer. All subsequent network traffic would then be redirected to `1.3.3.7` and lead in a **DDoS** attack.

**In fact, this would also affect the availability of the entire TLD. 50% of the DNS traffic would become faulty, and the impact of (both) DoS attacks could be amplified by setting a high TTL in the DNS replies.**

Taking this a step further, say I were to explicitly target TXT records served for `google.cd`. Then I would be able to abuse the Let’s Encrypts [DNS-01 challenge](https://letsencrypt.org/docs/challenge-types/#dns-01-challenge) to issue a valid certificate for `google.cd` and effectively **undermine SSL/TLS** communications.

As I could control the NS delegations of any `.cd` apex domain, and **get valid certificates**, I would have been able to perform a [MITM](https://labs.detectify.com/2018/11/29/abuse-mitm-regardless-of-https/) attack even when SSL/TLS is enforced by the target.

While Google has various counter measures and mitigations for this kind of abuse, it’s safe to say this is not the case for _all apex domain names_ under `.cd`. Further information on how CA’s verify the ownership of domain names can be found in [BR 1.7.3](https://cabforum.org/wp-content/uploads/CA-Browser-Forum-BR-1.7.3.pdf).

Last but not least, with privileged access on an upstream host with DNS control, I could even **infiltrate the local networks of companies** (redacted in screenshot below) that send DNS lookups for WPAD by monitoring their queries, spoofing a reply, and redirecting the local network caller to download and **execute malicious JS-based proxy configuration over the Internet**. The WPAD protocol has had its share of issues, including RCE vulnerabilities as discussed by [Google’s Project Zero](https://googleprojectzero.blogspot.com/2017/12/apacolypse-now-exploiting-windows-10-in_18.html).

![](https://labsadmin.detectify.com/app/uploads/2021/01/wpad-dns-hijack-1024x484-1.png)

## Mitigation

On January 7th, I reached out to the Administrative and Technical contacts listed for `.cd` on [IANA’s webpage](https://www.iana.org/domains/root/db/cd.html). My initial thought was to transfer back the ownership of the domain name to the entity operating `.cd`.

Although one of the contacts replied and delegated to their colleague, as of this writing, I haven’t received any follow-up confirmation that they fixed the issue. Nonetheless, the issue seems to have been patched shortly after I contacted them as the DNS traffic I previously controlled for `.cd` has since been redirected to `scpt-network.net`.

I also submitted a report on January 8th to the Internet Bug Bounty on HackerOne, and I’m looking forward to seeing how they respond.

## Conclusion

The potential implications for DNS hijacking of a ccTLD are widespread and have extreme negative consequences, especially if the attacker has bad intentions. This vulnerability affects more than a single website, [subdomain](https://labs.detectify.com/2014/10/21/hostile-subdomain-takeover-using-herokugithubdesk-more/), or even a single apex domain. All `.cd` websites, including those for major international companies, financial institutions, and other organizations that have a `.cd` domain in Africa’s second most populous country could have fallen victim to abuse, including phishing, MITM, or DDoS.

As of this writing, I still own the domain name for `scpt-network.com` although NS delegations from the ccTLD `.cd` seemed to have stopped around January 8, 2021 after I reached out to the ccTLD contacts on January 7th. I did this to prevent malicious actors from hijacking the ccTLD of the Democratic Republic of Congo within the narrow window of time the domain name for one of the name servers managing the `.cd` TLD could’ve been taken over by anyone. Luckily, in this case, no damage appears to have been done.

How can companies protect themselves from DNS hijacking and subdomain takeovers? Find out about [Detectify Surface Monitoring](https://detectify.com/product/surface-monitoring) or read the [complete guide to External Attack Surface Management](https://detectify.com/external-attack-surface-management).

Interested in joining me in the Detectify Crowdsource ethical hacker community? Take our challenge and find out if you got what it takes at [https://cs.detectify.com/apply.](https://cs.detectify.com/apply)

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/writeups/how-i-hijacked-the-top-level-domain-of-a-sovereign-state/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/writeups/how-i-hijacked-the-top-level-domain-of-a-sovereign-state/ "Share on LinkedIn")

![image of Fredrik Nordberg Almroth on purple background](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2012%2F10%2FFredrik-Nordberg-Almroth.png&w=128&q=75)

**Fredrik Nordberg Almroth**

Detectify Co-Founder

## Check out more content

The Detectify AI Agent Alfred fully automates the creation of security tests for new vulnerabilities, from research to a merge request. In its first six …

September 25, 2025

Combining response-type switching, invalid state and redirect-uri quirks using OAuth, with third-party javascript-inclusions has multiple vulnerable scenarios where authorization codes or tokens could leak to …

July 06, 2022

CloudKit, the data storage framework by Apple, has various access controls. These access controls could be misconfigured, even by Apple themselves, which affected Apple’s own apps using CloudKit. This blog post explains in detail three bugs found in iCrowd+, Apple News and Apple Shortcuts with different criticality uncovered by Frans Rosen while hacking Cloudkit. All bugs were reported to and fixed by the Apple Security Bounty program.

September 13, 2021

Security researchers in the Detectify Crowdsource community, Ai Ho (@j3ssiejjj) and Bao Bui (@Jok3rDb), found an undocumented security issue in Adobe Experience Manager (AEM) that bypassed authentication, and left the application open to information disclosure attacks

June 28, 2021