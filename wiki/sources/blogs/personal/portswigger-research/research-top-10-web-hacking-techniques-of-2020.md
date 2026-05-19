---
source: portswigger-research
source_url: https://portswigger.net/research/top-10-web-hacking-techniques-of-2020
title: "Top 10 web hacking techniques of 2020 | PortSwigger Research"
published: 2021-02-24T15:02:40
description: "Welcome to the Top 10 (novel) Web Hacking Techniques of 2020, our annual community-powered effort to identify the must-read web security research released in the previous year. Over the past few weeks"
---

# Top 10 web hacking techniques of 2020

![James Kettle](https://portswigger.net/content/images/profiles/callout_james_kettle_112px.png)

### [James Kettle](https://portswigger.net/research/james-kettle)

Director of Research

[@albinowax](https://twitter.com/albinowax)

- **Published:** Wednesday, 24 February 2021 at 15:02 UTC

- **Updated:** Friday, 26 February 2021 at 09:53 UTC


![](https://portswigger.net/cms/images/19/a4/08f1-article-top-10-web-hacking-techniques-of-2020-article.jpg)

Welcome to the Top 10 (novel) Web Hacking Techniques of 2020, our [annual community-powered effort](https://portswigger.net/research/top-10-web-hacking-techniques) to identify the must-read web security research released in the previous year.

Over the past few weeks, we've seen the community [nominate 54 innovative papers](https://portswigger.net/research/top-10-web-hacking-techniques-of-2020-nominations-open), posts and presentations, then cast their votes to whittle the list down to 15 potential candidates. Finally, an expert panel consisting of [Nicolas Grégoire](https://twitter.com/Agarri_FR), [Soroush Dalili](https://twitter.com/irsdl), [Filedescriptor](https://twitter.com/filedescriptor), and myself have voted in the 15 finalists to create the official top 10.

We've seen an undeniable increase in quality research since 2019, making the community vote even more competitive that usual. Numerous respectable posts didn't make the final 15; some that narrowly missed out include [Secret Fragments](https://www.ambionics.io/blog/symfony-secret-fragment), [AST Injection](https://blog.p6.is/AST-Injection/), [XSS without arbitrary JavaScript](https://portswigger.net/research/redefining-impossible-xss-without-arbitrary-javascript), and my own [Web Cache Entanglement](https://portswigger.net/research/web-cache-entanglement) amid countless others.

Other than the overall improved quality, two other themes stood out this year. The community vote demonstrated a strong interest in novel attacks exploiting proxies and multi-layered architectures; including follow-ups to [HTTP Desync Attacks](https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn) and some exciting novel techniques which we'll see shortly. We also observed that the best attack research is increasingly dipping below the application layer, whether it's abusing TLS, chunked encoding, PDF internals or packet fragmentation.

Without further ado, let's begin the countdown.

#### 10 - WAF evasion techniques

Much of [WAF evasion techniques](https://blog.isec.pl/waf-evasion-techniques/) is simply a robust but widely known methodology for understanding and evading Web Application Firewalls. What makes this stand out is [Paweł Hałdrzyński](https://twitter.com/phaldrzynski)'s gloriously low-level malformed chunk technique. There's surely more where that came from, and it may have impact beyond merely bypassing WAFs...

#### 9 - Attacking MS Exchange Web Interfaces

We all love a good class break, but good research isn't just about broadly applicable techniques. [Attacking MS Exchange Web Interfaces](https://swarm.ptsecurity.com/attacking-ms-exchange-web-interfaces/) by [Arseniy Sharoglazov](https://twitter.com/_mohemiv) stunned the entire panel while demonstrating the extreme depth you can achieve on a single target. If you run into this technology it will be invaluable, and it also lays extensive groundwork for future research.

#### 8 - ImageMagick - Shell injection via PDF password

In this post, [Alex](https://twitter.com/insertscript) targets the [notorious ImageMagick library](https://insert-script.blogspot.com/2020/11/imagemagick-shell-injection-via-pdf.html), twisting its vast array of features to create a polyglot that, with the help of a somewhat malicious bug report, gets RCE.

The research discovery process is often glossed over and at risk of seeming a bit magical to outsiders, but Alex does a great job of covering his discovery journey, making this post valuable for people looking to get into research as well as those of us who just want a shell.

#### 7 - Unauthenticated RCE on MobileIron MDM

Speaking of research journeys, this novel-esque post from top-10 frequenter [Orange Tsai](https://twitter.com/orange_8361) shows a master at work. [Unauthenticated RCE on MobileIron MDM](https://blog.orange.tw/2020/09/how-i-hacked-facebook-again-mobileiron-mdm-rce.html) follows his journey as he selects a target and chains multiple research-grade techniques in his pursuit of a shell. There's nothing like a case study exploiting a high profile target to prove research isn't just theoretical, and Orange provides one in style by landing RCE on Facebook. Awesome work, as usual.

#### 6 - Smuggling HTTP headers through reverse proxies

[Using underscores in header names](https://github.security.telekom.com/2020/05/smuggling-http-headers-through-reverse-proxies.html) has lurked on the edge of community awareness for quite a few years - for example, it's already implemented in [Param Miner](https://github.com/PortSwigger/param-miner) \- so it's great to see [Robin Verton](https://twitter.com/RobinVerton) drag it into the light with a case study showing critical impact! Even better that he uses it to crack SSL Client Authentication, which is far from a soft target.

#### 5 - NAT Slipstreaming

The panel was a bit conflicted about whether [Nat Slipstreaming](https://samy.pl/slipstream/) qualifies as a web hacking technique, but we had no doubts about the quality of the research.

[Samy Kamkar](https://twitter.com/samykamkar) used IP fragmentation to trick routers into interpreting part of a browser-issued HTTP request as a SIP packet and opening up the victim's NAT. This cross-layer, cross-discipline attack beautifully demonstrates the value of familiarity with underlying protocols and adjacent fields.

#### 4 - When TLS Hacks You

[SSRF](https://portswigger.net/web-security/ssrf) often has a critical impact, but if there's no convenient web services to target with it, it can appear frustratingly harmless. [When TLS Hacks You](https://github.com/jmdx/TLS-poison/) is an SNI injection-inspired technique by [Joshua Maddux](https://twitter.com/joshmdx) which elegantly combines DNS rebinding and TLS session resumption to exploit internal services that don't speak HTTP. As filedescriptor put it, _he brought gopher:// back!_

This is essential reading for anyone stuck with an SSRF, and we're looking forward to seeing this technique appearing in exploit writeups in future.

#### 3 - Attacking Secondary Contexts in Web Applications

Modern websites are a highly entangled mess of proxies, load balancers, and micro services. We've already seen quite a few [path traversal](https://portswigger.net/web-security/file-path-traversal) attacks exploiting this mess. What [Sam Curry](https://twitter.com/samwcyo) brings with Attacking Secondary Contexts in Web Applications ( [slides](https://docs.google.com/presentation/d/1N9Ygrpg0Z-1GFDhLMiG3jJV6B_yGqBk8tuRWO1ZicV8/edit#slide=id.g81ab6c90e0_0_51), [recording](https://www.youtube.com/watch?v=hWmXEAi9z5w)) is the exceptional clarity of someone who has spent a lot of time exploiting this stuff. The quality of explanation and numerous case studies make this an outstanding, must-watch presentation for newbies and experts alike.

#### 2 - Portable Data exFiltration: XSS for PDFs

Everyone knows what happens if you embed user input in HTML without encoding it, and in recent years people have also exploited servers that render user-uploaded PDFs using HTML. However, thanks to PDF's horrifying markup, nobody has publicly explored what happens when user input is embedded in a PDF, until now. In [Portable Data exFiltration](https://portswigger.net/research/portable-data-exfiltration), [Gareth Heyes](https://twitter.com/garethheyes) tackles the format and stretches PDF parsers to go from PDF link injection to document theft, JavaScript execution and SSRF.

Needless to say I didn't vote for this myself due to a [conflict of interest](https://portswigger.net/research/gareth-heyes).

#### 1 - H2C Smuggling: Request Smuggling Via HTTP/2 Cleartext

Given that no browsers support it, you could almost forget that HTTP/2 cleartext (H2C) exists, right up until [Jake Miller](https://twitter.com/theBumbleSec) unveiled [H2C Smuggling](https://labs.bishopfox.com/tech-blog/h2c-smuggling-request-smuggling-via-http/2-cleartext-h2c). This is an all-new technique that abuses H2C-unware front-ends to create a tunnel to backend systems, enabling attackers to bypass front-end rewrite rules and exploit internal HTTP headers.

It's conceptually similar to the previous year's [WebSocket Smuggling](https://github.com/0ang3el/websocket-smuggle) but looks significantly more practical. Request tunneling exploitation is an emerging art so this one may be a slow burn, but we anticipate some serious carnage in future.

Ultimately this research proves that, just like Gopher, this already-obsolete protocol is a gift to attackers. Massive congratulations to Jake Miller and Bishop Fox on a well-deserved winner!

### Conclusion

As ever, this top 10 list just scratches the surface and we recommend web security enthusiasts read the [entire nomination list](https://portswigger.net/research/top-10-web-hacking-techniques-of-2020-nominations-open).

We're looking forward to seeing what the community shares comes out this year! If you're interested in reading research the moment it's released, you might want to check out [@PortSwiggerRes](https://twitter.com/portswiggerres) and [r/websecurityresearch](https://www.reddit.com/r/websecurityresearch/), both of which were created to promote and curate quality web research. If you're tempted to attempt some research yourself, we have some [advice on becoming a web security researcher](https://portswigger.net/research/so-you-want-to-be-a-web-security-researcher). Also, you may want to check out previous year's top tens: [2019](https://portswigger.net/research/top-10-web-hacking-techniques-of-2019), [2018](https://portswigger.net/research/top-10-web-hacking-techniques-of-2018), [2017](https://portswigger.net/research/top-10-web-hacking-techniques-of-2017), [2015](https://web.archive.org/web/20191215103809/https://www.whitehatsec.com/blog/top-10-web-hacking-techniques-of-2015/), [2014](https://web.archive.org/web/20200313124651/https://www.whitehatsec.com/blog/top-10-web-hacking-techniques-of-2014//), [2013](https://web.archive.org/web/20160507023636/https://www.whitehatsec.com/blog/top-10-web-hacking-techniques-2013/), [2012](https://web.archive.org/web/20170903113359/https://www.whitehatsec.com/blog/top-ten-web-hacking-techniques-of-2012/), [2011](https://web.archive.org/web/20170831160914/https://www.whitehatsec.com/blog/vote-now-top-ten-web-hacking-techniques-of-2011/), [2010](http://jeremiahgrossman.blogspot.com/2011/01/top-ten-web-hacking-techniques-of-2010.html), [2009](http://jeremiahgrossman.blogspot.com/2010/01/top-ten-web-hacking-techniques-of-2009.html), [2008](http://jeremiahgrossman.blogspot.com/2009/02/top-ten-web-hacking-techniques-of-2008.html), [2007](http://jeremiahgrossman.blogspot.com/2008/01/top-ten-web-hacks-of-2007-official.html), [2006](http://jeremiahgrossman.blogspot.com/2006/12/top-10-web-hacks-of-2006.html).

We'd like to conclude with a massive thanks to the entire community - without your research, nominations and votes this wouldn't be possible.

Till next year!

\- by [James Kettle](https://twitter.com/albinowax), with insights from [Nicolas Grégoire](https://twitter.com/Agarri_FR), [Soroush Dalili](https://twitter.com/irsdl) and [Filedescriptor](https://twitter.com/filedescriptor).

[Top 10 Hacking Techniques](https://portswigger.net/research/top-10-web-hacking-techniques)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[05 February 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) [06 January 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025-nominations-open) [04 February 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024) [08 January 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024-nominations-open)