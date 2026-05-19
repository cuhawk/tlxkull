---
source: portswigger-research
source_url: https://portswigger.net/research/svg-animate-xss-vector
title: "SVG animate XSS vector | PortSwigger Research"
published: 2020-01-28T14:54:16
description: "As part of my recent research into obfuscating XSS payloads to bypass WAFs, I was looking at the SVG elements set, animate, animateTransform and animateMotion. I added a couple of known XSS vectors to"
---

# SVG animate XSS vector

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Tuesday, 28 January 2020 at 14:54 UTC

- **Updated:** Tuesday, 8 September 2020 at 12:22 UTC


As part of my recent research into obfuscating [XSS](https://portswigger.net/web-security/cross-site-scripting) payloads to bypass WAFs, I was looking at the SVG elements `set`, `animate`, `animateTransform` and `animateMotion`. I added a couple of known XSS vectors to the cheat sheet using those tags. Then focusing on the `animate` tag I found an interesting XSS vector using the `values` attribute. The `values` attribute lets you specify a number of values for an SVG animation separated by semi-colons:

`<svg><animate values="1;2;3" /></svg>`

I wondered if I could include a JavaScript URL in the middle of the values attribute - that might confuse a lot of WAFs looking for the JavaScript protocol. The problem was, if I didn't set a duration then the first value would always be shown and if I did set a duration then the URL would cycle through the values and therefore not always show the JavaScript URL. Looking at the SVG specification I noticed that there's a `keyTimes` attribute that allows you to control the pacing of the animation for each of the values. Using this with the `repeatCount` attribute would enable the animation to always show the JavaScript URL. Here is the final XSS vector:

`<svg><animate xlink:href=#xss attributeName=href dur=5s repeatCount=indefinite keytimes=0;0;1 values="https://portswigger.net?&semi;javascript:alert(1)&semi;0" /><a id=xss><text x=20 y=20>XSS</text></a>`

We have released an interactive XSS lab built around this technique in the [Web Security Academy](https://portswigger.net/web-security) so you can try it out for yourself:

[LAB\\
\\
SVG animate lab](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-event-handlers-and-href-attributes-blocked)

This vector will also shortly be integrated into our [XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet). Enjoy!

[Cross Site Scripting](https://portswigger.net/research/cross-site-scripting) [cheatsheet](https://portswigger.net/research/cheatsheet) [SVG](https://portswigger.net/research/svg) [vectors](https://portswigger.net/research/vectors)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**New crazy payloads in the URL Validation Bypass Cheat Sheet** 29 October 2024New crazy payloads in the URL Validation Bypass Cheat Sheet](https://portswigger.net/research/new-crazy-payloads-in-the-url-validation-bypass-cheat-sheet) [**Our favourite community contributions to the XSS cheat sheet** 03 October 2022Our favourite community contributions to the XSS cheat sheet](https://portswigger.net/research/our-favourite-community-contributions-to-the-xss-cheat-sheet) [**New XSS vectors** 20 April 2022New XSS vectors](https://portswigger.net/research/new-xss-vectors) [**DOM Clobbering strikes back** 06 February 2020DOM Clobbering strikes back](https://portswigger.net/research/dom-clobbering-strikes-back)