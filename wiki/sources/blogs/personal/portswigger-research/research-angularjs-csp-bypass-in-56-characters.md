---
source: portswigger-research
source_url: https://portswigger.net/research/angularjs-csp-bypass-in-56-characters
title: "AngularJS CSP bypass in 56 characters | PortSwigger Research"
published: 2019-10-14T13:04:06
description: "Often when you are testing websites you might encounter a length restriction on the input you are testing, that's why it's important to reduce the length of your vector as much as possible and of cour"
---

# AngularJS CSP bypass in 56 characters

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Monday, 14 October 2019 at 13:04 UTC

- **Updated:** Thursday, 12 January 2023 at 08:36 UTC


![Picture of a clamp squeezing a CSP bypass vector](https://portswigger.net/cms/images/64/89/5bf35cb90b6a-article-csp-bypass_article.png)

Often when you are testing websites you might encounter a length restriction on the input you are testing, that's why it's important to reduce the length of your vector as much as possible and of course it's really fun too.

When I did my [XSS magic tricks](https://www.slideshare.net/GarethHeyes/xss-magic-tricks) talk at [Allstars](https://ams.globalappsec.org/program/allstars) I presented a technique to bypass [CSP](https://portswigger.net/web-security/cross-site-scripting/content-security-policy) using [AngularJS](https://portswigger.net/web-security/cross-site-scripting/contexts/client-side-template-injection) in 63 characters:

`<input id=x ng-focus=$event.path|orderBy:'CSS&&[1].map(alert)'>`

It works by using the path property in Chrome which is an array of DOM objects which also contains the window object as the last element. The pipe character in AngularJS signifies a filter operation so the path array is sent to the orderBy filter and this accepts an expression. Then when the expression is executed the context in which it executes in the current element of the array. I then use the `CSS` property to detect when the array element is currently using the last element which is window. Then I use the map function to execute the `alert` function because the sandbox will detect window if calling `alert` as a normal function call. The vector is below:

I challenged the audience to reduce it further and [Erlend Oftedal](https://twitter.com/webtonull) managed to do it by replacing the `CSS` property with "x" which is the ID of the injected input element. This works because "x" will be a global property of window and thus can be used to detect the window object. See below:

`<input id=x ng-focus=$event.path|orderBy:'x&&[1].map(alert)'>`

I posted this vector on [Slackers](https://www.reddit.com/r/Slackers/comments/d9mwnt/angularjs_csp_bypass_can_you_make_it_shorter/) with a challenge to reduce it further. Taking up the challenge myself, I thought of ways to call `alert` without triggering AngularJS window detection. I came up with using an array and the `pop` method:

`<input id=x ng-focus=$event.path|orderBy:'x&&[alert].pop()(1)'>`

This payload is the same length as the original. But wait - AngularJS allows you to call undefined functions silently without throwing exceptions. So I could reduce the payload by removing the `&&` and property check:

`<input id=x ng-focus=$event.path|orderBy:'[alert].pop()(1)'>`

Still determined to reduce it further I tried using an array without the `pop` by referencing the first element and calling it:

`<input id=x ng-focus=$event.path|orderBy:'[alert][0](1)'>`

But this results in an illegal operation as the calling object is not window and JavaScript only lets us call `alert` on window. So I needed a way of calling `alert` as a direct call and maintaining the reference to window whilst still avoiding AngularJS's window check. Finally I came up with this simple but elegant method - using an assignment evades AngularJS's window object detection:

`<input id=x ng-focus=$event.path|orderBy:'(y=alert)(1)'>`

[AngularJS CSP bypass PoC](http://portswigger-labs.net/xss/angularjs.php?type=reflected&csp=1&version=1.4.5&x=%3Cinput%20id=x%20ng-focus=$event.path|orderBy:%27(y=alert)(1)%27%3E#x)

## Update...

Since Chrome 109 the path property has been removed. The workaround is to use composedPath() instead.

`<input id=x ng-focus=$event.composedPath()|orderBy:'(y=alert)(1)'>`

[AngularJS CSP bypass PoC](http://portswigger-labs.net/xss/angularjs.php?type=reflected&csp=1&version=1.4.5&x=%3Cinput%20id=x%20ng-focus=$event.composedPath()|orderBy:%27(y=alert)(1)%27%3E#x)

[angularjs](https://portswigger.net/research/angularjs) [csp](https://portswigger.net/research/csp) [JavaScript](https://portswigger.net/research/javascript)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Using form hijacking to bypass CSP** 05 March 2024Using form hijacking to bypass CSP](https://portswigger.net/research/using-form-hijacking-to-bypass-csp) [**Bypassing CSP via DOM clobbering** 05 June 2023Bypassing CSP via DOM clobbering](https://portswigger.net/research/bypassing-csp-via-dom-clobbering) [**Ambushed by AngularJS: a hidden CSP bypass in Piwik PRO** 28 April 2023Ambushed by AngularJS: a hidden CSP bypass in Piwik PRO](https://portswigger.net/research/ambushed-by-angularjs-a-hidden-csp-bypass-in-piwik-pro) [**Exploiting prototype pollution in Node without the filesystem** 23 March 2023Exploiting prototype pollution in Node without the filesystem](https://portswigger.net/research/exploiting-prototype-pollution-in-node-without-the-filesystem)