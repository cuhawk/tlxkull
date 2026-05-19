---
source: portswigger-research
source_url: https://portswigger.net/research/bypassing-web-cache-poisoning-countermeasures
title: "Bypassing Web Cache Poisoning Countermeasures | PortSwigger Research"
published: 2018-10-05T15:00:50
description: "Following my presentation and whitepaper on Web Cache Poisoning last month, various companies have deployed defences in an attempt to mitigate cache poisoning attacks. In this post I’ll take a look at"
---

# Bypassing Web Cache Poisoning Countermeasures

![James Kettle](https://portswigger.net/content/images/profiles/callout_james_kettle_112px.png)

### [James Kettle](https://portswigger.net/research/james-kettle)

Director of Research

[@albinowax](https://twitter.com/albinowax)

- **Published:** Friday, 5 October 2018 at 15:00 UTC

- **Updated:** Thursday, 29 September 2022 at 07:36 UTC


![](https://portswigger.net/cms/images/82/5d/3b6a23dba4a0-article-cache-poisoning-mitigation-article.png)

Following my [presentation](https://www.youtube.com/watch?v=iSDoUGjfW3Q) and [whitepaper](https://portswigger.net/blog/practical-web-cache-poisoning) on [Web Cache Poisoning](https://portswigger.net/web-security/web-cache-poisoning) last month, various companies have deployed defences in an attempt to mitigate cache poisoning attacks. In this post I’ll take a look at some common weaknesses that can be used to bypass them.

The research provoked responses from several major caching vendors. Akamai posted a minimal response, confusingly [citing mitigations](https://blogs.akamai.com/2018/08/on-cache-poisoning.html) for [Web Cache Deception](https://portswigger.net/web-security/web-cache-deception) which do virtually nothing to prevent Web Cache Poisoning. Fastly published a [security advisory](https://www.fastly.com/security-advisories/cache-poisoning-leveraging-various-x-headers) with detailed advice on mitigation, and Cloudflare took things one step further and deployed global mitigations, detailed in a blog post titled [How Cloudflare protects customers from cache poisoning](https://blog.cloudflare.com/cache-poisoning-protection/).

Let’s take a closer look at the two defences deployed by Cloudflare. The first was to add a rule to their WAF to block XSS-friendly characters like < in certain headers used in my research, like X-Forwarded-Host:

`GET / HTTP/1.1
Host: wafproxy.net
X-Forwarded-Host: xss<

HTTP/1.1 403 Forbidden

Attention Required!
`

This makes it harder to directly get [XSS](https://portswigger.net/web-security/cross-site-scripting) via cache poisoning using these headers but, as they note, still leaves some applications vulnerable as such characters aren't always required for an exploit. The second, more robust mitigation was to add these headers into their default cache key, theoretically making it impossible to use those headers for cache poisoning:

`GET / HTTP/1.1
Host: wafproxy.net
X-Forwarded-Host: evil.net

HTTP/1.1 200 OK

<a href="https://evil.net/"
`

Cache key before mitigation: https://wafproxy.net/

Cache key after mitigation: https://wafproxy.net/\|evil.net

Unfortunately there’s a critical implementation flaw in both of these defences, meaning that they can be completely bypassed. The stage is set by a small optimisation that means Cloudflare don’t add the X-Forwarded-Host header to the cache key if it matches the Host header:

`GET / HTTP/1.1
Host: wafproxy.net
X-Forwarded-Host: wafproxy.net
`Cache key after mitigation: https://wafproxy.net/

The fatal flaw is that Cloudflare only looks at the first instance of each header, so an attacker can provide a duplicate header, with the first instance being harmless and the second containing the payload. When a backend server handles such a request, it’ll typically concatenate the two header values using a comma.

`GET / HTTP/1.1
Host: wafproxy.net
X-Forwarded-Host: wafproxy.net
X-Forwarded-Host: evil.net"/><script...

HTTP/1.1 200 OK

<a href="https://wafproxy.net, evil.net"/><script...
`Cache key after mitigation: https://wafproxy.net/

I reported this issue to Cloudflare last week so it’ll probably be patched shortly and the cache key bypass has now been patched. Although their mitigation didn’t initially work out, they deserve credit for being the only vendor that tried technical mitigations, and now my bypass is patched I think they're the vendor with the most secure default configuration. That said, it’s worth noting that the mitigation won’t ever make sites hosted on Cloudflare immune to cache poisoning in general - it only prevents attacks using the most popular headers.

Individual companies’ attempts to patch can go wrong, too. One common mistake is to detect a cache poisoning attack and block it with a response that’s cacheable. This effectively creates a denial of service issue. This hazard can also be caused by WAFs - for example www.tesla.com uses a WAF that blocks requests that contain the string ‘burpcollaborator.net’ in any header:

`GET /en_GB/roadster HTTP/1.1
Host: www.tesla.com
Any-Header: burpcollaborator.net

HTTP/1.1 403 Forbidden

Access Denied. Please contact waf@tesla.com
`

After this attack, anyone that tried to access that page would find themselves blocked:

`GET /en_GB/roadster HTTP/1.1
Host: www.tesla.com

HTTP/1.1 403 Forbidden

Access Denied. Please contact waf@tesla.com
`

The other mistake I’ve seen occurs when companies try to patch the framework that’s introducing the vulnerability, but underestimate the full potential of the header. For example, one target whitelisted acceptable values of the request.host variable, which is populated by the X-Forwarded-Host header. However, they didn’t notice that this header can also populate request.port, enabling a persistent denial of service:

`GET / HTTP/1.1
Host: redacted.com
X-Forwarded-Host: redacted.com:123

HTTP/1.1 301 Moved Permanently
Location: https://redacted.com:123/
`

Ultimately, patching web cache poisoning on an ad-hoc basis can be tricky and the authors of web frameworks are the best placed people to resolve the most common types. Frameworks like Django and Flask have disabled support for these headers over recent years, and others like Ruby on Rails have been [repeatedly warned](https://github.com/rails/rails/issues/29893) but have only recently started to move toward deploying a fix.

Finally, I should mention I’ve pushed some substantial updates to [Param Miner](https://github.com/PortSwigger/param-miner) which will be released on Monday, notably including disabling the static ‘fcbz’ cache buster by default as it was breaking certain sites. This means that when using your browser or the Repeater to attempt cache poisoning, you’ll need to specify your own cache buster manually, or risk accidentally affecting other visitors.

Good luck and stay safe!

[web cache poisoning](https://portswigger.net/research/web-cache-poisoning)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Gotta cache 'em all: bending the rules of web cache exploitation** 08 August 2024Gotta cache 'em all: bending the rules of web cache exploitation](https://portswigger.net/research/gotta-cache-em-all) [**Web Cache Entanglement** 05 August 2020Web Cache Entanglement](https://portswigger.net/research/web-cache-entanglement) [**Responsible denial of service with web cache poisoning** 24 October 2019Responsible denial of service with web cache poisoning](https://portswigger.net/research/responsible-denial-of-service-with-web-cache-poisoning) [**Practical Web Cache Poisoning**Redefining 'unexploitable'09 August 2018Practical Web Cache PoisoningRedefining 'unexploitable'](https://portswigger.net/research/practical-web-cache-poisoning)