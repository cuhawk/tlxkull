---
source: portswigger-research
source_url: https://portswigger.net/research/introducing-the-url-validation-bypass-cheat-sheet
title: "Introducing the URL validation bypass cheat sheet | PortSwigger Research"
published: 2024-09-03T14:52:12
description: "URL validation bypasses are the root cause of numerous vulnerabilities including many instances of SSRF, CORS misconfiguration, and open redirection. These work by using ambiguous URLs to trigger URL"
---

# Introducing the URL validation bypass cheat sheet

![Zakhar Fedotkin](https://portswigger.net/content/images/profiles/callout_zakhar_fedotkin_114px.png)

### [Zakhar Fedotkin](https://portswigger.net/research/zakhar-fedotkin)

Researcher

[@zakfedotkin](https://twitter.com/zakfedotkin)

- **Published:** Tuesday, 3 September 2024 at 14:52 UTC

- **Updated:** Thursday, 5 September 2024 at 12:36 UTC


![](https://portswigger.net/cms/images/ba/2f/b01a-article-087ffac4-bf9f-4653-8947-b5e52b536f4e.png)URL validation bypasses are the root cause of numerous vulnerabilities
including many instances of
[SSRF](https://portswigger.net/web-security/ssrf),
[CORS misconfiguration](https://portswigger.net/web-security/cors), and
[open redirection](https://portswigger.net/web-security/dom-based/open-redirection). These work by using ambiguous URLs to trigger URL parsing discrepancies
and bypass validation. However, many of these techniques are poorly
documented and overlooked as a result.

To address this, we wanted to create a cheat sheet that consolidates all
known payloads, saving you the time and effort of searching and gathering
information from across the Internet. Today, we're excited to introduce a
new tool designed to solve this problem:
[the URL Validation Bypass Cheat Sheet](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet).

We hope you find it useful! This is a frequently updated repository of all
known techniques, allowing you to quickly generate a wordlist that meets
your needs.

## How to get started

The URL Validation Bypass Cheat Sheet is a brand new interactive web
application that automatically adjusts its settings based on your context.
Currently, there are three contexts available:

- A fully qualified absolute URL - useful for a situation where URL is
used in a request query parameter for example. All payloads are designed
to be Burp Suite Intruder friendly, so you don't have to worry about the
correct encoding.

- Only hostname - direct input of the domain, such as in the Host header
value.

- [CORS](https://portswigger.net/web-security/cors) Origin - where the hostname is intended to be used in a valid
browser origin header.


Initially, the cheat sheet provides six types of payload wordlists. The
advanced settings allow you to select a specific wordlist or use all of them
simultaneously. Here's a brief overview of the most important ones:

- Domain Allow List Bypass: Designed for domain confusion attacks. You can
customize the testing domains by entering the allowed and attacker
domains accordingly.

- Fake Relative URLs: This includes the browser-valid absolute URLs that
might be incorrectly validated by client-side code.

- Loopback Address: This wordlist includes various representations of
IPv4, IPv6 addresses, and their normalizations.


## Encodings

The [URL Validation Cheat Sheet](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet) supports several types of string encoding:

- Intruder's Percent Encoding: This option encodes a payload string by
replacing certain characters with one to four escape sequences that
represent the UTF-8 encoding of the character. It excludes Burp Suite
Intruder's default characters and is enabled by default, making it easily
compatible with Burp Suite

- Everything: This option percent-encodes all characters except alphanumeric
ones

- The Special Chars option encodes everything except the following
characters: `["!","$","'","\"","(",")","*",",","-",".","/","\\",":",";","[","]","^","_","{","}","|","~"]`
- Unicode Escape: This option represents a payload string as a six-character
escape sequence `\uXXXX`, except for the following characters:
`['"','\\','\b','\f','\n','\r','\t']` and those in the range `[0x0020 - 0x007f]`

**Note:** Unencoded strings should be used with caution, as Unicode values may
not be transmitted correctly.

## Advanced settings

### IPv4 Addresses representation

When working with web applications, encoding IP addresses into different
formats can be crucial for testing, validation, and security purposes. The
cheat sheet supports standard IPv4 address as attacker IP input and returns
an array of encoded representations, including octal, hexadecimal, binary,
and decimal formats. It also converts an IPv4 address into its IPv6-mapped
address format.

Encoding Details:

- Octal: Each segment of the IP address is converted to an octal number
and padded to 4 digits. For example, the loopback IP address 127.0.0.1
would be represented as `0177.0000.0000.0001`
- Hexadecimal: Each segment is converted to a hexadecimal number, prefixed
with 0x, and padded to 2 digits. The same loopback IP address would be
`0x7F.0x00.0x00.0x01`
- Binary: Each segment is converted to an 8-bit binary number. The example
IP address would be `01111111.00000000.00000000.00000001`
- Partial Decimal: Combines the third and fourth parts of the IP address
into a single decimal number: `127.0.1`
- DWORD Notation: The entire IP address is converted into an unsigned
32-bit integer: `2130706433`
- DWORD Notation with overflow: The result from the previous conversion is
added to 2^32 \* 10 = `45080379393`
- IPv6 Mapped Address: Converts the IPv4 segments into hexadecimal and
formats them into a standard IPv6-mapped address. The loopback IP address can be represented as `[::FFFF:7F00:0001]` or `::FFFF:127.0.0.1`

### Normalization

The wordlists include numerous payloads that exploit Unicode string
normalization. For instance, the normalization of the following characters results in an empty string:

- [ZeroWidthSpace, NegativeVeryThinSpace, NegativeThinSpace, NegativeMediumSpace, NegativeThickSpace](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet#id=a72c5cf60d09c89718bcae7129a21fa21d72ee0a)
- [Word Joiner (U+2060) (& NoBreak;)](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet#id=c420c74fcd31811b4edf3a681b8e7b676a01eb2a)
- [Soft Hyphen Character U+00AD (&shy;)](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet#id=e73aa1dc3d1e050be2108a6c73362c35cd9b89b2)

These techniques can be used to bypass Web Application Firewalls (WAFs).

Another example of an allowed domain bypass occurs when a validation regular
expression permits multiline strings. For instance, if the regex
^allowed\_domain$ is used, the following can bypass the validation:

- [attacker\_domain(U+2028)allowed\_domain](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet#id=9b1cb80212d530707269740ff78c2904885e4bb2) (Line Separator)
- [attacker\_domain(U+2029)allowed\_domain](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet#id=db71091f2fac46753094e03913880af31dd36fec) (Paragraph Separator)

## Credits

This cheat sheet wouldn't be possible without the web security community who
share their research. Big thanks to:
[Gareth Heyes](https://x.com/garethheyes),
[James Kettle](https://x.com/albinowax),
[Jann Horn](https://infosec.exchange/@jann),
[Liv Matan](https://x.com/terminatorLM),
[Takeshi Terada](https://github.com/t-tera),
[Orange Tsai](https://x.com/orange_8361),
[Nicolas Grégoire](https://x.com/Agarri_FR).

We published all payloads at our GitHub account [https://github.com/PortSwigger/url-cheatsheet-data](https://github.com/PortSwigger/url-cheatsheet-data), so you can contribute to this cheat sheet by creating a
[new issue](https://github.com/PortSwigger/url-cheatsheet-data/issues)
or updating the JSON files and submitting a
[pull request](https://github.com/PortSwigger/url-cheatsheet-data/pulls).

We look forward to your interesting discoveries using our new
[URL validation bypass cheat sheet](https://portswigger.net/web-security/ssrf/url-validation-bypass-cheat-sheet)!

[SSRF](https://portswigger.net/research/ssrf) [CORS](https://portswigger.net/research/cors) [Zakhar Favourites](https://portswigger.net/research/zakhar-fedotkin)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**The Fragile Lock:**\\
Novel Bypasses For SAML Authentication 10 December 2025The Fragile Lock:Novel Bypasses For SAML Authentication](https://portswigger.net/research/the-fragile-lock) [**WebSocket Turbo Intruder: Unearthing the WebSocket Goldmine** 17 September 2025WebSocket Turbo Intruder: Unearthing the WebSocket Goldmine](https://portswigger.net/research/websocket-turbo-intruder-unearthing-the-websocket-goldmine) [**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Drag and Pwnd: Leverage ASCII characters to exploit VS Code** 30 April 2025Drag and Pwnd: Leverage ASCII characters to exploit VS Code](https://portswigger.net/research/drag-and-pwnd-leverage-ascii-characters-to-exploit-vs-code)