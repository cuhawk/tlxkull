---
source: portswigger-research
source_url: https://portswigger.net/research/bypassing-firefoxs-html-sanitizer-api
title: "Bypassing Firefox's HTML Sanitizer API | PortSwigger Research"
published: 2022-06-29T14:00:00
description: "The HTML Sanitizer is a great new API that allows web developers to filter untrusted HTML natively in the browser rather than use a JavaScript library such as DOM Purify. Microsoft created a similar A"
---

# Bypassing Firefox's HTML Sanitizer API

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Wednesday, 29 June 2022 at 14:00 UTC

- **Updated:** Monday, 4 July 2022 at 07:46 UTC


![A picture of code flowing through a filter](https://portswigger.net/cms/images/91/4b/e6a7-article-firefox_html_sanitizer_blog_article.png)

The [HTML Sanitizer](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Sanitizer_API) is a great new API that allows web developers to filter untrusted HTML natively in the browser rather than use a JavaScript library such as [DOM Purify](https://github.com/cure53/DOMPurify). Microsoft created a similar API called toStaticHTML in 2008 for Internet Explorer but it was [riddled](https://web.archive.org/web/20101025032152/http://archives.neohapsis.com/archives/fulldisclosure/2010-08/0179.html) with [holes](https://blog.watchfire.com/wfblog/2012/07/tostatichtml-the-second-encounter-cve-2012-1858-html-sanitizing-information-disclosure-introduction-t.html) and wasn't widely adopted or standardised. Hopefully the Sanitizer will have more success.

The advantages of using a native browser feature are obvious; if the browser is used to filter HTML then it can use its own parsers to ensure the untrusted HTML is filtered consistently.

However, there can be a disagreement in what the Sanitizer thinks is safe compared to the actual reality of the filtered HTML. One such example is with SVG "use" elements; we've [shown in the past that "use" elements can be used to execute arbitrary JavaScript](https://portswigger.net/research/new-xss-vectors) by using data URLs.

The Sanitizer prevents these attacks by blocking SVG imports using both data URLs and relative URLs. However, it allowed SVG imports from absolute URLs, provided they were the same origin. This means if the target site allowed a file upload of an SVG file and protected it by forcing a download using Content-Disposition: attachment, it would still be possible to execute arbitrary JavaScript.

`<svg><use href="//portswigger-labs.net/use_element/upload.php#x"/></svg>`

[Proof of concept](https://portswigger-labs.net/xss/xss.php?x=%3Csvg%3E%3Cuse%20href=%22//portswigger-labs.net/use_element/upload.php%23x%22/%3E%3C/svg%3E)

Here's the result of the untrusted HTML being filtered incorrectly by the Sanitizer:

Input:

`<svg><use href="//portswigger-labs.net/use_element/upload.php#x" />`

Output:

`<div><svg><use href="//portswigger-labs.net/use_element/upload.php#x"></use></svg></div>`

### Conclusion

Browser APIs for sanitizing HTML are a good idea as the browser is in a better position to filter the HTML correctly however this doesn't mean they are a foolproof mechanism to prevent malicious HTML from sneaking past. As with any filter, a feature like this requires a large amount of testing to ensure correct filtering of malicious HTML.

### Note

Please note this is an experimental API and isn't widely supported yet.

### Timeline

2022-02-25 09:42 PST - Reported bug to Mozilla

2022-04-29 15:03 PDT - Fixed

2022-06-28  - Firefox 102.0 released

2022-06-29 15:00 PM GMT - Published this post

[XSS](https://portswigger.net/research/cross-site-scripting-research) [filter](https://portswigger.net/research/filter) [firefox](https://portswigger.net/research/firefox)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)