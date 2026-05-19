---
source: portswigger-research
source_url: https://portswigger.net/research/http-desync-attacks-what-happened-next
title: "HTTP Desync Attacks: what happened next | PortSwigger Research"
published: 2019-10-03T12:54:49
description: "Last month I published HTTP Desync Attacks: Request Smuggling Reborn. Since then, there's been a range of new developments. While vendors have been deploying fixes and publishing advisories, I've devi"
---

# HTTP Desync Attacks: what happened next

![James Kettle](https://portswigger.net/content/images/profiles/callout_james_kettle_112px.png)

### [James Kettle](https://portswigger.net/research/james-kettle)

Director of Research

[@albinowax](https://twitter.com/albinowax)

- **Published:** Thursday, 3 October 2019 at 12:54 UTC

- **Updated:** Tuesday, 20 September 2022 at 08:04 UTC


![](https://portswigger.net/cms/images/3a/c8/7cfb12a1aa0a-article-htttp-desync-article.png)

Last month I published [HTTP Desync Attacks: Request Smuggling Reborn](https://portswigger.net/blog/http-desync-attacks-request-smuggling-reborn). Since then, there's been a range of new developments. While vendors have been deploying fixes and publishing advisories, I've devised new desync techniques exposing yet more systems to attack. I've also adapted the tooling to make it easier to hunt down the dwindling number of vulnerable servers. In this post I'll take a look at what's new, then explore how to handle some common gotchas.

#### Patches

Akamai deployed a hotfix roughly 48 hours after my presentation - their network of front-end servers now respect [RFC 7230](https://datatracker.ietf.org/doc/html/rfc7230#section-3.3.1) and prioritise chunked Transfer-Encoding by default, meaning that the majority of websites using Akamai are no longer vulnerable. This appears to have been a silent fix with no public advisory or acknowledgement of the vulnerability.

F5 published advisory [K50375550](https://support.f5.com/csp/article/K50375550) for their BIG-IP servers, in which they suggest several potential workarounds, including configuration hardening and deploying newly released WAF rules. Enabling the protocol compliance enforcement sounds like the most reliable fix.

Nathan Davison [noticed that](https://nathandavison.com/blog/haproxy-http-request-smuggling) HAProxy failed to normalise the vertical tab technique included in HTTP Request Smuggler, leaving certain backend servers like gnunicorn exposed to attack. They resolved this with release 2.0.6. I hear another popular server is also vulnerable when paired with gnunicorn, so a patch for gnunicorn itself may be in order.

Finally, Golang published [CVE-2019-16276](https://groups.google.com/forum/#!topic/golang-announce/cszieYyuL9Q) for their net/http library.

#### New Techniques

When I initially researched HTTP Desync Attacks I discovered so many vulnerable servers I didn't have time to explore every idea for causing desynchronisation, let alone report every vulnerability. Since publication I've focused on exploring new desync techniques, to ensure my presentation last week at OWASP Global AppSec Amsterdam has some fresh content.

As usual I tried each of my desync ideas out on my scanning pipeline to identify which ones actually work. The coolest idea that completely failed was suggested to me by [@ZrariAnas](https://twitter.com/ZrariAnas). HTTP headers are ASCII so you can't apply classic unicode normalization attacks, but you can in theory use extended-ASCII characters, for example:

`Transfer-Encoding: chùnked`

Alas I couldn't find any webservers doing this kind of normalization. If you're interested in what else failed to make the cut, feel free to peruse [the commit log](https://github.com/PortSwigger/http-request-smuggler/commits/master).

So, what actually worked?

Some research originally done to bypass WAFs can be repurposed for full request smuggling attacks. One successful attack came from lifting a technique from [Steffen Ullrich's research](https://noxxi.de/research/dubious-http.html) on bypassing IDS:

> Suricata seems to interpret every value for Transfer-Encoding as chunked, even "chu"

You can exploit assorted real systems using this trick - to use it, ensure you've got the latest version of [HTTP Request Smuggler](https://github.com/PortSwigger/http-request-smuggler) and enable the 'lazygrep' technique.

I also had success using a subtle variation of an existing technique:

`Transfer-Encoding: \x00chunked`

The most successful new technique came from WAF-bypass research by Soroush Dalili, [buried in a spreadsheet](https://github.com/irsdl/httpninja/blob/master/Results_v0.1.xlsx):

`Foo: bar\r\n\rTransfer-Encoding: chunked`

This superfluous \\r enabled me to exploit numerous interesting systems leading to a $16,500 bounty - and teasingly caused false positives on Google's entire infrastructure (at least, I think they're false positives).

#### Tooling

During the original research I developed a way to scan for [HTTP Request Smuggling](https://portswigger.net/web-security/request-smuggling) without risk to other users or false-negatives, using a timeout-based heuristic. As it was inference-based, roughly 1% of the results were false positives. Unfortunately as real vulnerabilities get fixed while server behaviours that cause false positives get ignored, this false-positive rate can be expected to steadily increase over time. I've taken a few steps to address this in the latest release of HTTP Request Smuggler (v1.02):

- Added the 'only report exploitable' option which hides situations where desynchronisation is technically possible but not likely to be exploitable
- Added a 'risky mode' option which reduces false positives but may cause dropped requests for other users on vulnerable websites
- Added an extra request to the issue reported for CL.TE findings to help users quickly weed out less-promising findings

#### Methodology

A few people reported the same problem to me - they'd found a genuine request smuggling vulnerability, but seemed to only be able to exploit themselves, and wanted to know what to do in this situation.

First, make sure requestsPerConnection in Turbo Intruder is set to 1. Any higher, and you'll potentially cause a desync between Turbo Intruder and the front-end server, which is useless and effectively a false positive.

Next, recall you can only poison requests that are routed to the same back-end server. Since routing might be based on the request cookie, path, method or any other request property you should start with a 'victim' request that's near-identical to the attack request, then change each value and retry the attack in turn until the victim request resembles a regular GET request sent by another user.

If the regular GET request is still getting poisoned but you can't exploit other users, or the vulnerability is only visible intermittently, one possibility is that the target has multiple front-end servers and only some of them are vulnerable. You can explore this possibility using dig and the Hostname Resolution feature in Burp's Project Options.

Finally, the front-end's connection reuse might be tied to your IP. To explore this, try sending the victim requests from a different IP. I personally test this using regular Intruder, plus an upstream SOCKS proxy powered by an SSH tunnel. Turbo Intruder ignores proxy settings unless you set Engine=Engine.BURP.

If you find you're genuinely only able to affect requests from your own IP, the practical impact is limited to exploiting other people on the same corporate network... or direct attacks like the one I demonstrated on New Relic.

#### Further reading

The reports sent to [PayPal](https://hackerone.com/reports/510152) and [NewRelic](https://hackerone.com/reports/498052) are now public, as is [an exploit writeup by @memN0ps](https://memn0ps.github.io/http-request-smuggling-cl-te/).

Regilero just released [an excellent writeup](https://regilero.github.io/english/security/2019/10/17/security_apache_traffic_server_http_smuggling/) on some vulnerabilities he found in Apache Traffic Server last year, which includes a Docker image to set up your own vulnerable environment. As always, I advise getting familiar in a safe environment like the [Academy labs](https://portswigger.net/web-security/request-smuggling) before targeting live systems.

You may also be interested in the followup post [Breaking the chains on HTTP Request Smuggler](https://portswigger.net/research/breaking-the-chains-on-http-request-smuggler).

Finally, I still regard this as a promising topic for further research so you can expect more desync techniques to arrive from myself and others, and I'd encourage everyone to try out their own ideas.

[Request Smuggling](https://portswigger.net/research/request-smuggling)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**How to distinguish HTTP pipelining from request smuggling** 19 August 2025How to distinguish HTTP pipelining from request smuggling](https://portswigger.net/research/how-to-distinguish-http-pipelining-from-request-smuggling) [06 August 2025](https://portswigger.net/research/http1-must-die) [**Making desync attacks easy with TRACE** 19 March 2024Making desync attacks easy with TRACE](https://portswigger.net/research/trace-desync-attack) [**Making HTTP header injection critical via response queue poisoning** 22 September 2022Making HTTP header injection critical via response queue poisoning](https://portswigger.net/research/making-http-header-injection-critical-via-response-queue-poisoning)