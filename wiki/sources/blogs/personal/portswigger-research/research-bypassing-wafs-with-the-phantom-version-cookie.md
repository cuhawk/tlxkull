---
source: portswigger-research
source_url: https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie
title: "Bypassing WAFs with the phantom $Version cookie | PortSwigger Research"
published: 2024-12-04T15:03:35
description: "HTTP cookies often control critical website features, but their long and convoluted history exposes them to parser discrepancy vulnerabilities. In this post, I'll explore some dangerous, lesser-known"
---

# Bypassing WAFs with the phantom $Version cookie

![Zakhar Fedotkin](https://portswigger.net/content/images/profiles/callout_zakhar_fedotkin_114px.png)

### [Zakhar Fedotkin](https://portswigger.net/research/zakhar-fedotkin)

Researcher

[@zakfedotkin](https://twitter.com/zakfedotkin)

- **Published:** Wednesday, 4 December 2024 at 15:03 UTC

- **Updated:** Monday, 30 June 2025 at 16:01 UTC


![Tossing cookies](https://portswigger.net/cms/images/92/21/a237-article-64488e2d-1d5d-45d1-92e2-395fd491f11a.png)HTTP cookies often control critical website features, but their long and convoluted history exposes them to parser discrepancy vulnerabilities. In this post, I'll explore some dangerous, lesser-known features of modern cookie parsers and show how they can be abused to bypass web application firewalls. This is the first part of a series of blog posts on cookie parsing.

## Downgrading cookie parsers with $Version

There have been many attempts to standardize HTTP cookies, starting with the first official standard: [RFC2109](https://datatracker.ietf.org/doc/html/rfc2109). Even though modern browsers do not support legacy RFCs, many web servers still do. Here's an example valid Cookie header:

`Cookie: $Version=1; foo="bar"; $Path="/"; $Domain=abc;`

$Version is a required attribute, identifying the version of the state management specification to which the cookie conforms. Other interesting attributes include $Domain and $Path, which we’ll discuss later. According to the standard, a Cookie value can include special characters like spaces, semicolons, and equal signs if they are enclosed in double quotes:

Many HTTP/1.1 header field values consist of words separated by LWS (Linear
White Space) or special characters. These special characters MUST be in a
quoted string to be used within a parameter value. - [RFC 2068](https://datatracker.ietf.org/doc/html/rfc2068#section-2.2).

Modern frameworks analyze that header in the following ways:

`Flask:		{"foo":"bar","$Version":"1","$Path":"/","$Domain":"abc"}
Django:		{"foo":"bar","$Version":"1","$Path":"/","$Domain":"abc"}
PHP:		{"foo":"\"bar\"","$Version":"1","$Path":"\"\/\"","$Domain":"abc"}
Ruby:		{"foo":"\"bar\"","$Version":"1","$Path":"\"\/\"","$Domain":"abc"}
Spring:		{ "foo": "\"bar\""}
SimpleCookie:	{ "foo": "bar"}
`

As we can see, the results are messy. This mess gives us a chance to look for security weaknesses. Let’s focus on Spring Boot Starter Web 2.x.x first. It uses Apache Tomcat v. 9.0.83 by default, which processes cookie headers in the following ways:

- It handles both RFC6265 and RFC2109 standards, defaulting to legacy parsing logic if a string starts with the special $Version attribute.

- It also supports the $Path and $Domain attributes, which may enable users to change reflected cookie attributes if they aren’t checked properly before responding.

- The parser will also unescape any character starting with backslash (\), as shown in the following example.


`Cookie: $Version=1; foo="\b\a\r"; $Path=/abc; $Domain=example.com =>
Set-Cookie: foo="bar"; Path=/abc; Domain=example.com`

Another good example is the Python SimpleCookie parser, which supports legacy cookie request attributes when followed by key-value pairs. This enables the injection of malicious cookie attributes in the same manner demonstrated previously. All Python-based frameworks (Flask, Django, etc.) allow quoted cookie values but don't recognize the magic strings, like $Version, treating it as a normal cookie name instead. They also automatically decode octal escape sequences within quoted strings as follows:

Any non-text character is translated into a 4 character sequence: a
forward-slash followed by the three-digit octal equivalent of the character. -

[Cookies.py](https://github.com/python/cpython/blob/6fc643674983e27ec5cc312f2e83468050d1d364/Lib/http/cookies.py#L149)

For example:

`"\012" <=> \n
"\015" <=> \r
"\073" <=> ;`

## Bypass Web Application Firewalls (WAFs)

Many WAFs are not equipped to detect the techniques described above, allowing malicious payloads to be hidden within quoted strings.

### Bypassing value analysis with quoted-string encoding

In addition, quoted cookies can facilitate injection vulnerabilities, such as [SQL injection](https://portswigger.net/web-security/sql-injection/blind%23what-is-blind-sql-injection) or [command injection](https://portswigger.net/web-security/os-command-injection%23ways-of-injecting-os-commands). These types of attacks often use special command separators - such as semicolons (;), commas (,), newline characters (\\n), and backslashes (\). While typically restricted in cookie values, these can sometimes be manipulated to trigger vulnerabilities. Implementing this type of quoted cookie encoding can be easily achieved using a Burp Suite extension with the [HttpHandler interface](https://github.com/PortSwigger/burp-extensions-montoya-api-examples/blob/main/httphandler/src/main/java/example/httphandler/MyHttpHandler.java):

`def handleHttpRequestToBeSent(requestToBeSent):
    result = "$Version=1; "
    for param in requestToBeSent.parameters:
        result += f"{param.name}=\""
        for char in param.value:
            result += f"\\{char}"
        result += "\"; "
    return continueWith(requestToBeSent.withAddedHeader("Cookie",result))`

For example, the Amazon Web Services WAF blocks any request that contains any parameter inside disallowed function:

`eval() => allowed
eval('test') => forbidden
"\e\v\a\l\(\'\t\e\s\t\'\)" => allowed
"\145\166\141\154\050\047\164\145\163\164\047\051" => allowed`

### Bypassing cookie-name blocklists

Another crucial aspect of RFC2109: a server should also accept a comma (,) as a separator between cookie values. This can be exploited to bypass simple WAF signatures that may not anticipate a cookie name being concealed within the value. Additionally, the specification permits any number of space or tab characters before or after the equal sign in an injected attribute-value pair, which could also be used to avoid the detection. Consider the Cookie header example:

`$Version=1; foo=bar, abc = qux => "abc": "qux"`

### Bypassing value analysis with cookie splitting

Like many other HTTP headers, the Cookie header can be sent multiple times in a single request. The way how a server handles multiple identical headers may then vary. For example, I sent following GET request:

`GET / HTTP/1.1
Host: example.com
Cookie: param1=value1;
Cookie: param2=value2;
`

And got the following back:

`Flask:		{ "param1": "value1", ",param2": "value2"}
Django:		{ "param1": "value1", ",param2": "value2"}
PHP:		{ "param1": "value1", ",_param2": "value2"}
Ruby:		{ "param1": "value1", ", param2": "value2"}
Spring:		{ "param1": "value1", "param2": "value2"}
`

As we can see, Ruby, PHP, and the Python frameworks Django and Flask combine headers into a single comma-separated string (with an optional space between parameters). Quoted cookie values are also supported, which allows hiding malicious payloads by using the Cookie header as a multiline header continuation.

Unfortunately, the quoted strings technique does not work with PHP and Ruby. To bypass the mentioned AWS signatures, you can use the following request:

`Cookie: name=eval('test') => forbidden
Cookie: name=eval('test//
Cookie: comment')

Resulting cookie: name=eval('test//, comment') => allowed`

### Automation using Burp Extensions

We've implemented the best of these techniques in [Param Miner](https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943) for you:

![](https://portswigger.net/cms/images/22/25/09a8-article-python.png)![](https://portswigger.net/cms/images/2a/90/d0c2-article-springs.png)

## Preventing vulnerabilities

You can take a range of steps to prevent parser discrepancy vulnerabilities in cookies, as follows:

- Ensure that legacy support for RFC2109 is disabled on the web server unless it is explicitly required.
- Validate all user inputs rigorously to identify and mitigate potentially dangerous data. This helps ensure that inputs are safe for processing within your application or when interacting with other system components.
- Avoid relying on assumptions about the presence or absence of specific characters in user inputs to reduce the risk of unexpected behavior.

## Want to learn more?

This blog post is just the first part of our exploration into cookie parsing logic. To learn how these techniques can be applied in real-world scenarios to escalate vulnerabilities, be sure to check out the [Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique).

For our latest blog posts and security insights, follow us on [X (formerly Twitter)](https://x.com/portswiggerres) and [Bluesky](https://bsky.app/profile/portswiggerres.bsky.social), and join the [official PortSwigger Discord](https://discord.com/invite/portswigger).

If you're interested in learning more about quoted cookies, take a look at
my earlier research on
[the Memcached Command Injections at Pylibmc](https://btlfry.gitlab.io/notes/posts/memcached-command-injections-at-pylibmc/)

If you're curious about invalid characters in cookie headers,I recommend April King's [Handling Cookies is a Minefield](https://grayduck.mn/2024/11/21/handling-cookies-is-a-minefield/) research.

[Cookies](https://portswigger.net/research/cookies) [WAF](https://portswigger.net/research/waf) [SQL Injection](https://portswigger.net/research/sql-injection) [XSS](https://portswigger.net/research/cross-site-scripting-research) [Zakhar Favourites](https://portswigger.net/research/zakhar-fedotkin) [cookie chaos](https://portswigger.net/research/cookie-chaos)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**The Fragile Lock:**\\
Novel Bypasses For SAML Authentication 10 December 2025The Fragile Lock:Novel Bypasses For SAML Authentication](https://portswigger.net/research/the-fragile-lock) [**WebSocket Turbo Intruder: Unearthing the WebSocket Goldmine** 17 September 2025WebSocket Turbo Intruder: Unearthing the WebSocket Goldmine](https://portswigger.net/research/websocket-turbo-intruder-unearthing-the-websocket-goldmine) [**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Drag and Pwnd: Leverage ASCII characters to exploit VS Code** 30 April 2025Drag and Pwnd: Leverage ASCII characters to exploit VS Code](https://portswigger.net/research/drag-and-pwnd-leverage-ascii-characters-to-exploit-vs-code)