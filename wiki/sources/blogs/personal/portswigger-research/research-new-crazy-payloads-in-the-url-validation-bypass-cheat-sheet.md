---
source: portswigger-research
source_url: https://portswigger.net/research/new-crazy-payloads-in-the-url-validation-bypass-cheat-sheet
title: "New crazy payloads in the URL Validation Bypass Cheat Sheet | PortSwigger Research"
published: 2024-10-29T13:59:13
description: "The strength of our URL Validation Bypass Cheat Sheet lies in the contributions from the web security community, and today’s update is no exception. We are excited to introduce a new and improved IP a"
---

# New crazy payloads in the URL Validation Bypass Cheat Sheet

![Zakhar Fedotkin](https://portswigger.net/content/images/profiles/callout_zakhar_fedotkin_114px.png)

### [Zakhar Fedotkin](https://portswigger.net/research/zakhar-fedotkin)

Researcher

[@zakfedotkin](https://twitter.com/zakfedotkin)

- **Published:** Tuesday, 29 October 2024 at 13:59 UTC

- **Updated:** Friday, 22 November 2024 at 09:06 UTC


![URL validation bypass cheat sheet](https://portswigger.net/cms/images/64/c6/9fed-article-81a7457a-352e-4be5-a489-adfa890fc960.png)The strength of our [URL Validation Bypass Cheat Sheet](https://portswigger.net/url-cheat-sheet) lies in the
contributions from the web security community, and today’s update is no
exception. We are excited to introduce a new and improved IP address
calculator, inspired by [@e1abrador's](https://x.com/e1abrador) [Encode IP Burp Suite Extension](https://github.com/PortSwigger/encode-ip/tree/main)
and many more.

## New IP validation bypass techniques

In addition to the existing ways of representing an IPv4 address, we’ve
added the following new formats, supported by Chrome, Firefox, Safari. For example, the cloud metadata IP address [169.254.169.254](https://portswigger.net/url-cheat-sheet#id=0ccb496127f4b822d7284638041456c0cf9903a9) can be represented in the following ways:

- 169.254.43518
       Partial Decimal (Class B) format combines the third and
fourth parts of the IP address into a decimal number

- 169.16689662
       Partial Decimal (Class A) format combines the second,
third, and fourth parts of the IP address

- 0xA9.254.0251.0376
       Mixed Encodings: each segment of the IP address can
be presented in different formats: hexadecimal, decimal, or octal. To
keep our tool efficient, we don’t generate all possible combinations.
Instead, we convert the first segment to hexadecimal, the second to
decimal, and the last two segments to octal


The cheat sheet now also supports IPv6 addresses. When a valid IPv6 address
is entered into the attacker’s hostname, the wordlist will be updated with
the expanded form of the address. If the IPv6 address contains an embedded
IPv4 address, the cheat sheet will extract it and generate all the
previously mentioned formats. This behaviour can be disabled in the advanced
settings.

Additionally, you can encode the resulting IP formats using special
encodings like Circled Latin letters and numbers, Fullwidth Forms, or even
Seven-segment display characters. To apply these, open the Advanced
settings, go to Normalization settings, and select one or more encoding
options.

## Userinfo parsing discrepancies

We’ve added an intriguing new payload to our cheat sheet that targets
discrepancies in userinfo parsing, submitted by [@SeanPesce](https://x.com/SeanPesce):

- [https://example.com\[@attacker.com](https://portswigger.net/url-cheat-sheet#id=1da2f627d702248b9e61cc23912d2c729e52f878)\
\
The “left square bracket” character `[` in the userinfo segment can cause Spring’s\
UriComponentsBuilder to return a hostname value that differs from how major\
browsers interpret it. This discrepancy can potentially lead to\
vulnerabilities such as open redirects or [SSRF](https://portswigger.net/web-security/ssrf). While testing this payload\
with our cheat sheet, I was also able to reproduce a separate\
[exploit](https://portswigger.net/url-cheat-sheet#id=8372598e5b45fc427bfec93fddd1c57a48a001a7)\
that was patched in the same\
[update](https://github.com/spring-projects/spring-framework/commit/297cbae2990e1413537c55845a7e0ea0ffd9f9bb). This is a perfect example of how our URL Validation Bypass Cheat Sheet\
can be used to identify real-world vulnerabilities.\
\
## CORS validation bypass cheat sheet update\
\
We’ve recently updated our [CORS](https://portswigger.net/web-security/cors) Bypass Cheat Sheet with new techniques,\
including an edge case related to localhost regex implementations and\
Safari-specific domain splitting attacks, submitted by [@t0xodile](https://x.com/t0xodile). These updates address scenarios\
where attackers can manipulate domains using special characters to bypass\
validation checks. Examples include:\
\
- [https://example.com.{.web-attacker.com/](https://portswigger.net/url-cheat-sheet#id=8e46533db2e6e27f630a1ce5716eb835ecff1159)\
- [https://example.com.}.web-attacker.com/](https://portswigger.net/url-cheat-sheet#id=d0796bf59bf4fbccad4bbd07e87d722b5cba0b11)\
- [https://example.com.\`.web-attacker.com/](https://portswigger.net/url-cheat-sheet#id=d2e1de8bc41c3353f79681994c291b53899445c4)\
\
Make sure to follow us on X (formerly Twitter)\
[@PortSwiggerRes](https://x.com/portswiggerres) to stay informed\
about our latest updates and new attack techniques.\
\
A big thanks to the web security community for continuing to keep the URL\
Validation Bypass Cheat Sheet up to date with the latest techniques. If\
you’d like to contribute, feel free to raise an\
[issue](https://github.com/PortSwigger/url-cheatsheet-data/issues)\
or submit a\
[PR](https://github.com/PortSwigger/url-cheatsheet-data/pulls).\
\
[URL cheat sheet](https://portswigger.net/research/url-cheat-sheet) [SSRF](https://portswigger.net/research/ssrf) [cheatsheet](https://portswigger.net/research/cheatsheet)\
\
[Back to all articles](https://portswigger.net/research/articles)\
\
## Related Research\
\
[**Introducing the URL validation bypass cheat sheet** 03 September 2024Introducing the URL validation bypass cheat sheet](https://portswigger.net/research/introducing-the-url-validation-bypass-cheat-sheet) [**Listen to the whispers: web timing attacks that actually work** 07 August 2024Listen to the whispers: web timing attacks that actually work](https://portswigger.net/research/listen-to-the-whispers-web-timing-attacks-that-actually-work) [**SVG animate XSS vector** 28 January 2020SVG animate XSS vector](https://portswigger.net/research/svg-animate-xss-vector) [**One XSS cheatsheet to rule them all** 26 September 2019One XSS cheatsheet to rule them all](https://portswigger.net/research/one-xss-cheatsheet-to-rule-them-all)