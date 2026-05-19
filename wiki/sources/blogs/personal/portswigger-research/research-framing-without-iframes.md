---
source: portswigger-research
source_url: https://portswigger.net/research/framing-without-iframes
title: "Framing without iframes | PortSwigger Research"
published: 2022-07-27T14:57:48
description: "Whilst testing for XSS vectors, we found some new ways of framing a web site that don't use the iframe element. Naturally, we've updated our XSS cheat sheet to document them. We discovered that Chrome"
---

# Framing without iframes

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Wednesday, 27 July 2022 at 14:57 UTC

- **Updated:** Wednesday, 27 July 2022 at 14:57 UTC


![Illustration of UI windows showing the code in the article](https://portswigger.net/cms/images/11/fe/4a8b-article-framing-without-iframes-article.jpg)

Whilst testing for XSS vectors, we found some new ways of framing a web site that don't use the iframe element. Naturally, we've updated our [XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) to document them. We discovered that Chrome allows you to [use param tags to change the URL](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet#object-tag-supports-param-url) of an object tag much like an iframe:

`<object width=1000 height=1000 type=text/html><param name=url value="https://portswigger-labs.net">
<object width=1000 height=1000 type=text/html><param name=code value="https://portswigger-labs.net">
<object width=1000 height=1000 type=text/html><param name=movie value="https://portswigger-labs.net">
<object width=1000 height=1000 type=text/html><param name=src value="https://portswigger-labs.net">`

In addition Chrome & webkit allow you to [use the "code" attribute in an embed tag](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet#embed-supports-code-attribute) to reference an external URL:

`<embed code=https://portswigger-labs.net width=500 height=500 type=text/html>`

We tried exploiting these features for XSS but unfortunately JavaScript URLs don't work and although URLs with a data: protocol work they all execute from a null origin making them useless for XSS. Still, new ways of framing are always useful to chain other attacks or maybe even bypass [CSP](https://portswigger.net/web-security/cross-site-scripting/content-security-policy).

### Firefox and tabindex

In other XSS news it was [reported to us](https://twitter.com/bxmbn/status/1547254229789773824) that Firefox now exhibits the same behaviour as Chrome when it comes to the tabindex attributes. This makes events such as [onfocus](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet#onfocus) fire automatically on Firefox, when previously they didn't. Hurray for attack surface expansion! The cheat sheet has now been updated to reflect this change.

### Search interface

Finally, we had a request for a search interface for the [XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet), this would make it easier to find vectors when a WAF is filtering certain attributes or tags. So we've added one that allows you to search tags, events, and the code, using regular expressions.

[XSS cheat sheet](https://portswigger.net/research/xss-cheat-sheet) [XSS](https://portswigger.net/research/cross-site-scripting-research) [iframes](https://portswigger.net/research/iframes)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)