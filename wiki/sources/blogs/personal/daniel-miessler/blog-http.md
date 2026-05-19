---
source: daniel-miessler
source_url: https://danielmiessler.com/blog/http
title: "A Security-focused HTTP Primer | Daniel Miessler"
description: "What follows is a primer on the key security-oriented characteristics of the HTTP protocol. It’s a collection of a number of different sub-topics, explain"
---

What follows is a primer on the key security-oriented characteristics of the HTTP protocol. It’s a collection of a number of different sub-topics, [explained in my own way](https://danielmiessler.com/study/?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer&last_resource_guid=Post%3A22e3ce73-cb28-47a3-982f-21a006d2b227) >, for the purpose of having a single reference point when needed.

Message-based You make a request, you get a response.

Line-based Lines are quite significant in HTTP. Each header is on an individual line (each line ends with a ), and a blank line separates the header section from the optional body section.

Stateless HTTP doesn’t have the concept of state built-in, which is why things like cookies are used to track users within and across sessions.

Query Strings (?) A query string is defined by using the question mark (?) character after the URL being requested, and it defines what is being sent to the web application for processing. They are typically used to pass the contents of HTML forms, and are encoded using name:value pairs.http://google.com/search?query=mysearch

Parameters (something=something) In the request above the parameter is the "query" value–presumably indicating it’s what’s being searched for. It is followed by an equals sign (=) and then the value of the parameter.http://google.com/search?q=mysearch

The Ampersand (&) Ampersands are used to separate a list of parameters being sent to the same form, e.g. sending a query value, a language, and a verbose value to a search form.http://google.com/search?q=mysearch&lang=en&verbose=1

[ Ampersands are not mentioned in the HTTP spec itself; they are used as a matter of convention. ]

URL encoding seems more tricky than it is. It’s basically a workaround for a single rule in RFC 1738, which states that:

…Only alphanumerics [0-9a-zA-Z], the special characters "$-_.+!*'()," [not including the quotes – ed], and reserved characters used for their reserved purposes may be used unencoded within a URL.

The issue is that humans are inclined to use far more than just those characters, so we need some way of getting the larger range of characters transformed into the smaller, approved set. That’s what URL Encoding does. As mentioned [here](http://www.blooberry.com/indexdot/html/topics/urlencoding.htm?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer) > in a most excellent piece on the topic, there are a few basic groups of characters that need to be encoded:

**ASCII Control Characters:** because they’re not printable.

**Non-ASCII Characters:** because they’re not in the approved set (see the requirement above from RFC 1738). This includes the upper portion of the ISO-Latin character set (see [my encoding primer](https://danielmiessler.com/study/encoding/?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer&last_resource_guid=Post%3A22e3ce73-cb28-47a3-982f-21a006d2b227) > to learn more about character sets)

**Reserved Characters:** these are kind of like system variables in programming–they mean something within URLs, so they can’t be used outside of that meaning.

Dollar ("$")

Ampersand ("&")

Plus ("+")

Comma (",")

Forward slash/Virgule ("/")

Colon (":")

Semi-colon (";")

Equals ("=")

Question mark ("?")

‘At’ symbol ("@")

Space ( )

Quotes ("")

Less Than and Greater Than Symbols (<>)

Pound (#)

Percent (%)

Curly Braces ({})

The Pipe Symbol (|)

Backslash ()

Caret (^)

Tilde (~)

Square Brackets ([ ])

Backtick (`)

For any of these characters listed that can’t (or shouldn’t be) be put in a URL natively, the following encoding algorithm must be used to make it properly URL-encoded:

Find the [ISO 8859-1](https://danielmiessler.com/study/encoding/?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer&last_resource_guid=Post%3A22e3ce73-cb28-47a3-982f-21a006d2b227#iso8859) > code point for the character in question

Convert that code point to two characters of hex

Append a percent sign (%) to the front of the two hex characters

This is why you see so many instances of %20 in your URLs. That’s the URL-encoding for a space.

Here are the primary HTTP authentication types:

A user requests page protected by basic auth

Server sends back a 401 and a WWW-Authenticate header with the value of basic

The client takes his username and password–separated by a colon–and Base64 encodes it

The client then sends that value in an Authorization header, like so: Authorization: Basic BTxhZGRpbjpbcGAuINMlc2FtZC==

[ As the authors of The Web Application Hacker’s Handbook point out, Basic Authentication isn’t as bad as people make it out to be. Or, to be more precise, it’s no worse than Forms-based Authentication (the most common type). The reason for this is simple: Both send credentials in plain-text by default (actually, at least Basic offers Base64, whereas Forms-based isn’t even encoded). Either way, the only way for either protocol to even approach security is by adding SSL/TLS. ]

A user requests page protected by digest auth

The server sends back a 401 and a WWW-Authenticate header with the value of digest along with a nonce value and a realm value

The user concatenates his credentials with the nonce and realm and uses that as input to MD5 to produce one has (HA1)

The user concatenates the method and the URI to create a second MD5 hash (HA2)

The user then sends an Authorize header with the realm, nonce, URI, and the response–which is the MD5 of the two previous hashes combined

This is the most common type of web authentication, and it works by presenting a user with an HTML form for entering his/her username and password, and then sends those values to the server for verification. Some things to note:

The login information should be sent via POST rather than GET

The POST should be sent over HTTPS, not in the clear

Ideally, the entire login page itself should be HTTPS, not just the page that the credentials are being sent to

Shown below is a typical structure of a login form (this one from wordpress.com):

<form name="loginform" class="login-form" id="adminbarlogin" action="https://en.wordpress.com/wp-login.php" method="post">

Notice that the action URL is HTTPS, which means that the credentials entered into the form will be sent encrypted to that page.

IWA isn’t an authentication protocol itself, but rather a means of assigning a preferential order to various protocols, such as Kerberos, NTLMSSP, and SPNEGO.

This is being replaced with [Kerberos](https://en.wikipedia.org/wiki/Kerberos_(protocol)?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer) > now, but it’s still out there.

Client sends a Type 1 message telling the server what it supports in terms of key sizes, etc.

The server responds with its own list of supported values, as well as a pseudo-randomly generated challenge in a Type 2 message

The user concatenates his credentials with the challenge, implements MD5 and DES, and sends the response back to the server in a Type 3 message

There are four parts to an HTTP request:

**The Request Line:** the method, the URL, the version of the protocol

**The Request Headers [OPTIONAL]**: a series of lines (one per) in the format of name, colon(:), and the value of the header.

**A Blank Line:** required, worth mentioning by itself.

**The Request Body [OPTIONAL]:** Used in POST requests to send content to the server.

There are four parts to an HTTP response:

**The Response Line:** the version of the protocol, the status code, the status code description (OK, Not Found, etc.)

**The Response Headers:** a series of lines (one per) in the format of name, colon(:), and the value of the header.

**A Blank Line:** required, worth mentioning by itself.

**The Response Body:** contains the response from the server.

Here are the main categories:

100’s :: Informational

200’s :: Success

300’s :: Redirection

400’s :: Client Error

500’s :: Server Error

And here are some of the more common ones that are related to security:

* A more complete list of status codes can be found [here](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer) >.

Here are the main headers used by HTTP. For a more complete list (including non-security-related ones) look [here](https://en.wikipedia.org/wiki/List_of_HTTP_header_fields?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer) >.

* Additional, excellent information on caching can be found [here](https://www.mnot.net/cache_docs/?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer) >.

There are three primary considerations when looking at how HTTP proxies work: 1) whether you’re connecting to an HTTP vs. HTTPS resource, 2) whether the proxy is explicit or transparent, and 3) whether the proxy requires authentication.

**Connecting to an HTTP Resource** To connect to an HTTP resource through a proxy the client sends the full URL it wants to reach, including the protocol, host, and path. The proxy parses all that information and uses it to make its own new request on your behalf.

**Connecting to an HTTPS Resource** This won’t work for secure resources because an SSL/TLS handshake needs to occur, and we don’t generally want our corporate proxy seeing our bank details, or what have you. This is handled via the CONNECT method, which tells the proxy that it wants to be connected to the remote server at the TCP layer–not at the HTTP layer. The proxy returns a 200 response and from that point on you’re talking to the remote server, and you can then perform your handshake with the endpoint rather than the proxy in the middle.

**Dealing with Transparent Proxies and Proxy Authentication** The issue with transparent proxies is that a 407 can’t be used because the client doesn’t even know it’s dealing with a proxy.

**Proxies and Integrated Windows Authentication** Integrated Windows Authentication is one case that often has issues with proxies, but some vendors like BlueCoat have workarounds.

Cookies are used as a state mechanism, since none is built into HTTP natively. There are a few points worth noting regarding cookies:

Cookies are critical to security because they involve the sever setting information on the client, which it assumes the client will send back unmodified. Many developers make that assumption, and as a result they often place sensitive information within them which attacks can use to break the security of the application.

Cookies are set on the browser by the Set-Cookie header from the server.

Cookies are meant to be transparent, so they’re sent to the server every time the client makes a request.

The server can set multiple cookies by simply sending multiple Set-Cookie header values. All cookie values sent to the client via Set-Cookie are then combined into a single cookie, which is then sent to the server with a Cookie header. Each cookie is separated by a semicolon (;).

A major part of attacking web applications involves evaluating what sort of information is stored in cookies by the server, and determining whether it it can be deconstructed, manipulated, reconstructed, and re-sent to the server to gain unauthorized access.

For security purposes, the following values can be included with cookies within the Set-Cookie header: **expires** (creates a persistent cookie, as omitting this value will create a cookie that will expire when the browser closes); **HttpOnly** is supposed to prevent javascript from accessing the given cookie, but this is not foolproof; **secure** cookies will be sent only over HTTPS connections; **path** defines a scope of validity for a given cookie, e.g. /account/; domain specifies the domain that the cookie can be used within–must be the same or a parent of the domain the cookie came from.

In HTTP version 1.1 the Host: header is mandatory.

The referer (sic) header was misspelled in the original spec, and it remains so in the actual protocol today.

[URLs are actually a specific type of URI](https://danielmiessler.com/images/800px-URI_Euler_Diagram_no_lone_URIs.svg_.png?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer&last_resource_guid=Post%3A22e3ce73-cb28-47a3-982f-21a006d2b227) >, so they are not the same–despite what you may read or hear.

1 The one must-read book on Web Security is [The Web Application Hacker’s Handbook](https://support.portswigger.net/?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer) >, by Dafydd Stuttard and Marcus Pinto.2 Most everything you need to know about caching can be found [here](https://www.mnot.net/cache_docs/?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer) >.3 [Wikipedia’s HTTP article](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=a-security-focused-http-primer) >.