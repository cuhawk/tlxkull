---
source: portswigger-research
source_url: https://portswigger.net/research/new-exotic-events-in-the-xss-cheat-sheet
title: "onwebkitplaybacktargetavailabilitychanged?! New exotic events in the XSS cheat sheet | PortSwigger Research"
published: 2024-06-11T14:58:29
description: "The power of our XSS cheat sheet is we get fantastic contributions from the web security community and this update is no exception. We had valuable contributions from Mozilla to remove events that no"
---

# onwebkitplaybacktargetavailabilitychanged?! New exotic events in the XSS cheat sheet

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Tuesday, 11 June 2024 at 14:58 UTC

- **Updated:** Tuesday, 11 June 2024 at 14:58 UTC


The power of our
[XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) is we get fantastic contributions from the web security community and this update is no exception. We had valuable contributions from Mozilla to remove events that no longer work with the marquee tag on Firefox.

There was a wonderfully obscure Safari only vector that used the event
[onwebkitplaybacktargetavailabilitychanged](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet#onwebkitplaybacktargetavailabilitychanged) from
[@amirmsafari](https://x.com/amirmsafari) that works on audio and video tags:

![](https://portswigger.net/cms/images/25/45/bc12-article-onwebkitplaybacktargetavailabilitychanged.png)

We had a submission from
[@Wcraft-log](https://github.com/wcraft-log) with the
[onpointercancel](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet#onpointercancel) event that requires heavy user interaction:

`<xss onpointercancel=alert(1)>XSS</xss>`

[@Filipnyquist](https://github.com/filipnyquist) pointed out that we didn't document that pretty much every element can now use the
[autofocus attribute.](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet#onfocus(autofocus)) This was discovered earlier by
[@RenwaX23](https://x.com/RenwaX23) and
[@lbherrera\_](https://x.com/lbherrera_).

`<xss onfocus=alert(1) autofocus tabindex=1>`

Finally we had a submission from
[@zhenwarx](https://twitter.com/zhenwarx) that showed there are a bunch of webkit events we missed that require user interaction with the trackpad.

`
<xss onwebkitmouseforceup=alert(1)>XSS</xss>
<xss onwebkitmouseforcewillbegin=alert(1)>XSS</xss>
<xss onwebkitmouseforceup=alert(1)>XSS</xss>
<xss onwebkitmouseforcedown=alert(1)>XSS</xss>
<xss onwebkitmouseforcechanged=alert(1)>XSS</xss>
`

Big thanks to the web security community for keeping the
[XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) up to date with the latest [XSS](https://portswigger.net/web-security/cross-site-scripting) vectors. If you would like to contribute please
[raise an issue](https://github.com/PortSwigger/xss-cheatsheet-data/issues) or a
[PR](https://github.com/PortSwigger/xss-cheatsheet-data/pulls).

Note: If you are wondering what we use to generate code snippet images. We use the excellent online tool
[Ray.so](http://ray.so/).

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[05 February 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) [06 January 2026](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025-nominations-open) [**The Fragile Lock:**\\
Novel Bypasses For SAML Authentication 10 December 2025The Fragile Lock:Novel Bypasses For SAML Authentication](https://portswigger.net/research/the-fragile-lock) [**Introducing HTTP Anomaly Rank** 11 November 2025Introducing HTTP Anomaly Rank](https://portswigger.net/research/introducing-http-anomaly-rank)