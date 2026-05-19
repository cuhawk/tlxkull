---
source: portswigger-research
source_url: https://portswigger.net/research/abusing-jquery-for-css-powered-timing-attacks
title: "Abusing jQuery for CSS powered timing attacks | PortSwigger Research"
published: 2019-05-22T13:15:44
description: "Arthur Saftnes did some quite awesome research last year on timing attacks with jQuery CSS selectors, in fact it was probably my favourite blog post from last year. It's a common design pattern for we"
---

# Abusing jQuery for CSS powered timing attacks

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Wednesday, 22 May 2019 at 13:15 UTC

- **Updated:** Wednesday, 29 May 2019 at 12:10 UTC


![CSS timing attack](https://portswigger.net/cms/images/d1/57/598f88cf6fd5-article-blog_timing_attack_article.jpg)

[Arthur Saftnes](https://twitter.com/ArthurSaftnes) did some quite awesome research last year on [timing attacks with jQuery CSS selectors](https://blog.sheddow.xyz/css-timing-attack/), in fact it was probably my favourite blog post from last year.

It's a common design pattern for websites to pass location.hash to the [jQuery $ function](https://api.jquery.com/jQuery/):

`$(location.hash);`

The hash may be attacker controlled, and this used to cause [XSS](https://portswigger.net/web-security/cross-site-scripting), but jQuery patched that many years ago. Arthur found that this pattern can still theoretically be exploited using a timing attack. You can repeatedly invoke  jQuery's [:has selector](https://api.jquery.com/has-selector/) and measure the performance impact to infer content from the target page. This turns these situations from unexploitable XSS into reading pretty much any input value.

I decided to follow up on this research to find real world vulnerabilities using this technique. I first modified [Burp's dynamic analysis](https://portswigger.net/blog/dynamic-analysis-of-javascript) to look for jQuery selectors being executed inside `hashchange` events, and scanned a bunch of websites. The reason I was looking for `hashchange` events is a limitation of the attack; in order to measure the performance impact you need to repeatedly change the hash to run a binary search of all possible characters which is only possible when a `hashchange` event fires. Another limitation of the original technique posted was the fact that you need the site to URL decode the hash as most modern browsers now URL encode it - but I found a way around this.

I found a few bug bounty sites that did use `location.hash` with the jQuery `$` function inside a `hashchange` event, but most of the sites found didn't really have any interesting data to steal. There was one exception though, Red Hat was using a jQuery selector inside a `hashchange` event and had account functionality. Looking at the site it didn't have any inputs to steal data from but it did display your full name when logged on. Arthur's original attack used [CSS attribute selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/Attribute_selectors) but the full name was not inside any input element so I couldn't use them.

I looked through all the jQuery CSS selectors and found the [:contains](https://api.jquery.com/contains-selector/) selector which finds elements that contain the string specified. Unfortunately :contains doesn't allow you to look at the start or end of the string so I needed another way of extracting the value. I thought about using the space as an anchor point to extract the first name but the problem is that on Firefox the space will be URL encoded. Fortunately, backslash isn't URL encoded so I could use CSS hex escapes. At first I tried `\20` but this would break the selector because the next character would continue the hex escape, but if I padded the escape with zeros this would ensure the correct CSS escape would be used.  I modified Arthur's code to improve the make\_selector function to use spaces:

`function make_selector(prefix, characters, firstNameFlag, firstName) {
return characters.split("").map(c => !firstNameFlag ? SLOW_SELECTOR +
SELECTOR_TEMPLATE.replace('{}',  c + prefix + '\\000020') : SLOW_SELECTOR +
SELECTOR_TEMPLATE.replace("{}",  prefix.replace(/ /, '\\000020') + c))
                    .join(",");
}`

The code above uses the hex encoded space to scan for the name backwards. I use the firstNameFlag to decide if it's the first name or the second name, when the uppercase letter is found of the first name the flag is set and then it starts matching the second name scanning forwards but this time using the first name as the prefix and space.

`if(!firstNameFlag && /[A-Z]/.test(name)) {
firstNameFlag = true;
name += ' ';
backtracks = 0;
continue;
}`

The other problem I encountered was the fact you can't use a space in the actual selector because it gets URL encoded, and hex escapes won't work here. I spent a lot of time trying to construct a selector that didn't have spaces and still had a measurable performance impact. Finally I came up with the following selector:

`const SLOW_SELECTOR="*:has(*:has(*):parent:has(*):parent:has(*):parent:has(*):parent:has(*)):parent:has(";
const SELECTOR_TEMPLATE=".account-user:contains('{}'))";`

This causes a performance impact but is much slower than using spaces with the [CSS descendant selector](https://developer.mozilla.org/en-US/docs/Web/CSS/Descendant_combinator). Then my next issue was how to determine that you've reached the end of the name. Like I said before the :contains selector offers no way of looking at the end of the string. So the only way I came up with was to look for 6 backtracks in a row.

The vulnerability has now been fixed but I'll share the original PoC below so you can see the code I used:

[Firefox access.redhat.com jQuery selector PoC](http://portswigger-labs.net/redhat_ZnF5463PdXj/poc.html)

I also recorded a video so you can see it in action:

Video tags are not supported by your browser.

[XSS](https://portswigger.net/research/cross-site-scripting-research)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)