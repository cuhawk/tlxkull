---
source: portswigger-research
source_url: https://portswigger.net/research/bypassing-character-blocklists-with-unicode-overflows
title: "Bypassing character blocklists with unicode overflows | PortSwigger Research"
published: 2025-01-28T13:58:28
description: "Unicode codepoint truncation - also called a Unicode overflow attack - happens when a server tries to store a Unicode character in a single byte. Because the maximum value of a byte is 255, an overflo"
---

# Bypassing character blocklists with unicode overflows

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Tuesday, 28 January 2025 at 13:58 UTC

- **Updated:** Wednesday, 29 January 2025 at 08:10 UTC


![A code snippet showing CRLF injection bypass using Unicode overflows](https://portswigger.net/cms/images/4f/b7/81e7-article-bypass-character-blocklists-with-unicode-overflows.png)

[Unicode codepoint truncation](https://docs.google.com/presentation/d/1jW0o1YO3FNXlXVkAziM_wSGQqRdLP2kmfoBb6mF1bGY/edit#slide=id.g2f056d28156_1_250) \- also called a [Unicode overflow](https://portswigger.net/research/splitting-the-email-atom#unicode-overflows) attack - happens when a server tries to store a Unicode character in a single byte. Because the maximum value of a byte is 255, an overflow can be crafted to produce a specific ASCII character.

Here are a couple of examples that end with 0x41 which represents A:

`0x4e41 0x4f41 0x5041 0x5141`

If you perform a modulus operation on the code points above you'll see they produce the character "A":

`String.fromCodePoint(0x4e41 % 256, 0x4f41 % 256, 0x5041 % 256, 0x5141 % 256) // AAAA`

It's not only bytes that have this problem, JavaScript itself has a codepoint overflow in the `fromCharCode()` method. This method allows you to generate a character between 0-0xffff but if you go above this range it will be overflowed and produce a character by the overflow amount.

`String.fromCharCode(0x10000 + 0x31, 0x10000 + 0x33, 0x10000 + 0x33, 0x10000 + 0x37)

//1337`

The above code uses the hex value 0x10000 which is one above the maximum codepoint supported by the `fromCharCode()` method. Then I add an overflow to it, in this case the hex for each codepoint of 1337. Then when the overflow occurs it produces 1337.

This is being actively used by [bug bounty hunters](https://infosecwriteups.com/6000-with-microsoft-hall-of-fame-microsoft-firewall-bypass-crlf-to-xss-microsoft-bug-bounty-8f6615c47922) and was brought to our attention by [Ryan Barnett](https://x.com/ryancbarnett). For everyone's convenience we've added these truncation attacks to [ActiveScan++](https://portswigger.net/bappstore/3123d5b5f25c4128894d97ea1acc4976), thanks to Ryan for the PR and we've created a [Hackvertor tag](https://hackvertor.co.uk/urls/20) to help reproduce the characters. Big thanks to my colleague [Zak](https://x.com/d4d89704243) who I investigated this with. We've also updated the [Shazzer unicode table](https://shazzer.co.uk/unicode-table?fromTo=0x41&highlightsFromTo=) to display potential unicode truncation characters.

![Unicode table show unicode truncation characters](https://portswigger.net/cms/images/4e/e4/3623-article-codepoint-overflow.png)

[micropost](https://portswigger.net/research/micropost) [Unicode](https://portswigger.net/research/unicode)

[Back to all articles](https://portswigger.net/research/articles)