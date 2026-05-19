---
source: portswigger-research
source_url: https://portswigger.net/research/xss-in-hidden-input-fields
title: "XSS in hidden input fields | PortSwigger Research"
published: 2015-11-16T11:25:00
description: "At PortSwigger, we regularly run pre-release builds of Burp Suite against an internal testbed of popular web applications to make sure it's behaving properly. Whilst doing this recently, Liam found a"
---

# XSS in hidden input fields

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Monday, 16 November 2015 at 11:25 UTC

- **Updated:** Friday, 14 June 2019 at 12:03 UTC


![XSS hidden input fields](https://portswigger.net/cms/images/6e/96/b9ffb03974c5-article-xss-hidden-input-field-article.png)

At PortSwigger, we regularly run pre-release builds of Burp Suite against an internal testbed of popular web applications to make sure it's behaving properly. Whilst doing this recently, [Liam](https://twitter.com/MetalF0X) found a [Cross-Site Scripting](https://portswigger.net/web-security/cross-site-scripting) ( [XSS](https://portswigger.net/web-security/cross-site-scripting)) vulnerability in \[REDACTED\], inside a hidden input element:

`<input type="hidden" name="redacted" value="default" injection="xss" />`

XSS in hidden inputs is [frequently very difficult to exploit](https://web.archive.org/web/20130724031616/http://sla.ckers.org/forum/read.php?2,17217) because typical JavaScript events like onmouseover and onfocus can't be triggered due to the element being invisible.

I decided to investigate further to see if it was possible to exploit this on a modern browser. I tried a bunch of stuff like autofocus, CSS tricks and other stuff. Eventually I thought about access keys and wondered if the onclick event would be called on the hidden input when it activated via an access key. It most certainly does on Firefox! This means we can execute an XSS payload inside a hidden attribute, provided you can persuade the victim into pressing the key combination. On Firefox Windows/Linux the key combination is ALT+SHIFT+X and on OS X it is CTRL+ALT+X. You can specify a different key combination using a different key in the access key attribute. Here is the vector:

`<input type="hidden" accesskey="X" onclick="alert(1)">`

This vector isn't ideal because it involves some user interaction, but it's vastly better than expression() which only works on IE<=9. Please note if your reflection is repeated then the key combination will fail. A workaround is to then inject another attribute that breaks the second reflection. e.g. " accesskey="x" onclick="alert(1)" x='

Note: We've reported this vulnerability to the application's security team. However, they haven't responded in any way after 12 days and a couple of emails. We wanted to make people aware of this particular technique, but we won't be naming the vulnerable application concerned until a patch is available.

This [isn't the first time](https://twitter.com/LukasReschke/status/596304014502944769) that [Burp Scanner](https://portswigger.net/vulnerability-scanner/) has unearthed a vulnerability in an extremely popular web application, and we doubt it will be the last.

### Update - Now works on Chrome and link/meta and any other elements

This technique now works in Chrome! It also works in link elements that means previously unexploitable XSS bugs in link elements where you only control attributes can be exploited using this technique. For example you might have a link element with a rel attribute on canonical, if you inject the accesskey attribute with an onclick event then you have XSS.

`<link rel="canonical" accesskey="X" onclick="alert(1)" />`

[Poc using link elements](http://portswigger-labs.net/link/) (Press ALT+SHIFT+X on Windows) (CTRL+ALT+X on OS X)

Visit our Web Security Academy to [learn more about cross-site scripting (XSS)](https://portswigger.net/web-security/cross-site-scripting)

[XSS](https://portswigger.net/research/cross-site-scripting-research)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)