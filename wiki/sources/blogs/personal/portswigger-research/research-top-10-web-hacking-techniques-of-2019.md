---
source: portswigger-research
source_url: https://portswigger.net/research/top-10-web-hacking-techniques-of-2019
title: "Top 10 web hacking techniques of 2019 | PortSwigger Research"
published: 2020-02-17T14:36:02
description: "The results are in! After 51 nominations whittled down to 15 finalists by a community vote, an expert panel consisting of Nicolas Grégoire, Soroush Dalili, Filedescriptor, and myself have conferred, v"
---

# Top 10 web hacking techniques of 2019

![James Kettle](https://portswigger.net/content/images/profiles/callout_james_kettle_112px.png)

### [James Kettle](https://portswigger.net/research/james-kettle)

Director of Research

[@albinowax](https://twitter.com/albinowax)

- **Published:** Monday, 17 February 2020 at 14:36 UTC

- **Updated:** Tuesday, 5 January 2021 at 14:10 UTC


![](https://portswigger.net/cms/images/2e/da/ea1cb56b8752-article-web_hacking_techniques_2019_article.png)

The results are in!

After [51 nominations](https://portswigger.net/research/top-10-web-hacking-techniques-of-2019-nominations-open) whittled down to 15 finalists by a community vote, an expert panel consisting of [Nicolas Grégoire](https://twitter.com/Agarri_FR), [Soroush Dalili](https://twitter.com/irsdl), [Filedescriptor](https://twitter.com/filedescriptor), and [myself](https://twitter.com/albinowax) have conferred, voted, and selected the Top 10 new web hacking techniques of 2019.

Every year, professional researchers, seasoned pentesters, bug bounty hunters and academics release a flood of blog posts, presentations, videos and whitepapers. Whether they're suggesting new attack techniques, remixing old ones, or documenting findings, many of these contain novel ideas that can be applied elsewhere.

However, in these days of vulnerabilities arriving equipped with logos and marketing teams it's all too easy for innovative techniques and ideas to get missed in the noise, simply because they weren't broadcast loudly enough. That's why every year, we work with the community to seek out and enshrine ten techniques that we think will withstand the test of time.

We regard these ten as the creme of the most innovative web security research published in the last year. Every entry contains insights for aspiring researchers, pentesters, bug bounty hunters, and anyone else interested in recent developments in web security.

#### Community Favourite - HTTP Desync Attacks

The entry with the most community votes by a substantial margin was [HTTP Desync Attacks](https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn), in which I revived the long forgotten technique of [HTTP Request Smuggling](https://portswigger.net/web-security/request-smuggling) to earn over $90k in bug bounties, compromise PayPal's login page twice, and kick off a wave of findings for the wider community. I regard this as my best research to date, but I made the tactical decision to exclude it from the official top 10 because there's no way I'm going to write a post that declares my own research the best. Moving swiftly on...

### 10\. Exploiting Null Byte Buffer Overflow for a $40,000 bounty

At number 10 we have a fantastic heartbleed-style [memory-safety exploit](https://samcurry.net/filling-in-the-blanks-exploiting-null-byte-buffer-overflow-for-a-40000-bounty/) from [Sam Curry](https://twitter.com/samwcyo) and friends. This critical but easily-overlooked vulnerability almost certainly affects other websites, and serves us a reminder that even if you're an expert, there's still a place for simply fuzzing and keeping an eye out for anything unexpected.

### 9\. Microsoft Edge (Chromium) - EoP to Potential RCE

In this writeup, [Abdulrhman Alqabandi](https://twitter.com/Qab) uses a mixture of [web and binary attacks](https://leucosite.com/Edge-Chromium-EoP-RCE/) to pwn anyone who makes the mistake of visiting his site using Microsoft's new Chromium-Powered Edge (aka Edgium).

$40,000 in bounties later this is now patched, but it's still a sterling example of an exploit chain combining multiple low-severity vulnerabilities to achieve a critical impact, and also beautifully demonstrates how web vulnerabilities can bleed onto your desktop through privileged origins. It inspired us to update [Hackability](http://portswigger-labs.net/hackability/) to detect when it's on a privileged origin by scanning the chrome object.

For another look at web vulnerability chaos in the browser-chrome battleground, check out [Remote Code Execution in Firefox beyond memory corruptions](https://frederik-braun.com/firefox-ui-xss-leading-to-rce.html).

### 8\. Infiltrating Corporate Intranet Like NSA: Pre-Auth RCE On Leading SSL VPNs

The incumbent winner [Orange Tsai](https://twitter.com/orange_8361) makes his first appearance alongside [Meh Chang](https://twitter.com/mehqq_) with multiple unauthenticated RCE [vulnerabilities in SSL VPNs](https://www.youtube.com/watch?v=1IoythC_pIY).

The privileged, internet-exposed position VPNs typically sit in means that in terms of sheer impact, this is about as good as it gets. Although the techniques applied are largely classics, they use some creative twists that I won't spoil for you here. This research helped spawn a wave of audits targeting SSL VPNs, leading to numerous findings including a [clutch of SonicWall vulnerabilities](https://blog.scrt.ch/2020/02/11/sonicwall-sra-and-sma-vulnerabilties/) published last week.

### 7\. Exploring CI Services as a Bug Bounty Hunter

Modern websites are stitched together from numerous services reliant on secrets to identify each-other. When these get leaked, the web of trust can fall apart. Secrets leaking in Continuous Integration repositories/logs is a common occurrence, and finding them via automation is even more common. Yet [this research](https://edoverflow.com/2019/ci-knew-there-would-be-bugs-here/) by [EdOverflow](https://twitter.com/EdOverflow) et al systematically sheds new light on overlooked cases and potential future research areas. It's also quite possibly the inspiration for the hilarious site/tool [SSHGit](https://shhgit.darkport.co.uk/).

### 6\. All is XSS that comes to the .NET

Monitoring novel research is a core part of my job, but I still managed to completely miss this post when it was first released. Fortunately, someone in the community had sharper eyes and nominated it.

[Paweł Hałdrzyński](https://twitter.com/phaldrzynski) takes a [little-known legacy feature](https://blog.isec.pl/all-is-xss-that-comes-to-the-net/) of the .NET framework and shows how it can be used to add arbitrary content to URL paths on arbitrary endpoints, causing us some mild panic when we realised even our own website supported it.

Reminiscent of [Relative Path Overwrite](https://portswigger.net/research/detecting-and-exploiting-path-relative-stylesheet-import-prssi-vulnerabilities) attacks, this is a piece of arcana that can sometimes kick off an exploit chain. In the post it's used for [XSS](https://portswigger.net/web-security/cross-site-scripting), but we strongly suspect alternative abuses will emerge in future.

### 5\. Google Search XSS

The Google Search box is probably the most-tested input on the planet, so how [Masato Kinugawa](https://twitter.com/kinugawamasato) managed to XSS it was beyond comprehension, up until he revealed all via a collaboration with his colleague [LiveOverflow](https://twitter.com/liveoverflow).

These two videos provide a solid introduction on how to [find DOM parsing bugs](https://www.youtube.com/watch?v=lG7U3fuNw3A) by reading the docs and fuzzing, and also give a [rare look into](https://www.youtube.com/watch?v=gVrdE6g_fa8) the creativity behind this magnificent exploit.

### 4\. Abusing Meta Programming for Unauthenticated RCE

Orange Tsai returns with a pre-auth RCE in Jenkins, described over two posts. The [authentication bypass](https://blog.orange.tw/2019/01/hacking-jenkins-part-1-play-with-dynamic-routing.html) is nice, but our favourite innovation is the [use of meta-programming](https://blog.orange.tw/2019/02/abusing-meta-programming-for-unauthenticated-rce.html) to create a backdoor that executes at compile-time, in the face of numerous environmental constraints. We expect to see meta-programming again in future.

It's also an excellent example of research continuation, as the exploit was subsequently [improved by multiple researchers](https://github.com/orangetw/awesome-jenkins-rce-2019#references).

### **3\. Owning The Clout Through Server Side Request Forgery**

[This presentation](https://www.youtube.com/watch?v=o-tL9ULF0KI) from [Ben Sadeghipour](https://twitter.com/NahamSec) and [Cody Brocious](https://twitter.com/daeken) starts out with an overview of existing [SSRF](https://portswigger.net/web-security/ssrf) techniques, shows how they can be adapted and applied to server-side PDF generators, then brings DNS rebinding into the mix for good measure.

The work targeting PDF generators is an insightful look into a feature-class that's all too easily ignored. We first saw [DNS rebinding on server-side browsers](https://labs.f-secure.com/blog/from-http-referer-to-aws-security-credentials/) appear on the [2018 nomination list](https://portswigger.net/research/top-10-web-hacking-techniques-of-2018-nominations-open), and the release of HTTPRebind should help make this attack more accessible than ever.

Finally, I might be wrong about this but I suspect this presentation may deserve some credit for finally persuading Amazon to think about [securing their EC2 metadata endpoint](https://portswigger.net/daily-swig/aws-bolsters-security-to-defend-against-ssrf-attacks).

### **2\. Cross-Site Leaks**

Cross-site leaks have been a long time coming. First documented [over a decade ago](https://scarybeastsecurity.blogspot.com/2009/12/cross-domain-search-timing.html), and creeping into our [top 10 last year](https://portswigger.net/research/top-10-web-hacking-techniques-of-2018#10), it's in 2019 that awareness of this attack class and its sheer number of crazy variations exploded.

It's hard to apportion credit at such a scale but we clearly owe thanks to [Eduardo Vela](https://twitter.com/sirdarckcat)'s [succinct introduction](https://sirdarckcat.blogspot.com/2019/03/http-cache-cross-site-leaks.html) to the concept with a novel technique, the collaborative effort to build a public [list of known XS-Leak vectors](https://github.com/xsleaks/xsleaks/wiki/Browser-Side-Channels), and researchers applying the XS-Leaks technique to [great effect](https://medium.com/@terjanq/massive-xs-search-over-multiple-google-products-416e50dd2ec6).

XS-Leaks have already had a lasting impact on the web security landscape, as they played a major role in the death of browser XSS filters. Block-mode XSS filtering was a major source of XS-Leak vectors, and this combined with [even worse issues with filter-mode](https://medium.com/bugbountywriteup/xss-auditor-the-protector-of-unprotected-f900a5e15b7b) to persuade Edge and later Chrome to both discard their filters in a victory for web security and a disaster for web security researchers alike.

### **1\. Cached and Confused: Web Cache Deception in the Wild**

In [this academic whitepaper](https://sajjadium.github.io/files/usenixsec2020wcd_paper.pdf), [Sajjad Arshad](https://twitter.com/sajjadium) et al take Omer Gil's [Web Cache Deception](https://www.youtube.com/watch?v=mroq9eHFOIU) technique (which premiered at #2 in our top 10 back in 2017), and share a systematic exploration of [Web Cache Deception](https://portswigger.net/web-security/web-cache-deception) vulnerabilities across the Alexa Top 5000 websites.

For legal reasons, most offensive security research is conducted during professional audits or on websites with bug bounty programs, but through careful ethical footwork this research offers a glimpse into the state of security on the wider web. With the help of a well-crafted methodology that could easily be adapted for other techniques, they prove that Web Cache Deception is still a prevalent threat.

Aside from the methodology, the other key innovation is the introduction of five novel path confusion techniques which expand the number of vulnerable websites. They also do a better job of documenting web-caching provider's caching behaviour than many providers themselves. Overall, this is a superb example of the community taking existing research in a new direction, and a well deserved number one!

### Conclusion

We saw a particularly strong set of nominations this year, so many excellent pieces of research didn't make it into the top 10. As such, I recommend checking out the [full nomination list](https://portswigger.net/research/top-10-web-hacking-techniques-of-2019-nominations-open). For those interested in getting access to 2020 research as soon as it's released, we recently created the [r/websecurityresearch](https://www.reddit.com/r/websecurityresearch/) subreddit and [@PortSwiggerRes](https://twitter.com/portswiggerres) Twitter accounts to promote notable research. You can also find past year's top 10 lists here:

[2018](https://portswigger.net/research/top-10-web-hacking-techniques-of-2018), [2017](https://portswigger.net/research/top-10-web-hacking-techniques-of-2017), [2015](https://web.archive.org/web/20191215103809/https://www.whitehatsec.com/blog/top-10-web-hacking-techniques-of-2015/), [2014](https://web.archive.org/web/20200313124651/https://www.whitehatsec.com/blog/top-10-web-hacking-techniques-of-2014//), [2013](https://web.archive.org/web/20160507023636/https://www.whitehatsec.com/blog/top-10-web-hacking-techniques-2013/), [2012](https://web.archive.org/web/20170903113359/https://www.whitehatsec.com/blog/top-ten-web-hacking-techniques-of-2012/), [2011](https://web.archive.org/web/20170831160914/https://www.whitehatsec.com/blog/vote-now-top-ten-web-hacking-techniques-of-2011/), [2010](http://jeremiahgrossman.blogspot.com/2011/01/top-ten-web-hacking-techniques-of-2010.html), [2009](http://jeremiahgrossman.blogspot.com/2010/01/top-ten-web-hacking-techniques-of-2009.html), [2008](http://jeremiahgrossman.blogspot.com/2009/02/top-ten-web-hacking-techniques-of-2008.html), [2007](http://jeremiahgrossman.blogspot.com/2008/01/top-ten-web-hacks-of-2007-official.html), [2006](http://jeremiahgrossman.blogspot.com/2006/12/top-10-web-hacks-of-2006.html).

Year after year we see great research comes from building on other people's ideas, so we'd like to thank everyone who takes the time to publish their findings, whether nominated or not. Finally, we'd like to thank the wider community for your enthusiastic participation. Without your nominations and votes, this wouldn't be possible.

Till next year!

[top-10-techniques](https://portswigger.net/research/top-10-techniques) [Top 10 Hacking Techniques](https://portswigger.net/research/top-10-web-hacking-techniques)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[05 February 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) [06 January 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025-nominations-open) [04 February 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024) [08 January 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024-nominations-open)