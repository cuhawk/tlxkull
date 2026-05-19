---
source: portswigger-research
source_url: https://portswigger.net/research/alert-is-dead-long-live-print
title: "alert() is dead, long live print() | PortSwigger Research"
published: 2021-07-02T13:27:58
description: "Cross-Site Scripting and the alert() function have gone hand in hand for decades. Want to prove you can execute arbitrary JavaScript? Pop an alert. Want to find an XSS vulnerability the lazy way? Inje"
---

# alert() is dead, long live print()

![James Kettle](https://portswigger.net/content/images/profiles/callout_james_kettle_112px.png)

### [James Kettle](https://portswigger.net/research/james-kettle)

Director of Research

[@albinowax](https://twitter.com/albinowax)

- **Published:** Friday, 2 July 2021 at 13:27 UTC

- **Updated:** Monday, 5 July 2021 at 10:03 UTC


![](https://portswigger.net/cms/images/05/c9/ee0b-article-alert-print-article_(1).png)

[Cross-Site Scripting](https://portswigger.net/web-security/cross-site-scripting) and the alert() function have gone hand in hand for decades. Want to prove you can execute arbitrary JavaScript? Pop an alert. Want to find an XSS vulnerability the lazy way? Inject alert()-invoking payloads everywhere and see if anything pops up.

However, there's trouble brewing on the horizon. Malicious adverts have been abusing our beloved alert to distract and social engineer visitors from inside their iframe. Google Chrome has decided to tackle this by [disabling alert for cross-domain iframes](https://chromestatus.com/feature/5148698084376576). Cross-domain iframes are often built into websites deliberately, and are also a near-essential component of [certain relatively advanced XSS attacks](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source).

Once Chrome 92 lands on 20th July 2021, XSS vulnerabilities inside cross-domain iframes will:

- No longer enable alert-based PoCs.
- Be invisible to anyone using alert-based detection techniques.

What next? The obvious workaround is to use prompt or confirm, but unfortunately Chrome's mitigation blocks all dialogs. Triggering a [DNS pingback](https://portswigger.net/research/hunting-asynchronous-vulnerabilities) to a listener, [OAST-style](https://portswigger.net/burp/application-security-testing/oast) is another potential approach, but less suitable as a PoC due to the config requirements. We also ruled out console.log() as console functions are often proxied or disabled by JavaScript obfuscators.

It's quite funny that this "protection" against showing dialogs cross domain blocks alerts and prompts but as [Yosuke Hasegawa pointed out](https://twitter.com/hasegawayosuke/status/1410963117236916227) they forgot about basic authentication. This works in the current version of canary. It's likely to be blocked in future though.

We needed an alert-alternative that was:

- Simple, setup-free and easy to remember
- Highly visible, even when executed in an invisible iframe

After weeks of intensive research, we're thrilled to bring you...

## print()

![](https://portswigger.net/cms/images/5d/6a/cb54-article-print-cropped.png)

We will be updating our Web Security Academy labs to support print() based solutions shortly. The [XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) will also be updated to reflect the new print() payloads when using cross domain iframes. We'll keep using alert when there's no iframes involved... for now.

Long live print!

\- Gareth & James

[XSS](https://portswigger.net/research/cross-site-scripting-research)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)