---
source: portswigger-research
source_url: https://portswigger.net/research/template-injection
title: "Template Injection Research | PortSwigger Research"
description: "View the latest template injection research papers, tools, and techniques, from PortSwigger Research. Includes introductory and advanced content."
---

# Template Injection Research

Template injection occurs when user input is able to define template expressions. It's commonly classified into two types. These are known as Client side template injection and Server side template injection.

### Client Side Template Injection (CSTI)

Client side template injection usually occurs within the browser and HTML. It happens because a developer allows user input within a webpage, and allows them to define template expressions. This then allows an attacker to inject template expressions (which are simplified JavaScript) to exploit the web application. This is similar to how Cross Site Scripting works.

Some JavaScript frameworks, such as AngularJS, have a sandbox - this prevents a developer from using certain objects that they weren't supposed to. In order for an attacker to exploit this, they need to find a way to "escape" the sandbox. This means gaining access to areas such as the document object, in order to exploit the web application.

### Client Side Template Injection Research

If you're looking for the latest techniques and vectors related to CSTI then we've got you covered. You can learn how we [broke the AngularJS sandbox step by step](https://portswigger.net/research/xss-without-html-client-side-template-injection-with-angularjs), and even try it out for yourself with our [interactive labs](https://portswigger.net/web-security/cross-site-scripting/contexts/angularjs-sandbox).

We'll show you how we [exploited real world applications](https://portswigger.net/research/adapting-angularjs-payloads-to-exploit-real-world-applications), even with severe restrictions in place. If you're stuck with how to bypass Content Security Policy (CSP), we have numerous posts which describe how to use CSTI to bypass it.

In 2017 we presented [DOM Based Angular Sandbox Escapes](https://www.youtube.com/watch?v=jlSI5aVTEIg), at BSides Manchester, which describes how to break the AngularJS sandbox.

### Server-Side Template Injection (SSTI)

Back in 2015, [PortSwigger discovered a groundbreaking technique](https://portswigger.net/research/server-side-template-injection) to exploit web applications. This is now commonly known as Server Side Template injection (SSTI). SSTI occurs at the server level - in a server side language such as PHP, and templating engines such as Twig.

SSTI happens when a developer allows user input to define template code. This then allows an attacker to inject their own template expression. This is similar to CSTI but typically has a greater impact, as successful exploitation can often lead to Remote Code Execution (RCE).

Some templating engines employ a sandbox - this tries to prevent access to dangerous objects that can access the filesystem, or execute arbitrary code. This often makes it harder to exploit, but not impossible.

### Server Side Template Injection Research

Within our [template injection research](https://portswigger.net/research/server-side-template-injection), we will show you how to detect the various templating engines from an injection. We've also demonstrated how to [exploit those templating engines](https://portswigger.net/research/adapting-angularjs-payloads-to-exploit-real-world-applications) once you've detected them.

If you're newer to the topic, there are some great labs on SSTI to help you learn - and collect high impact bounties when testing real web applications.

We presented [Server-Side Template Injection: RCE for the Modern Webapp](https://www.youtube.com/watch?v=3cT0uE7Y87s) at Black Hat USA. This led to a flood of high impact bug bounty reports, both from us and the community.

## Template Injection Research Articles

[**DOM based AngularJS sandbox escapes** 11 May 2017DOM based AngularJS sandbox escapes](https://portswigger.net/research/dom-based-angularjs-sandbox-escapes) [**Adapting AngularJS payloads to exploit real world applications** 25 April 2016Adapting AngularJS payloads to exploit real world applications](https://portswigger.net/research/adapting-angularjs-payloads-to-exploit-real-world-applications) [**XSS without HTML: Client-Side Template Injection with AngularJS** 27 January 2016XSS without HTML: Client-Side Template Injection with AngularJS](https://portswigger.net/research/xss-without-html-client-side-template-injection-with-angularjs) [**Server-Side Template Injection** 05 August 2015Server-Side Template Injection](https://portswigger.net/research/server-side-template-injection)