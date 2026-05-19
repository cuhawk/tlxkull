---
source: portswigger-research
source_url: https://portswigger.net/research/ambushed-by-angularjs-a-hidden-csp-bypass-in-piwik-pro
title: "Ambushed by AngularJS: a hidden CSP bypass in Piwik PRO | PortSwigger Research"
published: 2023-04-28T12:00:00
description: "Any individual website component can undermine the security of the entire site, and analytics platforms are no exception. With this in mind, we decided to do a quick audit of Piwik PRO to make sure it"
---

# Ambushed by AngularJS: a hidden CSP bypass in Piwik PRO

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Friday, 28 April 2023 at 12:00 UTC

- **Updated:** Friday, 28 April 2023 at 12:31 UTC


![A picture of AngularJS style tribes people surrounding an CSP bypass vector in a pit](https://portswigger.net/cms/images/25/8d/ed5e-article-ambushed_by_angularjs_final_blog-article_copy_7.png)

Any individual website component can undermine the security of the entire site, and analytics platforms are no exception. With this in mind, we decided to do a quick audit of Piwik PRO to make sure it was safe to deploy on portswigger.net.

I decided to look for client-side issues like [DOM XSS](https://portswigger.net/web-security/cross-site-scripting/dom-based) \- I focussed on this because we were introducing new script resources and therefore the most likely vector would be a DOM XSS vulnerability. The first thing I did was browse the site with [DOM Invader](https://portswigger.net/burp/documentation/desktop/tools/dom-invader) enabled and try injecting canaries - this yielded no results, which was good news. Next, I changed the DOM Invader canary to a blank value which enabled me to see all the sinks being used regardless of whether the canary was present or not. This is super useful for spotting stuff like document.write() and sure enough, there was a document.write call and various innerHTML assignments. I got a stack trace and inspected the document.write() call and noticed there was a debug flag… That led me to my next question - what does this do?

I added the flag to the URL and low and behold, an analytics debugger appeared. I tested that the document.write call wasn't vulnerable to XSS and then I pondered my next question: how was this debugger constructed? I started inspecting the debugger using devtools and immediately noticed an "ng-app" event. Jackpot, this is my [old friend AngularJS](https://portswigger.net/research/xss-without-html-client-side-template-injection-with-angularjs).

You might be wondering why I hit the jackpot. This is because [AngularJS](https://portswigger.net/web-security/cross-site-scripting/contexts/client-side-template-injection) has well known [script gadgets](https://www.blackhat.com/docs/us-17/thursday/us-17-Lekies-Dont-Trust-The-DOM-Bypassing-XSS-Mitigations-Via-Script-Gadgets.pdf) that can be used to bypass [Content Security Policy](https://portswigger.net/web-security/cross-site-scripting/content-security-policy) ( [CSP](https://portswigger.net/web-security/cross-site-scripting/content-security-policy)). A script gadget is some JavaScript code, usually from a library, that adds additional functionality to HTML or JavaScript. You can then use this gadget to bypass [CSP](https://portswigger.net/web-security/cross-site-scripting/content-security-policy), since the gadget already has JavaScript execution and is allowed by the policy. A good example of this is ng-focus in AngularJS - this event lets you execute a browser focus event but because ng-focus is non-standard it will be allowed by the CSP and executed by AngularJS itself.

Once you have identified that you have a AngularJS gadget there are two possible outcomes. You can either perform [client-side template injection](https://portswigger.net/web-security/cross-site-scripting/contexts/client-side-template-injection) (CSTI), or you have a CSP bypass. CSTI wasn't possible because it requires a HTML injection vulnerability in order to inject the script resources. This left a CSP bypass, which is important to fix because if your site has a HTML injection vulnerability then you can use the CSP bypass to escalate to XSS. I've done this in the past to find [XSS in PayPal](https://portswigger.net/research/finding-dom-polyglot-xss-in-paypal-the-easy-way).

On further inspection, the debugger seemed to use an iframe and loaded various script resources that were allowed by our CSP. I consulted our [XSS cheat](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet#angularjs-csp-bypasses) sheet to see the various CSP bypasses for AngularJS. I picked the first one and entered the following into the console:

``document.body.innerHTML=`<iframe srcdoc="<div lang=en ng-app=application ng-csp class=ng-scope>
<script src=https://ps.containers.piwik.pro/container-debugger/vendor.js></script>
<script src=https://ps.containers.piwik.pro/container-debugger/scripts.js></script>
<script src=https://ps.containers.piwik.pro/container-debugger/templates.cache.js></script>
<input autofocus ng-focus=$event.composedPath()|orderBy:'[].constructor.from([1],alert)'>
</div>
">```

Sure enough, this bypassed CSP completely. Because the scripts were allow listed, an attacker could inject AngularJS directives and a ng-focus event using composedPath() to get the window object in an array. The orderBy filter, which traverses that array and the scope of executing code, then eventually becomes the window object and Array.from() is used to call the alert function indirectly - this then bypasses CSP. We reported this issue to Piwik and they updated their CSP deployment instructions to address this vulnerability. They [fixed it](https://github.com/PiwikPRO/PPMS-PublicDocs/pull/984/files) by tightening the CSP to allow list a specific JavaScript file rather than the whole domain. They also used nonces for certain scripts, as this prevented an attacker from injecting their own AngularJS script resources.

This is now live - if you find something we missed please report it to [PortSwigger's](https://hackerone.com/portswigger) and [Piwik PRO's](https://piwik.pro/bug-bounty-program/) bug bounty programs.

## Timeline

2nd Mar 2023, 10:51 - Reported CSP bypass to Piwik

2nd Mar 2023, 11:20 - Acknowledged by Piwik

3rd Mar 2023, 13:09 - Vulnerability confirmed

7th Mar 2023, 12:24 - CSP [deployment instructions](https://developers.piwik.pro/en/latest/tag_manager/content_security_policy.html) updated to fix vulnerability

28th April 2023, 13:00 - Blog post released

[csp](https://portswigger.net/research/csp) [angularjs](https://portswigger.net/research/angularjs)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Using form hijacking to bypass CSP** 05 March 2024Using form hijacking to bypass CSP](https://portswigger.net/research/using-form-hijacking-to-bypass-csp) [**Bypassing CSP via DOM clobbering** 05 June 2023Bypassing CSP via DOM clobbering](https://portswigger.net/research/bypassing-csp-via-dom-clobbering) [**Stealing passwords from infosec Mastodon - without bypassing CSP** 15 November 2022Stealing passwords from infosec Mastodon - without bypassing CSP](https://portswigger.net/research/stealing-passwords-from-infosec-mastodon-without-bypassing-csp) [**Bypassing CSP with dangling iframes** 14 June 2022Bypassing CSP with dangling iframes](https://portswigger.net/research/bypassing-csp-with-dangling-iframes)