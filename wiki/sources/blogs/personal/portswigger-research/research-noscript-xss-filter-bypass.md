---
source: portswigger-research
source_url: https://portswigger.net/research/noscript-xss-filter-bypass
title: "Noscript XSS filter bypass | PortSwigger Research"
published: 2015-07-28T13:47:00
description: "I thought I'd take a look at the Noscript's XSS filter and see if I could come up with a bypass. The filter is pretty impressive, it was tough to find one. I noticed that it allows function calls to u"
---

# Noscript XSS filter bypass

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Tuesday, 28 July 2015 at 13:47 UTC

- **Updated:** Friday, 14 June 2019 at 12:00 UTC


I thought I'd take a look at the Noscript's [XSS](https://portswigger.net/web-security/cross-site-scripting) filter and see if I could come up with a bypass. The filter is pretty impressive, it was tough to find one. I noticed that it allows function calls to user defined functions such as a, so a vector of ',a(1),' would work fine. This isn't exploitable since you need a function on the page that does something dangerous with the arguments but it gave me a clue how to get round the filter. It was time to fire up Hackvertor and have a look which methods might have been forgotten.

I inspected an object literal and found \_\_defineSetter\_\_. This would work on window since every object has the method. [Define setter](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/__defineSetter__) allows you to set a property with the first argument and the function you want to call in the second argument.

Because \_\_defineSetter\_\_ is a method of the window object you do not need to specify window when calling it. I tried an injection of ',\_\_defineSetter\_\_('x',alert),x=1,' and it worked perfectly bypassing Noscript's XSS filter check in script context. The output of the page would look like this:

`<script>x = '',__defineSetter__('x',alert),x=1,'';</script>`

Define setter is called on window with a property of x, alert is then called when an assignment of x occurs with an argument of 1.

You can also call arbitrary code by changing the alert to eval and the assignment to name. Using name as the assignment allows you to send a payload across domains using the window.name property. Usually you use an iframe with a name attribute of the payload you wish to execute then reuse that payload using the "name" property in the injected site. An example of that is below:

`<iframe name=alert(1) src="//somedomain?x=',__defineSetter__('x',eval),x=name,'"></iframe>`

The filter has now been patched and the vector no longer works.

Visit our Web Security Academy to [learn more about cross-site scripting (XSS)](https://portswigger.net/web-security/cross-site-scripting)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[05 February 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) [06 January 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025-nominations-open) [**The Fragile Lock:**\\
Novel Bypasses For SAML Authentication 10 December 2025The Fragile Lock:Novel Bypasses For SAML Authentication](https://portswigger.net/research/the-fragile-lock) [**Introducing HTTP Anomaly Rank** 11 November 2025Introducing HTTP Anomaly Rank](https://portswigger.net/research/introducing-http-anomaly-rank)